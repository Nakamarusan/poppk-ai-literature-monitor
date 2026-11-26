<!-- poppk-ai-selection -->

# PopPK × AI Methodology Literature Report

Run time: 2026-11-26 12:53 JST
Source retrieval: **Complete**
New articles: **0**
Archive selections: **1** (unreported papers published since 2020)

Evidence basis: titles and abstracts are used for screening; all interpretations use the abstract only. Full text is not fetched.

Source counts and warnings describe this run. Daily selections are retained when a later retry refreshes the report status.

Recent-search records: Crossref 5200, Europe PMC 3, arXiv 1

## Selection and search coverage

Selection outcome: **selected**
Papers selected in this run: **1**
Retrieval success does not mean that a paper was selected or that all literature was searched.

- Europe PMC: 1 pages; 0 capped queries; 0 failed queries.
- Crossref: 35 pages; 16 capped queries; 0 failed queries.
- arXiv: 1 pages; 0 capped queries; 0 failed queries.

Recent screening (one exclusion reason per unique record):
- retrieved: 5204
- unique: 2721
- duplicates: 2483
- already reported: 3
- excluded publication type: 157
- missing pk evidence: 2548
- missing ai evidence: 13

Archive candidates available: 29; unvisited/unfinished windows: 891; completed windows: 2.
Unfinished date windows are resumed on the next eligible run. API cursors are not stored across days.


## 1. [Precision Dosing in Presence of Multiobjective Therapies by Integrating Reinforcement Learning and PK-PD Models: Application to Givinostat Treatment of Polycythemia Vera.](https://europepmc.org/article/MED/40325832)

- **Selection:** Archive article (2020+ fallback)
- **Authors:** De Carlo A, Tosca EM, Magni P
- **Venue/source:** CPT: pharmacometrics & systems pharmacology
- **Publication date:** 2025-05-05
- **DOI:** 10.1002/psp4.70012

### Abstract-only interpretation

- **Prior limitation:** Not stated in the available abstract.
- **Methodological contribution:** In this study, this hybrid technique is applied to the real multiobjective precision dosing problem of givinostat treatment in polycythemia vera (PV) patients.
- **What becomes possible:** These results confirm that RL and PK-PD models can be valid tools for supporting adaptive dosing strategies as interesting performances were achieved in both learning a general set of rules and in customizing treatment for each patient.
- **Why it matters:** Precision dosing aims to optimize and customize pharmacological treatment at the individual level.

- **Relevance score:** 70/100 — PK 10, AI 30, method 30, title intersection 0
- **Summary method:** Abstract-only extractive summary

<details>
<summary>Abstract and screening evidence</summary>

- **Abstract:** Precision dosing aims to optimize and customize pharmacological treatment at the individual level. The integration of pharmacometric models with Reinforcement Learning (RL) algorithms is currently under investigation to support the personalization of adaptive dosing therapies. In this study, this hybrid technique is applied to the real multiobjective precision dosing problem of givinostat treatment in polycythemia vera (PV) patients. PV is a chronic myeloproliferative disease with an overproduction of platelets (PLT), white blood cells (WBC), and hematocrit (HCT). The therapeutic goal is to simultaneously normalize the levels of these efficacy/safety biomarkers, thus inducing a complete hematological response (CHR). An RL algorithm, Q-Learning (QL), was integrated with a PK-PD model describing the givinostat effect on PLT, WBC, and HCT to derive both an adaptive dosing protocol (QL pop -agent) for the whole population and personalized dosing strategies by coupling a specific QL-agent to each patient (QL ind -agents). QL pop -agent learned a general adaptive dosing protocol that achieved a similar CHR rate (77% vs. 83%) when compared to the actual givinostat clinical protocol on 10 simulated populations. Treatment efficacy and safety increased with a deeper dosing personalization by QL ind -agents. These QL-based patient-specific adaptive dosing rules outperformed both the clin…
- **PopPK/pharmacometrics terms:** pharmacometric
- **AI/ML terms:** reinforcement learning
- **Method terms:** algorithm

</details>

---
The relevance score measures topical and methodological alignment, not scientific quality, validity, or clinical utility.
