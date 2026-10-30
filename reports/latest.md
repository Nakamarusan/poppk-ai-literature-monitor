<!-- poppk-ai-selection -->

# PopPK × AI Methodology Literature Report

Run time: 2026-10-30 10:29 JST
Source retrieval: **Complete**
New articles: **0**
Archive selections: **1** (unreported papers published since 2020)

Evidence basis: titles and abstracts are used for screening; all interpretations use the abstract only. Full text is not fetched.

Source counts and warnings describe this run. Daily selections are retained when a later retry refreshes the report status.

Recent-search records: Crossref 5164, Europe PMC 4

## Selection and search coverage

Selection outcome: **selected**
Papers selected in this run: **1**
Retrieval success does not mean that a paper was selected or that all literature was searched.

- Europe PMC: 1 pages; 0 capped queries; 0 failed queries.
- Crossref: 36 pages; 16 capped queries; 0 failed queries.

Recent screening (one exclusion reason per unique record):
- retrieved: 5168
- unique: 2722
- duplicates: 2446
- already reported: 4
- missing pk evidence: 2565
- excluded publication type: 135
- missing ai evidence: 18

Archive candidates available: 48; unvisited/unfinished windows: 549; completed windows: 2.
Unfinished date windows are resumed on the next eligible run. API cursors are not stored across days.


## 1. [A machine learning approach to population pharmacokinetic modelling automation.](https://europepmc.org/article/MED/40745042)

- **Selection:** Archive article (2020+ fallback)
- **Authors:** Richardson S, Irurzun Arana I, Nowojewski A, Zhou D, Leander J, Tang W, Dearden R, Gibbs M
- **Venue/source:** Communications medicine
- **Publication date:** 2025-07-31
- **DOI:** 10.1038/s43856-025-01054-8

### Abstract-only interpretation

- **Prior limitation:** Adoption of automatic model search can accelerate popPK analysis, improve model quality, increase reproducibility, and reduce manual effort for modellers.
- **Methodological contribution:** This study demonstrates an automated, out-of-the-box approach for popPK model development, leveraging optimisation algorithms implemented using pyDarwin to efficiently handle a diverse range of extravascular drugs.
- **What becomes possible:** Conclusions These results demonstrate that a single penalty function and model space can be used within the pyDarwin framework to automatically identify model structures for a diverse range of drugs.
- **Why it matters:** This approach was evaluated on one synthetic and four clinical datasets, with results compared to manually developed models.

- **Relevance score:** 90/100 — PK 30, AI 20, method 30, title intersection 10
- **Summary method:** Abstract-only extractive summary

<details>
<summary>Abstract and screening evidence</summary>

- **Abstract:** Background Population pharmacokinetic (PopPK) models are crucial for understanding drug behaviour across populations, yet traditional development is often labour-intensive and slow. This study demonstrates an automated, out-of-the-box approach for popPK model development, leveraging optimisation algorithms implemented using pyDarwin to efficiently handle a diverse range of extravascular drugs. Methods We proposed a generic model search space for drugs with extravascular administration and developed a penalty function to discourage over-parameterisation whilst ensuring plausible parameter values. Optimisation within the model search space was conducted using pyDarwin, employing Bayesian optimisation with a random forest surrogate combined with exhaustive local search. This approach was evaluated on one synthetic and four clinical datasets, with results compared to manually developed models. Results Here we show that the automated approach reliably identifies model structures comparable to manually developed expert models in less than 48 h on average (40-CPU, 40 GB environment) while evaluating fewer than 2.6% of the models in the search space. Ablation experiments demonstrate the importance of our penalty function in selecting plausible models, and the benefit of global search algorithms in avoiding local minima. Conclusions These results demonstrate that a single penalty funct…
- **PopPK/pharmacometrics terms:** population pharmacokinetic, poppk
- **AI/ML terms:** machine learning
- **Method terms:** automation, framework, model development, automated

</details>

---
The relevance score measures topical and methodological alignment, not scientific quality, validity, or clinical utility.
