# PopPK × AI Literature Monitor

This repository is a vibe-coded proof of concept for automated literature monitoring.

## Watch the overview

[![Watch the 45-second illustrated overview: two medicine characters in white lab coats introduce the PopPK × AI Methodology Atlas](docs/media/atlas-explainer-poster.jpg)](https://nakamarusan.github.io/poppk-ai-literature-monitor/explainer.html)

**[Play the video](https://nakamarusan.github.io/poppk-ai-literature-monitor/explainer.html)** · [MP4](https://nakamarusan.github.io/poppk-ai-literature-monitor/media/atlas-explainer.mp4) · [English transcript](docs/media/transcript.md)

A 45-second illustrated walkthrough with English captions. The left capsule speaks in a low, measured male voice; the right tablet answers in a bright female voice. Both are stock synthetic voices, not imitations of real people. Click the thumbnail to open the video player. [Production and source notes](docs/media/README.md).

## What it does

GitHub Actions is scheduled at 07:00 JST to search Europe PMC, Crossref, and optionally arXiv for methodology papers connecting population pharmacokinetics, pharmacometrics, and AI or machine learning. Actual start times can be delayed by GitHub. When there is no new eligible paper, the monitor tries to select one previously unreported, abstract-bearing paper published in 2020 or later.

Titles and abstracts support screening and the 0–100 relevance score. Interpretations use the available abstract only; the program does not fetch or analyze full text. New selections require an available abstract and an in-range publication date. The score measures scope alignment, not scientific quality, validity, novelty, or clinical usefulness.

For each selection, the workflow writes a report in `reports/`, updates `data/articles.json`, queues a GitHub Issue, and rebuilds `docs/articles.json`. After a successful monitor run on `main`, a separate `workflow_run` deployment checks out the latest `main` and publishes `docs/`, including commits made with `GITHUB_TOKEN`.

## Recovery and empty days

Archive retrieval uses publication dates rather than registration dates. `src/archive.py` retains eligible candidates and unfinished source/query/date partitions in `state/archive.json`. API pagination follows cursors within each bounded session. Full date partitions are split and resumed instead of repeatedly requesting the same first page. Short-lived API cursors are not stored across days.

Retrieval success, paper selection, and notification delivery are separate states. The 07:20 fallback is skipped only after a paper has been delivered successfully and no notices remain pending. An empty day produces one status Issue with screening counts and search coverage; it does not fabricate a paper or weaken the eligibility criteria. A failed Issue request stays in a durable outbox for retry.

Default archive refill limits are eight requests, two pages per date window, 200 records per page, and an approximately eight-minute budget between request starts. Pending windows and eligible cached candidates are retained for later runs. API limits, missing abstracts, and keyword screening mean that one eligible paper per day cannot be guaranteed. Optional arXiv errors remain internal.

**[Open the dashboard](https://nakamarusan.github.io/poppk-ai-literature-monitor/)** · **[Check the latest run](https://nakamarusan.github.io/poppk-ai-literature-monitor/run-status.html)** · [Program and selection methods](https://nakamarusan.github.io/poppk-ai-literature-monitor/method.html)

The interface uses system typography, readable spacing, light/dark support, and optional geometric motion. All graphics are original; no third-party product imagery or brand assets are embedded.
