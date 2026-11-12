<!-- poppk-ai-selection -->

# PopPK × AI Methodology Literature Report

Run time: 2026-11-12 11:39 JST
Source retrieval: **Complete**
New articles: **1**
Archive selections: **0** (unreported papers published since 2020)

Evidence basis: titles and abstracts are used for screening; all interpretations use the abstract only. Full text is not fetched.

Source counts and warnings describe this run. Daily selections are retained when a later retry refreshes the report status.

Recent-search records: Crossref 5165, Europe PMC 2, arXiv 0

## Selection and search coverage

Selection outcome: **selected**
Papers selected in this run: **1**
Retrieval success does not mean that a paper was selected or that all literature was searched.

- Europe PMC: 1 pages; 0 capped queries; 0 failed queries.
- Crossref: 35 pages; 16 capped queries; 0 failed queries.
- arXiv: 1 pages; 0 capped queries; 0 failed queries.

Recent screening (one exclusion reason per unique record):
- retrieved: 5167
- unique: 2635
- duplicates: 2532
- excluded publication type: 116
- missing method evidence: 1
- eligible unreported: 1
- missing pk evidence: 2501
- missing ai evidence: 16


## 1. [Comparing Machine Learning and Population Pharmacokinetic Approaches for Drug Concentration Prediction in Dense and Sparse Data Settings](https://doi.org/10.1002/cpt.70570)

- **Selection:** New article
- **Authors:** Shuqi Huang, Qihan Xu, Shengnan Zhang, Yujie Wen, Guoping Yang, Qi Pei
- **Venue/source:** Clinical Pharmacology & Therapeutics
- **Publication date:** 2026-11-10
- **DOI:** 10.1002/cpt.70570

### Abstract-only interpretation

- **Prior limitation:** Population pharmacokinetic (PopPK) models, the gold standard for drug concentration prediction, are relatively complex and time‐consuming; machine learning (ML) excels with high‐dimensional data but remains exploratory.
- **Methodological contribution:** This study systematically evaluated seven ML algorithms—Extreme Gradient Boosting (XGBoost), Long Short‐Term Memory (LSTM), Bidirectional Long Short‐Term Memory (BiLSTM), Gated Recurrent Unit with Decay (GRUD), Phased Long Short‐Term Memory (PLSTM), Neural Controlled Differential Equations (NCDE), and Neural Ordinary…
- **What becomes possible:** On multi‐point sparse prior data, XGBoost (F30 = 26.84%, MdPE = −5.88%) outperformed PopPK (F30 = 23.63%, MdPE = −13.88%).
- **Why it matters:** Not stated in the available abstract.

- **Relevance score:** 80/100 — PK 30, AI 30, method 10, title intersection 10
- **Summary method:** Abstract-only extractive summary

<details>
<summary>Abstract and screening evidence</summary>

- **Abstract:** Population pharmacokinetic (PopPK) models, the gold standard for drug concentration prediction, are relatively complex and time‐consuming; machine learning (ML) excels with high‐dimensional data but remains exploratory. This study systematically evaluated seven ML algorithms—Extreme Gradient Boosting (XGBoost), Long Short‐Term Memory (LSTM), Bidirectional Long Short‐Term Memory (BiLSTM), Gated Recurrent Unit with Decay (GRUD), Phased Long Short‐Term Memory (PLSTM), Neural Controlled Differential Equations (NCDE), and Neural Ordinary Differential Equation (NODE)—and their heterogeneous XGBoost‐based ensembles against PopPK across three data settings: dense phase I trial data; simulated dense data: linear absorption and elimination (LL), Michaelis–Menten absorption with linear elimination (MMA), linear absorption with Michaelis–Menten elimination (MME); and sparse therapeutic drug‐monitoring (TDM) data. On two dense trial data, BiLSTM showed low systematic bias (F30 = 48.44%, MdPE = −6.86%; F30 = 50.62%, MdPE = 1.08%), whereas NCDE (F30 = 50.00%, MdPE = −19.39%) and NODE (F30 = 62.96%, MdPE = 11.77%) achieved the highest F30 values, respectively, compared with PopPK (F30 = 37.50%, MdPE = 24.73%; F30 = 61.73%, MdPE = 14.88%). BiLSTM showed robust extrapolation across LL, MMA, and MME datasets (F30 ≥ 75%, |MdPE| ≤ 10%). XGBoost lacked extrapolation ability, limiting ensemble gains…
- **PopPK/pharmacometrics terms:** population pharmacokinetic, poppk
- **AI/ML terms:** machine learning, neural network, neural ordinary differential equation
- **Method terms:** None

</details>

---
The relevance score measures topical and methodological alignment, not scientific quality, validity, or clinical utility.
