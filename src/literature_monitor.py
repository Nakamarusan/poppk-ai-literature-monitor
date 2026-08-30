#!/usr/bin/env python3
"""Daily PopPK-AI methodology literature monitor."""
from __future__ import annotations

import argparse
import datetime as dt
import os
import sys
from pathlib import Path
from typing import Any, Sequence

from .core import (JST, UTC, Match, MonitorError, Paper, already_succeeded_today,
                   clean, deduplicate, fingerprint, load_json, normalize_doi,
                   normalize_title, parse_date, request_json, save_json, screen)
from .insights import ResearchInsight, summarize_research
from .sources import fetch_arxiv, fetch_crossref, fetch_europe_pmc

__all__ = [
    "JST", "Match", "Paper", "ResearchInsight", "already_succeeded_today",
    "choose_historical", "deduplicate", "fingerprint", "normalize_doi",
    "normalize_title", "render_report", "screen", "summarize_research",
    "should_use_historical_fallback", "write_reports",
]

SELECTION_MARKER = "<!-- poppk-ai-selection -->"


def _is_unseen(match: Match, seen: dict[str, Any]) -> bool:
    return not any(key in seen for key in match.paper.keys())


def should_use_historical_fallback(state: dict[str, Any],
                                   today: dt.date) -> bool:
    """Limit the historical fallback to one reported selection per JST day."""
    return clean(state.get("last_selection_date_jst")) != today.isoformat()


def choose_historical(matches: Sequence[Match], seen: dict[str, Any],
                      start: dt.date, until: dt.date,
                      limit: int = 1) -> list[Match]:
    """Choose previously unreported eligible papers published in the date range."""
    candidates: list[Match] = []
    for match in matches:
        published = parse_date(match.paper.date)
        if published is None or not start <= published <= until:
            continue
        if not _is_unseen(match, seen):
            continue
        candidates.append(match)
    candidates.sort(
        key=lambda match: (
            match.priority != "High",
            -match.score,
            -parse_date(match.paper.date).toordinal(),
            match.paper.title.lower(),
        )
    )
    return candidates[:max(0, limit)]


def fetch_historical_pool(config: dict[str, Any], start: dt.date,
                          until: dt.date) -> tuple[list[Paper], dict[str, int],
                                                  dict[str, str]]:
    """Retrieve a broader 2020+ pool only when the recent search has no hit."""
    settings = config.get("historical_fallback", {})
    source_settings = settings.get("sources", {})
    fetchers = {
        "Europe PMC": ("europe_pmc", fetch_europe_pmc, True),
        "Crossref": ("crossref", fetch_crossref, True),
        "arXiv": ("arxiv", fetch_arxiv, False),
    }
    papers: list[Paper] = []
    counts: dict[str, int] = {}
    errors: dict[str, str] = {}
    for name, (key, fetcher, default_enabled) in fetchers.items():
        if not source_settings.get(key, default_enabled):
            continue
        try:
            found = fetcher(config, start, until)
            papers.extend(found)
            counts[name] = len(found)
            print(f"Historical {name}: {len(found)} records")
        except Exception as exc:
            message = clean(exc)
            contact = os.getenv("CONTACT_EMAIL", "").strip()
            if contact:
                message = message.replace(contact, "[REDACTED]")
            errors[f"Historical {name}"] = message[:1000]
            print(
                f"Historical {name} failed: {errors[f'Historical {name}']}",
                file=sys.stderr,
            )
    return papers, counts, errors


def render_report(matches: Sequence[Match], insights: dict[str, ResearchInsight],
                  now: dt.datetime, counts: dict[str, int],
                  errors: dict[str, str], *, selection_mode: str = "new",
                  historical_counts: dict[str, int] | None = None,
                  historical_start_year: int = 2020) -> str:
    new_count = len(matches) if selection_mode == "new" else 0
    historical_count = len(matches) if selection_mode == "historical" else 0
    lines: list[str] = []
    if matches:
        lines += [SELECTION_MARKER, ""]
    lines += [
        "# 母集団PK × AI 方法論文献アラート", "",
        f"実行日時: {now.astimezone(JST).strftime('%Y-%m-%d %H:%M JST')}",
        f"新着採択: **{new_count}件**",
        f"過去論文の紹介: **{historical_count}件**"
        f"（{historical_start_year}年以降・未紹介）", "",
        "新着検索の取得数: " + ", ".join(
            f"{name} {count}件" for name, count in sorted(counts.items())
        ), "",
    ]
    historical_counts = historical_counts or {}
    if historical_counts:
        lines += [
            "過去論文検索の取得数: " + ", ".join(
                f"{name} {count}件"
                for name, count in sorted(historical_counts.items())
            ),
            "",
        ]
    if errors:
        lines += ["## データソースの警告", ""]
        lines += [
            f"- **{name}:** {clean(message)}"
            for name, message in sorted(errors.items())
        ]
        lines += [""]
    if not matches:
        lines += [
            "通知条件を満たす未通知の新着論文および過去論文候補はありませんでした。",
            "",
        ]
    for number, item in enumerate(matches, 1):
        paper = item.paper
        insight = insights[paper.title_key()]
        link = paper.url or (
            f"https://doi.org/{normalize_doi(paper.doi)}" if paper.doi else ""
        )
        title = f"[{paper.title}]({link})" if link else paper.title
        authors = ", ".join(paper.authors[:8]) + (
            ", et al." if len(paper.authors) > 8 else ""
        )
        abstract = (
            paper.abstract[:700] + "…"
            if len(paper.abstract) > 700 else paper.abstract
        )
        category = (
            f"{historical_start_year}年以降の過去論文（新着がない日の補完）"
            if selection_mode == "historical" else "新着論文"
        )
        lines += [
            f"## {number}. {title}", "",
            f"- **区分:** {category}",
            f"- **著者:** {authors or '記載なし'}",
            f"- **掲載誌・公開元:** {paper.venue or ', '.join(paper.sources)}",
            f"- **公開日:** {paper.date or '記載なし'}",
            f"- **DOI:** {normalize_doi(paper.doi) or '記載なし'}", "",
            "### 研究の位置づけ（抄録ベース）", "",
            f"- **従来の課題:** {insight.prior_limitation}",
            f"- **今回の方法・新規性:** {insight.contribution}",
            f"- **新たに可能になったこと:** {insight.new_capability}",
            f"- **研究上の意義:** {insight.significance}", "",
            f"*要約方法: {insight.source}*", "",
            "<details>",
            "<summary>自動判定の根拠と抄録を表示</summary>", "",
            f"- **優先度:** {item.priority}（スコア {item.score}）",
            f"- **取得元:** {', '.join(dict.fromkeys(paper.sources))}",
            f"- **母集団PK関連語:** {', '.join(item.pk_hits)}",
            f"- **AI関連語:** {', '.join(item.ai_hits)}",
            f"- **方法論関連語:** "
            f"{', '.join(item.method_hits) or 'AI手法自体を方法論的と判定'}",
            f"- **抄録抜粋:** {abstract or '記載なし'}", "",
            "</details>", "",
        ]
    lines += [
        "---",
        "研究の位置づけはタイトルと抄録に基づく自動要約であり、本文全体の評価ではありません。",
        "",
    ]
    return "\n".join(lines)


def _report_has_selection(body: str) -> bool:
    if SELECTION_MARKER in body:
        return True
    return (
        "新着採択: **0件**" not in body
        and "新着採択:" in body
    ) or (
        "過去論文の紹介: **0件**" not in body
        and "過去論文の紹介:" in body
    )


def write_reports(directory: Path, body: str, now: dt.datetime,
                  selected_count: int) -> Path:
    """Write the daily report without losing a selection from an earlier run."""
    directory.mkdir(parents=True, exist_ok=True)
    local_time = now.astimezone(JST)
    day = local_time.date().isoformat()
    archive = directory / f"{day}.md"
    stored_body = body
    if archive.exists():
        previous = archive.read_text()
        if selected_count == 0:
            stored_body = previous
        elif _report_has_selection(previous):
            heading = local_time.strftime("%H:%M JST")
            stored_body = (
                previous.rstrip()
                + f"\n\n---\n\n## 追加検出（{heading}）\n\n"
                + body
            )
    archive.write_text(stored_body)
    (directory / "latest.md").write_text(stored_body)
    summary = os.getenv("GITHUB_STEP_SUMMARY", "")
    if summary:
        with Path(summary).open("a") as stream:
            stream.write(body + "\n")
    return archive


def create_issue(title: str, body: str, marker: str, token: str,
                 repository: str, owner: str) -> str:
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    endpoint = f"https://api.github.com/repos/{repository}/issues"
    query = endpoint + "?state=all&per_page=100"
    issues = request_json(query, headers=headers)
    for issue in issues if isinstance(issues, list) else []:
        if marker and marker in str(issue.get("body") or ""):
            return clean(issue.get("html_url"))
        if not marker and clean(issue.get("title")) == title:
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


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=Path("config.json"))
    parser.add_argument("--state", type=Path, default=Path("state/seen.json"))
    parser.add_argument("--report-dir", type=Path, default=Path("reports"))
    parser.add_argument("--lookback-days", type=int)
    parser.add_argument("--no-notify", action="store_true")
    args = parser.parse_args(argv)

    config = load_json(args.config)
    state = load_json(args.state, {"schema_version": 1, "seen": {}})
    now = dt.datetime.now(UTC)
    today = now.astimezone(JST).date()
    if (
        os.getenv("SKIP_IF_SUCCESS_TODAY", "").lower() == "true"
        and already_succeeded_today(state, today)
    ):
        print(f"Successful run already recorded for {today}; fallback skipped.")
        return 0

    lookback = args.lookback_days or int(
        os.getenv("LOOKBACK_DAYS") or config["lookback_days"]
    )
    if not 1 <= lookback <= 90:
        raise MonitorError("lookback_days must be between 1 and 90")
    since = today - dt.timedelta(days=lookback - 1)

    fetchers = {
        "Europe PMC": ("europe_pmc", fetch_europe_pmc),
        "Crossref": ("crossref", fetch_crossref),
        "arXiv": ("arxiv", fetch_arxiv),
    }
    papers: list[Paper] = []
    counts: dict[str, int] = {}
    errors: dict[str, str] = {}
    for name, (key, fetcher) in fetchers.items():
        if not config["sources"].get(key, True):
            continue
        try:
            found = fetcher(config, since, today)
            papers.extend(found)
            counts[name] = len(found)
            print(f"{name}: {len(found)} records")
        except Exception as exc:
            message = clean(exc)
            contact = os.getenv("CONTACT_EMAIL", "").strip()
            if contact:
                message = message.replace(contact, "[REDACTED]")
            errors[name] = message[:1000]
            print(f"{name} failed: {errors[name]}", file=sys.stderr)

    unique = deduplicate(papers)
    screened = [match for paper in unique if (match := screen(paper, config))]
    screened.sort(
        key=lambda match: (
            match.priority != "High", -match.score, match.paper.title.lower()
        )
    )
    seen = state.setdefault("seen", {})
    recent_new = [
        match for match in screened if _is_unseen(match, seen)
    ][:int(config["max_alerts"])]

    selected = recent_new
    selection_mode = "new" if selected else "none"
    historical_counts: dict[str, int] = {}
    historical_start_year = int(
        config.get("historical_fallback", {}).get("start_year", 2020)
    )
    fallback_settings = config.get("historical_fallback", {})
    fallback_enabled = bool(fallback_settings.get("enabled", True))
    if (
        counts and not selected and fallback_enabled
        and should_use_historical_fallback(state, today)
    ):
        historical_start = dt.date(historical_start_year, 1, 1)
        historical_papers, historical_counts, historical_errors = (
            fetch_historical_pool(config, historical_start, today)
        )
        errors.update(historical_errors)
        historical_unique = deduplicate(historical_papers)
        historical_screened = [
            match for paper in historical_unique
            if (match := screen(paper, config))
        ]
        selected = choose_historical(
            historical_screened,
            seen,
            historical_start,
            today,
            int(fallback_settings.get("count", 1)),
        )
        if selected:
            selection_mode = "historical"

    insights: dict[str, ResearchInsight] = {}
    for match in selected:
        insight = summarize_research(match, config)
        insights[match.paper.title_key()] = insight
        print(f"Insight: {match.paper.title} [{insight.source}]")

    body = render_report(
        selected,
        insights,
        now,
        counts,
        errors,
        selection_mode=selection_mode,
        historical_counts=historical_counts,
        historical_start_year=historical_start_year,
    )
    archive = write_reports(args.report_dir, body, now, len(selected))

    token = os.getenv("GITHUB_TOKEN", "")
    repository = os.getenv("GITHUB_REPOSITORY", "")
    owner = os.getenv("GITHUB_REPOSITORY_OWNER", "")
    can_notify = bool(token and repository and owner and not args.no_notify)

    if not counts:
        title = f"[母集団PK × AI] 全データソースの取得に失敗 — {today}"
        if can_notify:
            create_issue(title, f"@{owner}\n\n{body}", "", token, repository, owner)
        raise MonitorError("All enabled recent-literature sources failed")

    if selected:
        digest = fingerprint(selected)
        marker = f"<!-- poppk-ai-alert:{selection_mode}:{digest} -->"
        if selection_mode == "historical":
            title = (
                f"[母集団PK × AI] {historical_start_year}年以降の論文紹介 "
                f"{len(selected)}件 — {today}"
            )
        else:
            title = (
                f"[母集団PK × AI] 方法論の新着論文 "
                f"{len(selected)}件 — {today}"
            )
        if can_notify:
            issue_body = f"{marker}\n\n@{owner}\n\n{body}"
            print(
                "Issue:",
                create_issue(title, issue_body, marker, token, repository, owner),
            )
        else:
            print(
                "Notification skipped: GitHub credentials unavailable "
                "or --no-notify used."
            )

    stamp = now.isoformat()
    for item in selected:
        record = {
            "title": item.paper.title,
            "doi": normalize_doi(item.paper.doi),
            "notified_at": stamp,
            "selection_type": selection_mode,
        }
        for key in item.paper.keys():
            seen[key] = record
    if selected:
        state["last_selection_date_jst"] = today.isoformat()
    cutoff = now - dt.timedelta(days=int(config["state_retention_days"]))
    state["seen"] = {
        key: value for key, value in seen.items()
        if not value.get("notified_at")
        or dt.datetime.fromisoformat(
            value["notified_at"].replace("Z", "+00:00")
        ) >= cutoff
    }
    if errors:
        state["last_partial_utc"] = stamp
        state.pop("last_success_utc", None)
    else:
        state["last_success_utc"] = stamp
        state.pop("last_partial_utc", None)
    save_json(args.state, state)
    print(
        f"Report: {archive}; retrieved {len(papers)}, unique {len(unique)}, "
        f"screened {len(screened)}, recent_new {len(recent_new)}, "
        f"selected {len(selected)} ({selection_mode})"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except MonitorError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
