<!-- poppk-ai-selection -->

# PopPK × AI Methodology Literature Report

Run time: 2026-10-14 09:48 JST
Source retrieval: **Complete**
New articles: **0**
Archive selections: **1** (unreported papers published since 2020)

Evidence basis: titles and abstracts are used for screening; all interpretations use the abstract only. Full text is not fetched.

Source counts and warnings describe this run. Daily selections are retained when a later retry refreshes the report status.

Recent-search records: Crossref 5316, Europe PMC 1, arXiv 0

## Selection and search coverage

Selection outcome: **selected**
Papers selected in this run: **1**
Retrieval success does not mean that a paper was selected or that all literature was searched.

- Europe PMC: 1 pages; 0 capped queries; 0 failed queries.
- Crossref: 36 pages; 17 capped queries; 0 failed queries.
- arXiv: 1 pages; 0 capped queries; 0 failed queries.

Recent screening (one exclusion reason per unique record):
- retrieved: 5317
- unique: 2878
- duplicates: 2439
- excluded publication type: 126
- missing pk evidence: 2729
- missing ai evidence: 23

Archive candidates available: 14; unvisited/unfinished windows: 322; completed windows: 1.
Unfinished date windows are resumed on the next eligible run. API cursors are not stored across days.


## 1. [Personalized prophylactic therapy optimization in hemophilia A using a hybrid PK-PD-TTE model and deep RL.](https://europepmc.org/article/MED/42243590)

- **Selection:** Archive article (2020+ fallback)
- **Authors:** Rabbani M, Razavi SE, Goharimanesh M, Razavi SE
- **Venue/source:** Journal of pharmacokinetics and pharmacodynamics
- **Publication date:** 2026-06-04
- **DOI:** 10.1007/s10928-026-10041-y

### Abstract-only interpretation

- **Prior limitation:** However, individual variations in treatment response and reliance solely on plasma Factor VIII levels provide an imprecise assessment of bleeding risk.
- **Methodological contribution:** This study presents an intelligent dose-control system utilizing Deep Reinforcement Learning (DRL) integrated with a hybrid Pharmacokinetic-Pharmacodynamic Time-to-Event (PK-PD-TTE) environment.
- **What becomes possible:** These findings suggest that incorporating reinforcement learning with mechanistic PD feedback can act as a powerful complementary layer to established clinical protocols, facilitating personalized and cost-effective hemophilia management.
- **Why it matters:** The proposed DQN agent was benchmarked against standard prophylaxis, a Fuzzy Logic controller, and a Bayesian Adaptive Model-Informed Precision Dosing (MIPD) strategy.

- **Relevance score:** 50/100 — PK 10, AI 10, method 30, title intersection 0
- **Summary method:** Abstract-only extractive summary

<details>
<summary>Abstract and screening evidence</summary>

- **Abstract:** Hemophilia A is a genetic bleeding disorder caused by a deficiency or absence of Factor VIII, leading to recurrent and spontaneous hemorrhages. Standard treatment typically involves regular prophylactic infusions of clotting factors to prevent bleeding episodes. However, individual variations in treatment response and reliance solely on plasma Factor VIII levels provide an imprecise assessment of bleeding risk. This study presents an intelligent dose-control system utilizing Deep Reinforcement Learning (DRL) integrated with a hybrid Pharmacokinetic-Pharmacodynamic Time-to-Event (PK-PD-TTE) environment. Within this framework, the control policy is learned using a Deep Q‑Network (DQN), enabling the agent to adapt treatment decisions through interaction with the simulated physiological environment. Unlike conventional methods, this framework allows the agent to observe continuous physiological states via Endogenous Thrombin Potential (ETP) and learn optimal dosing policies through trial-and-error. The proposed DQN agent was benchmarked against standard prophylaxis, a Fuzzy Logic controller, and a Bayesian Adaptive Model-Informed Precision Dosing (MIPD) strategy. Simulation results from a virtual cohort (N = 200) demonstrate that the DQN agent achieves a safety profile comparable to Bayesian MIPD while significantly improving factor utilization efficiency. Notably, in patients wit…
- **PopPK/pharmacometrics terms:** model informed precision dosing, mipd
- **AI/ML terms:** reinforcement learning
- **Method terms:** optimization, framework

</details>

---
The relevance score measures topical and methodological alignment, not scientific quality, validity, or clinical utility.
