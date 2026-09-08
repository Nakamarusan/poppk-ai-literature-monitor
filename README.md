# PopPK × AI Literature Monitor

This repository is a vibe-coded proof of concept for automated literature monitoring.

Every day at 07:00 JST, GitHub Actions searches Europe PMC, Crossref, and optionally arXiv for methodology papers connecting population pharmacokinetics, pharmacometrics, and AI or machine learning. If no new eligible paper is found, the monitor selects one previously unreported, abstract-bearing paper published in 2020 or later.

An independent **Research Spotlight** adds one paper across the flagship journals **Science, Cell, and Nature**, not one per journal. It favors papers published in the last 30 days and falls back to unreported papers from 2020 onward. Exact journal titles and ISSNs exclude sister journals; an available abstract and research-article metadata are required. `flagship_config.json` defines connections to federated analysis, mechanistic modeling, vascular and lymphatic biology, sequential treatment decisions, and perturbation modeling. Potential research uses are labeled as suggestions, not findings established by the paper. No unrelated paper is substituted when no eligible candidate is available.

Titles and abstracts are used for primary screening and relevance scoring. Interpretations use the available abstract only; the program does not fetch or analyze full text.

For each selected primary paper, the workflow creates a GitHub Issue, writes a report in `reports/`, updates `data/articles.json`, and rebuilds `docs/articles.json`. The additional spotlight has its own Issue, `reports/flagship/`, `data/flagship.json`, and `docs/flagship.json`. Seen identifiers are shared to avoid introducing the same paper twice; daily selection limits are independent. The main library's 0–100 score is not applied to the broader research spotlight.

After every successful monitor run on `main`, a separate `workflow_run` deployment checks out the latest `main` and publishes `docs/`, including both catalogs. This also publishes changes made with `GITHUB_TOKEN`. Spotlight source failures do not stop the main monitor; a cached abstract-bearing candidate may be used during an outage. Archive searches are bounded and cached, not exhaustive.

Transient HTTP 429 and 5xx responses use bounded backoff and `Retry-After` handling. Later successful retries replace stale warnings while preserving same-day paper selections.

Dashboard: https://nakamarusan.github.io/poppk-ai-literature-monitor/

Program and selection methods: https://nakamarusan.github.io/poppk-ai-literature-monitor/method.html

The interface uses system typography, readable spacing, light/dark support, and optional geometric motion. All graphics are original; no third-party product imagery or brand assets are embedded.

The 0–100 primary relevance score measures scope alignment, not scientific quality, validity, novelty, or clinical usefulness.
