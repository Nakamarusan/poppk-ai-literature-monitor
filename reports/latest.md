<!-- poppk-ai-selection -->

# PopPK × AI Methodology Literature Report

Run time: 2026-11-15 10:28 JST
Source retrieval: **Complete**
New articles: **0**
Archive selections: **1** (unreported papers published since 2020)

Evidence basis: titles and abstracts are used for screening; all interpretations use the abstract only. Full text is not fetched.

Source counts and warnings describe this run. Daily selections are retained when a later retry refreshes the report status.

Recent-search records: Crossref 5259, Europe PMC 4, arXiv 0

## Selection and search coverage

Selection outcome: **selected**
Papers selected in this run: **1**
Retrieval success does not mean that a paper was selected or that all literature was searched.

- Europe PMC: 1 pages; 0 capped queries; 0 failed queries.
- Crossref: 36 pages; 16 capped queries; 0 failed queries.
- arXiv: 1 pages; 0 capped queries; 0 failed queries.

Recent screening (one exclusion reason per unique record):
- retrieved: 5263
- unique: 2737
- duplicates: 2526
- already reported: 3
- missing method evidence: 1
- excluded publication type: 121
- missing pk evidence: 2599
- missing ai evidence: 13

Archive candidates available: 36; unvisited/unfinished windows: 758; completed windows: 2.
Unfinished date windows are resumed on the next eligible run. API cursors are not stored across days.


## 1. [Machine Learning-Based Model Selection and Averaging Outperform Single-Model Approaches for a Priori Vancomycin Precision Dosing.](https://europepmc.org/article/MED/40734640)

- **Selection:** Archive article (2020+ fallback)
- **Authors:** van Os W, O'Jeanson A, Troisi C, Liu C, Brooks JT, Hughes JH, Tong DMH, Keizer RJ
- **Venue/source:** CPT: pharmacometrics & systems pharmacology
- **Publication date:** 2025-07-30
- **DOI:** 10.1002/psp4.70084

### Abstract-only interpretation

- **Prior limitation:** Not stated in the available abstract.
- **Methodological contribution:** We developed a machine learning (ML) model to guide individualized PK model selection for a priori MIPD of vancomycin based on routinely recorded patient characteristics.
- **What becomes possible:** Selecting the highest ranked PK model for each patient and ML-based model averaging outperformed all single PK models, body mass index-based selection, and naive averaging.
- **Why it matters:** Selecting an appropriate population pharmacokinetic (PK) model for individual patients in model-informed precision dosing (MIPD) can be challenging, particularly in the absence of therapeutic drug monitoring (TDM) samples.

- **Relevance score:** 70/100 — PK 10, AI 30, method 30, title intersection 0
- **Summary method:** Abstract-only extractive summary

<details>
<summary>Abstract and screening evidence</summary>

- **Abstract:** Selecting an appropriate population pharmacokinetic (PK) model for individual patients in model-informed precision dosing (MIPD) can be challenging, particularly in the absence of therapeutic drug monitoring (TDM) samples. We developed a machine learning (ML) model to guide individualized PK model selection for a priori MIPD of vancomycin based on routinely recorded patient characteristics. This retrospective analysis included 343,636 vancomycin TDM records, each from a distinct adult patient across 156 healthcare centers, along with a priori predictions from six PK models. A multi-label classification approach was applied, labeling PK model predictions based on whether they fell within 80%-125% of observed TDM values. Various modeling strategies were evaluated using XGBoost as the base algorithm, with binary relevance selected for the final model. At the prediction stage, PK models were ranked and averaged for each patient based on ML-predicted probabilities that predictions would fall within 80%-125% of the observed concentration. Selecting the highest ranked PK model for each patient and ML-based model averaging outperformed all single PK models, body mass index-based selection, and naive averaging. On a population level, these ML approaches resulted in more accurate predictions, a higher proportion of predictions within 80%-125% of observed vancomycin concentrations, and n…
- **PopPK/pharmacometrics terms:** population pharmacokinetic, model informed precision dosing, mipd
- **AI/ML terms:** machine learning
- **Method terms:** model selection, algorithm

</details>

---
The relevance score measures topical and methodological alignment, not scientific quality, validity, or clinical utility.
