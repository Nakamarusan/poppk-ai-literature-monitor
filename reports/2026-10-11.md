<!-- poppk-ai-selection -->

# PopPK × AI Methodology Literature Report

Run time: 2026-10-11 09:37 JST
Source retrieval: **Complete**
New articles: **0**
Archive selections: **1** (unreported papers published since 2020)

Evidence basis: titles and abstracts are used for screening; all interpretations use the abstract only. Full text is not fetched.

Source counts and warnings describe this run. Daily selections are retained when a later retry refreshes the report status.

Recent-search records: Crossref 5261, Europe PMC 1, arXiv 0

## Selection and search coverage

Selection outcome: **selected**
Papers selected in this run: **1**
Retrieval success does not mean that a paper was selected or that all literature was searched.

- Europe PMC: 1 pages; 0 capped queries; 0 failed queries.
- Crossref: 36 pages; 17 capped queries; 0 failed queries.
- arXiv: 1 pages; 0 capped queries; 0 failed queries.

Recent screening (one exclusion reason per unique record):
- retrieved: 5262
- unique: 2824
- duplicates: 2438
- excluded publication type: 138
- missing pk evidence: 2660
- missing ai evidence: 22
- already reported: 2
- missing abstract: 1
- missing method evidence: 1

Archive candidates available: 17; unvisited/unfinished windows: 265; completed windows: 1.
Unfinished date windows are resumed on the next eligible run. API cursors are not stored across days.


## 1. [Development and validation of a machine learning model for individualised meropenem dosing in CRRT patients.](https://europepmc.org/article/MED/41792368)

- **Selection:** Archive article (2020+ fallback)
- **Authors:** Li D, Qiao Z, Xiong X, Zhang Q, He Y, Yu Z, Zheng X, Zheng X
- **Venue/source:** Scientific reports
- **Publication date:** 2026-03-06
- **DOI:** 10.1038/s41598-026-43012-x

### Abstract-only interpretation

- **Prior limitation:** Optimizing meropenem dosing in critically ill patients undergoing continuous renal replacement therapy (CRRT) remains challenging due to significant pharmacokinetic variability.
- **Methodological contribution:** This study aimed to develop and validate a machine learning (ML)-based clinical decision support system (CDSS) for individualizing meropenem dosing in this population.
- **What becomes possible:** Notably, in the external validation cohort, the Gradient Boosting (GB) model robustly outperformed the conventional POPPK model across stringent pharmacodynamic targets (100% fT>MIC and 100% fT>4×MIC), achieving AUC values of 0.884 and 0.929, respectively, versus 0.823 and 0.871 for the POPPK model.
- **Why it matters:** The ML-driven CDSS 'MerDose' provides a clinically applicable tool for optimizing meropenem dosing in CRRT patients, potentially overcoming limitations of conventional approaches.

- **Relevance score:** 70/100 — PK 10, AI 30, method 30, title intersection 0
- **Summary method:** Abstract-only extractive summary

<details>
<summary>Abstract and screening evidence</summary>

- **Abstract:** Optimizing meropenem dosing in critically ill patients undergoing continuous renal replacement therapy (CRRT) remains challenging due to significant pharmacokinetic variability. This study aimed to develop and validate a machine learning (ML)-based clinical decision support system (CDSS) for individualizing meropenem dosing in this population. A large-scale virtual cohort (n = 48,000) was generated using a published population pharmacokinetic (POPPK) model to simulate diverse dosing regimens. Various ML models were trained to predict the probability of achieving two stringent pharmacodynamic (PD) targets: 100% fT>MIC and 100% fT>4×MIC. Feature importance was interpreted using SHAP (Shapley Additive exPlanations) analysis. External validation was conducted using clinical CRRT patient data, and predictive performance was compared with that of the traditional POPPK model. The top-performing model was deployed into a Streamlit-based web CDSS, named "MerDose" for clinical use. The ML models exhibited excellent predictive performance on the simulated test set, with accuracy and F1 scores predominantly above 0.95. Notably, in the external validation cohort, the Gradient Boosting (GB) model robustly outperformed the conventional POPPK model across stringent pharmacodynamic targets (100% fT>MIC and 100% fT>4×MIC), achieving AUC values of 0.884 and 0.929, respectively, versus 0.823 and…
- **PopPK/pharmacometrics terms:** population pharmacokinetic, poppk
- **AI/ML terms:** machine learning
- **Method terms:** validation

</details>

---
The relevance score measures topical and methodological alignment, not scientific quality, validity, or clinical utility.
