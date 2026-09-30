"""Offline regression tests for the September empty-day failure mode."""
import copy
import datetime as dt
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit

from src.archive import ArchiveResult, diagnose, search_archive
from src.core import MonitorError, Paper, article_id, load_json, save_json
from src.delivery import deliver_pending, queue_notification, should_skip_retry
from src.literature_monitor import FetchResult, main
from src.sources import Records, SourcePage, _collect, crossref_page, europe_pmc_page
from src.site_generator import build_payload

CONFIG = json.loads(Path("config.json").read_text())
TODAY = dt.date(2026, 9, 30)


def paper(key="new", date="2026-04-01"):
    return Paper(["Europe PMC"], [key], f"A {key} machine learning framework for population pharmacokinetics",
        abstract="We propose a machine learning framework for automated model selection in population pharmacokinetics.",
        doi=f"10.1234/{key}", date=date, venue="Test Journal", url=f"https://doi.org/10.1234/{key}")


def profile(**retrieval):
    config = copy.deepcopy(CONFIG)
    config["sources"]["crossref"]["enabled"] = False
    config["historical_fallback"]["sources"] = ["europe_pmc"]
    config["historical_fallback"]["retrieval"] = {"refill_target": 1, "page_size": 1, **retrieval}
    return config


class SourcePaginationTests(unittest.TestCase):
    def test_full_first_page_does_not_end_search(self):
        result = Records()
        with patch("builtins.print"):
            fetch = unittest.mock.Mock(side_effect=[SourcePage([paper("a")], 1, 2, "c"),
                                                   SourcePage([paper("b")], 1, 2, None)])
            _collect(result, fetch, 3)
        self.assertEqual(len(result), 2)
        self.assertEqual(fetch.call_args_list[1].args[0], "c")
        self.assertEqual(result.limited_queries, 0)

    def test_constant_crossref_cursor_can_return_different_pages(self):
        result = Records()
        fetch = unittest.mock.Mock(side_effect=[SourcePage([paper("a")], 1, 3, "same"),
            SourcePage([paper("b")], 1, 3, "same"), SourcePage([paper("c")], 1, 3, "same")])
        _collect(result, fetch, 4)
        self.assertEqual(len(result), 3)
        self.assertEqual(result.limited_queries, 0)

    def test_repeated_page_is_limited_not_complete(self):
        result = Records()
        fetch = unittest.mock.Mock(return_value=SourcePage([paper()], 1, 50, "c"))
        _collect(result, fetch, 4)
        self.assertEqual(len(result), 1)
        self.assertEqual(result.limited_queries, 1)

    def test_error_after_page_preserves_partial_results(self):
        result = Records()
        fetch = unittest.mock.Mock(side_effect=[SourcePage([paper()], 1, 50, "c"), MonitorError("HTTP 503")])
        _collect(result, fetch, 3)
        self.assertEqual(len(result), 1)
        self.assertEqual(result.errors, ["HTTP 503"])

    @patch("src.sources.request_json")
    def test_epmc_uses_different_date_fields_and_parses_nested_journal(self, request):
        request.return_value = {"hitCount": 1, "resultList": {"result": [{
            "title": "Example", "id": "1", "source": "MED", "firstPublicationDate": "2021-02-03",
            "journalInfo": {"journal": {"title": "Actual Journal"}}, "abstractText": "Abstract."}]}}
        result = europe_pmc_page(CONFIG, dt.date(2020, 1, 1), TODAY, historical=True)
        query = parse_qs(urlsplit(request.call_args.args[0]).query)["query"][0]
        self.assertIn("FIRST_PDATE:", query)
        self.assertIn("TITLE_ABS:", query)
        self.assertEqual(result.papers[0].venue, "Actual Journal")
        europe_pmc_page(CONFIG, TODAY, TODAY)
        self.assertIn("FIRST_IDATE:", parse_qs(urlsplit(request.call_args.args[0]).query)["query"][0])

    @patch("src.sources.time.sleep")
    @patch("src.sources.request_json")
    def test_crossref_archive_does_not_use_registration_dates(self, request, sleep):
        request.return_value = {"message": {"total-results": 1, "items": [{
            "title": ["Example"], "DOI": "10.1234/a", "created": {"date-parts": [[2026, 9, 1]]}}]}}
        page = crossref_page(CONFIG, dt.date(2020, 1, 1), TODAY, "query", "journal-article", historical=True)
        params = parse_qs(urlsplit(request.call_args.args[0]).query)
        self.assertIn("from-pub-date:", params["filter"][0])
        self.assertEqual(params["cursor"], ["*"])
        self.assertEqual(page.papers[0].date, "")

    @patch("src.sources.request_json", return_value={"error": "invalid query"})
    def test_api_error_payload_is_not_an_empty_success(self, request):
        with self.assertRaises(MonitorError):
            europe_pmc_page(CONFIG, TODAY, TODAY)


class ArchiveRecoveryTests(unittest.TestCase):
    @patch("src.archive.europe_pmc_page")
    def test_finds_unseen_paper_beyond_known_first_page(self, fetch):
        known, new = paper("known"), paper("new")
        fetch.side_effect = [SourcePage([known], 1, 2, "next"), SourcePage([new], 1, 2, None)]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "archive.json"
            result = search_archive(profile(), path, {article_id(known)}, TODAY)
            self.assertEqual([p.doi for p in result.papers], [new.doi])
            self.assertEqual(fetch.call_args_list[1].kwargs["cursor"], "next")
            self.assertEqual(load_json(path)["completed_windows"], 1)
            self.assertNotIn("next", json.dumps(load_json(path)))

    @patch("src.archive.europe_pmc_page")
    def test_checks_older_year_when_newest_year_has_no_match(self, fetch):
        fetch.side_effect = [SourcePage([], 0, 0, None), SourcePage([paper(date="2025-04-01")], 1, 1, None)]
        with tempfile.TemporaryDirectory() as directory:
            result = search_archive(profile(), Path(directory) / "archive.json", set(), TODAY)
        self.assertEqual(fetch.call_args_list[0].args[1].year, 2026)
        self.assertEqual(fetch.call_args_list[1].args[1].year, 2025)
        self.assertEqual(len(result.papers), 1)

    @patch("src.archive.europe_pmc_page")
    def test_budgeted_work_survives_restart_and_uses_another_partition(self, fetch):
        fetch.return_value = SourcePage([paper("known")], 1, 100, "temporary")
        config = profile(max_requests=1)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "archive.json"
            first = search_archive(config, path, {article_id(paper("known"))}, TODAY)
            before = load_json(path)["pending"][0]
            self.assertGreater(first.diagnostics["pending_windows"], 0)
            self.assertFalse(first.diagnostics["exhausted"])
            fetch.return_value = SourcePage([paper(date=before["since"])], 1, 1, None)
            second = search_archive(config, path, set(), TODAY)
            self.assertEqual(fetch.call_args.args[1].isoformat(), before["since"])
            self.assertEqual(len(second.papers), 1)
            self.assertNotIn("temporary", path.read_text())

    @patch("src.archive.europe_pmc_page")
    def test_cache_is_used_without_refetching_and_known_entries_are_removed(self, fetch):
        fetch.return_value = SourcePage([paper()], 1, 1, None)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "archive.json"
            search_archive(profile(), path, set(), TODAY)
            fetch.reset_mock()
            cached = search_archive(profile(), path, set(), TODAY)
            fetch.assert_not_called()
            self.assertEqual(len(cached.papers), 1)
            fetch.return_value = SourcePage([], 0, 0, None)
            consumed = search_archive(profile(), path, {article_id(paper())}, TODAY)
            self.assertEqual(consumed.papers, [])

    @patch("src.archive.europe_pmc_page", side_effect=MonitorError("HTTP 503"))
    def test_failed_partition_is_not_marked_completed(self, fetch):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "archive.json"
            result = search_archive(profile(max_requests=1), path, set(), TODAY)
            stored = load_json(path)
        self.assertEqual(stored["completed_windows"], 0)
        self.assertEqual(len(stored["pending"]), 7)
        self.assertIn("Europe PMC", result.warnings)
        self.assertFalse(result.diagnostics["exhausted"])

    def test_exclusions_are_counted_once_per_unique_record(self):
        known = paper("known")
        no_abstract = paper("empty")
        no_abstract.abstract = ""
        review = paper("review")
        review.publication_type = "Review"
        result = diagnose([known, known, no_abstract, review, paper("old", "2019-01-01"), paper()],
            CONFIG, {article_id(known)}, dt.date(2020, 1, 1), TODAY, require_abstract=True)
        self.assertEqual(result["duplicates"], 1)
        for reason in ("already_reported", "missing_abstract", "excluded_publication_type",
                       "outside_publication_window", "eligible_unreported"):
            self.assertEqual(result[reason], 1)
        self.assertEqual(result["unique"], 5)


class DeliveryRecoveryTests(unittest.TestCase):
    def test_retrieval_success_without_delivery_does_not_skip_retry(self):
        state = {"last_success_utc": "2026-09-30T00:00:00+00:00", "last_selection_date_jst": "2026-09-29"}
        self.assertFalse(should_skip_retry(state, TODAY))
        state["last_delivery_date_jst"] = str(TODAY)
        self.assertTrue(should_skip_retry(state, TODAY))
        state["pending_notifications"] = [{"marker": "pending"}]
        self.assertFalse(should_skip_retry(state, TODAY))

    @patch.dict(os.environ, {"GITHUB_TOKEN": "test", "GITHUB_REPOSITORY": "owner/repo", "GITHUB_REPOSITORY_OWNER": "owner"})
    @patch("src.delivery.create_issue")
    def test_failed_delivery_is_retried_without_losing_outbox(self, create):
        state = {}
        queue_notification(state, title="Title", body="Body", marker="marker", date=str(TODAY), kind="papers")
        queue_notification(state, title="Title", body="Body", marker="marker", date=str(TODAY), kind="papers")
        self.assertEqual(len(state["pending_notifications"]), 1)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "seen.json"
            save_json(path, state)
            create.side_effect = MonitorError("HTTP 503")
            with self.assertRaises(MonitorError):
                deliver_pending(state, path)
            self.assertEqual(len(load_json(path)["pending_notifications"]), 1)
            create.side_effect = None
            create.return_value = "https://github.com/owner/repo/issues/1"
            deliver_pending(state, path)
            self.assertEqual(state["pending_notifications"], [])
            self.assertEqual(state["last_delivery_date_jst"], str(TODAY))

    def prepare(self, directory):
        root = Path(directory)
        save_json(root / "config.json", CONFIG)
        return ["--config", str(root / "config.json"), "--state", str(root / "state/seen.json"),
                "--catalog", str(root / "data/articles.json"), "--report-dir", str(root / "reports")]

    @patch.dict(os.environ, {"GITHUB_TOKEN": "test", "GITHUB_REPOSITORY": "owner/repo", "GITHUB_REPOSITORY_OWNER": "owner", "SKIP_IF_SUCCESS_TODAY": "true"})
    @patch("src.delivery.create_issue", return_value="https://github.com/owner/repo/issues/1")
    @patch("src.literature_monitor.search_archive")
    @patch("src.literature_monitor.fetch_sources", return_value=FetchResult(required_successes=1))
    def test_empty_day_notifies_once_but_retry_keeps_searching(self, recent, archive, create):
        archive.return_value = ArchiveResult(diagnostics={"eligible_candidates": 0, "pending_windows": 3,
            "completed_windows": 1, "screening": {}})
        with tempfile.TemporaryDirectory() as directory:
            args = self.prepare(directory)
            self.assertEqual(main(args), 0)
            self.assertEqual(main(args), 0)
            catalog = load_json(Path(directory) / "data/articles.json")
            self.assertEqual(catalog["run_status"]["selection_status"], "search_pending")
            self.assertEqual(catalog["articles"], [])
        self.assertEqual(recent.call_count, 2)
        self.assertEqual(archive.call_count, 2)
        self.assertEqual(create.call_count, 1)

    @patch.dict(os.environ, {"GITHUB_TOKEN": "test", "GITHUB_REPOSITORY": "owner/repo", "GITHUB_REPOSITORY_OWNER": "owner", "SKIP_IF_SUCCESS_TODAY": "false"})
    @patch("src.delivery.create_issue")
    @patch("src.literature_monitor.fetch_sources")
    def test_selection_survives_issue_failure_and_recovers_on_next_run(self, recent, create):
        recent.return_value = FetchResult(papers=[paper("recover", "2021-04-01")], required_successes=1)
        create.side_effect = MonitorError("HTTP 503")
        with tempfile.TemporaryDirectory() as directory:
            args = self.prepare(directory)
            with self.assertRaises(MonitorError):
                main(args)
            root = Path(directory)
            self.assertEqual(len(load_json(root / "data/articles.json")["articles"]), 1)
            self.assertEqual(len(load_json(root / "state/seen.json")["pending_notifications"]), 1)
            create.side_effect = None
            create.return_value = "https://github.com/owner/repo/issues/2"
            self.assertEqual(main(args), 0)
            self.assertEqual(load_json(root / "state/seen.json")["pending_notifications"], [])
            self.assertEqual(len(load_json(root / "data/articles.json")["articles"]), 1)

    def test_pages_payload_carries_status_without_creating_an_article(self):
        status = {"selection_status": "search_pending", "selected_count": 0}
        result = build_payload({"articles": [], "run_status": status})
        self.assertEqual(result["run_status"], status)
        self.assertEqual(result["article_count"], 0)


if __name__ == "__main__":
    unittest.main()
