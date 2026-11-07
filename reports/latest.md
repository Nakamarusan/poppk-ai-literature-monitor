<!-- poppk-ai-selection -->

# PopPK × AI Methodology Literature Report

Run time: 2026-11-07 10:31 JST
Source retrieval: **Complete**
New articles: **0**
Archive selections: **1** (unreported papers published since 2020)

Evidence basis: titles and abstracts are used for screening; all interpretations use the abstract only. Full text is not fetched.

Source counts and warnings describe this run. Daily selections are retained when a later retry refreshes the report status.

Recent-search records: Crossref 5180, Europe PMC 4, arXiv 0

## Selection and search coverage

Selection outcome: **selected**
Papers selected in this run: **1**
Retrieval success does not mean that a paper was selected or that all literature was searched.

- Europe PMC: 1 pages; 0 capped queries; 0 failed queries.
- Crossref: 36 pages; 16 capped queries; 0 failed queries.
- arXiv: 1 pages; 0 capped queries; 0 failed queries.

Recent screening (one exclusion reason per unique record):
- retrieved: 5184
- unique: 2706
- duplicates: 2478
- excluded publication type: 134
- already reported: 4
- missing method evidence: 1
- missing pk evidence: 2550
- missing ai evidence: 17

Archive candidates available: 42; unvisited/unfinished windows: 644; completed windows: 2.
Unfinished date windows are resumed on the next eligible run. API cursors are not stored across days.


## 1. [Hybrid Population Pharmacokinetic-Machine Learning Modeling to Predict Infliximab Pharmacokinetics in Pediatric and Young Adult Patients with Crohn's Disease.](https://europepmc.org/article/MED/40885855)

- **Selection:** Archive article (2020+ fallback)
- **Authors:** Irie K, Minar P, Reifenberg J, Boyle BM, Noe JD, Hyams JS, Mizuno T
- **Venue/source:** Clinical pharmacokinetics
- **Publication date:** 2025-08-30
- **DOI:** 10.1007/s40262-025-01564-7

### Abstract-only interpretation

- **Prior limitation:** Background and objective Population pharmacokinetic (PK) model-based Bayesian estimation is widely used for dose individualization, particularly when sample availability is limited.
- **Methodological contribution:** In this study, we developed a hybrid approach that combines machine learning (ML) with population PK-based Bayesian methods to improve the prediction of infliximab concentrations in children with Crohn's disease.
- **What becomes possible:** Among the ML algorithms, the XGBoost model demonstrated the best performance, achieving an RMSE of 3.78 ± 0.85 µg/mL and an MPE of - 0.03 ± 0.69 µg/mL in 5-fold cross-validation.
- **Why it matters:** Conclusion This hybrid population PK-ML approach provides a promising framework for improving the predictive performance of Bayesian estimation, with the potential for continuous learning from new clinical data to enhance dose individualization.

- **Relevance score:** 80/100 — PK 30, AI 30, method 10, title intersection 10
- **Summary method:** Abstract-only extractive summary

<details>
<summary>Abstract and screening evidence</summary>

- **Abstract:** Background and objective Population pharmacokinetic (PK) model-based Bayesian estimation is widely used for dose individualization, particularly when sample availability is limited. However, its predictive accuracy can be compromised by factors such as misspecified prior information, intra-patient variability, and uncertainties in PK variations. In this study, we developed a hybrid approach that combines machine learning (ML) with population PK-based Bayesian methods to improve the prediction of infliximab concentrations in children with Crohn's disease. Methods We calculated prediction errors between Bayesian-estimated and observed infliximab concentrations from 292 measurements across 93 patients. Incorporating clinical patient features, we explored various ML algorithms, including linear regression, random forest, support vector regression, neural networks, and XGBoost to correct the Bayesian-based prediction errors. The predictive performance of these ML models was assessed using root mean square error (RMSE) and mean prediction error (MPE) with 5-fold cross-validation. Results For Bayesian estimation alone, the RMSE and MPE were 4.8 µg/mL and - 0.67 µg/mL, respectively. Among the ML algorithms, the XGBoost model demonstrated the best performance, achieving an RMSE of 3.78 ± 0.85 µg/mL and an MPE of - 0.03 ± 0.69 µg/mL in 5-fold cross-validation. The ML-corrected Bayesian…
- **PopPK/pharmacometrics terms:** population pharmacokinetic
- **AI/ML terms:** machine learning
- **Method terms:** framework, estimation, validation

</details>

---
The relevance score measures topical and methodological alignment, not scientific quality, validity, or clinical utility.
