#!/usr/bin/env python3
"""Build GitHub Pages data from the canonical article catalog."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Sequence

from .core import MonitorError, load_json


def _validate_article(article: Any, position: int) -> dict[str, Any]:
    """Validate fields required by the static dashboard."""

    if not isinstance(article, dict):
        raise MonitorError(f"Catalog article {position} must be an object")
    if not article.get("id") or not article.get("title"):
        raise MonitorError(f"Catalog article {position} requires id and title")
    if article.get("evidence", {}).get("basis") != "abstract-only":
        raise MonitorError(
            f"Catalog article {position} does not declare abstract-only evidence"
        )

    score = article.get("score", {})
    try:
        total = int(score.get("total"))
    except (AttributeError, TypeError, ValueError) as exc:
        raise MonitorError(f"Catalog article {position} has an invalid score") from exc
    if not 0 <= total <= 100:
        raise MonitorError(
            f"Catalog article {position} has a score outside 0-100"
        )
    return article


def build_payload(catalog: dict[str, Any]) -> dict[str, Any]:
    """Validate, de-duplicate, sort, and add dashboard statistics."""

    raw_articles = catalog.get("articles", [])
    if not isinstance(raw_articles, list):
        raise MonitorError("Catalog field 'articles' must be a list")

    # The last occurrence wins if an interrupted migration left duplicate IDs.
    unique = {
        article["id"]: article
        for position, raw in enumerate(raw_articles, 1)
        if (article := _validate_article(raw, position))
    }
    ordered = sorted(
        unique.values(),
        key=lambda article: (
            str(article.get("reported_at", "")),
            str(article.get("publication_date", "")),
            str(article.get("title", "")).casefold(),
        ),
        reverse=True,
    )
    years = sorted(
        {
            str(article.get("publication_date", ""))[:4]
            for article in ordered
            if str(article.get("publication_date", ""))[:4].isdigit()
        },
        reverse=True,
    )

    return {
        "schema_version": 2,
        "evidence_basis": "abstract-only",
        "last_scan_at": catalog.get("last_scan_at", ""),
        "article_count": len(ordered),
        "new_count": sum(
            article.get("selection_type") == "new" for article in ordered
        ),
        "historical_count": sum(
            article.get("selection_type") == "historical"
            for article in ordered
        ),
        "years": years,
        "articles": ordered,
    }


def write_site_data(catalog_path: Path, output_path: Path) -> dict[str, Any]:
    """Write the generated dashboard payload only when its content changes."""

    payload = build_payload(load_json(catalog_path))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    if not output_path.exists() or output_path.read_text(encoding="utf-8") != text:
        output_path.write_text(text, encoding="utf-8")
    return payload


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--catalog", type=Path, default=Path("data/articles.json")
    )
    parser.add_argument(
        "--output", type=Path, default=Path("docs/articles.json")
    )
    args = parser.parse_args(argv)

    payload = write_site_data(args.catalog, args.output)
    print(
        f"Generated {args.output} with {payload['article_count']} articles "
        f"(last scan: {payload['last_scan_at'] or 'unknown'})."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
