<!-- poppk-ai-selection -->

# PopPK × AI Methodology Literature Report

Run time: 2026-10-22 09:21 JST
Source retrieval: **Complete**
New articles: **4**
Archive selections: **0** (unreported papers published since 2020)

Evidence basis: titles and abstracts are used for screening; all interpretations use the abstract only. Full text is not fetched.

Source counts and warnings describe this run. Daily selections are retained when a later retry refreshes the report status.

Recent-search records: Crossref 5246, Europe PMC 7

## Selection and search coverage

Selection outcome: **selected**
Papers selected in this run: **4**
Retrieval success does not mean that a paper was selected or that all literature was searched.

- Europe PMC: 1 pages; 0 capped queries; 0 failed queries.
- Crossref: 36 pages; 16 capped queries; 0 failed queries.

Recent screening (one exclusion reason per unique record):
- retrieved: 5253
- unique: 2817
- duplicates: 2436
- eligible unreported: 4
- already reported: 2
- excluded publication type: 157
- missing ai evidence: 11
- missing pk evidence: 2643


## 1. [Toward Reinforcement Learning–Enabled Model-Informed Precision Dosing: Concepts, Applications, and Implementation](https://doi.org/10.1097/ftd.0000000000001540)

- **Selection:** New article
- **Authors:** Kei Irie, Wen Rui Tan, Tomoyuki Mizuno
- **Venue/source:** Therapeutic Drug Monitoring
- **Publication date:** 2026-10-21
- **DOI:** 10.1097/ftd.0000000000001540

### Abstract-only interpretation

- **Prior limitation:** A narrative literature review of studies that applied reinforcement learning to dosing optimization was conducted, using database searches and manual screening.
- **Methodological contribution:** Thus, reinforcement learning is a potential dosing optimization framework.
- **What becomes possible:** Reinforcement learning provides a flexible framework that complements pharmacometric models to support dosing optimization.
- **Why it matters:** This aligns with therapeutic drug monitoring and model-informed precision dosing, in which dosage is iteratively refined as conditions evolve.

- **Relevance score:** 100/100 — PK 30, AI 30, method 30, title intersection 10
- **Summary method:** Abstract-only extractive summary

<details>
<summary>Abstract and screening evidence</summary>

- **Abstract:** Purpose: Reinforcement learning is suited to sequential decision making in clinical settings, where treatment strategies are adjusted based on patient response. This aligns with therapeutic drug monitoring and model-informed precision dosing, in which dosage is iteratively refined as conditions evolve. Thus, reinforcement learning is a potential dosing optimization framework. This review provides a structured and clinically interpretable overview of these applications and their implementation. Methods: A narrative literature review of studies that applied reinforcement learning to dosing optimization was conducted, using database searches and manual screening. Studies were qualitatively analyzed for drug type, algorithm, training environment, and their state, action, and reward definitions. A simplified implementation example using a deep Q-network illustrates the core workflow. Results: Reinforcement learning has been applied across diverse clinical settings, including anesthesia, oncology, and critical care. Most studies used simulation-based environments (pharmacokinetic, pharmacodynamic, or mathematical models) to enable safe, scalable training. Off-policy methods (eg, Q-learning and deep Q-networks) were commonly used for discrete dosing decisions and retrospective data; on-policy methods (eg, actor–critic approaches) were applied when adaptive dose adjustment was require…
- **PopPK/pharmacometrics terms:** model informed precision dosing, pharmacometric
- **AI/ML terms:** reinforcement learning
- **Method terms:** framework, algorithm, optimization, model evaluation, workflow

</details>

## 2. [Machine Learning–Augmented Precision Dosing: Integrating Pharmacokinetic Modeling With Clinical Decision Support](https://doi.org/10.1002/psp4.70354)

- **Selection:** New article
- **Authors:** Yunmeng Pang, Bingqi Zhang, Zhiqiu He, Yuliu Li, Jiaxin Yu, Wei Zuo
- **Venue/source:** CPT: Pharmacometrics & Systems Pharmacology
- **Publication date:** 2026-10-20
- **DOI:** 10.1002/psp4.70354

### Abstract-only interpretation

- **Prior limitation:** Physiologically based pharmacokinetic (PBPK) modeling has a complementary role in extrapolation to special populations, evaluation of drug–drug interactions, and simulation of unobserved scenarios, but it remains uncommon for bedside dose adjustment.
- **Methodological contribution:** Not stated in the available abstract.
- **What becomes possible:** ML can support exposure prediction, limited‐sampling AUC estimation, outcome‐risk stratification, and monitoring prioritization.
- **Why it matters:** Routine model‐informed precision dosing (MIPD) relies mainly on population pharmacokinetic (PopPK) models, Bayesian forecasting, and therapeutic drug monitoring (TDM).

- **Relevance score:** 50/100 — PK 10, AI 30, method 10, title intersection 0
- **Summary method:** Abstract-only extractive summary

<details>
<summary>Abstract and screening evidence</summary>

- **Abstract:** ABSTRACT Inter‐individual variability in drug exposure can lead to ineffective therapy or toxicity, particularly in vulnerable patients. Routine model‐informed precision dosing (MIPD) relies mainly on population pharmacokinetic (PopPK) models, Bayesian forecasting, and therapeutic drug monitoring (TDM). Physiologically based pharmacokinetic (PBPK) modeling has a complementary role in extrapolation to special populations, evaluation of drug–drug interactions, and simulation of unobserved scenarios, but it remains uncommon for bedside dose adjustment. Machine learning (ML) may provide additional support when critical illness, organ dysfunction, or polypharmacy creates complex nonlinear relationships. The increasing availability of electronic health records, real‐world data, and high‐dimensional biomedical datasets has accelerated interest in ML for precision dosing. ML can support exposure prediction, limited‐sampling AUC estimation, outcome‐risk stratification, and monitoring prioritization. Its clinical role depends on the decision target, the availability of concentration data, and whether pharmacological constraints are retained within the modeling architecture. This review covers direct prediction models, limited‐sampling AUC estimators, hybrid pharmacometric‐ML models, neural ordinary differential equation approaches, and reinforcement learning for sequential dose decision…
- **PopPK/pharmacometrics terms:** population pharmacokinetic, poppk, pharmacometric, model informed precision dosing, mipd
- **AI/ML terms:** machine learning, reinforcement learning, neural ordinary differential equation
- **Method terms:** estimation, workflow, architecture, validation

</details>

## 3. [Predictive Performance of pyDarwin-Selected Versus Expert-Developed Paediatric Tobramycin Population Pharmacokinetic Models for Model-Informed Precision Dosing.](https://europepmc.org/article/MED/42897405)

- **Selection:** New article
- **Authors:** Wang J, Harwood K, Yang W, Lei A, Lai T, Nieforth K, Duffull S, Sale M, et al.
- **Venue/source:** The AAPS journal
- **Publication date:** 2026-10-19
- **DOI:** 10.1208/s12248-026-01321-z

### Abstract-only interpretation

- **Prior limitation:** PyDarwin is an open-source Python package integrating machine learning with NONMEM for automated model selection; however, its utility in model-informed precision dosing (MIPD) remains unvalidated.
- **Methodological contribution:** This study aims to evaluate pyDarwin for population pharmacokinetics (PopPK) model development in MIPD compared with expert-developed models, using paediatric tobramycin as a representative case.
- **What becomes possible:** In external validation using all TDM data, the pyDarwin-selected model demonstrated better predictive performance for CF patients than manual model (prediction-based MPE -14.6% vs -41.6%; MAPE 34.0% vs 54.4%).
- **Why it matters:** These findings support pyDarwin-based automated PopPK model selection as a reliable and efficient framework for MIPD.

- **Relevance score:** 50/100 — PK 30, AI 10, method 10, title intersection 0
- **Summary method:** Abstract-only extractive summary

<details>
<summary>Abstract and screening evidence</summary>

- **Abstract:** PyDarwin is an open-source Python package integrating machine learning with NONMEM for automated model selection; however, its utility in model-informed precision dosing (MIPD) remains unvalidated. This study aims to evaluate pyDarwin for population pharmacokinetics (PopPK) model development in MIPD compared with expert-developed models, using paediatric tobramycin as a representative case. The model-building dataset included 450 plasma concentrations from 63 children with cystic fibrosis (CF). One group manually developed a model using stepwise covariate selection, while another applied pyDarwin within a predefined 27-dimensional model space, using a fitness function that incorporated a penalty based on 24-h area under the curve (AUC 24h ). External validation was performed using 1011 concentrations from 144 children, including evaluation using all therapeutic drug monitoring (TDM) data and clinically relevant MIPD scenarios (a priori [AP], Bayesian 1, Bayesian 2). Both models included weight-based scaling, a maturation function, and estimated glomerular filtration rate as covariates on clearance, yielding comparable clearance estimates. The pyDarwin-selected model was a two-compartment model with fixed allometric scaling exponents, whereas the manual model was a one-compartment model with estimated exponents. Both models showed comparable probability of target attainment for…
- **PopPK/pharmacometrics terms:** population pharmacokinetic, model informed precision dosing, population pharmacokinetics, poppk, mipd
- **AI/ML terms:** machine learning
- **Method terms:** framework, model selection, covariate selection, model development, automated, validation

</details>

## 4. [Application of Machine Learning Models to Predict Tigecycline Exposure in Critically Ill Patients Using Different Limited Sampling Strategies.](https://europepmc.org/article/MED/42894723)

- **Selection:** New article
- **Authors:** Dai A, Liu H, Yang B, Zheng F, Guan Y, Liu J, Zhu J, Liang G, et al.
- **Venue/source:** Drug design, development and therapy
- **Publication date:** 2026-10-14
- **DOI:** 10.2147/dddt.s630414

### Abstract-only interpretation

- **Prior limitation:** Not stated in the available abstract.
- **Methodological contribution:** Furthermore, on the internal test set, we evaluated the accuracy of the published tigecycline Population Pharmacokinetics (PopPK) models.
- **What becomes possible:** Three-point sampling provided the lowest prediction error, whereas C 0 alone reduced the sampling burden.
- **Why it matters:** These findings provide an effective modeling reference for tigecycline therapeutic drug monitoring.

- **Relevance score:** 50/100 — PK 10, AI 30, method 10, title intersection 0
- **Summary method:** Abstract-only extractive summary

<details>
<summary>Abstract and screening evidence</summary>

- **Abstract:** Background The high variability in the pharmacokinetics of tigecycline may impact therapeutic efficacy, particularly in critically ill patients. This study introduces machine learning (ML) methods, aiming to clarify their effectiveness in individualized drug exposure prediction and determine the optimal modeling strategy. Methods The least absolute shrinkage and selection operator (LASSO) method was used to screen the covariates. Four ML models, random forest, extreme gradient boosting, multilayer perceptron, and long short-term memory network (LSTM), were trained and tested using 751 concentrations from 98 patients in the pharmacokinetic dataset to predict the area under the steady-state plasma concentration-time curve within 24 hours (AUC 0-24h ) of tigecycline. Furthermore, on the internal test set, we evaluated the accuracy of the published tigecycline Population Pharmacokinetics (PopPK) models. Results Seven covariates were screened out by LASSO method, including total bilirubin, creatinine clearance, Sequential Organ Failure Assessment (SOFA) score, body mass index, serum creatinine, age, and prothrombin time. Internal validation showed that, among the four ML models, the LSTM model performed the best, with the combination of covariates and the plasma concentration feature "C 0 + C 0.5 + C 6 " exhibited the optimal predictive performance (R 2 : 0.887, RMSE: 2.496 mg·h/L,…
- **PopPK/pharmacometrics terms:** population pharmacokinetics, poppk
- **AI/ML terms:** machine learning
- **Method terms:** validation

</details>

---
The relevance score measures topical and methodological alignment, not scientific quality, validity, or clinical utility.
