# PopPK × AI Literature Monitor

This repository is a vibe-coded proof of concept for automated literature monitoring.

Every day at 07:00 JST, GitHub Actions searches Europe PMC, Crossref, and optionally arXiv for methodology papers connecting population pharmacokinetics, pharmacometrics, and AI or machine learning. If no new eligible paper is found, the monitor selects one previously unreported, abstract-bearing paper published in 2020 or later.

Titles and abstracts are used for screening and relevance scoring. All interpretive statements are based on the available abstract only; the program does not fetch or analyze full text.

For each selected paper, the workflow:

- creates a GitHub Issue;
- writes a Markdown report in `reports/`;
- updates the canonical catalog in `data/articles.json`; and
- rebuilds `docs/articles.json` for the GitHub Pages dashboard.

After every successful monitor run on `main`, a separate `workflow_run` deployment checks out the latest `main` branch and publishes the current `docs/` directory. This ensures that commits created by the monitor's `GITHUB_TOKEN` also reach GitHub Pages.

Transient HTTP 429 and 5xx responses are retried with bounded exponential backoff and `Retry-After` handling. When a later retry succeeds, the daily report replaces stale source warnings while retaining papers already reported on the same JST date.

Dashboard: https://nakamarusan.github.io/poppk-ai-literature-monitor/

Program and scoring method: https://nakamarusan.github.io/poppk-ai-literature-monitor/method.html

The Pages interface uses a clean, system-native visual language with generous spacing, layered translucent materials, high-contrast typography, touch-friendly controls, and optional geometric motion. All interface graphics are original; no third-party product imagery or brand assets are embedded.

The 0–100 relevance score measures alignment with the monitoring scope, not scientific quality, validity, novelty, or clinical usefulness.
