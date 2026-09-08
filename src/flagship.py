"""One additional Science, Cell, or Nature paper per JST day.

The primary PopPK x AI monitor is unchanged. This module has its own selection
history and report, but shares seen identifiers to prevent duplicate alerts.
Findings use abstracts only; potential research uses are explicitly suggestions.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import os
import re
from dataclasses import asdict
from pathlib import Path
from typing import Any, Sequence
from urllib.parse import urlencode

from .core import (JST, UTC, Match, MonitorError, Paper, Score, article_id, clean,
                   load_json, normalize_doi, normalize_text, parse_date,
                   phrase_hits, request_json, save_json)
from .insights import summarize_research
from .reporting import create_issue

# Both the journal title and a print/electronic ISSN must match. A publisher
# name, DOI prefix, or the word "Nature" in an article title is not sufficient.
JOURNALS = {
    "Science": {"names": {"science", "science new york n y"},
                "issns": {"0036-8075", "1095-9203"}},
    "Cell": {"names": {"cell"}, "issns": {"0092-8674", "1097-4172"}},
    "Nature": {"names": {"nature"}, "issns": {"0028-0836", "1476-4687"}},
}
EXCLUDED_TYPES = ("review", "meta analysis", "editorial", "comment", "news",
                  "letter", "published erratum", "retracted publication")
RESEARCH_TYPES = ("journal article", "research article", "clinical trial",
                  "comparative study", "evaluation study", "validation study")
REVIEW_CUE = re.compile(
    r"\b(?:purpose of review|this (?:narrative |systematic |scoping )?review|"
    r"we (?:conducted|present|provide) a (?:narrative |systematic |scoping )?review)\b", re.I
)
API = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"


def validate_settings(settings: dict[str, Any]) -> None:
    """Validate the small research profile before making any requests."""
    for key, low, high in (("recent_days", 1, 90), ("start_year", 2020, 2100),
                           ("page_size", 1, 1000), ("max_pages", 1, 5),
                           ("archive_refresh_days", 1, 30)):
        value = settings.get(key)
        if type(value) is not int or not low <= value <= high:
            raise MonitorError(f"Invalid flagship setting: {key}")
    topics = settings.get("topics")
    if not isinstance(topics, list) or not topics:
        raise MonitorError("The flagship research profile requires topics")
    for topic in topics:
        if not all(clean(topic.get(key)) for key in ("name", "potential_use")):
            raise MonitorError("Each research topic requires a name and potential use")
        for key in ("terms", "context_terms"):
            values = topic.get(key)
            if not isinstance(values, list) or any(not isinstance(x, str) or not x.strip() for x in values):
                raise MonitorError(f"Invalid research topic {key}")
        if not topic["terms"] or type(topic.get("priority")) is not int or not 1 <= topic["priority"] <= 100:
            raise MonitorError("Each topic requires search terms and a priority from 1 to 100")


def journal_name(title: str, issns: Sequence[str]) -> str | None:
    normalized = normalize_text(title)
    identifiers = {clean(value).upper() for value in issns if value}
    for name, identity in JOURNALS.items():
        if normalized in identity["names"] and identifiers & identity["issns"]:
            return name
    return None


def parse_record(raw: dict[str, Any]) -> dict[str, Any] | None:
    """Accept research articles with verified flagship identity and abstracts."""
    journal = raw.get("journalInfo", {}).get("journal", {}) or raw.get("journalIssue", {}).get("journal", {})
    issns = [journal.get(key, "") for key in ("issn", "essn", "eissn")]
    name = journal_name(journal.get("title") or raw.get("journalTitle", ""), issns)
    types = raw.get("pubTypeList", {}).get("pubType", []) or raw.get("pubType", [])
    type_text = " ".join(types) if isinstance(types, list) else clean(types)
    abstract, title = clean(raw.get("abstractText")), clean(raw.get("title"))
    if not name or not title or not abstract:
        return None
    if phrase_hits(type_text, EXCLUDED_TYPES) or REVIEW_CUE.search(abstract):
        return None
    if not phrase_hits(type_text, RESEARCH_TYPES):
        return None
    if phrase_hits(title, ("correction", "retraction", "editorial")):
        return None
    doi = normalize_doi(raw.get("doi", ""))
    pmid = clean(raw.get("id"))
    if not (doi or pmid) or clean(raw.get("source", "MED")) != "MED":
        return None
    return {
        "id": f"doi:{doi}" if doi else f"pubmed:{pmid}",
        "title": title, "journal": name, "issns": [value for value in issns if value],
        "doi": doi, "source_id": f"MED:{pmid}",
        "url": f"https://doi.org/{doi}" if doi else f"https://europepmc.org/article/MED/{pmid}",
        "publication_date": clean(raw.get("firstPublicationDate")),
        "authors": [clean(a.get("fullName")) for a in raw.get("authorList", {}).get("author", []) if clean(a.get("fullName"))],
        "abstract": abstract, "publication_type": type_text,
    }


def as_paper(item: dict[str, Any]) -> Paper:
    return Paper(sources=["Europe PMC"], source_ids=[item.get("source_id", "")],
                 title=item["title"], authors=item.get("authors", []),
                 venue=item["journal"], date=item["publication_date"],
                 doi=item.get("doi", ""), url=item["url"], abstract=item["abstract"])


def research_connections(abstract: str, topics: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
    """Require abstract evidence, including context for broad biological terms."""
    matches = []
    for topic in topics:
        hits = phrase_hits(abstract, topic["terms"])
        context = phrase_hits(abstract, topic["context_terms"])
        if hits and (not topic["context_terms"] or context):
            matches.append({"topic": topic["name"], "priority": topic["priority"],
                            "matched_terms": hits + context,
                            "potential_use": topic["potential_use"]})
    return sorted(matches, key=lambda match: (-match["priority"], match["topic"]))


def choose_candidate(candidates: Sequence[dict[str, Any]], settings: dict[str, Any],
                     known: set[str], since: dt.date, until: dt.date) -> dict[str, Any] | None:
    """Rank topical fit first, then date. Return at most one unreported article."""
    eligible = {}
    for item in candidates:
        published = parse_date(item.get("publication_date", ""))
        if not published or not since <= published <= until:
            continue
        if not journal_name(item.get("journal", ""), item.get("issns", [])):
            continue
        paper = as_paper(item)
        if item["id"] in known or set(paper.keys()) & known:
            continue
        connections = research_connections(item["abstract"], settings["topics"])
        if connections:
            eligible[item["id"]] = {**item, "connections": connections}
    if not eligible:
        return None
    return min(eligible.values(), key=lambda item: (
        -item["connections"][0]["priority"], -min(len(item["connections"]), 3),
        -parse_date(item["publication_date"]).toordinal(), item["id"]))


def fetch_candidates(settings: dict[str, Any], since: dt.date, until: dt.date) -> list[dict[str, Any]]:
    """Fetch bounded, cursor-paginated metadata, never publisher full text."""
    issns = sorted({issn for journal in JOURNALS.values() for issn in journal["issns"]})
    terms = sorted({term for topic in settings["topics"] for term in topic["terms"]})
    journal_clause = " OR ".join(f"ISSN:{issn}" for issn in issns)
    topic_clause = " OR ".join('TITLE_ABS:"' + term.replace('"', '') + '"' for term in terms)
    query = f"({journal_clause}) AND ({topic_clause}) AND SRC:MED AND HAS_ABSTRACT:Y AND FIRST_PDATE:[{since} TO {until}]"
    cursor, visited, candidates = "*", set(), []
    for _ in range(settings["max_pages"]):
        params = {"query": query, "format": "json", "resultType": "core",
                  "pageSize": str(settings["page_size"]), "cursorMark": cursor,
                  "sort": "FIRST_PDATE_D desc"}
        payload = request_json(API + "?" + urlencode(params), retries=3)
        results = payload.get("resultList", {}).get("result")
        if not isinstance(results, list):
            raise MonitorError("Europe PMC returned no valid result list")
        candidates.extend(item for raw in results if (item := parse_record(raw)))
        visited.add(cursor)
        cursor = payload.get("nextCursorMark")
        if not results or not cursor or cursor in visited:
            break
    return candidates


def known_identifiers(root: Path, history: dict[str, Any]) -> set[str]:
    """Share exclusions with the primary monitor, not its daily selection limit."""
    primary = load_json(root / "data/articles.json", {"articles": []})
    seen = load_json(root / "state/seen.json", {"seen": {}})
    known = set(seen.get("seen", {}))
    for item in [*primary["articles"], *history.get("articles", [])]:
        known.add(item["id"])
        if item.get("doi"):
            known.add(f"doi:{normalize_doi(item['doi'])}")
        known.add(Paper([], [], item["title"]).title_key())
    return known


def render_spotlight(item: dict[str, Any]) -> str:
    """Keep paper findings separate from proposed research applications."""
    title = clean(item["title"]).replace("[", "\\[").replace("]", "\\]")
    lines = ["# Science · Cell · Nature — Research Spotlight", "",
             f"Selected: {item['reported_at']}", f"Journal: **{item['journal']}**",
             f"Published: {item['publication_date']}",
             f"Selection: {item['selection_type']} (one additional paper across all three journals)",
             "", f"## [{title}]({item['url']})", "",
             "Authors: " + (", ".join(item.get("authors", [])) or "Not available"),
             "DOI: " + (item.get("doi") or "Not available"), "",
             "## Abstract-only findings", ""]
    for key, label in (("prior_limitation", "Prior limitation"), ("contribution", "Contribution"),
                       ("new_capability", "What becomes possible"), ("significance", "Significance")):
        lines.append(f"- **{label}:** {item['summary'][key]}")
    lines += ["", "## Research connections — proposed uses, not paper findings", ""]
    for connection in item["connections"][:2]:
        lines += [f"### {connection['topic']}",
                  "Matched in the abstract: " + ", ".join(connection["matched_terms"]),
                  connection["potential_use"], ""]
    lines += ["These connections are rule-based research suggestions, not validated applications or clinical recommendations.",
              "", "Summary method: " + item["summary"]["source"],
              "Evidence: available abstract only. Full text and supplementary material are not fetched.", ""]
    return "\n".join(lines)


def notify_pending(history: dict[str, Any], disabled: bool) -> None:
    """Retry unsent notifications with stable markers without selecting again."""
    token, repo, owner = (os.getenv(key, "") for key in
                          ("GITHUB_TOKEN", "GITHUB_REPOSITORY", "GITHUB_REPOSITORY_OWNER"))
    if disabled or not all((token, repo, owner)):
        return
    for item in history["articles"]:
        if item.get("issue_url"):
            continue
        digest = hashlib.sha256(item["id"].encode()).hexdigest()[:16]
        marker = f"<!-- poppk-flagship:{digest} -->"
        try:
            item["issue_url"] = create_issue(
                f"[Research spotlight] {item['journal']} — {item['reported_at'][:10]}",
                f"{marker}\n\n@{owner}\n\n" + render_spotlight(item), marker, token, repo, owner)
        except MonitorError as exc:
            print(f"Spotlight notification deferred: {clean(exc)}")
            break


def run(root: Path, settings: dict[str, Any], monitor_config: dict[str, Any],
        now: dt.datetime, *, no_notify: bool = False) -> dict[str, Any]:
    """Select independently of the main monitor; source failure is non-fatal."""
    history_path, state_path = root / "data/flagship.json", root / "state/flagship.json"
    history = load_json(history_path, {"schema_version": 1, "articles": []})
    state = load_json(state_path, {})
    today, stamp = now.astimezone(JST).date(), now.astimezone(JST).strftime("%Y-%m-%d %H:%M JST")
    if not settings.get("enabled", True):
        return history
    # Catalog history is the durable day guard, even if the state write was interrupted.
    if any(item["reported_at"][:10] == today.isoformat() for item in history["articles"]):
        notify_pending(history, no_notify)
        save_json(history_path, history)
        return history

    known = known_identifiers(root, history)
    since = today - dt.timedelta(days=settings["recent_days"] - 1)
    start = dt.date(settings["start_year"], 1, 1)
    candidate, error, mode = None, "", "recent"
    try:
        recent = fetch_candidates(settings, since, today)
        candidate = choose_candidate(recent, settings, known, since, today)
        if candidate is None:
            cached_at = parse_date(state.get("archive_checked_at", ""))
            pool = state.get("archive_pool", [])
            candidate = choose_candidate(pool, settings, known, start, today)
            if candidate is None or not cached_at or (today - cached_at).days >= settings["archive_refresh_days"]:
                pool = fetch_candidates(settings, start, today)
                state.update(archive_pool=pool, archive_checked_at=today.isoformat())
                candidate = choose_candidate(pool, settings, known, start, today)
            mode = "archive"
    except MonitorError as exc:
        # Previously fetched abstracts remain usable during an index outage.
        error = clean(exc)
        if email := os.getenv("CONTACT_EMAIL", ""):
            error = error.replace(email, "[REDACTED]")
        candidate = choose_candidate(state.get("archive_pool", []), settings, known, start, today)
        mode = "cached archive"
        print(f"Spotlight source unavailable: {error}")

    status = "selected" if candidate else "source unavailable" if error else "no eligible match"
    history.update(last_checked_at=stamp, status=status)
    state.update(last_checked_at=stamp, last_status=status, last_source_error=error)
    if candidate:
        paper = as_paper(candidate)
        empty = {group: [] for group in ("pk", "ai", "method")}
        # Reuse only the abstract summarizer. The main 0–100 score is not applied.
        match = Match(paper, Score(0, 0, 0, 0), "", empty, empty)
        entry = {**candidate, "reported_at": stamp, "selection_type": mode,
                 "evidence_basis": "abstract-only",
                 "summary": asdict(summarize_research(match, monitor_config))}
        history["articles"].insert(0, entry)
        save_json(history_path, history)  # Write before external notification.
        reports = root / "reports/flagship"
        reports.mkdir(parents=True, exist_ok=True)
        body = render_spotlight(entry)
        (reports / f"{today}.md").write_text(body, encoding="utf-8")
        (reports / "latest.md").write_text(body, encoding="utf-8")
        if step_summary := os.getenv("GITHUB_STEP_SUMMARY", ""):
            with Path(step_summary).open("a", encoding="utf-8") as stream:
                stream.write("\n\n" + body)
        # Only add identifiers; preserve the primary monitor's status and day guard.
        primary_path = root / "state/seen.json"
        primary = load_json(primary_path, {"schema_version": 2, "seen": {}})
        for key in paper.keys():
            primary.setdefault("seen", {})[key] = {"title": paper.title, "doi": paper.doi,
                "notified_at": now.isoformat(), "selection_type": "flagship"}
        save_json(primary_path, primary)
    notify_pending(history, no_notify)
    save_json(history_path, history)
    save_json(state_path, state)
    print(f"Flagship spotlight: {status}; {len(history['articles'])} papers in its own archive")
    return history


def build_site(root: Path) -> dict[str, Any]:
    """Publish a separate catalog; never overwrite the primary article catalog."""
    history = load_json(root / "data/flagship.json", {"schema_version": 1, "articles": []})
    unique = {}
    for item in history["articles"]:
        if not journal_name(item.get("journal", ""), item.get("issns", [])) or item.get("evidence_basis") != "abstract-only":
            raise MonitorError("Invalid flagship identity or evidence policy in the catalog")
        if not item.get("abstract") or not item.get("summary") or not item.get("connections"):
            raise MonitorError("A flagship entry requires an abstract, summary, and research connection")
        unique[item["id"]] = item
    payload = {**history, "articles": sorted(unique.values(), key=lambda item: item["reported_at"], reverse=True)}
    payload["article_count"] = len(unique)
    save_json(root / "docs/flagship.json", payload)
    return payload


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--build-only", action="store_true")
    parser.add_argument("--no-notify", action="store_true")
    args = parser.parse_args(argv)
    if not args.build_only:
        settings = load_json(args.root / "flagship_config.json")
        validate_settings(settings)
        run(args.root, settings, load_json(args.root / "config.json"),
            dt.datetime.now(UTC), no_notify=args.no_notify)
    build_site(args.root)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except MonitorError as exc:
        print(f"ERROR: {exc}")
        raise SystemExit(1)
