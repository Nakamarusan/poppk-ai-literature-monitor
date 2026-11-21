<!-- poppk-ai-selection -->

# PopPK × AI Methodology Literature Report

Run time: 2026-11-21 11:56 JST
Source retrieval: **Complete**
New articles: **0**
Archive selections: **1** (unreported papers published since 2020)

Evidence basis: titles and abstracts are used for screening; all interpretations use the abstract only. Full text is not fetched.

Source counts and warnings describe this run. Daily selections are retained when a later retry refreshes the report status.

Recent-search records: Crossref 5240, Europe PMC 2, arXiv 0

## Selection and search coverage

Selection outcome: **selected**
Papers selected in this run: **1**
Retrieval success does not mean that a paper was selected or that all literature was searched.

- Europe PMC: 1 pages; 0 capped queries; 0 failed queries.
- Crossref: 36 pages; 16 capped queries; 0 failed queries.
- arXiv: 1 pages; 0 capped queries; 0 failed queries.

Recent screening (one exclusion reason per unique record):
- retrieved: 5242
- unique: 2696
- duplicates: 2546
- excluded publication type: 134
- already reported: 2
- missing pk evidence: 2544
- missing ai evidence: 16

Archive candidates available: 32; unvisited/unfinished windows: 834; completed windows: 2.
Unfinished date windows are resumed on the next eligible run. API cursors are not stored across days.


## 1. [Stochastic gates for covariate selection in population pharmacokinetics modelling](https://europepmc.org/article/PPR/PPR1029163)

- **Selection:** Archive article (2020+ fallback)
- **Authors:** Kekic M, Stepanov O, Wang W, Richardson S, Olabode D, Traynor C, Dearden R, Zhou D, et al.
- **Venue/source:** Europe PMC
- **Publication date:** 2025-06-01
- **DOI:** 10.1101/2025.05.28.656586

### Abstract-only interpretation

- **Prior limitation:** Traditional stepwise covariate modelling is often time-consuming, compared to the new machine learning alternatives.
- **Methodological contribution:** This study investigates the use of Neural Networks with Stochastic Gates for automated covariate selection, aiming to efficiently identify relevant covariates while penalizing excessive covariate inclusion.
- **What becomes possible:** Neural Networks with Stochastic Gates provide a reliable approach in accurately detecting covariates because they can effectively eliminate irrelevant covariates even in cases with high inter-covariates correlation.
- **Why it matters:** This approach accelerates pharmacokinetic model development by significantly reducing the time required for covariate evaluation.

- **Relevance score:** 70/100 — PK 30, AI 10, method 30, title intersection 0
- **Summary method:** Abstract-only extractive summary

<details>
<summary>Abstract and screening evidence</summary>

- **Abstract:** Covariate selection in population pharmacokinetics modelling is essential for understanding interindividual variability in drug response and optimizing dosing. Traditional stepwise covariate modelling is often time-consuming, compared to the new machine learning alternatives. This study investigates the use of Neural Networks with Stochastic Gates for automated covariate selection, aiming to efficiently identify relevant covariates while penalizing excessive covariate inclusion. On various synthetic datasets the approach demonstrated robustness in detecting important covariates, overcoming challenges such as high correlations, low covariate frequencies, high interindividual variability and complex covariate dependencies. In real clinical data from a monalizumab study, the method successfully identified covariates that matched those found by experts. However, for tixagevimab/cilgavimab, it identified a superset of covariates, indicating a potential need for further pruning. This machine learning-based method enhances the covariate pre-selection process in population pharmacokinetics model development, offering significant time savings and improving efficiency even under challenging scenarios. Graphical Abstract Study Highlights WHAT IS THE CURRENT KNOWLEDGE ON THE TOPIC? Covariate selection in population pharmacokinetics modelling is a crucial step in drug development and dosin…
- **PopPK/pharmacometrics terms:** population pharmacokinetics
- **AI/ML terms:** machine learning, automated covariate selection
- **Method terms:** covariate selection, model development, automated

</details>

---
The relevance score measures topical and methodological alignment, not scientific quality, validity, or clinical utility.
