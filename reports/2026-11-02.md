<!-- poppk-ai-selection -->

# PopPK × AI Methodology Literature Report

Run time: 2026-11-02 10:10 JST
Source retrieval: **Complete**
New articles: **0**
Archive selections: **1** (unreported papers published since 2020)

Evidence basis: titles and abstracts are used for screening; all interpretations use the abstract only. Full text is not fetched.

Source counts and warnings describe this run. Daily selections are retained when a later retry refreshes the report status.

Recent-search records: Crossref 5124, Europe PMC 5, arXiv 0

## Selection and search coverage

Selection outcome: **selected**
Papers selected in this run: **1**
Retrieval success does not mean that a paper was selected or that all literature was searched.

- Europe PMC: 1 pages; 0 capped queries; 0 failed queries.
- Crossref: 35 pages; 16 capped queries; 0 failed queries.
- arXiv: 1 pages; 0 capped queries; 0 failed queries.

Recent screening (one exclusion reason per unique record):
- retrieved: 5129
- unique: 2725
- duplicates: 2404
- excluded publication type: 135
- missing method evidence: 1
- already reported: 2
- missing pk evidence: 2573
- missing ai evidence: 14

Archive candidates available: 45; unvisited/unfinished windows: 606; completed windows: 2.
Unfinished date windows are resumed on the next eligible run. API cursors are not stored across days.


## 1. [Precision dosing of voriconazole in immunocompromised children under 2 years: integrated machine learning and population pharmacokinetic modeling.](https://europepmc.org/article/MED/41031158)

- **Selection:** Archive article (2020+ fallback)
- **Authors:** Shen L, Hu M, Xu X, Zhou Y, Wu W, Ge X, Wang G, Wang Y, et al.
- **Venue/source:** Frontiers in pharmacology
- **Publication date:** 2025-09-15
- **DOI:** 10.3389/fphar.2025.1671652

### Abstract-only interpretation

- **Prior limitation:** Not stated in the available abstract.
- **Methodological contribution:** Objective This study aimed to develop an individualized dosing strategy for voriconazole (VRZ) in children under 2 years of age by integrating machine learning (ML) and population pharmacokinetic (PopPK) modeling.
- **What becomes possible:** The XGBoost model demonstrated potential in identifying an initial dose recommendation for VRZ.
- **Why it matters:** The selected final model was analyzed for interpretability using Shapley Additive Explanations (SHAP).

- **Relevance score:** 80/100 — PK 30, AI 30, method 10, title intersection 10
- **Summary method:** Abstract-only extractive summary

<details>
<summary>Abstract and screening evidence</summary>

- **Abstract:** Objective This study aimed to develop an individualized dosing strategy for voriconazole (VRZ) in children under 2 years of age by integrating machine learning (ML) and population pharmacokinetic (PopPK) modeling. Methods This retrospective observational study included 76 eligible pediatric patients for model development, analyzing their baseline characteristics and laboratory parameters. A population pharmacokinetic (PopPK) model using NONMEM ® software was performed to assess the clearance (CL) and volume of distribution (V) of VRZ. The individual CL and V were included as input variables. The Boruta algorithm was employed for feature selection, after which six machine learning algorithms were applied. The models were evaluated using Mean Squared Error (MSE), Root Mean Squared Error (RMSE), Mean Absolute Error (MAE), and coefficient of determination (R 2 ) to identify the optimal algorithm, which then underwent independent external validation. The selected final model was analyzed for interpretability using Shapley Additive Explanations (SHAP). Results A total of 76 pediatric patients were enrolled for model development, consisting of 58 males (76.3%) and 18 females (23.7%), with a median age of 11 months and a median weight of 8.05 kg. We analyzed 110 therapeutic drug monitoring (TDM) samples of VRZ from these participants. A one-compartment model with first-order absorptio…
- **PopPK/pharmacometrics terms:** population pharmacokinetic, population pharmacokinetics, poppk
- **AI/ML terms:** machine learning
- **Method terms:** algorithm, model development, software, validation

</details>

---
The relevance score measures topical and methodological alignment, not scientific quality, validity, or clinical utility.
