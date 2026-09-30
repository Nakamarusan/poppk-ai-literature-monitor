#!/usr/bin/env python3
"""Orchestrate discovery, resumable archive selection, and durable delivery."""
from __future__ import annotations

import argparse
import datetime as dt
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Sequence

from .core import (JST, UTC, Match, MonitorError, Paper, article_id, clean,
                   deduplicate, fingerprint, load_json, normalize_doi,
                   normalize_text, parse_date, save_json, screen, validate_config)
from .archive import diagnose, search_archive
from .delivery import deliver_pending, queue_notification, should_skip_retry
from .insights import rule_based_summary, summarize_research
from .reporting import article_record, render_report, update_catalog, write_report
from .sources import fetch_arxiv, fetch_crossref, fetch_europe_pmc

Fetcher = Callable[[dict[str, Any], dt.date, dt.date], list[Paper]]
_SOURCE_FETCHERS: dict[str, tuple[str, Fetcher]] = {
    "europe_pmc": ("Europe PMC", fetch_europe_pmc),
    "crossref": ("Crossref", fetch_crossref), "arxiv": ("arXiv", fetch_arxiv),
}
_GENERIC_VENUES = {"", "Europe PMC", "Crossref", "arXiv"}


@dataclass
class FetchResult:
    papers: list[Paper] = field(default_factory=list)
    counts: dict[str, int] = field(default_factory=dict)
    warnings: dict[str, str] = field(default_factory=dict)
    hidden_errors: dict[str, str] = field(default_factory=dict)
    coverage: dict[str, Any] = field(default_factory=dict)
    required_successes: int = 0


def _redact(message: Any) -> str:
    text = clean(message)
    if email := os.getenv("CONTACT_EMAIL", "").strip():
        text = text.replace(email, "[REDACTED]")
    return text[:1000]


def fetch_sources(config: dict[str, Any], state: dict[str, Any], since: dt.date,
                  until: dt.date, now: dt.datetime, *, historical: bool = False) -> FetchResult:
    """Retrieve recent records; preserve partial pages and report their limits."""
    result = FetchResult()
    dates = state.setdefault("source_attempt_dates", {})
    health = state.setdefault("source_health", {})
    keys = config["historical_fallback"]["sources"] if historical else _SOURCE_FETCHERS.keys()
    for key in keys:
        label, fetcher = _SOURCE_FETCHERS[key]
        settings = config["sources"][key]
        if not settings.get("enabled", True):
            continue
        once = settings.get("once_per_day", False) and not historical
        if once and dates.get(key) == until.isoformat():
            print(f"{label}: skipped; already attempted on {until}")
            continue
        optional = bool(settings.get("optional", False))
        try:
            papers = fetcher(config, since, until)
            result.papers.extend(papers)
            result.counts[label] = len(papers)
            result.required_successes += int(not optional)
            errors = getattr(papers, "errors", [])
            limited = getattr(papers, "limited_queries", 0)
            result.coverage[label] = {
                "pages": getattr(papers, "pages", 1),
                "limited_queries": limited, "failed_queries": len(errors),
            }
            if errors:
                result.warnings[label] = _redact(errors[0])
            health[key] = {"status": "partial" if errors else "ok",
                           "last_attempt_utc": now.isoformat(), "records": len(papers)}
            print(f"{label}: {len(papers)} records; capped queries {limited}")
        except Exception as exc:
            message = _redact(exc)
            health[key] = {"status": "error", "last_attempt_utc": now.isoformat(), "message": message}
            if optional and settings.get("silent_errors", True):
                result.hidden_errors[label] = message
                print(f"Optional source {label} unavailable: {message}", file=sys.stderr)
            else:
                result.warnings[label] = message
        finally:
            if once:
                dates[key] = until.isoformat()
    return result


def _known(match: Match, seen: dict[str, Any], catalog_ids: set[str]) -> bool:
    return article_id(match.paper) in catalog_ids or any(
        key in seen or key in catalog_ids for key in match.paper.keys())


def rank_matches(matches: Sequence[Match]) -> list[Match]:
    priority = {"High": 0, "Medium": 1, "Low": 2}
    return sorted(matches, key=lambda m: (priority.get(m.priority, 3), -m.score.total,
        not bool(clean(m.paper.abstract)), -(parse_date(m.paper.date) or dt.date.min).toordinal(),
        m.paper.title.casefold()))


def select_unseen(papers: Sequence[Paper], config: dict[str, Any], seen: dict[str, Any],
                  catalog_ids: set[str], limit: int) -> list[Match]:
    matches = [m for p in deduplicate(papers) if (m := screen(p, config))
               and not _known(m, seen, catalog_ids)]
    return rank_matches(matches)[:max(0, limit)]


def select_historical(papers: Sequence[Paper], config: dict[str, Any], seen: dict[str, Any],
                      catalog_ids: set[str], start: dt.date, until: dt.date,
                      limit: int) -> list[Match]:
    matches = select_unseen(papers, config, seen, catalog_ids, 10_000)
    require = config["historical_fallback"].get("require_abstract", True)
    return [m for m in matches if (date := parse_date(m.paper.date)) and start <= date <= until
            and (not require or bool(clean(m.paper.abstract)))][:max(0, limit)]


def _catalog_match(records: dict[str, dict[str, Any]], paper: Paper):
    key = article_id(paper)
    if key in records:
        return key, records[key]
    title = normalize_text(paper.title)
    return next(((key, item) for key, item in records.items()
                 if normalize_text(item.get("title", "")) == title), None)


def _enriched_paper(record: dict[str, Any], incoming: Paper) -> Paper:
    authors = record.get("authors", [])
    venue = record.get("venue", "")
    abstract = record.get("abstract", "")
    return Paper(
        sources=list(dict.fromkeys([*record.get("sources", []), *incoming.sources])),
        source_ids=incoming.source_ids, title=incoming.title or record.get("title", ""),
        authors=incoming.authors if len(incoming.authors) > len(authors) else authors,
        venue=incoming.venue if venue in _GENERIC_VENUES and incoming.venue not in _GENERIC_VENUES else venue or incoming.venue,
        date=record.get("publication_date", "") or incoming.date,
        doi=record.get("doi", "") or incoming.doi, url=record.get("url", "") or incoming.url,
        abstract=incoming.abstract if len(clean(incoming.abstract)) > len(clean(abstract)) else abstract,
        publication_type=incoming.publication_type)


def refresh_catalog(catalog: dict[str, Any], papers: Sequence[Paper], config: dict[str, Any]) -> int:
    """Enrich existing articles without creating another notification."""
    records = {r["id"]: r for r in catalog.get("articles", []) if isinstance(r, dict) and r.get("id")}
    refreshed = 0
    for incoming in deduplicate(papers):
        located = _catalog_match(records, incoming)
        if not located:
            continue
        old_id, record = located
        old_abstract = clean(record.get("abstract", ""))
        paper = _enriched_paper(record, incoming)
        match = screen(paper, config)
        if not match:
            continue
        changed = False
        key = article_id(paper)
        if key != old_id and key not in records:
            del records[old_id]
            record["id"] = key
            records[key] = record
            changed = True
        fields = {
            "title": paper.title, "authors": [a for a in paper.authors if clean(a)],
            "venue": paper.venue, "publication_date": paper.date, "doi": normalize_doi(paper.doi),
            "url": paper.url, "sources": paper.sources, "abstract": paper.abstract,
            "score": {"total": match.score.total, "priority": match.priority, "components": match.score.as_dict()},
            "evidence": {"basis": "abstract-only", "title_terms": match.title_hits,
                         "abstract_terms": match.abstract_hits, "terms": match.hits},
        }
        for name, value in fields.items():
            if record.get(name) != value:
                record[name] = value
                changed = True
        if len(clean(paper.abstract)) > len(old_abstract) and record.get("summary", {}).get("source", "") in {
            "", "No abstract available", "Abstract-only extractive summary", "Abstract-only rule-based summary"}:
            insight = rule_based_summary(match)
            record["summary"] = {k: getattr(insight, k) for k in
                ("prior_limitation", "contribution", "new_capability", "significance", "source")}
            changed = True
        refreshed += int(changed)
    catalog["articles"] = list(records.values())
    return refreshed


def update_state(state: dict[str, Any], selected: Sequence[Match], selection_type: str,
                 now: dt.datetime, warnings: dict[str, str], hidden_errors: dict[str, str]) -> None:
    """Retrieval success and selection date are deliberately separate from delivery."""
    timestamp = now.isoformat()
    for match in selected:
        record = {"title": match.paper.title, "doi": normalize_doi(match.paper.doi),
                  "selected_at": timestamp, "selection_type": selection_type}
        for key in match.paper.keys():
            state.setdefault("seen", {})[key] = record
    if selected:
        state["last_selection_date_jst"] = str(now.astimezone(JST).date())
    if hidden_errors:
        state["last_optional_source_errors"] = {s: {"message": v, "at_utc": timestamp} for s, v in hidden_errors.items()}
    else:
        state.pop("last_optional_source_errors", None)
    if warnings:
        state["last_partial_utc"] = timestamp
        state.pop("last_success_utc", None)
    else:
        state["last_success_utc"] = timestamp
        state.pop("last_partial_utc", None)


def known_identifiers(state: dict[str, Any], catalog: dict[str, Any]) -> set[str]:
    keys = set(state.get("seen", {}))
    for item in catalog.get("articles", []):
        keys.add(item["id"])
        keys.update(Paper([], [], item["title"], doi=item.get("doi", "")).keys())
    return keys


def _diagnostic_text(status: dict[str, Any]) -> str:
    """Place run diagnostics in the report header, outside article sections."""
    rows = ["## Selection and search coverage", "",
            f"Selection outcome: **{status['selection_status']}**",
            f"Papers selected in this run: **{status['selected_count']}**",
            "Retrieval success does not mean that a paper was selected or that all literature was searched.", ""]
    for source, counts in status["recent_coverage"].items():
        rows.append(f"- {source}: {counts['pages']} pages; {counts['limited_queries']} capped queries; {counts['failed_queries']} failed queries.")
    rows += ["", "Recent screening (one exclusion reason per unique record):"]
    rows.extend(f"- {key.replace('_', ' ')}: {value}" for key, value in status["recent_screening"].items())
    if archive := status["archive"]:
        rows += ["", f"Archive candidates available: {archive['eligible_candidates']}; "
                 f"unvisited/unfinished windows: {archive['pending_windows']}; "
                 f"completed windows: {archive['completed_windows']}.",
                 "Unfinished date windows are resumed on the next eligible run. API cursors are not stored across days."]
        if archive["screening"]:
            rows += ["", "Archive screening (per page; records can recur between queries):"]
            rows.extend(f"- {key.replace('_', ' ')}: {value}" for key, value in archive["screening"].items())
    return "\n".join(rows) + "\n\n"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=Path("config.json"))
    parser.add_argument("--state", type=Path, default=Path("state/seen.json"))
    parser.add_argument("--catalog", type=Path, default=Path("data/articles.json"))
    parser.add_argument("--report-dir", type=Path, default=Path("reports"))
    parser.add_argument("--lookback-days", type=int)
    parser.add_argument("--no-notify", action="store_true")
    args = parser.parse_args(argv)
    config = load_json(args.config)
    validate_config(config)
    state = load_json(args.state, {"schema_version": 2, "seen": {}})
    catalog = load_json(args.catalog, {"schema_version": 2, "last_scan_at": "", "articles": []})
    now = dt.datetime.now(UTC)
    today = now.astimezone(JST).date()
    stamp = now.astimezone(JST).strftime("%Y-%m-%d %H:%M JST")
    # Recover a selected-but-not-published record after interruption before I/O.
    pending_records = [r for notice in state.get("pending_notifications", []) for r in notice.get("records", [])]
    if pending_records:
        catalog = update_catalog(catalog, pending_records, catalog.get("last_scan_at", stamp))
        save_json(args.catalog, catalog)
    if os.getenv("SKIP_IF_SUCCESS_TODAY", "").casefold() == "true" and should_skip_retry(state, today):
        print(f"A paper was delivered successfully on {today}; retry skipped.")
        return 0
    lookback = args.lookback_days or int(os.getenv("LOOKBACK_DAYS") or config["monitor"]["lookback_days"])
    if not 1 <= lookback <= 90:
        raise MonitorError("lookback_days must be between 1 and 90")
    recent = fetch_sources(config, state, today - dt.timedelta(days=lookback - 1), today, now)
    refreshed = refresh_catalog(catalog, recent.papers, config)
    known = known_identifiers(state, catalog)
    fallback = config["historical_fallback"]
    start = dt.date(int(fallback["start_year"]), 1, 1)
    # Newly indexed records must still have an in-range publication date and
    # an abstract. Missing evidence is not replaced with a guessed summary.
    selected = select_historical(recent.papers, config, state["seen"], known,
                                 start, today, int(config["monitor"]["max_new_articles"]))
    selection_type = "new" if selected else "none"
    archive_counts, archive_warnings, archive_info = {}, {}, {}
    selected_today = state.get("last_selection_date_jst") == str(today) or any(
        r.get("reported_at", "")[:10] == str(today) for r in catalog.get("articles", []))
    if not selected and fallback.get("enabled", True) and not selected_today:
        archive = search_archive(config, args.state.with_name("archive.json"), known, today)
        archive_counts, archive_warnings, archive_info = archive.counts, archive.warnings, archive.diagnostics
        selected = select_historical(archive.papers, config, state["seen"], known,
                                     start, today, int(fallback["count"]))
        if selected:
            selection_type = "historical"
    warnings = {**recent.warnings, **{s: _redact(v) for s, v in archive_warnings.items()}}
    if recent.required_successes == 0:
        warnings["required_sources"] = "All enabled required recent-search sources failed."
    records = [article_record(m, summarize_research(m, config), selection_type, now) for m in selected]
    outcome = ("selected" if records else "already_selected_today" if selected_today else
               "source_error" if warnings else "search_pending" if archive_info.get("pending_windows", 0) else
               "no_eligible_candidate")
    status = {"checked_at": stamp, "source_status": "partial" if warnings else "ok",
              "selection_status": outcome, "selected_count": len(records),
              "selection_type": selection_type, "recent_coverage": recent.coverage,
              "recent_screening": diagnose(recent.papers, config, known, start, today, require_abstract=True),
              "archive": archive_info, "warnings": warnings,
              "delivery_status": "disabled" if args.no_notify else "pending"}
    body = render_report(records, now, recent.counts, archive_counts, warnings, start.year)
    body = body.replace("Run status:", "Source retrieval:", 1)
    insertion = body.find("\n## 1.")
    if insertion < 0:
        insertion = body.rfind("\n---\n")
    body = body[:insertion] + "\n" + _diagnostic_text(status) + body[insertion:]
    report_path = write_report(args.report_dir, body, now, len(records))
    update_state(state, selected, selection_type, now, warnings, recent.hidden_errors)
    if not args.no_notify:
        if records:
            marker = f"<!-- poppk-ai-alert:{selection_type}:{fingerprint(selected)} -->"
            label = "Archive methodology paper" if selection_type == "historical" else "New methodology paper"
            queue_notification(state, title=f"[PopPK × AI] {label}: {len(records)} — {today}",
                               body=body, marker=marker, date=str(today), kind="papers")
            next(n for n in state["pending_notifications"] if n["marker"] == marker)["records"] = records
        elif not selected_today and state.get("last_status_notice_date_jst") != str(today):
            queue_notification(state, title=f"[PopPK × AI] Search status — {today}",
                body=body, marker=f"<!-- poppk-ai-status:{today} -->", date=str(today), kind="status")
    # Save the outbox before the catalog. It contains enough information to
    # restore the catalog and retry an interrupted notification without loss.
    state["last_run"] = status
    save_json(args.state, state)
    catalog = update_catalog(catalog, records, stamp)
    catalog["run_status"] = status
    save_json(args.catalog, catalog)
    delivery_error = ""
    try:
        if not args.no_notify:
            urls = deliver_pending(state, args.state)
            status["notification_urls"] = urls
            status["delivery_status"] = "sent" if urls else "no_new_notice"
            for url in urls:
                print("Issue:", url)
    except MonitorError as exc:
        delivery_error = _redact(exc)
        status["delivery_status"] = "pending_retry"
        status["delivery_error"] = delivery_error
    state["last_run"] = status
    save_json(args.state, state)
    catalog["run_status"] = status
    save_json(args.catalog, catalog)
    save_json(args.report_dir / f"{today}.status.json", status)
    save_json(args.report_dir / "latest.status.json", status)
    print(f"Report: {report_path}; selected {len(selected)} ({selection_type}), refreshed {refreshed}, outcome {outcome}")
    if delivery_error:
        raise MonitorError(delivery_error)
    if recent.required_successes == 0:
        raise MonitorError("All enabled required recent-search sources failed")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except MonitorError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
