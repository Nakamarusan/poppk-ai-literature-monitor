<!-- poppk-ai-selection -->

# PopPK × AI Methodology Literature Report

Run time: 2026-10-18 08:42 JST
Source retrieval: **Complete**
New articles: **0**
Archive selections: **1** (unreported papers published since 2020)

Evidence basis: titles and abstracts are used for screening; all interpretations use the abstract only. Full text is not fetched.

Source counts and warnings describe this run. Daily selections are retained when a later retry refreshes the report status.

Recent-search records: Crossref 5306, Europe PMC 3, arXiv 0

## Selection and search coverage

Selection outcome: **selected**
Papers selected in this run: **1**
Retrieval success does not mean that a paper was selected or that all literature was searched.

- Europe PMC: 1 pages; 0 capped queries; 0 failed queries.
- Crossref: 36 pages; 17 capped queries; 0 failed queries.
- arXiv: 1 pages; 0 capped queries; 0 failed queries.

Recent screening (one exclusion reason per unique record):
- retrieved: 5309
- unique: 2875
- duplicates: 2434
- excluded publication type: 145
- already reported: 2
- missing pk evidence: 2708
- missing ai evidence: 20

Archive candidates available: 12; unvisited/unfinished windows: 360; completed windows: 1.
Unfinished date windows are resumed on the next eligible run. API cursors are not stored across days.


## 1. [Artificial Intelligence, LLM-based generation of synthetic patients with Parkinson’s Disease: towards a digital twin paradigm for in silico studies](https://europepmc.org/article/PPR/PPR1265459)

- **Selection:** Archive article (2020+ fallback)
- **Authors:** Merlo Pich E, Pomponio O, Magno MA, Berti M, Li Lu L, Coser A, Cani I, Calandra Buonaura G, et al.
- **Venue/source:** Europe PMC
- **Publication date:** 2026-04-29
- **DOI:** 10.64898/2026.04.28.26351471

### Abstract-only interpretation

- **Prior limitation:** Access to large PD datasets that may help in clustering this heterogeneity is restricted by privacy and regulatory constraints.
- **Methodological contribution:** We developed a large language model (LLM)-framework to generate high-fidelity synthetic PD patients from the Parkinson’s Progression Markers Initiative (PPMI) dataset based on the open-source Qwen3-8B-Base model.
- **What becomes possible:** Not stated in the available abstract.
- **Why it matters:** These findings support the use of a dedicated LLM framework for patient simulation, contributing to the foundations of digital twins for PD in silico trials.

- **Relevance score:** 50/100 — PK 10, AI 30, method 10, title intersection 0
- **Summary method:** Abstract-only extractive summary

<details>
<summary>Abstract and screening evidence</summary>

- **Abstract:** Heterogeneity in sporadic Parkinson’s Disease (PD) is a critical problem that drives variable rates of progression and treatment response and complicates clinical trials. Access to large PD datasets that may help in clustering this heterogeneity is restricted by privacy and regulatory constraints. Simulated patients or digital twins may offer a solution. We developed a large language model (LLM)-framework to generate high-fidelity synthetic PD patients from the Parkinson’s Progression Markers Initiative (PPMI) dataset based on the open-source Qwen3-8B-Base model. Using a relational, tree-structured representation and domain-specific fine-tuning, the model produces patient-level records with longitudinal clinical, imaging, and biomarker data. Fidelity was assessed through distributional similarity, correlation structure, and neurologist review. Utility was tested by training diagnostic classifiers, reproducing a published pharmacometric disease progression model applied to in silico trials, and by extracting a stringent dopamine–motor impairment relationship at early PD stages. Privacy was evaluated via identical match share, distance-to-closest-record, and membership inference attacks. These findings support the use of a dedicated LLM framework for patient simulation, contributing to the foundations of digital twins for PD in silico trials.
- **PopPK/pharmacometrics terms:** pharmacometric
- **AI/ML terms:** artificial intelligence, llm, large language model
- **Method terms:** framework, inference

</details>

---
The relevance score measures topical and methodological alignment, not scientific quality, validity, or clinical utility.
