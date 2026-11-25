<!-- poppk-ai-selection -->

# PopPK × AI Methodology Literature Report

Run time: 2026-11-25 13:44 JST
Source retrieval: **Complete**
New articles: **1**
Archive selections: **0** (unreported papers published since 2020)

Evidence basis: titles and abstracts are used for screening; all interpretations use the abstract only. Full text is not fetched.

Source counts and warnings describe this run. Daily selections are retained when a later retry refreshes the report status.

Recent-search records: Crossref 5224, Europe PMC 3, arXiv 1

## Selection and search coverage

Selection outcome: **selected**
Papers selected in this run: **1**
Retrieval success does not mean that a paper was selected or that all literature was searched.

- Europe PMC: 1 pages; 0 capped queries; 0 failed queries.
- Crossref: 36 pages; 16 capped queries; 0 failed queries.
- arXiv: 1 pages; 0 capped queries; 0 failed queries.

Recent screening (one exclusion reason per unique record):
- retrieved: 5228
- unique: 2722
- duplicates: 2506
- already reported: 2
- excluded publication type: 146
- missing pk evidence: 2560
- missing ai evidence: 13
- eligible unreported: 1


## 1. [From the ELBO to Maximum Likelihood: Convergence of Variational Autoencoders for Nonlinear Mixed-Effects Modeling](https://arxiv.org/abs/2611.32372v1)

- **Selection:** New article
- **Authors:** Jan Rohleff, Johannes Schropp
- **Venue/source:** arXiv
- **Publication date:** 2026-11-24T10:41:06Z
- **DOI:** Not available

### Abstract-only interpretation

- **Prior limitation:** Not stated in the available abstract.
- **Methodological contribution:** This paper provides the convergence analysis of the VAE-NLME algorithm.
- **What becomes possible:** Not stated in the available abstract.
- **Why it matters:** Nonlinear mixed-effects (NLME) models are the central statistical models of pharmacometrics, where they support dose selection, individualized dosing and regulatory decisions in drug development.

- **Relevance score:** 50/100 — PK 30, AI 10, method 10, title intersection 0
- **Summary method:** Abstract-only extractive summary

<details>
<summary>Abstract and screening evidence</summary>

- **Abstract:** Nonlinear mixed-effects (NLME) models are the central statistical models of pharmacometrics, where they support dose selection, individualized dosing and regulatory decisions in drug development. Statistically, NLME modeling is a marginalized likelihood problem. Variational autoencoders (VAEs) solve such problems with a neural network encoder that amortizes the approximation of the intractable posterior distribution, and allow the integration of AI components into NLME modeling. This paper provides the convergence analysis of the VAE-NLME algorithm. First, its version for the evidence lower bound (ELBO) is proven to converge almost surely to the set of stationary points of the ELBO, without assuming that the encoder is trained exactly. Second, the final VAE-NLME algorithm trains the encoder on the ELBO by gradient-based optimization and uses it as proposal for importance-weighted sufficient statistics. It converges almost surely to the set of stationary points of the marginal log-likelihood, without any assumption on the training of the encoder. Thus, it combines the fast gradient-based training of VAEs with the limit of maximum likelihood estimation.
- **PopPK/pharmacometrics terms:** nonlinear mixed effects, pharmacometrics, nlme
- **AI/ML terms:** neural network
- **Method terms:** algorithm, estimation, optimization

</details>

---
The relevance score measures topical and methodological alignment, not scientific quality, validity, or clinical utility.
