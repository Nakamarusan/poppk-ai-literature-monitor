#!/usr/bin/env python3
"""Daily PopPK-AI methodology literature monitor."""
from __future__ import annotations

import argparse
import datetime as dt
import os
import sys
from pathlib import Path
from typing import Sequence

from .core import (JST, UTC, Match, MonitorError, Paper, already_succeeded_today,
                   clean, deduplicate, fingerprint, load_json, normalize_doi,
                   normalize_title, request_json, save_json, screen)
from .sources import fetch_arxiv, fetch_crossref, fetch_europe_pmc

__all__ = [
    "JST", "Match", "Paper", "already_succeeded_today", "deduplicate",
    "fingerprint", "normalize_doi", "normalize_title", "screen",
]


def render_report(matches: Sequence[Match], now: dt.datetime, counts: dict[str, int],
                  errors: dict[str, str]) -> str:
    lines = [
        "# 母集団PK × AI 方法論文献アラート", "",
        f"実行日時: {now.astimezone(JST).strftime('%Y-%m-%d %H:%M JST')}",
        f"新着採択: **{len(matches)}件**", "",
        "取得数: " + ", ".join(f"{name} {count}件" for name, count in sorted(counts.items())), "",
    ]
    if errors:
        lines += ["## データソースの警告", ""]
        lines += [f"- **{name}:** {clean(message)}" for name, message in sorted(errors.items())]
        lines += [""]
    if not matches:
        lines += ["通知条件を満たす未通知の新着論文はありませんでした。", ""]
    for number, item in enumerate(matches, 1):
        paper = item.paper
        link = paper.url or (f"https://doi.org/{normalize_doi(paper.doi)}" if paper.doi else "")
        title = f"[{paper.title}]({link})" if link else paper.title
        authors = ", ".join(paper.authors[:8]) + (", et al." if len(paper.authors) > 8 else "")
        abstract = paper.abstract[:700] + "…" if len(paper.abstract) > 700 else paper.abstract
        lines += [
            f"## {number}. {title}", "",
            f"- **優先度:** {item.priority}（スコア {item.score}）",
            f"- **著者:** {authors or '記載なし'}",
            f"- **掲載誌・公開元:** {paper.venue or ', '.join(paper.sources)}",
            f"- **公開日:** {paper.date or '記載なし'}",
            f"- **DOI:** {normalize_doi(paper.doi) or '記載なし'}",
            f"- **取得元:** {', '.join(dict.fromkeys(paper.sources))}",
            f"- **母集団PK関連語:** {', '.join(item.pk_hits)}",
            f"- **AI関連語:** {', '.join(item.ai_hits)}",
            f"- **方法論関連語:** {', '.join(item.method_hits) or 'AI手法自体を方法論的と判定'}",
            f"- **抄録抜粋:** {abstract or '記載なし'}", "",
        ]
    lines += ["---", "自動スクリーニング結果であり、論文の質を評価するものではありません。", ""]
    return "\n".join(lines)


def write_reports(directory: Path, body: str, now: dt.datetime) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    day = now.astimezone(JST).date().isoformat()
    archive = directory / f"{day}.md"
    archive.write_text(body)
    (directory / "latest.md").write_text(body)
    summary = os.getenv("GITHUB_STEP_SUMMARY", "")
    if summary:
        with Path(summary).open("a") as stream:
            stream.write(body + "\n")
    return archive


def create_issue(title: str, body: str, marker: str, token: str, repository: str, owner: str) -> str:
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
        result = request_json(endpoint, method="POST", payload=payload, headers=headers, retries=1)
    except MonitorError as exc:
        if "HTTP 422" not in str(exc):
            raise
        payload.pop("assignees", None)
        result = request_json(endpoint, method="POST", payload=payload, headers=headers, retries=1)
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
    if os.getenv("SKIP_IF_SUCCESS_TODAY", "").lower() == "true" and already_succeeded_today(state, today):
        print(f"Successful run already recorded for {today}; fallback skipped.")
        return 0

    lookback = args.lookback_days or int(os.getenv("LOOKBACK_DAYS") or config["lookback_days"])
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
    screened.sort(key=lambda match: (match.priority != "High", -match.score, match.paper.title.lower()))
    seen = state.setdefault("seen", {})
    new = [match for match in screened if not any(key in seen for key in match.paper.keys())]
    new = new[:int(config["max_alerts"])]
    body = render_report(new, now, counts, errors)
    archive = write_reports(args.report_dir, body, now)

    token = os.getenv("GITHUB_TOKEN", "")
    repository = os.getenv("GITHUB_REPOSITORY", "")
    owner = os.getenv("GITHUB_REPOSITORY_OWNER", "")
    can_notify = token and repository and owner and not args.no_notify

    if not counts:
        title = f"[母集団PK × AI] 全データソースの取得に失敗 — {today}"
        if can_notify:
            create_issue(title, f"@{owner}\n\n{body}", "", token, repository, owner)
        raise MonitorError("All enabled literature sources failed")

    if new or errors:
        digest = fingerprint(new) if new else ""
        marker = f"<!-- poppk-ai-alert:{digest} -->" if digest else ""
        title = (f"[母集団PK × AI] 方法論の新着論文 {len(new)}件 — {today}"
                 if new else f"[母集団PK × AI] データソース警告 — {today}")
        if can_notify:
            issue_body = f"{marker}\n\n@{owner}\n\n{body}" if marker else f"@{owner}\n\n{body}"
            print("Issue:", create_issue(title, issue_body, marker, token, repository, owner))
        elif new:
            print("Notification skipped: GitHub credentials unavailable or --no-notify used.")

    stamp = now.isoformat()
    for item in new:
        record = {"title": item.paper.title, "doi": normalize_doi(item.paper.doi), "notified_at": stamp}
        for key in item.paper.keys():
            seen[key] = record
    cutoff = now - dt.timedelta(days=int(config["state_retention_days"]))
    state["seen"] = {
        key: value for key, value in seen.items()
        if not value.get("notified_at")
        or dt.datetime.fromisoformat(value["notified_at"].replace("Z", "+00:00")) >= cutoff
    }
    state["last_success_utc"] = stamp
    save_json(args.state, state)
    print(f"Report: {archive}; retrieved {len(papers)}, unique {len(unique)}, screened {len(screened)}, new {len(new)}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except MonitorError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
