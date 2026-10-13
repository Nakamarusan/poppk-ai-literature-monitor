<!-- poppk-ai-selection -->

# PopPK × AI Methodology Literature Report

Run time: 2026-10-13 11:48 JST
Source retrieval: **Complete**
New articles: **0**
Archive selections: **1** (unreported papers published since 2020)

Evidence basis: titles and abstracts are used for screening; all interpretations use the abstract only. Full text is not fetched.

Source counts and warnings describe this run. Daily selections are retained when a later retry refreshes the report status.

Recent-search records: Crossref 5289, Europe PMC 1, arXiv 0

## Selection and search coverage

Selection outcome: **selected**
Papers selected in this run: **1**
Retrieval success does not mean that a paper was selected or that all literature was searched.

- Europe PMC: 1 pages; 0 capped queries; 0 failed queries.
- Crossref: 36 pages; 16 capped queries; 0 failed queries.
- arXiv: 1 pages; 0 capped queries; 0 failed queries.

Recent screening (one exclusion reason per unique record):
- retrieved: 5290
- unique: 2839
- duplicates: 2451
- excluded publication type: 126
- missing pk evidence: 2689
- missing ai evidence: 23
- already reported: 1

Archive candidates available: 15; unvisited/unfinished windows: 303; completed windows: 1.
Unfinished date windows are resumed on the next eligible run. API cursors are not stored across days.


## 1. [Stochastic Gates for Covariate Selection in Population Pharmacokinetics Modeling.](https://europepmc.org/article/MED/41637692)

- **Selection:** Archive article (2020+ fallback)
- **Authors:** Kekic M, Stepanov O, Wang W, Richardson S, Olabode D, Traynor C, Dearden R, Zhou D, et al.
- **Venue/source:** CPT: pharmacometrics & systems pharmacology
- **Publication date:** 2026-02-01
- **DOI:** 10.1002/psp4.70147

### Abstract-only interpretation

- **Prior limitation:** Traditional stepwise covariate modeling is often time-consuming, compared to the new machine learning alternatives.
- **Methodological contribution:** This study investigates the use of neural networks with stochastic gates for automated covariate selection, aiming to efficiently identify relevant covariates while penalizing excessive covariate inclusion.
- **What becomes possible:** On various synthetic datasets, the approach demonstrated robustness in detecting important covariates, overcoming challenges such as high correlations, low covariate frequencies, high interindividual variability, and complex covariate dependencies.
- **Why it matters:** However, for tixagevimab/cilgavimab, it identified a superset of covariates, indicating a potential need for further pruning.

- **Relevance score:** 70/100 — PK 30, AI 10, method 30, title intersection 0
- **Summary method:** Abstract-only extractive summary

<details>
<summary>Abstract and screening evidence</summary>

- **Abstract:** Covariate selection in population pharmacokinetics modeling is essential for understanding interindividual variability in drug response and optimizing dosing. Traditional stepwise covariate modeling is often time-consuming, compared to the new machine learning alternatives. This study investigates the use of neural networks with stochastic gates for automated covariate selection, aiming to efficiently identify relevant covariates while penalizing excessive covariate inclusion. On various synthetic datasets, the approach demonstrated robustness in detecting important covariates, overcoming challenges such as high correlations, low covariate frequencies, high interindividual variability, and complex covariate dependencies. In real clinical data from a monalizumab study, the method successfully identified covariates that matched those found by experts. However, for tixagevimab/cilgavimab, it identified a superset of covariates, indicating a potential need for further pruning. This machine learning-based method enhances the covariate preselection process in population pharmacokinetics model development, offering significant time savings and improving efficiency even under challenging scenarios.
- **PopPK/pharmacometrics terms:** population pharmacokinetics
- **AI/ML terms:** machine learning, automated covariate selection
- **Method terms:** covariate selection, model development, automated

</details>

---
The relevance score measures topical and methodological alignment, not scientific quality, validity, or clinical utility.
