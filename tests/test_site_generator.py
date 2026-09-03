import json
import re
import tempfile
import unittest
from pathlib import Path

from src.site_generator import build_payload, write_site_data


class SiteGeneratorTests(unittest.TestCase):
    def test_payload_counts_and_sorts_articles(self):
        catalog = {
            "last_scan_at": "2026-09-03 07:00 JST",
            "articles": [
                {
                    "id": "doi:10.1/old",
                    "title": "Older",
                    "publication_date": "2021-01-01",
                    "reported_at": "2026-09-01 07:00 JST",
                    "selection_type": "historical",
                },
                {
                    "id": "doi:10.1/new",
                    "title": "Newer",
                    "publication_date": "2026-01-01",
                    "reported_at": "2026-09-03 07:00 JST",
                    "selection_type": "new",
                },
            ],
        }
        payload = build_payload(catalog)
        self.assertEqual(payload["article_count"], 2)
        self.assertEqual(payload["new_count"], 1)
        self.assertEqual(payload["historical_count"], 1)
        self.assertEqual(payload["articles"][0]["title"], "Newer")
        self.assertEqual(payload["evidence_basis"], "abstract-only")

    def test_duplicate_ids_are_collapsed(self):
        payload = build_payload({
            "articles": [
                {"id": "doi:10.1/a", "title": "First"},
                {"id": "doi:10.1/a", "title": "Second"},
            ]
        })
        self.assertEqual(payload["article_count"], 1)
        self.assertEqual(payload["articles"][0]["title"], "Second")

    def test_write_site_data_is_valid_json(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            catalog = root / "catalog.json"
            output = root / "articles.json"
            catalog.write_text(json.dumps({"articles": []}))
            write_site_data(catalog, output)
            self.assertEqual(json.loads(output.read_text())["article_count"], 0)

    def test_pages_interface_is_english(self):
        paths = [
            Path("docs/index.html"),
            Path("docs/method.html"),
            Path("docs/assets/app.js"),
        ]
        japanese = re.compile(r"[\u3040-\u30ff\u3400-\u9fff]")
        for path in paths:
            self.assertIsNone(
                japanese.search(path.read_text()),
                f"Japanese text remains in {path}",
            )

    def test_catalog_summaries_are_abstract_only(self):
        catalog = json.loads(Path("data/articles.json").read_text())
        for article in catalog["articles"]:
            self.assertEqual(article["evidence"]["basis"], "abstract-only")
            self.assertIn("Abstract-only", article["summary"]["source"])


if __name__ == "__main__":
    unittest.main()
