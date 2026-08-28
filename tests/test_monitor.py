import datetime as dt
import json
import tempfile
import unittest
from pathlib import Path

from src.insights import ResearchInsight, heuristic_insight, parse_insight_json
from src.literature_monitor import (
    JST, Match, Paper, already_succeeded_today, deduplicate, fingerprint,
    normalize_doi, normalize_title, render_report, screen, write_reports,
)


class MonitorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = json.loads(Path("config.json").read_text())

    def test_methodology_paper_is_selected(self):
        paper = Paper(
            ["x"], ["1"],
            "Federated learning framework for population pharmacokinetic estimation",
            abstract=(
                "We propose a distributed optimization algorithm for "
                "nonlinear mixed effects models."
            ),
        )
        self.assertIsNotNone(screen(paper, self.config))

    def test_routine_application_is_excluded(self):
        paper = Paper(
            ["x"], ["1"],
            "Machine learning population pharmacokinetic model of vancomycin",
            abstract="A retrospective drug-specific clinical application.",
        )
        self.assertIsNone(screen(paper, self.config))

    def test_review_is_excluded(self):
        paper = Paper(
            ["x"], ["1"],
            "Review of machine learning methods in population pharmacokinetics",
            abstract="A review of algorithms.",
            publication_type="review",
        )
        self.assertIsNone(screen(paper, self.config))

    def test_doi_deduplication(self):
        a = Paper(["Europe PMC"], ["MED:1"], "One title", doi="10.1/ABC")
        b = Paper(
            ["Crossref"], ["10.1/abc"], "One title",
            doi="https://doi.org/10.1/abc", abstract="Long abstract",
        )
        result = deduplicate([a, b])
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].abstract, "Long abstract")
        self.assertEqual(normalize_doi(result[0].doi), "10.1/abc")

    def test_non_latin_title_key_is_stable(self):
        self.assertEqual(
            normalize_title("母集団 薬物動態"),
            normalize_title("母集団　薬物動態"),
        )

    def test_fingerprint_is_stable(self):
        p1 = Paper(["x"], ["1"], "A", doi="10.1/a")
        p2 = Paper(["x"], ["2"], "B", doi="10.1/b")
        a = Match(p1, 10, "High", [], [], [])
        b = Match(p2, 10, "High", [], [], [])
        self.assertEqual(fingerprint([a, b]), fingerprint([b, a]))

    def test_fallback_uses_japan_date(self):
        state = {"last_success_utc": "2026-08-28T22:10:00+00:00"}
        self.assertTrue(
            already_succeeded_today(state, dt.date(2026, 8, 29))
        )

    def test_model_selection_insight_is_specific(self):
        paper = Paper(
            ["Europe PMC"], ["MED:1"],
            "Development and validation of machine learning model for "
            "selecting the optimal population pharmacokinetic model",
            abstract=(
                "No objective criteria for model selection have been established. "
                "This study aimed to develop and validate a machine learning model "
                "to optimize population pharmacokinetic model selection."
            ),
        )
        match = Match(
            paper, 10, "High",
            ["population pharmacokinetic"],
            ["machine learning"],
            ["model selection"],
        )
        insight = heuristic_insight(match)
        self.assertIn("客観的基準", insight.prior_limitation)
        self.assertIn("患者ごと", insight.new_capability)
        self.assertIn("個別化投与設計", insight.significance)

    def test_parse_ai_insight_json(self):
        text = """```json
        {
          "prior_limitation": "従来の課題。",
          "contribution": "今回の方法。",
          "new_capability": "新たに可能になったこと。",
          "significance": "研究上の意義。"
        }
        ```"""
        insight = parse_insight_json(text, "test")
        self.assertEqual(insight.contribution, "今回の方法。")
        self.assertEqual(insight.source, "test")

    def test_report_contains_research_positioning(self):
        paper = Paper(
            ["x"], ["1"], "A methodology paper",
            authors=["A Author"], venue="Journal", date="2026-08-28",
            doi="10.1/a", abstract="An abstract.",
        )
        match = Match(
            paper, 10, "High",
            ["population pharmacokinetic"], ["machine learning"], ["framework"],
        )
        insight = ResearchInsight(
            "従来の課題。", "今回の方法。", "新たに可能になったこと。",
            "研究上の意義。", "test",
        )
        body = render_report(
            [match], {paper.title_key(): insight},
            dt.datetime(2026, 8, 28, 0, tzinfo=dt.timezone.utc),
            {"Crossref": 1}, {},
        )
        self.assertIn("### 研究の位置づけ（抄録ベース）", body)
        self.assertIn("**従来の課題:** 従来の課題。", body)
        self.assertIn("**新たに可能になったこと:**", body)
        self.assertIn("<details>", body)

    def test_fallback_does_not_overwrite_alert_report(self):
        now = dt.datetime(2026, 8, 28, 0, tzinfo=dt.timezone.utc)
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            alert_body = "新着採択: **1件**\n\n論文A"
            empty_body = "新着採択: **0件**\n\n新着なし"
            write_reports(directory, alert_body, now, 1)
            write_reports(directory, empty_body, now + dt.timedelta(minutes=20), 0)
            archive = directory / "2026-08-28.md"
            self.assertEqual(archive.read_text(), alert_body)
            self.assertEqual((directory / "latest.md").read_text(), alert_body)

    def test_later_new_alert_is_appended(self):
        now = dt.datetime(2026, 8, 28, 0, tzinfo=dt.timezone.utc)
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            first = "新着採択: **1件**\n\n論文A"
            second = "新着採択: **1件**\n\n論文B"
            write_reports(directory, first, now, 1)
            write_reports(directory, second, now + dt.timedelta(minutes=20), 1)
            combined = (directory / "2026-08-28.md").read_text()
            self.assertIn("論文A", combined)
            self.assertIn("論文B", combined)
            self.assertIn("追加検出", combined)


if __name__ == "__main__":
    unittest.main()
