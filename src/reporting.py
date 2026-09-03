"""Article catalog, Markdown report, and GitHub Issue output."""

from __future__ import annotations

import datetime as dt
import os
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


def article_record(
    match: Match,
    insight: ResearchInsight,
    selection_type: str,
    now: dt.datetime,
) -> dict[str, Any]:
    """Convert a selected paper into the canonical JSON catalog schema."""

    paper = match.paper
    return {
        "id": article_id(paper),
        "title": paper.title,
        "url": paper.url or (
            f"https://doi.org/{normalize_doi(paper.doi)}" if paper.doi else ""
        ),
        "authors": paper.authors,
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


def update_catalog(
    catalog: dict[str, Any],
    records: Sequence[dict[str, Any]],
    scan_at: str,
) -> dict[str, Any]:
    """Merge records by canonical identifier and update the last scan time."""

    merged = {
        article["id"]: article for article in catalog.get("articles", [])
    }
    for record in records:
        existing = merged.get(record["id"])
        if existing and len(existing.get("abstract", "")) > len(record["abstract"]):
            record["abstract"] = existing["abstract"]
        merged[record["id"]] = record

    return {
        "schema_version": 2,
        "last_scan_at": scan_at,
        "articles": list(merged.values()),
    }


def _score_line(record: dict[str, Any]) -> str:
    components = record["score"]["components"]
    return (
        f"{record['score']['total']}/100 — PK {components['pk']}, "
        f"AI {components['ai']}, method {components['method']}, "
        f"title intersection {components['intersection']}"
    )


def render_report(
    records: Sequence[dict[str, Any]],
    now: dt.datetime,
    recent_counts: dict[str, int],
    archive_counts: dict[str, int],
    warnings: dict[str, str],
    archive_start_year: int,
) -> str:
    """Render the human-readable report used in both Markdown and Issues."""

    new_count = sum(item["selection_type"] == "new" for item in records)
    archive_count = sum(
        item["selection_type"] == "historical" for item in records
    )
    lines: list[str] = [SELECTION_MARKER, ""] if records else []
    lines.extend(
        (
            "# PopPK × AI Methodology Literature Report",
            "",
            f"Run time: {now.astimezone(JST):%Y-%m-%d %H:%M JST}",
            f"New articles: **{new_count}**",
            f"Archive selections: **{archive_count}** "
            f"(unreported papers published since {archive_start_year})",
            "",
            "Evidence basis: titles and abstracts are used for screening; "
            "all interpretations use the abstract only. Full text is not fetched.",
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
        lines.extend(("No eligible, unreported paper was selected.", ""))

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

        lines.extend(
            (
                f"## {number}. [{record['title']}]({record['url']})",
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


def write_report(
    report_dir: Path, body: str, now: dt.datetime, selected_count: int
) -> Path:
    """Write one report per day without losing a 07:00 selection at 07:20."""

    report_dir.mkdir(parents=True, exist_ok=True)
    date = now.astimezone(JST).date().isoformat()
    archive = report_dir / f"{date}.md"
    stored = body

    if archive.exists():
        previous = archive.read_text(encoding="utf-8")
        if selected_count == 0:
            stored = previous
        elif SELECTION_MARKER in previous:
            stored = (
                previous.rstrip()
                + f"\n\n---\n\n## Additional selection "
                f"({now.astimezone(JST):%H:%M JST})\n\n"
                + body
            )

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
