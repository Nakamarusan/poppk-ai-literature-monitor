# PopPK × AI Literature Monitor

This repository is a proof-of-concept built through vibe coding to test an automated literature-monitoring workflow.

A GitHub Actions workflow runs every day at 7:00 AM JST and searches Europe PMC, Crossref, and arXiv for methodological studies at the intersection of population pharmacokinetics, pharmacometrics, and artificial intelligence or machine learning. When no newly published eligible paper is found, the workflow selects one previously unreported eligible paper published in 2020 or later.

For each selected paper, the workflow creates a GitHub Issue and stores a report in `reports/` containing:

- Bibliographic information and a link to the paper
- The limitation of previous approaches
- The methodological contribution
- What the study makes newly possible
- Its relevance to population PK and pharmacometrics research

Screening and summarization are automated, so the results should be verified against the original paper.
