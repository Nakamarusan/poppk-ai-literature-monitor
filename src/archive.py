"""Resumable archive search with a durable queue of eligible abstracts.

API cursors stay within a session. Date partitions record cross-run progress
independently of provider-specific cursor lifetimes and indexing changes.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import time
from collections import Counter
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from .core import (MonitorError, Paper, article_id, clean, deduplicate, load_json,
                   parse_date, phrase_hits, save_json, screen)
from .sources import crossref_page, europe_pmc_page


@dataclass
class ArchiveResult:
    papers: list[Paper] = field(default_factory=list)
    counts: dict[str, int] = field(default_factory=dict)
    warnings: dict[str, str] = field(default_factory=dict)
    diagnostics: dict[str, Any] = field(default_factory=dict)


def exclusion_reason(paper: Paper, config: dict[str, Any], known: set[str],
                     start: dt.date, until: dt.date, *, require_abstract: bool) -> str:
    """One mutually exclusive reason per normalized record; gate is unchanged."""
    if article_id(paper) in known or set(paper.keys()) & known:
        return "already_reported"
    if phrase_hits(f"{paper.publication_type} {paper.title}", config["terms"]["exclude"]):
        return "excluded_publication_type"
    if screen(paper, config) is None:
        text = f"{paper.title} {paper.abstract}"
        if not phrase_hits(text, config["terms"]["pk"]):
            return "missing_pk_evidence"
        if not phrase_hits(text, config["terms"]["ai"]):
            return "missing_ai_evidence"
        return "missing_method_evidence"
    date = parse_date(paper.date)
    if date is None:
        return "missing_publication_date"
    if not start <= date <= until:
        return "outside_publication_window"
    if require_abstract and not clean(paper.abstract):
        return "missing_abstract"
    return "eligible_unreported"


def diagnose(papers: list[Paper], config: dict[str, Any], known: set[str],
             start: dt.date, until: dt.date, *, require_abstract: bool) -> dict[str, int]:
    unique = deduplicate(papers)
    counts = Counter(exclusion_reason(p, config, known, start, until,
                                     require_abstract=require_abstract) for p in unique)
    return {"retrieved": len(papers), "unique": len(unique),
            "duplicates": len(papers) - len(unique), **dict(counts)}


def _tasks(config: dict[str, Any], start: dt.date, until: dt.date) -> list[dict[str, str]]:
    windows = [(max(start, dt.date(y, 1, 1)), min(until, dt.date(y, 12, 31)))
               for y in range(until.year, start.year - 1, -1)]
    tasks = []
    enabled = [s for s in config["historical_fallback"]["sources"]
               if config["sources"][s].get("enabled", True)]
    for source in enabled:
        for low, high in windows:
            queries = ([("", "")] if source == "europe_pmc" else
                       [(q, t) for q in config["search"]["crossref_queries"]
                        for t in ("journal-article", "posted-content")])
            for query, content_type in queries:
                tasks.append({"source": source, "since": low.isoformat(),
                              "until": high.isoformat(), "query": query,
                              "content_type": content_type})
    return tasks


def _split(task: dict[str, Any]) -> list[dict[str, Any]]:
    low, high = dt.date.fromisoformat(task["since"]), dt.date.fromisoformat(task["until"])
    if low == high:
        return []
    mid = low + (high - low) // 2
    return [{**task, "since": (mid + dt.timedelta(days=1)).isoformat()},
            {**task, "until": mid.isoformat()}]


def search_archive(config: dict[str, Any], path: Path, known: set[str],
                   today: dt.date) -> ArchiveResult:
    """Refill the candidate queue within a bounded request/time budget."""
    fallback = config["historical_fallback"]
    start = dt.date(int(fallback["start_year"]), 1, 1)
    options = fallback.get("retrieval", {})
    def setting(key, default, upper):
        value = options.get(key, default)
        if type(value) is not int or not 1 <= value <= upper:
            raise MonitorError(f"Invalid historical_fallback.retrieval.{key}")
        return value
    max_requests = setting("max_requests", 8, 40)
    page_limit = setting("pages_per_window", 2, 10)
    page_size = setting("page_size", 200, 1000)
    target = setting("refill_target", 5, 100)
    seconds = setting("budget_seconds", 480, 1200)
    recheck_days = setting("recheck_days", 7, 90)
    identity = {"version": 1, "start": str(start), "terms": config["terms"],
                "search": config["search"], "sources": fallback["sources"],
                "enabled": {k: v.get("enabled", True) for k, v in config["sources"].items()}}
    signature = hashlib.sha256(json.dumps(identity, sort_keys=True).encode()).hexdigest()
    state = load_json(path, {})
    if state.get("query_signature") != signature:
        state = {"schema_version": 1, "query_signature": signature, "pool": [],
                 "pending": _tasks(config, start, today), "through": str(today),
                 "completed_windows": 0, "cycle_started": str(today)}
    pool = [Paper(**p) for p in state["pool"]]
    pool = [p for p in deduplicate(pool) if exclusion_reason(
        p, config, known, start, today, require_abstract=True) == "eligible_unreported"]
    completed = parse_date(state.get("cycle_completed", ""))
    if not pool and completed and (today - completed).days >= recheck_days:
        state.update(pending=_tasks(config, start, today), completed_windows=0,
                     cycle_started=str(today), cycle_completed="", through=str(today))
    # Daily tail checks must not reset the age of the completed full cycle.
    through = dt.date.fromisoformat(state["through"])
    if through < today:
        state["pending"].extend(_tasks(config, through + dt.timedelta(days=1), today))
        state["through"] = str(today)
    result = ArchiveResult()
    counts, reasons = Counter(), Counter()
    calls, splits, repeated_pages = 0, 0, 0
    cached_before = len(pool)
    deadline = time.monotonic() + seconds
    deferred = []

    def checkpoint():
        # Include deferred work on disk, but do not immediately retry it in
        # this session. A crash can replay work; it cannot lose a partition.
        state["pool"] = [asdict(p) for p in deduplicate(pool)]
        save_json(path, {**state, "pending": [*state["pending"], *deferred]})

    while state["pending"] and len(pool) < target and calls < max_requests and time.monotonic() < deadline:
        task = state["pending"].pop(0)
        label = "Europe PMC" if task["source"] == "europe_pmc" else "Crossref"
        low, high = dt.date.fromisoformat(task["since"]), dt.date.fromisoformat(task["until"])
        cursor, received, complete, failed = "*", 0, False, False
        signatures = set()
        allowance = min(int(task.get("page_limit", page_limit)), max_requests)
        for _ in range(allowance):
            if calls >= max_requests or time.monotonic() >= deadline:
                break
            calls += 1
            try:
                if task["source"] == "europe_pmc":
                    page = europe_pmc_page(config, low, high, cursor=cursor,
                                           historical=True, size=page_size)
                else:
                    page = crossref_page(config, low, high, task["query"],
                        task["content_type"], cursor=cursor, historical=True, size=page_size)
            except Exception as exc:
                result.warnings[label] = clean(exc)
                failed = True
                break
            counts[label] += page.raw_count
            received += page.raw_count
            key = tuple((p.doi, p.title, tuple(p.source_ids)) for p in page.papers)
            if page.raw_count and key in signatures:
                repeated_pages += 1
                break
            signatures.add(key)
            reasons.update(diagnose(page.papers, config, known, start, today, require_abstract=True))
            pool.extend(p for p in page.papers if exclusion_reason(
                p, config, known, start, today, require_abstract=True) == "eligible_unreported")
            pool = deduplicate(pool)
            if received >= page.total:
                complete = True
                break
            if not page.raw_count or not page.next_cursor:
                # Empty data while the API reports more hits is not EOF.
                break
            cursor = page.next_cursor
        if complete:
            state["completed_windows"] += 1
        elif failed:
            deferred.append(task)
        elif children := _split(task):
            state["pending"][0:0] = children
            splits += 1
        else:
            task["page_limit"] = min(allowance * 2, max_requests)
            deferred.append(task)
            result.warnings[label] = "A dense or incomplete one-day archive window remains beyond the page budget."
        checkpoint()
    remaining = len(state["pending"]) + len(deferred)
    if not remaining and not state.get("cycle_completed"):
        state["cycle_completed"] = str(today)
    result.papers = deduplicate(pool)
    result.counts = dict(counts)
    result.diagnostics = {
        "requests": calls, "cached_candidates_before": cached_before,
        "eligible_candidates": len(result.papers), "pending_windows": remaining,
        "completed_windows": state["completed_windows"], "split_windows": splits,
        "repeated_pages": repeated_pages, "exhausted": not remaining and not pool,
        "screening": dict(reasons),
        "note": "Screening counts are per retrieved page; a record can recur across queries or split windows.",
    }
    state["last_check"] = str(today)
    state["last_run"] = result.diagnostics
    checkpoint()
    return result
