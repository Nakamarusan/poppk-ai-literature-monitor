import datetime as dt
import json
import unittest
from pathlib import Path

from src.literature_monitor import (JST, Match, Paper, already_succeeded_today,
                                    deduplicate, fingerprint, normalize_doi,
                                    normalize_title, screen)


class MonitorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = json.loads(Path("config.json").read_text())

    def test_methodology_paper_is_selected(self):
        paper = Paper(["x"], ["1"],
            "Federated learning framework for population pharmacokinetic estimation",
            abstract="We propose a distributed optimization algorithm for nonlinear mixed effects models.")
        self.assertIsNotNone(screen(paper, self.config))

    def test_routine_application_is_excluded(self):
        paper = Paper(["x"], ["1"],
            "Machine learning population pharmacokinetic model of vancomycin",
            abstract="A retrospective drug-specific clinical application.")
        self.assertIsNone(screen(paper, self.config))

    def test_review_is_excluded(self):
        paper = Paper(["x"], ["1"],
            "Review of machine learning methods in population pharmacokinetics",
            abstract="A review of algorithms.", publication_type="review")
        self.assertIsNone(screen(paper, self.config))

    def test_doi_deduplication(self):
        a = Paper(["Europe PMC"], ["MED:1"], "One title", doi="10.1/ABC")
        b = Paper(["Crossref"], ["10.1/abc"], "One title", doi="https://doi.org/10.1/abc", abstract="Long abstract")
        result = deduplicate([a, b])
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].abstract, "Long abstract")
        self.assertEqual(normalize_doi(result[0].doi), "10.1/abc")

    def test_non_latin_title_key_is_stable(self):
        self.assertEqual(normalize_title("母集団 薬物動態"), normalize_title("母集団　薬物動態"))

    def test_fingerprint_is_stable(self):
        p1 = Paper(["x"], ["1"], "A", doi="10.1/a")
        p2 = Paper(["x"], ["2"], "B", doi="10.1/b")
        a = Match(p1, 10, "High", [], [], [])
        b = Match(p2, 10, "High", [], [], [])
        self.assertEqual(fingerprint([a, b]), fingerprint([b, a]))

    def test_fallback_uses_japan_date(self):
        state = {"last_success_utc": "2026-08-28T22:10:00+00:00"}
        self.assertTrue(already_succeeded_today(state, dt.date(2026, 8, 29)))


if __name__ == "__main__":
    unittest.main()
