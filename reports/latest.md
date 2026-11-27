<!-- poppk-ai-selection -->

# PopPK × AI Methodology Literature Report

Run time: 2026-11-27 12:54 JST
Source retrieval: **Complete**
New articles: **0**
Archive selections: **1** (unreported papers published since 2020)

Evidence basis: titles and abstracts are used for screening; all interpretations use the abstract only. Full text is not fetched.

Source counts and warnings describe this run. Daily selections are retained when a later retry refreshes the report status.

Recent-search records: Crossref 5169, Europe PMC 4, arXiv 1

## Selection and search coverage

Selection outcome: **selected**
Papers selected in this run: **1**
Retrieval success does not mean that a paper was selected or that all literature was searched.

- Europe PMC: 1 pages; 0 capped queries; 0 failed queries.
- Crossref: 35 pages; 16 capped queries; 0 failed queries.
- arXiv: 1 pages; 0 capped queries; 0 failed queries.

Recent screening (one exclusion reason per unique record):
- retrieved: 5174
- unique: 2725
- duplicates: 2449
- already reported: 4
- excluded publication type: 154
- missing pk evidence: 2556
- missing ai evidence: 11

Archive candidates available: 28; unvisited/unfinished windows: 910; completed windows: 2.
Unfinished date windows are resumed on the next eligible run. API cursors are not stored across days.


## 1. [Learning Chemotherapy Drug Action via Universal Physics-Informed Neural Networks.](https://europepmc.org/article/MED/40244511)

- **Selection:** Archive article (2020+ fallback)
- **Authors:** Podina L, Ghodsi A, Kohandel M
- **Venue/source:** Pharmaceutical research
- **Publication date:** 2025-04-17
- **DOI:** 10.1007/s11095-025-03858-8

### Abstract-only interpretation

- **Prior limitation:** However, significant manual distillation of the literature is needed in order to construct a QSP model.
- **Methodological contribution:** Then, we use the UPINN method to fit the parameters for several synthetic datasets simultaneously.
- **What becomes possible:** UPINNs can be used to find these terms and analyze them further to understand new chemotherapeutics and biological mechanisms that interact with them.
- **Why it matters:** Objective Quantitative systems pharmacology (QSP) is widely used to assess drug effects and toxicity before the drug goes to clinical trial.

- **Relevance score:** 70/100 — PK 10, AI 30, method 30, title intersection 0
- **Summary method:** Abstract-only extractive summary

<details>
<summary>Abstract and screening evidence</summary>

- **Abstract:** Objective Quantitative systems pharmacology (QSP) is widely used to assess drug effects and toxicity before the drug goes to clinical trial. However, significant manual distillation of the literature is needed in order to construct a QSP model. Parameters may need to be fit, and simplifying assumptions of the model need to be made. In this work, we apply Universal Physics-Informed Neural Networks (UPINNs) to learn unknown components of various differential equations that model chemotherapy pharmacodynamics. Methods Using UPINNs, we learn three commonly employed chemotherapeutic drug actions (log-kill, Norton-Simon, and Emax ) from synthetic data. Then, we use the UPINN method to fit the parameters for several synthetic datasets simultaneously. Finally, we learn the net proliferation rate in a model of doxorubicin (a chemotherapeutic) pharmacodynamics. Results We show that the UPINN can successfully learn the hidden terms and unknown parameters in a variety of differential equations (with differing time and variable scales) that model the effect of chemotherapeutics on cancer cells. Conclusions As the examples we study are only toy examples, we highlight the usefulness of UPINNs in learning unknown terms in pharmacodynamic and pharmacokinetic models. UPINNs can be used to find these terms and analyze them further to understand new chemotherapeutics and biological mechanisms tha…
- **PopPK/pharmacometrics terms:** quantitative systems pharmacology, qsp
- **AI/ML terms:** physics informed
- **Method terms:** None

</details>

---
The relevance score measures topical and methodological alignment, not scientific quality, validity, or clinical utility.
