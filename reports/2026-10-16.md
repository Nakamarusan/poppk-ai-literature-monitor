<!-- poppk-ai-selection -->

# PopPK × AI Methodology Literature Report

Run time: 2026-10-16 09:00 JST
Source retrieval: **Complete**
New articles: **0**
Archive selections: **1** (unreported papers published since 2020)

Evidence basis: titles and abstracts are used for screening; all interpretations use the abstract only. Full text is not fetched.

Source counts and warnings describe this run. Daily selections are retained when a later retry refreshes the report status.

Recent-search records: Crossref 5337, Europe PMC 0

## Selection and search coverage

Selection outcome: **selected**
Papers selected in this run: **1**
Retrieval success does not mean that a paper was selected or that all literature was searched.

- Europe PMC: 1 pages; 0 capped queries; 0 failed queries.
- Crossref: 36 pages; 16 capped queries; 0 failed queries.

Recent screening (one exclusion reason per unique record):
- retrieved: 5337
- unique: 2886
- duplicates: 2451
- missing pk evidence: 2738
- excluded publication type: 125
- missing ai evidence: 22
- already reported: 1

Archive candidates available: 13; unvisited/unfinished windows: 341; completed windows: 1.
Unfinished date windows are resumed on the next eligible run. API cursors are not stored across days.


## 1. [Raltegravir Plasma Exposure: A Machine Learning-Based Model for its Prediction Using Limited Sampling Strategy.](https://europepmc.org/article/MED/42091773)

- **Selection:** Archive article (2020+ fallback)
- **Authors:** De Lucca Thomaz M, de Azevedo KLR, Paz TA, Nardotto GHB, de Lima Moreira F, Duarte G, Woillard JB, Lanchote VL, et al.
- **Venue/source:** The AAPS journal
- **Publication date:** 2026-05-06
- **DOI:** 10.1208/s12248-026-01248-5

### Abstract-only interpretation

- **Prior limitation:** Recent studies have applied machine learning (ML)-based limited sampling strategies (LSS) to predict drug exposure (AUC), achieving low prediction error and performance comparable to or better than multiple linear regression and population pharmacokinetics LSS.
- **Methodological contribution:** This study aimed to develop and validate a machine learning-based limited sampling strategy capable of predicting raltegravir (RAL) exposure.
- **What becomes possible:** This approach provides a tool for pharmacokinetic and PK/PD studies and reduces intensive sampling need in clinical settings.
- **Why it matters:** Model performance was assessed by the lowest root mean square error (RMSE) in the cross-validation, and the best performing model was evaluated in the test set and externally validated using simulated PK profiles from an independent POPPK model and patient data from a clinical study.

- **Relevance score:** 50/100 — PK 10, AI 30, method 10, title intersection 0
- **Summary method:** Abstract-only extractive summary

<details>
<summary>Abstract and screening evidence</summary>

- **Abstract:** Recent studies have applied machine learning (ML)-based limited sampling strategies (LSS) to predict drug exposure (AUC), achieving low prediction error and performance comparable to or better than multiple linear regression and population pharmacokinetics LSS. This study aimed to develop and validate a machine learning-based limited sampling strategy capable of predicting raltegravir (RAL) exposure. Four machine learning algorithms (XGBoost, Random Forest, GLMNet, and SVM) were trained using pharmacokinetic profiles generated via Monte Carlo simulation from a population pharmacokinetic (POPPK) model. Data were divided into training (75%) and test (25%) sets. All possible combinations of sampling times, pairs and triplets, in steady-state, up to 12 h post-dose were evaluated. Model performance was assessed by the lowest root mean square error (RMSE) in the cross-validation, and the best performing model was evaluated in the test set and externally validated using simulated PK profiles from an independent POPPK model and patient data from a clinical study. XGBoost trained with concentrations at 0.5, 2, and 4 h showed the best predictive performance. The model achieved excellent accuracy in the test set (bias/RMSE: 0.8%/8.7%) and in the independent simulation (1.9%/14.3%). Performance decreased in real patient data (5.0%/24.1%), highlighting the need for caution when extrapolati…
- **PopPK/pharmacometrics terms:** population pharmacokinetic, population pharmacokinetics, poppk
- **AI/ML terms:** machine learning
- **Method terms:** estimation, validation

</details>

---
The relevance score measures topical and methodological alignment, not scientific quality, validity, or clinical utility.
