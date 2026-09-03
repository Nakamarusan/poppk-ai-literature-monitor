#!/usr/bin/env python3
"""Orchestrate the daily PopPK × AI literature monitor."""

from __future__ import annotations

import argparse
import datetime as dt
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Sequence

from .core import (
    JST,
    UTC,
    Match,
    MonitorError,
    Paper,
    article_id,
    clean,
    deduplicate,
    fingerprint,
    load_json,
    normalize_doi,
    parse_date,
    save_json,
    screen,
    succeeded_on_jst_date,
)
from .insights import summarize_research
from .reporting import (
    article_record,
    create_issue,
    render_report,
    update_catalog,
    write_report,
)
from .sources import fetch_arxiv, fetch_crossref, fetch_europe_pmc

Fetcher = Callable[[dict[str, Any], dt.date, dt.date], list[Paper]]

_SOURCE_FETCHERS: dict[str, tuple[str, Fetcher]] = {
    "europe_pmc": ("Europe PMC", fetch_europe_pmc),
    "crossref": ("Crossref", fetch_crossref),
    "arxiv": ("arXiv", fetch_arxiv),
}


@dataclass
class FetchResult:
    """Results from one pass over configured literature sources."""

    papers: list[Paper] = field(default_factory=list)
    counts: dict[str, int] = field(default_factory=dict)
    warnings: dict[str, str] = field(default_factory=dict)
    hidden_errors: dict[str, str] = field(default_factory=dict)
    required_successes: int = 0


def _redact(message: Any) -> str:
    text = clean(message)
    if email := os.getenv("CONTACT_EMAIL", "").strip():
        text = text.replace(email, "[REDACTED]")
    return text[:1000]


def fetch_sources(
    config: dict[str, Any],
    state: dict[str, Any],
    since: dt.date,
    until: dt.date,
    now: dt.datetime,
    *,
    historical: bool = False,
) -> FetchResult:
    """Fetch enabled sources through one shared error-handling path."""

    result = FetchResult()
    attempt_dates = state.setdefault("source_attempt_dates", {})
    health = state.setdefault("source_health", {})
    keys = (
        config["historical_fallback"]["sources"]
        if historical
        else _SOURCE_FETCHERS
    )

    for key in keys:
        label, fetcher = _SOURCE_FETCHERS[key]
        settings = config["sources"][key]
        if not settings.get("enabled", True):
            continue

        once_per_day = settings.get("once_per_day", False) and not historical
        if once_per_day and attempt_dates.get(key) == until.isoformat():
            print(f"{label}: skipped; already attempted on {until}")
            continue

        optional = bool(settings.get("optional", False))
        try:
            papers = fetcher(config, since, until)
            result.papers.extend(papers)
            result.counts[label] = len(papers)
            result.required_successes += int(not optional)
            health[key] = {
                "status": "ok",
                "last_attempt_utc": now.isoformat(),
                "records": len(papers),
            }
            print(f"{label}: {len(papers)} records")
        except Exception as exc:
            message = _redact(exc)
            health[key] = {
                "status": "error",
                "last_attempt_utc": now.isoformat(),
                "message": message,
            }
            if optional and settings.get("silent_errors", True):
                result.hidden_errors[label] = message
                print(
                    f"Optional source {label} unavailable: {message}",
                    file=sys.stderr,
                )
            else:
                result.warnings[label] = message
                print(f"{label} failed: {message}", file=sys.stderr)
        finally:
            if once_per_day:
                attempt_dates[key] = until.isoformat()

    return result


def _known(match: Match, seen: dict[str, Any], catalog_ids: set[str]) -> bool:
    return article_id(match.paper) in catalog_ids or any(
        key in seen for key in match.paper.keys()
    )


def rank_matches(matches: Sequence[Match]) -> list[Match]:
    """Sort by relevance, then recency."""

    priority = {"High": 0, "Medium": 1, "Low": 2}
    return sorted(
        matches,
        key=lambda item: (
            priority.get(item.priority, 3),
            -item.score.total,
            -(parse_date(item.paper.date) or dt.date.min).toordinal(),
            item.paper.title.casefold(),
        ),
    )


def select_unseen(
    papers: Sequence[Paper],
    config: dict[str, Any],
    seen: dict[str, Any],
    catalog_ids: set[str],
    limit: int,
) -> list[Match]:
    """Screen, de-duplicate, rank, and return unreported papers."""

    matches = [
        match
        for paper in deduplicate(papers)
        if (match := screen(paper, config))
        and not _known(match, seen, catalog_ids)
    ]
    return rank_matches(matches)[: max(0, limit)]


def select_historical(
    papers: Sequence[Paper],
    config: dict[str, Any],
    seen: dict[str, Any],
    catalog_ids: set[str],
    start: dt.date,
    until: dt.date,
    limit: int,
) -> list[Match]:
    """Restrict archive candidates to the configured date window."""

    candidates = select_unseen(
        papers, config, seen, catalog_ids, limit=10_000
    )
    candidates = [
        match
        for match in candidates
        if (date := parse_date(match.paper.date)) and start <= date <= until
    ]
    return rank_matches(candidates)[: max(0, limit)]


def update_state(
    state: dict[str, Any],
    selected: Sequence[Match],
    selection_type: str,
    now: dt.datetime,
    warnings: dict[str, str],
    hidden_errors: dict[str, str],
) -> None:
    """Record selections and run status for de-duplication and fallback logic."""

    timestamp = now.isoformat()
    seen = state.setdefault("seen", {})
    for match in selected:
        record = {
            "title": match.paper.title,
            "doi": normalize_doi(match.paper.doi),
            "notified_at": timestamp,
            "selection_type": selection_type,
        }
        for key in match.paper.keys():
            seen[key] = record

    if selected:
        state["last_selection_date_jst"] = now.astimezone(JST).date().isoformat()

    if hidden_errors:
        state["last_optional_source_errors"] = {
            source: {"message": message, "at_utc": timestamp}
            for source, message in hidden_errors.items()
        }
    else:
        state.pop("last_optional_source_errors", None)

    if warnings:
        state["last_partial_utc"] = timestamp
        state.pop("last_success_utc", None)
    else:
        state["last_success_utc"] = timestamp
        state.pop("last_partial_utc", None)


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
    state = load_json(args.state, {"schema_version": 2, "seen": {}})
    catalog = load_json(
        args.catalog, {"schema_version": 2, "last_scan_at": "", "articles": []}
    )
    now = dt.datetime.now(UTC)
    today = now.astimezone(JST).date()

    # The 07:20 run is only a fallback for an incomplete 07:00 run.
    if (
        os.getenv("SKIP_IF_SUCCESS_TODAY", "").casefold() == "true"
        and succeeded_on_jst_date(state, today)
    ):
        print(f"Successful run already recorded for {today}; fallback skipped.")
        return 0

    lookback = args.lookback_days or int(
        os.getenv("LOOKBACK_DAYS")
        or config["monitor"]["lookback_days"]
    )
    if not 1 <= lookback <= 90:
        raise MonitorError("lookback_days must be between 1 and 90")

    recent = fetch_sources(
        config,
        state,
        today - dt.timedelta(days=lookback - 1),
        today,
        now,
    )
    catalog_ids = {
        article["id"] for article in catalog.get("articles", [])
    }
    seen = state.setdefault("seen", {})
    selected = select_unseen(
        recent.papers,
        config,
        seen,
        catalog_ids,
        int(config["monitor"]["max_new_articles"]),
    )
    selection_type = "new" if selected else "none"

    archive_counts: dict[str, int] = {}
    archive_warnings: dict[str, str] = {}
    fallback = config["historical_fallback"]
    already_selected_today = (
        state.get("last_selection_date_jst") == today.isoformat()
    )

    # Only search the archive when the recent search found nothing.
    if (
        recent.required_successes > 0
        and not selected
        and fallback.get("enabled", True)
        and not already_selected_today
    ):
        start = dt.date(int(fallback["start_year"]), 1, 1)
        archive = fetch_sources(
            config, state, start, today, now, historical=True
        )
        archive_counts = archive.counts
        archive_warnings = archive.warnings
        selected = select_historical(
            archive.papers,
            config,
            seen,
            catalog_ids,
            start,
            today,
            int(fallback["count"]),
        )
        if selected:
            selection_type = "historical"

    insights = {
        article_id(match.paper): summarize_research(match, config)
        for match in selected
    }
    records = [
        article_record(
            match,
            insights[article_id(match.paper)],
            selection_type,
            now,
        )
        for match in selected
    ]

    warnings = {**recent.warnings, **archive_warnings}
    body = render_report(
        records,
        now,
        recent.counts,
        archive_counts,
        warnings,
        int(fallback["start_year"]),
    )
    report_path = write_report(args.report_dir, body, now, len(records))

    scan_at = now.astimezone(JST).strftime("%Y-%m-%d %H:%M JST")
    save_json(args.catalog, update_catalog(catalog, records, scan_at))

    # Required sources determine run success; optional arXiv errors stay silent.
    if recent.required_successes == 0:
        update_state(
            state,
            selected,
            selection_type,
            now,
            {"required_sources": "All required literature sources failed."},
            recent.hidden_errors,
        )
        save_json(args.state, state)
        raise MonitorError("All enabled required literature sources failed")

    token = os.getenv("GITHUB_TOKEN", "")
    repository = os.getenv("GITHUB_REPOSITORY", "")
    owner = os.getenv("GITHUB_REPOSITORY_OWNER", "")
    if selected and token and repository and owner and not args.no_notify:
        marker = f"<!-- poppk-ai-alert:{selection_type}:{fingerprint(selected)} -->"
        label = (
            "Archive methodology paper"
            if selection_type == "historical"
            else "New methodology paper"
        )
        title = f"[PopPK × AI] {label}: {len(selected)} — {today}"
        print(
            "Issue:",
            create_issue(
                title,
                f"{marker}\n\n@{owner}\n\n{body}",
                marker,
                token,
                repository,
                owner,
            ),
        )

    update_state(
        state,
        selected,
        selection_type,
        now,
        warnings,
        recent.hidden_errors,
    )
    save_json(args.state, state)

    print(
        f"Report: {report_path}; recent records {len(recent.papers)}, "
        f"selected {len(selected)} ({selection_type})"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except MonitorError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
