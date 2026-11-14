<!-- poppk-ai-selection -->

# PopPK × AI Methodology Literature Report

Run time: 2026-11-14 10:56 JST
Source retrieval: **Complete**
New articles: **0**
Archive selections: **1** (unreported papers published since 2020)

Evidence basis: titles and abstracts are used for screening; all interpretations use the abstract only. Full text is not fetched.

Source counts and warnings describe this run. Daily selections are retained when a later retry refreshes the report status.

Recent-search records: Crossref 5248, Europe PMC 5, arXiv 0

## Selection and search coverage

Selection outcome: **selected**
Papers selected in this run: **1**
Retrieval success does not mean that a paper was selected or that all literature was searched.

- Europe PMC: 1 pages; 0 capped queries; 0 failed queries.
- Crossref: 36 pages; 16 capped queries; 0 failed queries.
- arXiv: 1 pages; 0 capped queries; 0 failed queries.

Recent screening (one exclusion reason per unique record):
- retrieved: 5253
- unique: 2731
- duplicates: 2522
- already reported: 3
- missing method evidence: 2
- excluded publication type: 122
- missing pk evidence: 2593
- missing ai evidence: 11

Archive candidates available: 37; unvisited/unfinished windows: 739; completed windows: 2.
Unfinished date windows are resumed on the next eligible run. API cursors are not stored across days.


## 1. [Individualized Meropenem Dosing in CRRT Patients: Development and Validation of a Machine Learning-Based Decision Support Tool](https://europepmc.org/article/PPR/PPR1087815)

- **Selection:** Archive article (2020+ fallback)
- **Authors:** Li D, Qiao Z, Xiong X, Zhang Q, He Y, Yu Z, Zheng X, Zheng X
- **Venue/source:** Europe PMC
- **Publication date:** 2025-09-19
- **DOI:** 10.21203/rs.3.rs-7564311/v1

### Abstract-only interpretation

- **Prior limitation:** Abstract Background The optimization of meropenem dosing in critically ill patients undergoing continuous renal replacement therapy (CRRT) remains a significant clinical challenge.
- **Methodological contribution:** This study aimed to assess whether a machine learning–based clinical decision support system (CDSS) can support clinicians in determining the optimal meropenem dosing strategy.
- **What becomes possible:** Results Across the simulated test dataset, ML models demonstrated outstanding predictive performance for both PD targets, with most accuracy and F1 scores surpassing 0.95.
- **Why it matters:** Conclusion We developed an ML-driven CDSS, "MerDose," capable of accurately predicting individualized meropenem dosing in critically ill CRRT patients.

- **Relevance score:** 70/100 — PK 10, AI 30, method 30, title intersection 0
- **Summary method:** Abstract-only extractive summary

<details>
<summary>Abstract and screening evidence</summary>

- **Abstract:** Abstract Background The optimization of meropenem dosing in critically ill patients undergoing continuous renal replacement therapy (CRRT) remains a significant clinical challenge. This study aimed to assess whether a machine learning–based clinical decision support system (CDSS) can support clinicians in determining the optimal meropenem dosing strategy. Methods Using a previously published population pharmacokinetic (POPPK) model of meropenem, we generated a virtual cohort of 2000 CRRT patients to simulate various dosing strategies and pathogen susceptibility profiles. Patient demographics, dosing parameters, and CRRT settings were incorporated as features to train ML models predicting the probability of achieving two pharmacodynamic (PD) endpoints (100% fT > MIC and 100% fT > 4×MIC). Feature importance was further assessed using SHAP analysis. External validation was conducted with clinical CRRT patient data, and predictive performance was compared against the traditional POPPK model. The top-performing model was deployed into a Streamlit-based web CDSS, named "MerDose," for clinical use. Results Across the simulated test dataset, ML models demonstrated outstanding predictive performance for both PD targets, with most accuracy and F1 scores surpassing 0.95. SHAP analysis indicated that MIC, dosing interval, administered dose, CLCRRT, and CRCL were the key determinants of pr…
- **PopPK/pharmacometrics terms:** population pharmacokinetic, poppk
- **AI/ML terms:** machine learning
- **Method terms:** validation, framework, optimization

</details>

---
The relevance score measures topical and methodological alignment, not scientific quality, validity, or clinical utility.
