import json
import re
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path

from src.site_generator import build_payload, write_site_data


class _StrictEnoughHTMLParser(HTMLParser):
    """Exercise the standard parser so malformed markup is caught in CI."""


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
            catalog.write_text(json.dumps({"articles": []}), encoding="utf-8")
            write_site_data(catalog, output)
            self.assertEqual(json.loads(output.read_text())["article_count"], 0)

    def test_pages_interface_is_english(self):
        paths = [
            Path("docs/index.html"),
            Path("docs/method.html"),
            Path("docs/assets/app.js"),
            Path("docs/assets/observatory.css"),
        ]
        japanese = re.compile(r"[\u3040-\u30ff\u3400-\u9fff]")
        for path in paths:
            self.assertIsNone(
                japanese.search(path.read_text(encoding="utf-8")),
                f"Japanese text remains in {path}",
            )

    def test_html_pages_parse_and_have_canonical_links(self):
        for path in (Path("docs/index.html"), Path("docs/method.html")):
            text = path.read_text(encoding="utf-8")
            parser = _StrictEnoughHTMLParser(convert_charrefs=True)
            parser.feed(text)
            parser.close()
            self.assertIn('rel="canonical"', text)
            self.assertIn('href="./assets/mark.svg"', text)
            self.assertIn('lang="en"', text)

    def test_library_exposes_accessible_motion_control(self):
        html = Path("docs/index.html").read_text(encoding="utf-8")
        javascript = Path("docs/assets/app.js").read_text(encoding="utf-8")
        css = Path("docs/assets/observatory.css").read_text(encoding="utf-8")
        self.assertIn('id="motionToggle"', html)
        self.assertIn('aria-pressed="false"', html)
        self.assertIn("Resume motion", javascript)
        self.assertIn("motion-paused", css)
        self.assertIn("prefers-reduced-motion", css)

    def test_card_reveal_has_a_non_observer_fallback(self):
        javascript = Path("docs/assets/app.js").read_text(encoding="utf-8")
        self.assertIn('if (!("IntersectionObserver" in window))', javascript)
        self.assertIn('card.classList.add("is-visible")', javascript)

    def test_stylesheets_have_balanced_braces(self):
        for path in (
            Path("docs/assets/styles.css"),
            Path("docs/assets/observatory.css"),
        ):
            text = path.read_text(encoding="utf-8")
            self.assertEqual(
                text.count("{"),
                text.count("}"),
                f"Unbalanced CSS braces in {path}",
            )

    def test_site_mark_is_original_inline_svg(self):
        mark = Path("docs/assets/mark.svg").read_text(encoding="utf-8")
        self.assertIn("<svg", mark)
        self.assertIn("<ellipse", mark)
        self.assertNotIn("<image", mark)
        self.assertNotIn("http://", mark)
        self.assertNotIn("https://", mark)

    def test_catalog_summaries_are_abstract_only(self):
        catalog = json.loads(Path("data/articles.json").read_text(encoding="utf-8"))
        for article in catalog["articles"]:
            self.assertEqual(article["evidence"]["basis"], "abstract-only")
            self.assertIn("Abstract-only", article["summary"]["source"])


if __name__ == "__main__":
    unittest.main()
