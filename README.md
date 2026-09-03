# PopPK × AI Literature Monitor

This repository is a vibe-coded proof of concept for automated literature monitoring.

Every day at 07:00 JST, GitHub Actions searches Europe PMC, Crossref, and optionally arXiv for methodological studies connecting population pharmacokinetics, pharmacometrics, and AI or machine learning. If no new eligible paper is found, the monitor selects one previously unreported paper published in 2020 or later.

Screening uses titles and abstracts. All interpretive statements are based on the available abstract only; the program does not fetch or analyze full text.

For each selected paper, the workflow:

- creates a GitHub Issue;
- writes a Markdown report in `reports/`;
- updates the structured catalog in `data/articles.json`; and
- rebuilds the GitHub Pages dashboard.

Dashboard: https://nakamarusan.github.io/poppk-ai-literature-monitor/

Program and scoring method: https://nakamarusan.github.io/poppk-ai-literature-monitor/method.html

The dashboard uses an original chiaroscuro interface inspired by the visual logic of Rembrandt's *Girl at a Window*, sometimes called the “Mona Lisa of London.” No artwork image is reproduced or embedded.

The relevance score measures alignment with the monitoring scope, not scientific quality, validity, or clinical usefulness.
