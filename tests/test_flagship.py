"""Regression tests for the independent daily flagship-journal selection."""
import copy
import datetime as dt
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit

from src.core import MonitorError, Paper, save_json
from src.flagship import (build_site, choose_candidate, fetch_candidates, journal_name,
                          parse_record, research_connections, run, validate_settings)
from src.insights import ResearchInsight

ROOT = Path(__file__).resolve().parents[1]
NOW = dt.datetime(2026, 9, 8, 0, tzinfo=dt.timezone.utc)


def raw_record(title="A distributed learning framework", doi="10.1038/example"):
    return {
        "id": "1234", "source": "MED", "title": title, "doi": doi,
        "firstPublicationDate": "2026-08-20",
        "abstractText": "We present a federated learning framework for clinical prediction. The framework enables decentralized training without pooling data.",
        "pubTypeList": {"pubType": ["Journal Article"]},
        "journalInfo": {"journal": {"title": "Nature", "issn": "0028-0836", "essn": "1476-4687"}},
        "authorList": {"author": [{"fullName": "Test Author"}]},
    }


class FlagshipTests(unittest.TestCase):
    def setUp(self):
        self.settings = json.loads((ROOT / "flagship_config.json").read_text())
        self.item = parse_record(raw_record())

    def choose(self, candidates, known=None):
        return choose_candidate(candidates, self.settings, known or set(),
                                dt.date(2020, 1, 1), NOW.date())

    def test_profile_is_valid(self):
        validate_settings(self.settings)
        invalid = copy.deepcopy(self.settings)
        invalid["max_pages"] = 1000
        with self.assertRaises(MonitorError):
            validate_settings(invalid)

    def test_only_three_exact_journal_identities(self):
        self.assertEqual(journal_name("Science (New York, N.Y.)", ["1095-9203"]), "Science")
        self.assertEqual(journal_name("Cell", ["0092-8674"]), "Cell")
        self.assertEqual(journal_name("Nature", ["1476-4687"]), "Nature")
        for title, issns in (("Nature Medicine", ["1078-8956"]),
                             ("Nature Communications", ["2041-1723"]),
                             ("Science Advances", ["2375-2548"]),
                             ("Cell Systems", ["2405-4712"]),
                             ("Nature", ["2041-1723"]),
                             ("Nature Medicine", ["0028-0836"]), ("Nature", [])):
            self.assertIsNone(journal_name(title, issns))

    def test_nested_europe_pmc_journal_issue_is_supported(self):
        raw = raw_record()
        raw["journalIssue"] = raw.pop("journalInfo")
        self.assertEqual(parse_record(raw)["journal"], "Nature")

    def test_review_news_and_missing_abstract_are_rejected(self):
        for publication_type in ("Review", "Editorial", "News", "Comment", "Journal Article; Review"):
            raw = raw_record()
            raw["pubTypeList"]["pubType"] = [publication_type]
            self.assertIsNone(parse_record(raw))
        raw = raw_record()
        raw["abstractText"] = "This review summarizes federated learning methods."
        self.assertIsNone(parse_record(raw))
        raw["abstractText"] = ""
        self.assertIsNone(parse_record(raw))

    def test_title_alone_cannot_establish_research_fit(self):
        item = copy.deepcopy(self.item)
        item["title"] = "Federated learning and QSP for vascular malformations"
        item["abstract"] = "We examine atmospheric dust deposition over a large ocean region."
        self.assertIsNone(self.choose([item]))

    def test_broad_signaling_term_requires_vascular_context(self):
        topics = self.settings["topics"]
        self.assertFalse(research_connections("We examine mTOR regulation in unrelated tissue.", topics))
        self.assertTrue(research_connections("We examine mTOR regulation in lymphatic endothelial cells.", topics))
        self.assertFalse(research_connections("Reinforcement learning improves a board game algorithm.", topics))

    def test_profile_does_not_require_the_main_pk_ai_gate(self):
        item = copy.deepcopy(self.item)
        item["abstract"] = "We report a mechanism of lymphangiogenesis in lymphatic endothelial cells."
        self.assertIsNotNone(self.choose([item]))

    def test_future_pre2020_and_known_papers_are_excluded(self):
        for date in ("2019-12-31", "2027-01-01", ""):
            item = {**self.item, "publication_date": date}
            self.assertIsNone(self.choose([item]))
        self.assertIsNone(self.choose([self.item], {self.item["id"]}))
        key = Paper([], [], self.item["title"]).title_key()
        self.assertIsNone(self.choose([self.item], {key}))

    @patch("src.flagship.request_json")
    def test_api_query_has_exact_journals_dates_and_bounded_pagination(self, request):
        request.side_effect = [
            {"resultList": {"result": [raw_record()]}, "nextCursorMark": "next"},
            {"resultList": {"result": []}, "nextCursorMark": "next"},
        ]
        papers = fetch_candidates(self.settings, dt.date(2020, 1, 1), NOW.date())
        self.assertEqual(len(papers), 1)
        self.assertEqual(request.call_count, 2)
        params = parse_qs(urlsplit(request.call_args_list[0].args[0]).query)
        self.assertIn("ISSN:0028-0836", params["query"][0])
        self.assertIn("ISSN:0036-8075", params["query"][0])
        self.assertIn("ISSN:0092-8674", params["query"][0])
        self.assertIn("FIRST_PDATE:[2020-01-01 TO 2026-09-08]", params["query"][0])
        self.assertIn("TITLE_ABS:", params["query"][0])
        self.assertEqual(params["resultType"], ["core"])
        self.assertEqual(params["cursorMark"], ["*"])

    def initialize_root(self, root):
        save_json(root / "data/articles.json", {"articles": []})
        save_json(root / "state/seen.json", {
            "seen": {}, "last_selection_date_jst": "2026-09-08",
            "last_success_utc": NOW.isoformat(), "source_health": {"crossref": {"status": "ok"}},
        })

    @patch("src.flagship.summarize_research", return_value=ResearchInsight(
        "Not stated in the available abstract.", "A framework is described.",
        "Decentralized training is reported.", "Not stated in the available abstract.",
        "Abstract-only test summary"))
    @patch("src.flagship.fetch_candidates")
    def test_daily_addition_is_independent_idempotent_and_published(self, fetch, summarize):
        fetch.return_value = [self.item]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.initialize_root(root)
            first = run(root, self.settings, {}, NOW, no_notify=True)
            second = run(root, self.settings, {}, NOW + dt.timedelta(minutes=20), no_notify=True)
            self.assertEqual(len(first["articles"]), 1)
            self.assertEqual(len(second["articles"]), 1)
            self.assertEqual(fetch.call_count, 1)
            self.assertEqual(summarize.call_count, 1)
            seen = json.loads((root / "state/seen.json").read_text())
            self.assertEqual(seen["last_selection_date_jst"], "2026-09-08")
            self.assertEqual(seen["source_health"]["crossref"]["status"], "ok")
            self.assertIn(self.item["id"], seen["seen"])
            self.assertEqual(json.loads((root / "data/articles.json").read_text())["articles"], [])
            payload = build_site(root)
            self.assertEqual(payload["article_count"], 1)
            self.assertEqual(payload["articles"][0]["evidence_basis"], "abstract-only")
            self.assertNotIn("score", payload["articles"][0])
            report = (root / "reports/flagship/2026-09-08.md").read_text()
            self.assertIn("proposed uses, not paper findings", report)
            self.assertIn(self.item["title"], report)

    @patch("src.flagship.summarize_research", return_value=ResearchInsight(
        "Gap.", "Method.", "Capability.", "Significance.", "Abstract-only test summary"))
    @patch("src.flagship.fetch_candidates")
    def test_recent_zero_triggers_archive_even_after_primary_selection(self, fetch, summarize):
        old = {**self.item, "publication_date": "2021-05-26"}
        fetch.side_effect = [[], [old]]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.initialize_root(root)
            result = run(root, self.settings, {}, NOW, no_notify=True)
            self.assertEqual(result["articles"][0]["selection_type"], "archive")
            self.assertEqual(fetch.call_args_list[1].args[1], dt.date(2020, 1, 1))

    @patch("src.flagship.fetch_candidates", side_effect=MonitorError("HTTP 503"))
    def test_optional_outage_keeps_primary_data_unchanged(self, fetch):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.initialize_root(root)
            before = (root / "data/articles.json").read_bytes()
            result = run(root, self.settings, {}, NOW, no_notify=True)
            self.assertEqual(result["status"], "source unavailable")
            self.assertEqual(result["articles"], [])
            self.assertEqual(before, (root / "data/articles.json").read_bytes())
            self.assertEqual(build_site(root)["article_count"], 0)

    def test_site_build_rejects_sister_journals(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            save_json(root / "data/flagship.json", {"articles": [{
                **self.item, "journal": "Nature Medicine", "evidence_basis": "abstract-only"
            }]})
            with self.assertRaises(MonitorError):
                build_site(root)

    def test_frontend_assets_and_daily_workflow_are_connected(self):
        html = (ROOT / "docs/index.html").read_text()
        workflow = (ROOT / ".github/workflows/daily-literature-monitor.yml").read_text()
        self.assertIn('id="research-spotlight"', html)
        self.assertIn('src="./assets/flagship.js"', html)
        self.assertIn('href="./assets/flagship.css"', html)
        self.assertIn("python -m src.flagship", workflow)
        self.assertIn("python -m src.flagship --build-only", workflow)
        for file in ("docs/assets/flagship.js", "docs/assets/flagship.css", "flagship_config.json"):
            self.assertNotRegex((ROOT / file).read_text(), r"[\u3040-\u30ff\u3400-\u9fff]")


if __name__ == "__main__":
    unittest.main()
