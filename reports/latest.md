<!-- poppk-ai-selection -->

# PopPK × AI Methodology Literature Report

Run time: 2026-11-19 11:54 JST
Source retrieval: **Complete**
New articles: **0**
Archive selections: **1** (unreported papers published since 2020)

Evidence basis: titles and abstracts are used for screening; all interpretations use the abstract only. Full text is not fetched.

Source counts and warnings describe this run. Daily selections are retained when a later retry refreshes the report status.

Recent-search records: Crossref 5271, Europe PMC 2, arXiv 1

## Selection and search coverage

Selection outcome: **selected**
Papers selected in this run: **1**
Retrieval success does not mean that a paper was selected or that all literature was searched.

- Europe PMC: 1 pages; 0 capped queries; 0 failed queries.
- Crossref: 36 pages; 16 capped queries; 0 failed queries.
- arXiv: 1 pages; 0 capped queries; 0 failed queries.

Recent screening (one exclusion reason per unique record):
- retrieved: 5274
- unique: 2748
- duplicates: 2526
- already reported: 3
- missing method evidence: 1
- missing ai evidence: 17
- missing pk evidence: 2598
- excluded publication type: 129

Archive candidates available: 33; unvisited/unfinished windows: 815; completed windows: 2.
Unfinished date windows are resumed on the next eligible run. API cursors are not stored across days.


## 1. [Leveraging Neural ODEs for Population Pharmacokinetics of Dalbavancin in Sparse Clinical Data.](https://europepmc.org/article/MED/40566189)

- **Selection:** Archive article (2020+ fallback)
- **Authors:** Giacometti T, Rocchi E, Cojutti PG, Magnani F, Remondini D, Pea F, Castellani G
- **Venue/source:** Entropy (Basel, Switzerland)
- **Publication date:** 2025-06-05
- **DOI:** 10.3390/e27060602

### Abstract-only interpretation

- **Prior limitation:** Given the challenge of limited data availability, a data augmentation strategy was employed to pre-train NODEs.
- **Methodological contribution:** This study investigates the use of Neural Ordinary Differential Equations (NODEs) as an alternative to traditional compartmental models and Nonlinear Mixed-Effects (NLME) models for drug concentration prediction in pharmacokinetics.
- **What becomes possible:** However, when covariates were incorporated, NODEs demonstrated superior predictive accuracy.
- **Why it matters:** Not stated in the available abstract.

- **Relevance score:** 70/100 — PK 30, AI 20, method 10, title intersection 10
- **Summary method:** Abstract-only extractive summary

<details>
<summary>Abstract and screening evidence</summary>

- **Abstract:** This study investigates the use of Neural Ordinary Differential Equations (NODEs) as an alternative to traditional compartmental models and Nonlinear Mixed-Effects (NLME) models for drug concentration prediction in pharmacokinetics. Unlike standard models that rely on strong assumptions and often struggle with high-dimensional covariate relationships, NODEs offer a data-driven approach, learning differential equations directly from data while integrating covariates. To evaluate their performance, NODEs were applied to a real-world Dalbavancin pharmacokinetic dataset comprising 218 patients and compared against a two-compartment model and an NLME within a cross-validation framework, which ensures an evaluation of robustness. Given the challenge of limited data availability, a data augmentation strategy was employed to pre-train NODEs. Their predictive performance was assessed both with and without covariates, while model explainability was analyzed using Shapley additive explanations (SHAP) values. Results show that, in the absence of covariates, NODEs performed comparably to state-of-the-art NLME models. However, when covariates were incorporated, NODEs demonstrated superior predictive accuracy. SHAP analyses further revealed how NODEs leverage covariates in their predictions. These results establish NODEs as a promising alternative for pharmacokinetic modeling, particularly i…
- **PopPK/pharmacometrics terms:** population pharmacokinetics, nonlinear mixed effects, nlme
- **AI/ML terms:** neural odes
- **Method terms:** framework, validation

</details>

---
The relevance score measures topical and methodological alignment, not scientific quality, validity, or clinical utility.
