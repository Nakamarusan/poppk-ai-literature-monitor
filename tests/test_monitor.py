import datetime as dt
import json
import tempfile
import unittest
from pathlib import Path

from src.core import (
    JST,
    Match,
    Paper,
    Score,
    article_id,
    deduplicate,
    normalize_doi,
    screen,
    succeeded_on_jst_date,
)
from src.insights import rule_based_summary
from src.literature_monitor import rank_matches, select_historical, select_unseen
from src.reporting import (
    ResearchInsight,
    article_record,
    render_report,
    update_catalog,
    write_report,
)


class MonitorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = json.loads(Path("config.json").read_text())

    def test_relevance_score_is_bounded_and_transparent(self):
        paper = Paper(
            ["test"],
            ["1"],
            "Federated learning framework for population pharmacokinetic estimation",
            abstract=(
                "We propose a distributed optimization algorithm for nonlinear "
                "mixed effects models."
            ),
        )
        match = screen(paper, self.config)
        self.assertIsNotNone(match)
        self.assertEqual(match.score.as_dict(), {
            "pk": 30,
            "ai": 30,
            "method": 30,
            "intersection": 10,
            "total": 100,
        })
        self.assertEqual(match.priority, "High")

    def test_synonyms_do_not_inflate_component_points(self):
        paper = Paper(
            ["test"],
            ["1"],
            "Population pharmacokinetic and population pharmacokinetics machine learning framework",
            abstract="A pharmacometrics machine learning framework is evaluated.",
        )
        match = screen(paper, self.config)
        self.assertIsNotNone(match)
        self.assertLessEqual(match.score.pk, 30)
        self.assertLessEqual(match.score.ai, 30)
        self.assertLessEqual(match.score.method, 30)
        self.assertLessEqual(match.score.total, 100)

    def test_all_three_concepts_are_required(self):
        paper = Paper(
            ["test"],
            ["1"],
            "Machine learning framework for clinical prediction",
            abstract="A new algorithm is presented.",
        )
        self.assertIsNone(screen(paper, self.config))

    def test_review_is_excluded(self):
        paper = Paper(
            ["test"],
            ["1"],
            "Review of machine learning methods in population pharmacokinetics",
            abstract="A framework comparison.",
            publication_type="review",
        )
        self.assertIsNone(screen(paper, self.config))

    def test_doi_deduplication_keeps_longer_abstract(self):
        first = Paper(
            ["Europe PMC"], ["MED:1"], "One title", doi="10.1/ABC"
        )
        second = Paper(
            ["Crossref"],
            ["10.1/abc"],
            "One title",
            doi="https://doi.org/10.1/abc",
            abstract="Long abstract",
        )
        result = deduplicate([first, second])
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].abstract, "Long abstract")
        self.assertEqual(normalize_doi(result[0].doi), "10.1/abc")

    def test_summary_does_not_infer_when_abstract_is_missing(self):
        match = Match(
            Paper(["test"], ["1"], "A title only"),
            Score(20, 20, 20, 10),
            "High",
            {"pk": ["poppk"], "ai": ["machine learning"], "method": ["framework"]},
            {"pk": [], "ai": [], "method": []},
        )
        insight = rule_based_summary(match)
        self.assertIn("no abstract", insight.prior_limitation.casefold())
        self.assertEqual(insight.source, "No abstract available")

    def test_summary_category_uses_abstract(self):
        paper = Paper(
            ["test"],
            ["1"],
            "A neutral title",
            abstract=(
                "Patient-level sharing is restricted. This synthetic data "
                "benchmark compares generative algorithms for a PopPK model."
            ),
        )
        match = Match(
            paper,
            Score(0, 10, 10, 0),
            "Low",
            {"pk": [], "ai": [], "method": []},
            {
                "pk": ["poppk"],
                "ai": ["artificial intelligence"],
                "method": ["benchmark"],
            },
        )
        insight = rule_based_summary(match)
        self.assertIn("protecting patient data", insight.prior_limitation.casefold())
        self.assertIn("synthetic", insight.contribution.casefold())

    def test_recent_selection_excludes_cataloged_paper(self):
        paper = Paper(
            ["test"],
            ["1"],
            "Federated learning framework for population pharmacokinetics",
            abstract="A distributed optimization algorithm for NLME estimation.",
            doi="10.1/known",
            date="2026-01-01",
        )
        selected = select_unseen(
            [paper],
            self.config,
            seen={},
            catalog_ids={article_id(paper)},
            limit=10,
        )
        self.assertEqual(selected, [])

    def test_historical_selection_respects_date_and_seen_state(self):
        old = Paper(
            ["test"],
            ["old"],
            "Federated learning framework for population pharmacokinetics",
            abstract="A distributed optimization algorithm for NLME estimation.",
            date="2019-12-31",
        )
        candidate = Paper(
            ["test"],
            ["candidate"],
            "Machine learning framework for population pharmacokinetics",
            abstract="An automated model selection algorithm for PopPK analysis.",
            date="2021-05-01",
            doi="10.1/candidate",
        )
        selected = select_historical(
            [old, candidate],
            self.config,
            seen={},
            catalog_ids=set(),
            start=dt.date(2020, 1, 1),
            until=dt.date(2026, 1, 1),
            limit=1,
        )
        self.assertEqual([item.paper.title for item in selected], [candidate.title])

    def test_rank_prefers_higher_score(self):
        low = Match(
            Paper(["x"], ["1"], "Low", date="2026-01-01"),
            Score(10, 10, 10, 0),
            "Low",
            {"pk": [], "ai": [], "method": []},
            {"pk": [], "ai": [], "method": []},
        )
        high = Match(
            Paper(["x"], ["2"], "High", date="2020-01-01"),
            Score(30, 30, 30, 10),
            "High",
            {"pk": [], "ai": [], "method": []},
            {"pk": [], "ai": [], "method": []},
        )
        self.assertEqual(rank_matches([low, high])[0].paper.title, "High")

    def test_jst_success_date(self):
        state = {"last_success_utc": "2026-08-28T22:10:00+00:00"}
        self.assertTrue(succeeded_on_jst_date(state, dt.date(2026, 8, 29)))

    def test_report_is_english_and_abstract_only(self):
        paper = Paper(
            ["test"],
            ["1"],
            "A methodology paper",
            authors=["A Author"],
            venue="Journal",
            date="2026-08-28",
            doi="10.1/a",
            url="https://example.org/a",
            abstract="An abstract describing a machine learning framework.",
        )
        match = Match(
            paper,
            Score(30, 30, 30, 10),
            "High",
            {"pk": ["poppk"], "ai": ["machine learning"], "method": ["framework"]},
            {"pk": [], "ai": [], "method": []},
        )
        insight = ResearchInsight(
            "Prior limitation.",
            "Contribution.",
            "New capability.",
            "Significance.",
            "Abstract-only test",
        )
        record = article_record(
            match, insight, "new", dt.datetime(2026, 8, 28, tzinfo=dt.timezone.utc)
        )
        report = render_report(
            [record],
            dt.datetime(2026, 8, 28, tzinfo=dt.timezone.utc),
            {"Crossref": 1},
            {},
            {},
            2020,
        )
        self.assertIn("Abstract-only interpretation", report)
        self.assertIn("100/100", report)
        self.assertIn("Full text is not fetched", report)
        self.assertNotRegex(report, r"[\u3040-\u30ff\u3400-\u9fff]")

    def test_catalog_merge_uses_canonical_id(self):
        catalog = {"articles": [{"id": "doi:10.1/a", "abstract": "old"}]}
        updated = update_catalog(
            catalog,
            [{"id": "doi:10.1/a", "abstract": "new and longer"}],
            "2026-01-01 07:00 JST",
        )
        self.assertEqual(len(updated["articles"]), 1)
        self.assertEqual(updated["articles"][0]["abstract"], "new and longer")

    def test_fallback_report_does_not_overwrite_selection(self):
        now = dt.datetime(2026, 8, 28, tzinfo=dt.timezone.utc)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            selected = "<!-- poppk-ai-selection -->\nSelected paper"
            empty = "No eligible paper"
            write_report(path, selected, now, 1)
            write_report(path, empty, now + dt.timedelta(minutes=20), 0)
            self.assertEqual((path / "2026-08-28.md").read_text(), selected)


if __name__ == "__main__":
    unittest.main()
