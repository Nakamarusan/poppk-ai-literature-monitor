<!-- poppk-ai-selection -->

# PopPK × AI Methodology Literature Report

Run time: 2026-10-20 09:52 JST
Source retrieval: **Complete**
New articles: **0**
Archive selections: **1** (unreported papers published since 2020)

Evidence basis: titles and abstracts are used for screening; all interpretations use the abstract only. Full text is not fetched.

Source counts and warnings describe this run. Daily selections are retained when a later retry refreshes the report status.

Recent-search records: Crossref 5274, Europe PMC 5, arXiv 0

## Selection and search coverage

Selection outcome: **selected**
Papers selected in this run: **1**
Retrieval success does not mean that a paper was selected or that all literature was searched.

- Europe PMC: 1 pages; 0 capped queries; 0 failed queries.
- Crossref: 36 pages; 17 capped queries; 0 failed queries.
- arXiv: 1 pages; 0 capped queries; 0 failed queries.

Recent screening (one exclusion reason per unique record):
- retrieved: 5279
- unique: 2841
- duplicates: 2438
- already reported: 2
- excluded publication type: 155
- missing pk evidence: 2669
- missing ai evidence: 15

Archive candidates available: 10; unvisited/unfinished windows: 398; completed windows: 1.
Unfinished date windows are resumed on the next eligible run. API cursors are not stored across days.


## 1. [Predicting Ketamine Exposure in Pediatric Status Epilepticus: A Pharmacokinetic-Machine Learning Approach.](https://europepmc.org/article/MED/41933112)

- **Selection:** Archive article (2020+ fallback)
- **Authors:** Bamgboye AO, Coles LD, Illamola SM, Wolfson J, Cloyd JC
- **Venue/source:** European journal of drug metabolism and pharmacokinetics
- **Publication date:** 2026-04-03
- **DOI:** 10.1007/s13318-026-00996-1

### Abstract-only interpretation

- **Prior limitation:** Early drug exposure estimates could inform dosing, but intensive pharmacokinetic sampling is challenging in pediatric emergency settings due to logistical and ethical constraints.
- **Methodological contribution:** Results We evaluated four machine learning algorithms, including LASSO, random forest (RF), K-nearest neighbor (KNN), and gradient boosted machine (GBM).
- **What becomes possible:** The root mean square errors for RF and GBM were 0.183 mg h/L and 0.185 mg h/L respectively, while mean absolute errors of RF and GBM were 0.103 mg h/L and 0.102 mg h/L, respectively CONCLUSIONS: We demonstrate the feasibility of developing population pharmacokinetic-informed machine learning models to accurately predi…
- **Why it matters:** Not stated in the available abstract.

- **Relevance score:** 50/100 — PK 10, AI 30, method 10, title intersection 0
- **Summary method:** Abstract-only extractive summary

<details>
<summary>Abstract and screening evidence</summary>

- **Abstract:** Background and objective Status epilepticus is a life-threatening neurological emergency. Ketamine combined with levetiracetam is a promising therapy being investigated for established status epilepticus. Early drug exposure estimates could inform dosing, but intensive pharmacokinetic sampling is challenging in pediatric emergency settings due to logistical and ethical constraints. Existing population pharmacokinetic methods with Bayesian forecasting require multiple samples per individual, which is difficult in this context. The objective of this work was to develop a framework that utilizes population pharmacokinetic-simulated datasets as inputs for machine learning models to predict early ketamine exposure in pediatric status epilepticus. Methods We simulated 100,000 concentration-time profiles with covariates using a published population pharmacokinetic model. Additional predictor variables were simulated using distributions from a previously published status epilepticus trial. The simulated data were used to train machine learning algorithms to predict early exposure (AUC 0-2h ) using two samples per individual. The machine learning models were validated internally. Results We evaluated four machine learning algorithms, including LASSO, random forest (RF), K-nearest neighbor (KNN), and gradient boosted machine (GBM). The ensemble models (GBM and RF) achieved superior perf…
- **PopPK/pharmacometrics terms:** population pharmacokinetic
- **AI/ML terms:** machine learning
- **Method terms:** framework, validation

</details>

---
The relevance score measures topical and methodological alignment, not scientific quality, validity, or clinical utility.
