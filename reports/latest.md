<!-- poppk-ai-selection -->

# PopPK × AI Methodology Literature Report

Run time: 2026-11-16 10:31 JST
Source retrieval: **Complete**
New articles: **0**
Archive selections: **1** (unreported papers published since 2020)

Evidence basis: titles and abstracts are used for screening; all interpretations use the abstract only. Full text is not fetched.

Source counts and warnings describe this run. Daily selections are retained when a later retry refreshes the report status.

Recent-search records: Crossref 5254, Europe PMC 3

## Selection and search coverage

Selection outcome: **selected**
Papers selected in this run: **1**
Retrieval success does not mean that a paper was selected or that all literature was searched.

- Europe PMC: 1 pages; 0 capped queries; 0 failed queries.
- Crossref: 36 pages; 16 capped queries; 0 failed queries.

Recent screening (one exclusion reason per unique record):
- retrieved: 5257
- unique: 2732
- duplicates: 2525
- already reported: 3
- missing method evidence: 1
- missing pk evidence: 2597
- missing ai evidence: 14
- excluded publication type: 117

Archive candidates available: 35; unvisited/unfinished windows: 777; completed windows: 2.
Unfinished date windows are resumed on the next eligible run. API cursors are not stored across days.


## 1. [Estimation of Overall Cyclosporine Exposure Using Machine Learning.](https://europepmc.org/article/MED/40698833)

- **Selection:** Archive article (2020+ fallback)
- **Authors:** Woillard JB, Labriffe M, Marquet P
- **Venue/source:** Therapeutic drug monitoring
- **Publication date:** 2025-07-23
- **DOI:** 10.1097/ftd.0000000000001346

### Abstract-only interpretation

- **Prior limitation:** The interdose area under the concentration-time curve (AUC 0-12 h ) is considered to be a superior metric of drug exposure compared with single concentration measurements but is, nevertheless, resource-intensive.
- **Methodological contribution:** Machine learning (ML) offers a novel approach for AUC prediction by leveraging patient-specific data without relying on traditional pharmacokinetic assumptions.
- **What becomes possible:** Results The three-sample XGBoost model achieved high accuracy in kidney transplant recipients (root mean square error [RMSE] Conclusions ML-based AUC prediction is a promising alternative to MAP-BE, particularly for kidney transplantation.
- **Why it matters:** Not stated in the available abstract.

- **Relevance score:** 70/100 — PK 10, AI 30, method 30, title intersection 0
- **Summary method:** Abstract-only extractive summary

<details>
<summary>Abstract and screening evidence</summary>

- **Abstract:** Background Cyclosporine (CsA), an immunosuppressant widely used in solid-organ transplantation, requires precise therapeutic drug monitoring to balance its efficacy and toxicity. The interdose area under the concentration-time curve (AUC 0-12 h ) is considered to be a superior metric of drug exposure compared with single concentration measurements but is, nevertheless, resource-intensive. Machine learning (ML) offers a novel approach for AUC prediction by leveraging patient-specific data without relying on traditional pharmacokinetic assumptions. This study intended to develop and evaluate XGBoost ML models for predicting CsA AUC 0-12 h using either two or three blood concentrations and to compare their performance against maximum a posteriori Bayesian estimation (MAP-BE) based on population pharmacokinetic models. Methods Using data from 2009 patients and 6360 dose-adjustment requests on the Immunosuppressant Bayesian Dose Adjustment website ( https://abis.chu-limoges.fr/ ), supervised ML models were trained with predictors including CsA concentrations at predefined time points (C0, C1, and C3), dose, age, and sampling time deviations. External validation was performed using rich pharmacokinetic profiles of kidney, heart, lung, and bone marrow transplant recipients. Results The three-sample XGBoost model achieved high accuracy in kidney transplant recipients (root mean square…
- **PopPK/pharmacometrics terms:** population pharmacokinetic
- **AI/ML terms:** machine learning
- **Method terms:** estimation, validation

</details>

---
The relevance score measures topical and methodological alignment, not scientific quality, validity, or clinical utility.
