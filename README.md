# PopPK × AI Literature Monitor

This repository is a vibe-coded proof of concept for automated literature monitoring.

Every day at 07:00 JST, GitHub Actions searches Europe PMC, Crossref, and optionally arXiv for methodology papers connecting population pharmacokinetics, pharmacometrics, and AI or machine learning. If no new eligible paper is found, the monitor selects one previously unreported, abstract-bearing paper published in 2020 or later.

Titles and abstracts are used for screening and relevance scoring. All interpretive statements are based on the available abstract only; the program does not fetch or analyze full text.

For each selected paper, the workflow:

- creates a GitHub Issue;
- writes a Markdown report in `reports/`;
- updates the canonical catalog in `data/articles.json`; and
- rebuilds the GitHub Pages dashboard.

Dashboard: https://nakamarusan.github.io/poppk-ai-literature-monitor/

Program and scoring method: https://nakamarusan.github.io/poppk-ai-literature-monitor/method.html

The interface combines a chiaroscuro palette with an original rotating geometric observation instrument. No artwork image or traced composition is embedded.

The 0–100 relevance score measures alignment with the monitoring scope, not scientific quality, validity, novelty, or clinical usefulness.
