<!-- poppk-ai-selection -->

# PopPK × AI Methodology Literature Report

Run time: 2026-10-21 09:20 JST
Source retrieval: **Complete**
New articles: **0**
Archive selections: **1** (unreported papers published since 2020)

Evidence basis: titles and abstracts are used for screening; all interpretations use the abstract only. Full text is not fetched.

Source counts and warnings describe this run. Daily selections are retained when a later retry refreshes the report status.

Recent-search records: Crossref 5257, Europe PMC 5, arXiv 0

## Selection and search coverage

Selection outcome: **selected**
Papers selected in this run: **1**
Retrieval success does not mean that a paper was selected or that all literature was searched.

- Europe PMC: 1 pages; 0 capped queries; 0 failed queries.
- Crossref: 36 pages; 16 capped queries; 0 failed queries.
- arXiv: 1 pages; 0 capped queries; 0 failed queries.

Recent screening (one exclusion reason per unique record):
- retrieved: 5262
- unique: 2819
- duplicates: 2443
- already reported: 2
- excluded publication type: 158
- missing ai evidence: 14
- missing pk evidence: 2645

Archive candidates available: 9; unvisited/unfinished windows: 417; completed windows: 1.
Unfinished date windows are resumed on the next eligible run. API cursors are not stored across days.


## 1. [Model-Driven Hybrid AI Framework for End-to-End Autonomous Decision-Making in Drug Development](https://europepmc.org/article/PPR/PPR1225063)

- **Selection:** Archive article (2020+ fallback)
- **Authors:** Lee H, Kang H, Jung W, Cho H, Goo S, Yun H, Kim M, Chae J, et al.
- **Venue/source:** Europe PMC
- **Publication date:** 2026-02-06
- **DOI:** 10.64898/2026.02.03.703154

### Abstract-only interpretation

- **Prior limitation:** Decision-making in drug development spans heterogeneous stages from molecular design to clinical optimization, yet computer-aided workflows across stages remain fragmented, limiting traceability from evidence-derived clinical questions to simulation scenarios and decision endpoints.
- **Methodological contribution:** We present a model-driven hybrid AI framework for end-to-end decision support that treats PICO (Participants, Intervention, Comparison, Outcome) as a machine-actionable specification to define scenarios and align endpoints across modules.
- **What becomes possible:** Overall, the framework provides a modular, traceable blueprint linking evidence-defined questions to exposure simulation and TDM decision support while preserving mechanistic interpretability.
- **Why it matters:** For clinical utility, CPCS improves TDM performance over a PKS baseline on phenobarbital and vancomycin, reducing MAPE by approximately 26–60% depending on configuration.

- **Relevance score:** 50/100 — PK 10, AI 10, method 30, title intersection 0
- **Summary method:** Abstract-only extractive summary

<details>
<summary>Abstract and screening evidence</summary>

- **Abstract:** Decision-making in drug development spans heterogeneous stages from molecular design to clinical optimization, yet computer-aided workflows across stages remain fragmented, limiting traceability from evidence-derived clinical questions to simulation scenarios and decision endpoints. We present a model-driven hybrid AI framework for end-to-end decision support that treats PICO (Participants, Intervention, Comparison, Outcome) as a machine-actionable specification to define scenarios and align endpoints across modules. Given a PICO-defined clinical question and a drug SMILES, the framework infers PBPK-ready parameters from structure, generates exposure via mechanistic PBPK simulation, and links exposure outputs to clinic-facing therapeutic drug monitoring (TDM) decision support using an open-source NLME-based Clinical Pharmacokinetic Consultant Service (CPCS). We additionally implement an LLM-based PICO extraction layer to structure clinical abstracts into P/I/C/O elements for systematic evidence ingestion. Results include backbone verification for DTI-guided intrinsic clearance prediction under fold-error bounds and PBPK trajectory plausibility, and external validation of the hybrid AI–PBPK pipeline showing substantial dispersion for several endpoints. An input-controlled comparison between PhysioSim and PK-Sim on N = 9 drugs yields similarly degraded accuracy under identical A…
- **PopPK/pharmacometrics terms:** nlme
- **AI/ML terms:** federated learning, llm
- **Method terms:** framework, inference, optimization, validation

</details>

---
The relevance score measures topical and methodological alignment, not scientific quality, validity, or clinical utility.
