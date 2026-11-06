<!-- poppk-ai-selection -->

# PopPK × AI Methodology Literature Report

Run time: 2026-11-06 10:57 JST
Source retrieval: **Complete**
New articles: **0**
Archive selections: **1** (unreported papers published since 2020)

Evidence basis: titles and abstracts are used for screening; all interpretations use the abstract only. Full text is not fetched.

Source counts and warnings describe this run. Daily selections are retained when a later retry refreshes the report status.

Recent-search records: Crossref 5181, Europe PMC 6, arXiv 0

## Selection and search coverage

Selection outcome: **selected**
Papers selected in this run: **1**
Retrieval success does not mean that a paper was selected or that all literature was searched.

- Europe PMC: 1 pages; 0 capped queries; 0 failed queries.
- Crossref: 36 pages; 17 capped queries; 0 failed queries.
- arXiv: 1 pages; 0 capped queries; 0 failed queries.

Recent screening (one exclusion reason per unique record):
- retrieved: 5187
- unique: 2727
- duplicates: 2460
- excluded publication type: 130
- already reported: 4
- missing method evidence: 1
- missing pk evidence: 2576
- missing ai evidence: 16

Archive candidates available: 43; unvisited/unfinished windows: 625; completed windows: 2.
Unfinished date windows are resumed on the next eligible run. API cursors are not stored across days.


## 1. [AI-NLME: A New Artificial Intelligence-Driven Nonlinear Mixed Effect Modeling Approach for Analyzing Longitudinal Data in Randomized Placebo-Controlled Clinical Trials.](https://europepmc.org/article/MED/40898887)

- **Selection:** Archive article (2020+ fallback)
- **Authors:** Gomeni R, Bressolle-Gomeni F
- **Venue/source:** Clinical and translational science
- **Publication date:** 2025-09-01
- **DOI:** 10.1111/cts.70345

### Abstract-only interpretation

- **Prior limitation:** To overcome this limitation, a new artificial intelligence driven nonlinear mixed effect modeling approach (AI-NLME) is proposed.
- **Methodological contribution:** This approach involves the development of the ANN model using a dataset that is independent from the dataset used to estimate the treatment effect.
- **What becomes possible:** Not stated in the available abstract.
- **Why it matters:** These findings provide convergent evidence on the potential role of AI-NLME to become the reference approach for analyzing placebo-controlled clinical trials.

- **Relevance score:** 80/100 — PK 30, AI 30, method 10, title intersection 10
- **Summary method:** Abstract-only extractive summary

<details>
<summary>Abstract and screening evidence</summary>

- **Abstract:** A propensity weighted (PSW) methodology was recently proposed for assessing the treatment effect conditional to the probability of non-specific response to a treatment (prob-NSRT). Prob-NSRT was estimated using an artificial neural network (ANN) model applied to pre-randomization and study endpoint observations in a placebo arm of a placebo-controlled clinical trial. Placebo data were initially used to estimate prob-NSRT, then the ANN model was applied to the data of each individual in each treatment arm (placebo + active) for estimating the individual prob-NSRT, and finally all data in the trial enriched by the prob-NSRT values were used to assess the treatment effect. One of the major limitations of this methodology was that the ANN model was developed and applied to analyze data in the same dataset. To overcome this limitation, a new artificial intelligence driven nonlinear mixed effect modeling approach (AI-NLME) is proposed. This approach involves the development of the ANN model using a dataset that is independent from the dataset used to estimate the treatment effect. A case study is presented using data from a randomized, placebo-controlled trial in major depressive disorders. The AI-NLME approach provided an effective tool for controlling the confounding effect of treatment non-specific response, for increasing signal detection, for decreasing heterogeneity in the res…
- **PopPK/pharmacometrics terms:** nlme
- **AI/ML terms:** artificial intelligence, neural network
- **Method terms:** methodology

</details>

---
The relevance score measures topical and methodological alignment, not scientific quality, validity, or clinical utility.
