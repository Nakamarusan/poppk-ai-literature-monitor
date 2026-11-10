<!-- poppk-ai-selection -->

# PopPK × AI Methodology Literature Report

Run time: 2026-11-10 12:55 JST
Source retrieval: **Complete**
New articles: **0**
Archive selections: **1** (unreported papers published since 2020)

Evidence basis: titles and abstracts are used for screening; all interpretations use the abstract only. Full text is not fetched.

Source counts and warnings describe this run. Daily selections are retained when a later retry refreshes the report status.

Recent-search records: Crossref 5192, Europe PMC 7, arXiv 0

## Selection and search coverage

Selection outcome: **selected**
Papers selected in this run: **1**
Retrieval success does not mean that a paper was selected or that all literature was searched.

- Europe PMC: 1 pages; 0 capped queries; 0 failed queries.
- Crossref: 36 pages; 16 capped queries; 0 failed queries.
- arXiv: 1 pages; 0 capped queries; 0 failed queries.

Recent screening (one exclusion reason per unique record):
- retrieved: 5199
- unique: 2657
- duplicates: 2542
- excluded publication type: 133
- missing method evidence: 1
- already reported: 4
- missing pk evidence: 2504
- missing ai evidence: 15

Archive candidates available: 39; unvisited/unfinished windows: 701; completed windows: 2.
Unfinished date windows are resumed on the next eligible run. API cursors are not stored across days.


## 1. [A Real-Time Plasma Concentration Prediction Model for Voriconazole in Elderly Patients via Machine Learning Combined with Population Pharmacokinetics.](https://europepmc.org/article/MED/40401163)

- **Selection:** Archive article (2020+ fallback)
- **Authors:** Liu R, Ma P, Chen D, Yu M, Xie L, Zhao L, Huang Y, Shang S, et al.
- **Venue/source:** Drug design, development and therapy
- **Publication date:** 2025-05-17
- **DOI:** 10.2147/dddt.s495050

### Abstract-only interpretation

- **Prior limitation:** Not stated in the available abstract.
- **Methodological contribution:** Not stated in the available abstract.
- **What becomes possible:** Feature selection reduced the number of features from 31 to 9 without compromising predictive performance.
- **Why it matters:** The model was optimized using feature selection and may serve as a reference for individualized VCZ dosing in clinical practice, thereby enhancing the efficacy and safety of VCZ treatment in elderly patients.

- **Relevance score:** 80/100 — PK 30, AI 30, method 10, title intersection 10
- **Summary method:** Abstract-only extractive summary

<details>
<summary>Abstract and screening evidence</summary>

- **Abstract:** Purpose Voriconazole (VCZ) is a first-line treatment for invasive fungal disease, characterized by a narrow therapeutic window and significant inter-individual variability. It is primarily metabolized by the liver, the function of which declines with age. Pathological and physiological changes in elderly patients contribute to increased fluctuations in VCZ plasma concentrations. Thus, it is crucial to develop a model that accurately predicts the VCZ plasma concentrations in elderly patients. Patients and methods This retrospective study incorporated 31 features, including pharmacokinetic parameters derived from a population pharmacokinetic (PPK) model. Feature selection for machine learning (ML) models was performed using Recursive Feature Elimination with Cross-Validation (RFECV). Multiple algorithms were selected and combined into an ML ensemble model, which was interpreted using Shapley Additive exPlanations (SHAP). Results The predictive performance of ML models was significantly improved by incorporating pharmacokinetic parameters. The ensemble model consisting of XGBoost, random forest (RF), and CatBoost (1:1:8) achieved the highest R 2 (0.828) and was selected as the final ML model. Feature selection reduced the number of features from 31 to 9 without compromising predictive performance. The R 2 , mean absolute error (MAE), and mean squared error (MSE) of the external v…
- **PopPK/pharmacometrics terms:** population pharmacokinetics, population pharmacokinetic
- **AI/ML terms:** machine learning
- **Method terms:** validation

</details>

---
The relevance score measures topical and methodological alignment, not scientific quality, validity, or clinical utility.
