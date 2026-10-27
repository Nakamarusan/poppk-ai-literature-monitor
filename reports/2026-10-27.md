<!-- poppk-ai-selection -->

# PopPK × AI Methodology Literature Report

Run time: 2026-10-27 10:02 JST
Source retrieval: **Complete**
New articles: **0**
Archive selections: **1** (unreported papers published since 2020)

Evidence basis: titles and abstracts are used for screening; all interpretations use the abstract only. Full text is not fetched.

Source counts and warnings describe this run. Daily selections are retained when a later retry refreshes the report status.

Recent-search records: Crossref 5246, Europe PMC 4, arXiv 0

Archive-search records: Europe PMC 92

## Selection and search coverage

Selection outcome: **selected**
Papers selected in this run: **1**
Retrieval success does not mean that a paper was selected or that all literature was searched.

- Europe PMC: 1 pages; 0 capped queries; 0 failed queries.
- Crossref: 36 pages; 16 capped queries; 0 failed queries.
- arXiv: 1 pages; 0 capped queries; 0 failed queries.

Recent screening (one exclusion reason per unique record):
- retrieved: 5250
- unique: 2786
- duplicates: 2464
- already reported: 4
- excluded publication type: 136
- missing pk evidence: 2629
- missing ai evidence: 17

Archive candidates available: 50; unvisited/unfinished windows: 511; completed windows: 2.
Unfinished date windows are resumed on the next eligible run. API cursors are not stored across days.

Archive screening (per page; records can recur between queries):
- retrieved: 92
- unique: 90
- duplicates: 2
- excluded publication type: 29
- eligible unreported: 47
- missing method evidence: 12
- missing pk evidence: 1
- missing abstract: 1


## 1. [Machine learning-assisted tacrolimus dose optimization in childhood- onset systemic lupus erythematosus through population pharmacokinetic modeling.](https://europepmc.org/article/MED/40684660)

- **Selection:** Archive article (2020+ fallback)
- **Authors:** Liang H, Xuan Q, Liu C, Wan A, You N, Xiao M, Zhang H, Han M, et al.
- **Venue/source:** Computers in biology and medicine
- **Publication date:** 2025-07-19
- **DOI:** 10.1016/j.compbiomed.2025.110782

### Abstract-only interpretation

- **Prior limitation:** Not stated in the available abstract.
- **Methodological contribution:** Objective This study aimed to improve treatment effectiveness in childhood-onset systemic lupus erythematosus (cSLE) by developing machine learning algorithms integrated with pharmacokinetic parameters to predict individualized tacrolimus dosing for optimized therapy.
- **What becomes possible:** Among the 27 machine learning models, the XGBoost algorithm demonstrated the best prediction accuracy for tacrolimus dose (R 2 = 0.74, mean absolute error [MAE] = 0.016, mean square error [MSE] = 0.0005).
- **Why it matters:** Conclusion This study successfully developed an accurate machine learning-based model for predicting individualized tacrolimus dosing in cSLE patients.

- **Relevance score:** 100/100 — PK 30, AI 30, method 30, title intersection 10
- **Summary method:** Abstract-only extractive summary

<details>
<summary>Abstract and screening evidence</summary>

- **Abstract:** Objective This study aimed to improve treatment effectiveness in childhood-onset systemic lupus erythematosus (cSLE) by developing machine learning algorithms integrated with pharmacokinetic parameters to predict individualized tacrolimus dosing for optimized therapy. Methods Data from 480 trough tacrolimus concentrations in 86 cSLE patients over five years were analyzed. A nonlinear mixed-effects model was constructed to characterize the pharmacokinetics of tacrolimus. We screened 27 machine learning and deep learning models using 29 clinical variables to select the best-performing individualized dose prediction model. To further enhance prediction accuracy, the pharmacokinetic parameters were subsequently embedded within the optimized model. Model performance was assessed through the utilization of goodness-of-fit plots and diagnostic parameters such as objective function values and Shapley Additive exPlanations (SHAP) values. Results The pharmacokinetic profile of tacrolimus was best accurately characterized by a one-compartment model, which incorporated first-order kinetics for both absorption and elimination processes. The typical estimates for apparent clearance (CL/F) and volume of distribution (V/F) were 3.52 L/h/70 kg and 124.84 L/70 kg, respectively. Among the 27 machine learning models, the XGBoost algorithm demonstrated the best prediction accuracy for tacrolimus d…
- **PopPK/pharmacometrics terms:** population pharmacokinetic, nonlinear mixed effects
- **AI/ML terms:** machine learning, deep learning
- **Method terms:** optimization, algorithm

</details>

---
The relevance score measures topical and methodological alignment, not scientific quality, validity, or clinical utility.
