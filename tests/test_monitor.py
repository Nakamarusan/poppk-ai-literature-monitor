import copy
import datetime as dt
import json
import tempfile
import unittest
from pathlib import Path

from src.core import (
    Match,
    MonitorError,
    Paper,
    Score,
    article_id,
    deduplicate,
    normalize_doi,
    screen,
    succeeded_on_jst_date,
    validate_config,
)
from src.insights import ResearchInsight, rule_based_summary
from src.literature_monitor import (
    rank_matches,
    refresh_catalog,
    select_historical,
    select_unseen,
)
from src.reporting import article_record, render_report, update_catalog, write_report


class MonitorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = json.loads(Path("config.json").read_text(encoding="utf-8"))
        validate_config(cls.config)

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
        self.assertEqual(
            match.score.as_dict(),
            {
                "pk": 30,
                "ai": 30,
                "method": 30,
                "intersection": 10,
                "total": 100,
            },
        )
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

    def test_review_is_excluded_as_a_phrase(self):
        review = Paper(
            ["test"],
            ["1"],
            "Review of machine learning methods in population pharmacokinetics",
            abstract="A framework comparison.",
            publication_type="review",
        )
        preview = Paper(
            ["test"],
            ["2"],
            "Preview model for population pharmacokinetic machine learning framework",
            abstract="A model development algorithm is evaluated.",
        )
        self.assertIsNone(screen(review, self.config))
        self.assertIsNotNone(screen(preview, self.config))

    def test_config_rejects_a_score_above_100(self):
        invalid = copy.deepcopy(self.config)
        invalid["scoring"]["intersection_bonus"] = 11
        with self.assertRaises(MonitorError):
            validate_config(invalid)

    def test_doi_deduplication_keeps_richer_metadata(self):
        first = Paper(
            ["Europe PMC"], ["MED:1"], "One title", doi="10.1/ABC"
        )
        second = Paper(
            ["Crossref"],
            ["10.1/abc"],
            "One title",
            authors=["A", "B"],
            venue="Journal",
            date="2026-01-02",
            doi="https://doi.org/10.1/abc",
            abstract="Long abstract",
        )
        result = deduplicate([first, second])
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].abstract, "Long abstract")
        self.assertEqual(result[0].authors, ["A", "B"])
        self.assertEqual(result[0].venue, "Journal")
        self.assertEqual(normalize_doi(result[0].doi), "10.1/abc")

    def test_transitive_duplicates_are_collapsed(self):
        by_title = Paper(["source-a"], ["a"], "Shared title")
        by_doi = Paper(
            ["source-b"], ["b"], "Different title", doi="10.1/shared"
        )
        bridge = Paper(
            ["source-c"], ["c"], "Shared title", doi="10.1/shared"
        )
        result = deduplicate([by_title, by_doi, bridge])
        self.assertEqual(len(result), 1)
        self.assertEqual(normalize_doi(result[0].doi), "10.1/shared")
        self.assertEqual(set(result[0].sources), {"source-a", "source-b", "source-c"})

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

    def test_extractive_summary_uses_abstract_sentences(self):
        abstract = (
            "Current PopPK model development is manual and time consuming. "
            "We propose a machine learning framework for automated model selection. "
            "The framework enables candidate structures to be compared consistently. "
            "This approach may support reproducible pharmacometric analysis."
        )
        match = Match(
            Paper(["test"], ["1"], "Neutral title", abstract=abstract),
            Score(10, 10, 10, 0),
            "Low",
            {"pk": [], "ai": [], "method": []},
            {"pk": ["poppk"], "ai": ["machine learning"], "method": ["framework"]},
        )
        insight = rule_based_summary(match)
        self.assertEqual(
            insight.prior_limitation,
            "Current PopPK model development is manual and time consuming.",
        )
        self.assertEqual(
            insight.contribution,
            "We propose a machine learning framework for automated model selection.",
        )
        self.assertIn("enables", insight.new_capability)
        self.assertIn("may support", insight.significance)
        self.assertEqual(insight.source, "Abstract-only extractive summary")

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

    def test_historical_selection_requires_an_abstract(self):
        no_abstract = Paper(
            ["test"],
            ["a"],
            "Machine learning framework without an abstract for population pharmacokinetics",
            date="2022-01-01",
            doi="10.1/no-abstract",
        )
        with_abstract = Paper(
            ["test"],
            ["b"],
            "Machine learning framework with an abstract for population pharmacokinetics",
            abstract="An automated model selection algorithm for PopPK analysis.",
            date="2021-05-01",
            doi="10.1/with-abstract",
        )
        selected = select_historical(
            [no_abstract, with_abstract],
            self.config,
            seen={},
            catalog_ids=set(),
            start=dt.date(2020, 1, 1),
            until=dt.date(2026, 1, 1),
            limit=2,
        )
        self.assertEqual([item.paper.doi for item in selected], ["10.1/with-abstract"])

    def test_rank_prefers_an_abstract_when_scores_are_equal(self):
        without = Match(
            Paper(["x"], ["1"], "Without", date="2026-01-01"),
            Score(20, 20, 20, 0),
            "Medium",
            {"pk": [], "ai": [], "method": []},
            {"pk": [], "ai": [], "method": []},
        )
        with_abstract = Match(
            Paper(["x"], ["2"], "With", abstract="Evidence.", date="2025-01-01"),
            Score(20, 20, 20, 0),
            "Medium",
            {"pk": [], "ai": [], "method": []},
            {"pk": [], "ai": [], "method": []},
        )
        self.assertEqual(rank_matches([without, with_abstract])[0].paper.title, "With")

    def test_refresh_catalog_adds_a_later_abstract(self):
        paper = Paper(
            ["Europe PMC"],
            ["MED:1"],
            "Machine learning framework for population pharmacokinetics",
            abstract=(
                "Current model development is manual. We propose an automated "
                "model selection framework for PopPK analysis."
            ),
            doi="10.1/refresh",
            venue="Journal",
        )
        catalog = {
            "articles": [
                {
                    "id": "doi:10.1/refresh",
                    "title": paper.title,
                    "authors": [],
                    "venue": "Europe PMC",
                    "publication_date": "",
                    "doi": "10.1/refresh",
                    "url": "",
                    "sources": [],
                    "abstract": "",
                    "summary": {"source": "No abstract available"},
                }
            ]
        }
        refreshed = refresh_catalog(catalog, [paper], self.config)
        record = catalog["articles"][0]
        self.assertEqual(refreshed, 1)
        self.assertEqual(record["abstract"], paper.abstract)
        self.assertEqual(record["venue"], "Journal")
        self.assertEqual(record["summary"]["source"], "Abstract-only extractive summary")

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
            self.assertEqual(
                (path / "2026-08-28.md").read_text(encoding="utf-8"), selected
            )


if __name__ == "__main__":
    unittest.main()
