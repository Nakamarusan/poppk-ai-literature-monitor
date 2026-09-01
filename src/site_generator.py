#!/usr/bin/env python3
"""Build a static HTML dashboard from Markdown literature reports."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any, Iterable

ARTICLE_HEADING = re.compile(
    r"^##\s+\d+\.\s+\[(?P<title>.+?)\]\((?P<url>https?://[^)]+)\)\s*$",
    re.MULTILINE,
)
BULLET = re.compile(
    r"^-\s+\*\*(?P<label>[^*]+?):\*\*\s*(?P<value>.*)$",
    re.MULTILINE,
)
RUN_AT = re.compile(r"^実行日時:\s*(?P<value>.+?)\s*$", re.MULTILINE)
NEW_COUNT = re.compile(r"^新着採択:\s*\*\*(?P<value>\d+)件\*\*", re.MULTILINE)
HISTORICAL_COUNT = re.compile(
    r"^過去論文の紹介:\s*\*\*(?P<value>\d+)件\*\*", re.MULTILINE
)
SUMMARY_METHOD = re.compile(
    r"^\*要約方法:\s*(?P<value>.+?)\*\s*$", re.MULTILINE
)
REPORT_NAME = re.compile(r"^\d{4}-\d{2}-\d{2}\.md$")


def clean(value: Any) -> str:
    if value is None:
        return ""
    return re.sub(r"\s+", " ", str(value)).strip()


def normalize_doi(value: str) -> str:
    value = clean(value)
    value = re.sub(
        r"^(?:https?://(?:dx\.)?doi\.org/|doi:\s*)", "", value, flags=re.I
    )
    if value in {"", "記載なし"}:
        return ""
    return value.lower().rstrip(". ")


def normalize_title(value: str) -> str:
    value = clean(value).casefold()
    return re.sub(r"\s+", " ", re.sub(r"[^\w]+", " ", value)).strip()


def _last_match(pattern: re.Pattern[str], text: str) -> str:
    matches = list(pattern.finditer(text))
    return clean(matches[-1].group("value")) if matches else ""


def _split_terms(value: str) -> list[str]:
    if not value or value == "記載なし":
        return []
    values: list[str] = []
    for item in value.split(","):
        item = clean(item).replace(r"\b", "").replace("\\", "")
        if item and item not in values:
            values.append(item)
    return values


def _parse_priority(value: str) -> tuple[str, int | None]:
    value = clean(value)
    priority_match = re.search(r"\b(High|Medium|Low)\b", value, re.I)
    score_match = re.search(r"スコア\s*(\d+)", value)
    priority = priority_match.group(1).title() if priority_match else ""
    score = int(score_match.group(1)) if score_match else None
    return priority, score


def _article_id(doi: str, title: str) -> str:
    if doi:
        return "doi:" + doi
    digest = hashlib.sha256(normalize_title(title).encode("utf-8")).hexdigest()
    return "title:" + digest[:20]


def _infer_selection_type(fields: dict[str, str], prefix: str) -> str:
    category = fields.get("区分", "")
    if "過去" in category:
        return "historical"
    if "新着" in category:
        return "new"
    new_count = _last_match(NEW_COUNT, prefix)
    historical_count = _last_match(HISTORICAL_COUNT, prefix)
    if new_count and int(new_count) > 0:
        return "new"
    if historical_count and int(historical_count) > 0:
        return "historical"
    return "new"


def parse_report(path: Path) -> tuple[list[dict[str, Any]], str]:
    """Parse all article sections in one generated Markdown report."""
    text = path.read_text(encoding="utf-8")
    headings = list(ARTICLE_HEADING.finditer(text))
    latest_scan = _last_match(RUN_AT, text)
    articles: list[dict[str, Any]] = []

    for index, heading in enumerate(headings):
        start = heading.start()
        end = headings[index + 1].start() if index + 1 < len(headings) else len(text)
        prefix = text[:start]
        section = text[start:end]
        fields = {
            clean(match.group("label")): clean(match.group("value"))
            for match in BULLET.finditer(section)
        }
        title = clean(heading.group("title"))
        url = clean(heading.group("url"))
        doi = normalize_doi(fields.get("DOI", ""))
        source = fields.get("取得元", "")
        venue = fields.get("掲載誌・公開元", "")
        if venue in {"", "[]", "記載なし"}:
            venue = source
        priority, score = _parse_priority(fields.get("優先度", ""))
        report_scan = _last_match(RUN_AT, prefix) or latest_scan
        selection_type = _infer_selection_type(fields, prefix)
        summary_method_match = SUMMARY_METHOD.search(section)

        articles.append({
            "id": _article_id(doi, title),
            "title": title,
            "url": url,
            "authors": fields.get("著者", ""),
            "venue": venue,
            "publication_date": fields.get("公開日", ""),
            "doi": doi,
            "selection_type": selection_type,
            "report_date": path.stem,
            "reported_at": report_scan,
            "priority": priority,
            "score": score,
            "insights": {
                "prior_limitation": fields.get("従来の課題", ""),
                "contribution": fields.get("今回の方法・新規性", ""),
                "new_capability": fields.get("新たに可能になったこと", ""),
                "significance": fields.get("研究上の意義", ""),
                "source": clean(summary_method_match.group("value"))
                if summary_method_match else "",
            },
            "terms": {
                "pk": _split_terms(fields.get("母集団PK関連語", "")),
                "ai": _split_terms(fields.get("AI関連語", "")),
                "method": _split_terms(fields.get("方法論関連語", "")),
            },
            "abstract": fields.get("抄録抜粋", ""),
            "source": source,
        })

    return articles, latest_scan


def _merge_article(existing: dict[str, Any], incoming: dict[str, Any]) -> dict[str, Any]:
    result = dict(existing)
    result["selection_type"] = (
        "new"
        if "new" in {existing.get("selection_type"), incoming.get("selection_type")}
        else "historical"
    )
    if incoming.get("report_date", "") < existing.get("report_date", ""):
        result["report_date"] = incoming["report_date"]
        result["reported_at"] = incoming.get("reported_at", result.get("reported_at", ""))
    for key in (
        "url", "authors", "venue", "publication_date", "doi",
        "priority", "score", "source",
    ):
        current = result.get(key)
        candidate = incoming.get(key)
        if current in {"", None, "[]", "記載なし"} and candidate not in {
            "", None, "[]", "記載なし"
        }:
            result[key] = candidate
    if len(incoming.get("abstract", "")) > len(result.get("abstract", "")):
        result["abstract"] = incoming["abstract"]
    for group in ("pk", "ai", "method"):
        result.setdefault("terms", {}).setdefault(group, [])
        for term in incoming.get("terms", {}).get(group, []):
            if term not in result["terms"][group]:
                result["terms"][group].append(term)
    result.setdefault("insights", {})
    for key, value in incoming.get("insights", {}).items():
        if not result["insights"].get(key) and value:
            result["insights"][key] = value
    return result


def collect_reports(report_dir: Path) -> tuple[list[dict[str, Any]], str]:
    """Collect and de-duplicate article records from all dated reports."""
    records: dict[str, dict[str, Any]] = {}
    latest_scan = ""
    for path in sorted(report_dir.iterdir() if report_dir.exists() else []):
        if not path.is_file() or not REPORT_NAME.match(path.name):
            continue
        articles, scan = parse_report(path)
        if scan:
            latest_scan = scan
        for article in articles:
            article_id = article["id"]
            if article_id in records:
                records[article_id] = _merge_article(records[article_id], article)
            else:
                records[article_id] = article

    articles = list(records.values())
    articles.sort(
        key=lambda article: (
            article.get("reported_at", ""),
            article.get("publication_date", ""),
            article.get("title", "").casefold(),
        ),
        reverse=True,
    )
    return articles, latest_scan


def build_payload(report_dir: Path) -> dict[str, Any]:
    articles, latest_scan = collect_reports(report_dir)
    years = sorted(
        {
            article["publication_date"][:4]
            for article in articles
            if re.match(r"^\d{4}", article.get("publication_date", ""))
        },
        reverse=True,
    )
    return {
        "schema_version": 1,
        "last_scan_at": latest_scan,
        "article_count": len(articles),
        "new_count": sum(article.get("selection_type") == "new" for article in articles),
        "historical_count": sum(
            article.get("selection_type") == "historical" for article in articles
        ),
        "years": years,
        "articles": articles,
    }


def write_site_data(report_dir: Path, output: Path) -> dict[str, Any]:
    payload = build_payload(report_dir)
    output.parent.mkdir(parents=True, exist_ok=True)
    serialized = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    if not output.exists() or output.read_text(encoding="utf-8") != serialized:
        output.write_text(serialized, encoding="utf-8")
    return payload


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reports", type=Path, default=Path("reports"))
    parser.add_argument("--output", type=Path, default=Path("docs/articles.json"))
    args = parser.parse_args(list(argv) if argv is not None else None)
    payload = write_site_data(args.reports, args.output)
    print(
        f"Generated {args.output} with {payload['article_count']} articles "
        f"(last scan: {payload['last_scan_at'] or 'unknown'})."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
