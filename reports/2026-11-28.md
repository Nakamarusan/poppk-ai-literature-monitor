<!-- poppk-ai-selection -->

# PopPK × AI Methodology Literature Report

Run time: 2026-11-28 12:41 JST
Source retrieval: **Complete**
New articles: **0**
Archive selections: **1** (unreported papers published since 2020)

Evidence basis: titles and abstracts are used for screening; all interpretations use the abstract only. Full text is not fetched.

Source counts and warnings describe this run. Daily selections are retained when a later retry refreshes the report status.

Recent-search records: Crossref 5154, Europe PMC 3, arXiv 1

## Selection and search coverage

Selection outcome: **selected**
Papers selected in this run: **1**
Retrieval success does not mean that a paper was selected or that all literature was searched.

- Europe PMC: 1 pages; 0 capped queries; 0 failed queries.
- Crossref: 35 pages; 16 capped queries; 0 failed queries.
- arXiv: 1 pages; 0 capped queries; 0 failed queries.

Recent screening (one exclusion reason per unique record):
- retrieved: 5158
- unique: 2699
- duplicates: 2459
- already reported: 3
- excluded publication type: 152
- missing pk evidence: 2533
- missing ai evidence: 11

Archive candidates available: 27; unvisited/unfinished windows: 929; completed windows: 2.
Unfinished date windows are resumed on the next eligible run. API cursors are not stored across days.


## 1. [Estimation of Ganciclovir Exposure in Adults Transplant Patients by Machine Learning.](https://europepmc.org/article/MED/40021573)

- **Selection:** Archive article (2020+ fallback)
- **Authors:** Sayadi H, Fromage Y, Labriffe M, Billat PA, Codde C, Arraki Zava S, Marquet P, Woillard JB
- **Venue/source:** The AAPS journal
- **Publication date:** 2025-02-28
- **DOI:** 10.1208/s12248-025-01034-9

### Abstract-only interpretation

- **Prior limitation:** Conclusions XGBoost ML models accurately estimated GCV AUC0-24 h from limited samples and CrCL, providing a strategy for optimized therapeutic drug monitoring.
- **Methodological contribution:** This study aimed to train, test and validate machine learning (ML) algorithms for accurate GCV AUC0-24 h estimation in solid organ transplantation.
- **What becomes possible:** XGBoost algorithms outperformed or matched MAP-BE, showing enhanced generalization and robustness in their estimates.
- **Why it matters:** Methods We simulated patients for different dosing regimen (900 mg/24 h, 450 mg/24 h, 450 mg/48 h, 450 mg/72 h) using two literature population pharmacokinetic models, allocating 75% for training and 25% for testing.

- **Relevance score:** 70/100 — PK 10, AI 30, method 30, title intersection 0
- **Summary method:** Abstract-only extractive summary

<details>
<summary>Abstract and screening evidence</summary>

- **Abstract:** Introduction Valganciclovir, a prodrug of ganciclovir (GCV), is used to prevent cytomegalovirus infection after transplantation, with doses adjusted based on creatinine clearance (CrCL) to target GCV AUC0-24 h of 40-60 mg*h/L. This sometimes leads to overexposure or underexposure. This study aimed to train, test and validate machine learning (ML) algorithms for accurate GCV AUC0-24 h estimation in solid organ transplantation. Methods We simulated patients for different dosing regimen (900 mg/24 h, 450 mg/24 h, 450 mg/48 h, 450 mg/72 h) using two literature population pharmacokinetic models, allocating 75% for training and 25% for testing. Simulations from two other literature models and real patients provided validation datasets. Three independent sets of ML algorithms were created for each regimen, incorporating CrCL and 2 or 3 concentrations. We evaluated their performance on testing and validation datasets and compared them with MAP-BE. Results XGBoost using 3 concentrations generated the most accurate predictions. In testing dataset, they exhibited a relative bias of -0.02 to 1.5% and a relative RMSE of 2.6 to 8.5%. In the validation dataset, a relative bias of 1.5 to 5.8% and 8.9 to 16.5%, and a relative RMSE of 8.5 to 9.6% and 10.7% to 19.7% were observed depending on the model used. XGBoost algorithms outperformed or matched MAP-BE, showing enhanced generalization and r…
- **PopPK/pharmacometrics terms:** population pharmacokinetic
- **AI/ML terms:** machine learning
- **Method terms:** estimation, validation

</details>

---
The relevance score measures topical and methodological alignment, not scientific quality, validity, or clinical utility.
