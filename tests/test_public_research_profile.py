"""Keep the public Research Spotlight profile limited to approved topics."""

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class PublicResearchProfileTests(unittest.TestCase):
    def test_public_profile_contains_only_approved_topics(self):
        settings = json.loads(
            (ROOT / "flagship_config.json").read_text(encoding="utf-8")
        )
        names = {topic["name"] for topic in settings["topics"]}
        self.assertEqual(
            names,
            {
                "Federated and privacy-preserving analysis",
                "Lymphatic and vascular disease biology",
                "Mechanistic modeling and inference",
                "Endothelial signaling and targeted therapy",
                "Sequential treatment decisions",
                "Virtual cells and perturbation modeling",
            },
        )

    def test_public_documentation_matches_the_profile(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        method = (ROOT / "docs/method.html").read_text(encoding="utf-8")
        for phrase in (
            "federated analysis",
            "mechanistic modeling",
            "vascular and lymphatic biology",
            "sequential treatment decisions",
            "perturbation modeling",
        ):
            self.assertIn(phrase, readme)
        self.assertIn("virtual cells and perturbations", method)
        self.assertIn("virtual-cell methods 40", method)


if __name__ == "__main__":
    unittest.main()
