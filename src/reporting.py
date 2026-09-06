"""Canonical catalog, Markdown report, and GitHub Issue output."""

from __future__ import annotations

import copy
import datetime as dt
import os
import re
from pathlib import Path
from typing import Any, Sequence

from .core import (
    JST,
    Match,
    MonitorError,
    article_id,
    clean,
    normalize_doi,
    request_json,
)
from .insights import ResearchInsight

SELECTION_MARKER = "<!-- poppk-ai-selection -->"
_GENERIC_VENUES = {"", "Europe PMC", "Crossref", "arXiv"}
_ARTICLE_BLOCK = re.compile(
    r"(?ms)^##\s+\d+\.\s+.*?(?=^##\s+\d+\.\s+|\n---\n|\Z)"
)
_REPORT_FOOTER = "\n---\n"


def article_record(
    match: Match,
    insight: ResearchInsight,
    selection_type: str,
    now: dt.datetime,
) -> dict[str, Any]:
    """Convert one selected paper to the canonical catalog schema."""

    paper = match.paper
    return {
        "id": article_id(paper),
        "title": paper.title,
        "url": paper.url or (
            f"https://doi.org/{normalize_doi(paper.doi)}" if paper.doi else ""
        ),
        "authors": [author for author in paper.authors if clean(author)],
        "venue": paper.venue or ", ".join(paper.sources),
        "publication_date": paper.date,
        "doi": normalize_doi(paper.doi),
        "selection_type": selection_type,
        "reported_at": now.astimezone(JST).strftime("%Y-%m-%d %H:%M JST"),
        "sources": list(dict.fromkeys(paper.sources)),
        "score": {
            "total": match.score.total,
            "priority": match.priority,
            "components": match.score.as_dict(),
        },
        "evidence": {
            "basis": "abstract-only",
            "title_terms": match.title_hits,
            "abstract_terms": match.abstract_hits,
            "terms": match.hits,
        },
        "summary": {
            "prior_limitation": insight.prior_limitation,
            "contribution": insight.contribution,
            "new_capability": insight.new_capability,
            "significance": insight.significance,
            "source": insight.source,
        },
        "abstract": paper.abstract,
    }


def _first_value(*values: Any) -> Any:
    return next((value for value in values if value not in (None, "", [])), "")


def _merge_catalog_record(
    existing: dict[str, Any], incoming: dict[str, Any]
) -> dict[str, Any]:
    """Merge without replacing richer metadata with an incomplete record."""

    merged = copy.deepcopy(existing)
    merged["title"] = _first_value(incoming.get("title"), merged.get("title"))
    merged["doi"] = _first_value(incoming.get("doi"), merged.get("doi"))
    merged["url"] = _first_value(incoming.get("url"), merged.get("url"))
    merged["publication_date"] = _first_value(
        incoming.get("publication_date"), merged.get("publication_date")
    )

    incoming_authors = incoming.get("authors", [])
    if len(incoming_authors) > len(merged.get("authors", [])):
        merged["authors"] = incoming_authors

    current_venue = merged.get("venue", "")
    incoming_venue = incoming.get("venue", "")
    if current_venue in _GENERIC_VENUES and incoming_venue not in _GENERIC_VENUES:
        merged["venue"] = incoming_venue
    elif not current_venue:
        merged["venue"] = incoming_venue

    if len(clean(incoming.get("abstract", ""))) > len(
        clean(merged.get("abstract", ""))
    ):
        merged["abstract"] = incoming["abstract"]

    merged["sources"] = list(
        dict.fromkeys([*merged.get("sources", []), *incoming.get("sources", [])])
    )
    merged["selection_type"] = (
        "new"
        if "new" in {
            merged.get("selection_type"),
            incoming.get("selection_type"),
        }
        else incoming.get("selection_type", merged.get("selection_type", "historical"))
    )

    timestamps = [
        value
        for value in (merged.get("reported_at"), incoming.get("reported_at"))
        if value
    ]
    if timestamps:
        merged["reported_at"] = min(timestamps)

    # Scoring and evidence reflect the current configuration. Preserve an
    # informative summary if an incoming duplicate lacks an abstract.
    for field_name in ("score", "evidence"):
        if incoming.get(field_name):
            merged[field_name] = incoming[field_name]
    if incoming.get("summary", {}).get("source") != "No abstract available":
        merged["summary"] = incoming.get("summary", merged.get("summary", {}))

    return merged


def update_catalog(
    catalog: dict[str, Any],
    records: Sequence[dict[str, Any]],
    scan_at: str,
) -> dict[str, Any]:
    """Merge selected records by canonical identifier and update scan time."""

    merged = {
        article["id"]: copy.deepcopy(article)
        for article in catalog.get("articles", [])
        if isinstance(article, dict) and article.get("id")
    }
    for record in records:
        existing = merged.get(record["id"])
        merged[record["id"]] = (
            _merge_catalog_record(existing, record) if existing else copy.deepcopy(record)
        )

    articles = sorted(
        merged.values(),
        key=lambda article: (
            article.get("reported_at", ""),
            article.get("publication_date", ""),
            article.get("title", "").casefold(),
        ),
        reverse=True,
    )
    return {
        "schema_version": 2,
        "last_scan_at": scan_at,
        "articles": articles,
    }


def _score_line(record: dict[str, Any]) -> str:
    components = record["score"]["components"]
    return (
        f"{record['score']['total']}/100 — PK {components['pk']}, "
        f"AI {components['ai']}, method {components['method']}, "
        f"title intersection {components['intersection']}"
    )


def _markdown_text(value: str) -> str:
    """Escape the minimal characters that can break a Markdown link label."""

    return clean(value).replace("\\", "\\\\").replace("[", "\\[").replace("]", "\\]")


def render_report(
    records: Sequence[dict[str, Any]],
    now: dt.datetime,
    recent_counts: dict[str, int],
    archive_counts: dict[str, int],
    warnings: dict[str, str],
    archive_start_year: int,
) -> str:
    """Render the report used for both Markdown files and GitHub Issues."""

    new_count = sum(item["selection_type"] == "new" for item in records)
    archive_count = sum(
        item["selection_type"] == "historical" for item in records
    )
    status = "Partial" if warnings else "Complete"
    lines: list[str] = [SELECTION_MARKER, ""] if records else []
    lines.extend(
        (
            "# PopPK × AI Methodology Literature Report",
            "",
            f"Run time: {now.astimezone(JST):%Y-%m-%d %H:%M JST}",
            f"Run status: **{status}**",
            f"New articles: **{new_count}**",
            f"Archive selections: **{archive_count}** "
            f"(unreported papers published since {archive_start_year})",
            "",
            "Evidence basis: titles and abstracts are used for screening; "
            "all interpretations use the abstract only. Full text is not fetched.",
            "",
            "Source counts and warnings describe this run. Daily selections are "
            "retained when a later retry refreshes the report status.",
            "",
            "Recent-search records: "
            + ", ".join(
                f"{source} {count}"
                for source, count in sorted(recent_counts.items())
            ),
            "",
        )
    )

    if archive_counts:
        lines.extend(
            (
                "Archive-search records: "
                + ", ".join(
                    f"{source} {count}"
                    for source, count in sorted(archive_counts.items())
                ),
                "",
            )
        )

    if warnings:
        lines.extend(("## Source warnings", ""))
        lines.extend(
            f"- **{source}:** {message}"
            for source, message in sorted(warnings.items())
        )
        lines.append("")

    if not records:
        lines.extend(("No eligible, unreported paper was selected in this run.", ""))

    for number, record in enumerate(records, 1):
        summary = record["summary"]
        terms = record["evidence"]["terms"]
        authors = ", ".join(record["authors"][:8])
        if len(record["authors"]) > 8:
            authors += ", et al."

        abstract = clean(record["abstract"])
        if len(abstract) > 1400:
            abstract = abstract[:1399].rstrip() + "…"
        selection = (
            "New article"
            if record["selection_type"] == "new"
            else f"Archive article ({archive_start_year}+ fallback)"
        )
        title = _markdown_text(record["title"])
        heading = (
            f"## {number}. [{title}]({record['url']})"
            if record.get("url")
            else f"## {number}. {title}"
        )

        lines.extend(
            (
                heading,
                "",
                f"- **Selection:** {selection}",
                f"- **Authors:** {authors or 'Not available'}",
                f"- **Venue/source:** {record['venue'] or 'Not available'}",
                f"- **Publication date:** "
                f"{record['publication_date'] or 'Not available'}",
                f"- **DOI:** {record['doi'] or 'Not available'}",
                "",
                "### Abstract-only interpretation",
                "",
                f"- **Prior limitation:** {summary['prior_limitation']}",
                f"- **Methodological contribution:** {summary['contribution']}",
                f"- **What becomes possible:** {summary['new_capability']}",
                f"- **Why it matters:** {summary['significance']}",
                "",
                f"- **Relevance score:** {_score_line(record)}",
                f"- **Summary method:** {summary['source']}",
                "",
                "<details>",
                "<summary>Abstract and screening evidence</summary>",
                "",
                f"- **Abstract:** {abstract or 'Not available'}",
                f"- **PopPK/pharmacometrics terms:** "
                f"{', '.join(terms['pk']) or 'None'}",
                f"- **AI/ML terms:** {', '.join(terms['ai']) or 'None'}",
                f"- **Method terms:** {', '.join(terms['method']) or 'None'}",
                "",
                "</details>",
                "",
            )
        )

    lines.extend(
        (
            "---",
            "The relevance score measures topical and methodological alignment, "
            "not scientific quality, validity, or clinical utility.",
            "",
        )
    )
    return "\n".join(lines)


def _article_blocks(body: str) -> list[str]:
    """Extract and de-duplicate article sections from a daily report."""

    blocks: list[str] = []
    seen: set[str] = set()
    for match in _ARTICLE_BLOCK.finditer(body):
        block = match.group(0).strip()
        heading = block.splitlines()[0]
        key = re.sub(r"^##\s+\d+\.\s+", "", heading).casefold()
        if key not in seen:
            seen.add(key)
            blocks.append(block)
    return blocks


def _report_header(body: str) -> str:
    """Return run metadata without article sections or the empty-selection note."""

    text = body.replace(SELECTION_MARKER, "", 1).lstrip()
    article = _ARTICLE_BLOCK.search(text)
    footer = text.rfind(_REPORT_FOOTER)
    end = article.start() if article else footer if footer >= 0 else len(text)
    header = text[:end]
    header = re.sub(
        r"\n?No eligible, unreported paper was selected(?: in this run)?\.\n?",
        "\n",
        header,
    )
    return header.strip()


def _report_footer(body: str) -> str:
    position = body.rfind(_REPORT_FOOTER)
    return body[position + 1 :].strip() if position >= 0 else ""


def _renumber_blocks(blocks: Sequence[str]) -> list[str]:
    numbered: list[str] = []
    for number, block in enumerate(blocks, 1):
        numbered.append(
            re.sub(r"^##\s+\d+\.", f"## {number}.", block, count=1)
        )
    return numbered


def _update_selection_counts(header: str, blocks: Sequence[str]) -> str:
    new_count = sum("- **Selection:** New article" in block for block in blocks)
    archive_count = sum(
        "- **Selection:** Archive article" in block for block in blocks
    )
    header = re.sub(
        r"New articles: \*\*\d+\*\*",
        f"New articles: **{new_count}**",
        header,
    )
    return re.sub(
        r"Archive selections: \*\*\d+\*\*",
        f"Archive selections: **{archive_count}**",
        header,
    )


def _merge_daily_snapshot(previous: str, current: str) -> str:
    """Keep daily selections while replacing stale run status and warnings."""

    blocks = _article_blocks(previous)
    known = {
        re.sub(r"^##\s+\d+\.\s+", "", block.splitlines()[0]).casefold()
        for block in blocks
    }
    for block in _article_blocks(current):
        key = re.sub(r"^##\s+\d+\.\s+", "", block.splitlines()[0]).casefold()
        if key not in known:
            known.add(key)
            blocks.append(block)

    if not blocks:
        return current

    blocks = _renumber_blocks(blocks)
    header = _update_selection_counts(_report_header(current), blocks)
    footer = _report_footer(current)
    parts = [SELECTION_MARKER, "", header, "", "\n\n".join(blocks)]
    if footer:
        parts.extend(("", footer))
    return "\n".join(parts).rstrip() + "\n"


def write_report(
    report_dir: Path, body: str, now: dt.datetime, selected_count: int
) -> Path:
    """Write a current daily snapshot while preserving same-day selections.

    A retry replaces the run time, source counts, status, and warnings. Article
    sections already reported that day remain in the snapshot, so a recovery
    does not erase the paper that triggered the first notification.
    """

    report_dir.mkdir(parents=True, exist_ok=True)
    date = now.astimezone(JST).date().isoformat()
    archive = report_dir / f"{date}.md"
    stored = body

    if archive.exists():
        previous = archive.read_text(encoding="utf-8")
        stored = _merge_daily_snapshot(previous, body)
    elif selected_count and not body.startswith(SELECTION_MARKER):
        stored = f"{SELECTION_MARKER}\n\n{body}"

    archive.write_text(stored, encoding="utf-8")
    (report_dir / "latest.md").write_text(stored, encoding="utf-8")

    if summary_path := os.getenv("GITHUB_STEP_SUMMARY", ""):
        with Path(summary_path).open("a", encoding="utf-8") as stream:
            stream.write(body + "\n")
    return archive


def create_issue(
    title: str,
    body: str,
    marker: str,
    token: str,
    repository: str,
    owner: str,
) -> str:
    """Create one GitHub Issue unless its hidden marker already exists."""

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    endpoint = f"https://api.github.com/repos/{repository}/issues"
    issues = request_json(f"{endpoint}?state=all&per_page=100", headers=headers)
    for issue in issues if isinstance(issues, list) else []:
        if marker in str(issue.get("body") or ""):
            return clean(issue.get("html_url"))

    payload = {"title": title, "body": body, "assignees": [owner]}
    try:
        result = request_json(
            endpoint, method="POST", payload=payload, headers=headers, retries=1
        )
    except MonitorError as exc:
        if "HTTP 422" not in str(exc):
            raise
        payload.pop("assignees", None)
        result = request_json(
            endpoint, method="POST", payload=payload, headers=headers, retries=1
        )
    return clean(result.get("html_url"))
