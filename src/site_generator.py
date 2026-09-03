#!/usr/bin/env python3
"""Build the GitHub Pages data file from the canonical article catalog."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Sequence

from .core import MonitorError, load_json


def build_payload(catalog: dict[str, Any]) -> dict[str, Any]:
    """Validate, sort, and add dashboard statistics."""

    articles = catalog.get("articles", [])
    if not isinstance(articles, list):
        raise MonitorError("Catalog field 'articles' must be a list")

    # One canonical identifier per card prevents duplicates on the dashboard.
    unique = {
        article["id"]: article
        for article in articles
        if isinstance(article, dict) and article.get("id")
    }
    ordered = sorted(
        unique.values(),
        key=lambda article: (
            article.get("reported_at", ""),
            article.get("publication_date", ""),
            article.get("title", "").casefold(),
        ),
        reverse=True,
    )
    years = sorted(
        {
            article.get("publication_date", "")[:4]
            for article in ordered
            if article.get("publication_date", "")[:4].isdigit()
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
