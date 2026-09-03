"""Create concise summaries using only the available abstract."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any

from .core import Match, MonitorError, clean, normalize_text, request_json


@dataclass(frozen=True)
class ResearchInsight:
    """Four questions used in every report and dashboard card."""

    prior_limitation: str
    contribution: str
    new_capability: str
    significance: str
    source: str


_NO_ABSTRACT = ResearchInsight(
    prior_limitation="Not stated because no abstract was available.",
    contribution="Not stated because no abstract was available.",
    new_capability="Not stated because no abstract was available.",
    significance="The paper requires manual review before its relevance can be interpreted.",
    source="No abstract available",
)


# Category templates are deliberately cautious. They describe what the abstract
# supports, not what the full paper may contain.
_TEMPLATES: dict[str, tuple[str, str, str, str]] = {
    "federated": (
        "The abstract addresses the inability to pool patient-level data across institutions.",
        "It describes a federated or distributed method for PopPK or pharmacometric analysis.",
        "Institutions can contribute to a joint analysis without transferring individual records.",
        "The approach may extend multicenter modeling to settings with data-sharing restrictions.",
    ),
    "synthetic_data": (
        "The abstract identifies a trade-off between protecting patient data and preserving pharmacometric structure.",
        "It evaluates synthetic-data methods against pharmacometric privacy and fidelity criteria.",
        "Synthetic datasets can be compared on both disclosure risk and preservation of PK or dosing properties.",
        "The work makes the privacy-fidelity trade-off explicit for pharmacometric data sharing.",
    ),
    "privacy": (
        "The abstract identifies privacy constraints as a barrier to combining pharmacometric data.",
        "It applies a privacy-preserving method to PopPK or pharmacometric analysis.",
        "Cross-site analysis may be performed with lower exposure of patient-level information.",
        "The method may support broader data use while retaining explicit privacy controls.",
    ),
    "llm_automation": (
        "The abstract describes model development as iterative, expertise-dependent, or difficult to automate with a single prompt.",
        "It introduces an agentic or staged LLM workflow for pharmacometric model development.",
        "Multiple modeling steps can be coordinated through structured expert prompts rather than one-pass code generation.",
        "The study tests whether LLM agents can reduce manual work while remaining auditable against expert practice.",
    ),
    "neural_ode": (
        "The abstract contrasts labor-intensive model building with the limited interpretability of black-box neural ODEs.",
        "It combines neural ODE learning with a procedure that selects or simplifies an interpretable model structure.",
        "Complex PK or PD dynamics can be learned from data and translated into a more interpretable representation.",
        "The method connects automated structure discovery with conventional pharmacometric interpretation.",
    ),
    "reinforcement_learning": (
        "The abstract addresses treatment decisions that must adapt over time rather than at a single dosing step.",
        "It applies reinforcement learning to sequential dosing or treatment decisions.",
        "Dose changes, switching, or combination choices can be evaluated as a time-dependent policy.",
        "The approach extends precision dosing from static prediction to sequential decision making.",
    ),
    "model_selection": (
        "The abstract identifies a lack of objective criteria for choosing among candidate pharmacometric models.",
        "It uses machine learning to select the model expected to perform best for a patient or dataset.",
        "Model choice can become an explicit, data-driven step before prediction or dose calculation.",
        "The method reduces reliance on a single fixed model when several plausible models are available.",
    ),
    "automated_modeling": (
        "The abstract describes manual model selection, equation rewriting, or repeated parameter adjustment as a reproducibility burden.",
        "It proposes a reusable framework that automates parts of mechanistic PK or PD model development.",
        "A common modeling structure can be adapted across scenarios with less repeated implementation work.",
        "The framework may reduce analyst-dependent steps and improve reproducibility.",
    ),
    "hybrid": (
        "The abstract identifies a gap between mechanistic coverage and data-driven flexibility.",
        "It links mechanistic QSP, PBPK, PK/PD, or related models with machine-learning components.",
        "Several biological or pharmacological scales can be analyzed within one connected computational workflow.",
        "The approach may support model-informed development while retaining mechanistic structure.",
    ),
    "generic": (
        "The abstract identifies a modeling task that remains manual, inflexible, or difficult to generalize.",
        "It introduces an AI-assisted method within PopPK or pharmacometrics.",
        "The targeted modeling task can be supported by a more automated or data-driven procedure.",
        "The work is relevant as a methodological extension, although its practical value requires review of the full study.",
    ),
}


def _category(abstract: str) -> str:
    """Assign a template from abstract text only."""

    text = normalize_text(abstract)
    rules = (
        ("synthetic_data", ("synthetic data", "generative algorithm")),
        ("federated", ("federated learning", "distributed optimization")),
        ("privacy", ("differential privacy", "privacy preserving")),
        ("llm_automation", ("large language model", "llm", "agentic")),
        (
            "neural_ode",
            (
                "neural ordinary differential equation",
                "neural ode",
                "neural differential equation",
            ),
        ),
        ("reinforcement_learning", ("reinforcement learning",)),
        (
            "automated_modeling",
            (
                "automated model development",
                "automated pharmacodynamic",
                "automated pharmacometric",
                "unified mechanistic",
            ),
        ),
        ("model_selection", ("model selection",)),
        (
            "hybrid",
            (
                "quantitative systems pharmacology",
                "mechanistic machine learning",
                "physics informed",
                "multiscale computational platform",
            ),
        ),
    )
    for category, phrases in rules:
        if any(normalize_text(phrase) in text for phrase in phrases):
            return category
    return "generic"


def rule_based_summary(match: Match) -> ResearchInsight:
    """Return a deterministic, abstract-only summary."""

    abstract = clean(match.paper.abstract)
    if not abstract:
        return _NO_ABSTRACT

    values = _TEMPLATES[_category(abstract)]
    return ResearchInsight(
        prior_limitation=values[0],
        contribution=values[1],
        new_capability=values[2],
        significance=values[3],
        source="Abstract-only rule-based summary",
    )


def _response_text(response: dict[str, Any]) -> str:
    direct = response.get("output_text")
    if isinstance(direct, str) and direct.strip():
        return direct.strip()

    parts: list[str] = []
    for item in response.get("output", []):
        for content in item.get("content", []) if isinstance(item, dict) else []:
            if content.get("type") == "output_text" and content.get("text"):
                parts.append(content["text"])
    return "\n".join(parts).strip()


def _parse_json_summary(text: str, model: str) -> ResearchInsight:
    start, end = text.find("{"), text.rfind("}")
    if start < 0 or end <= start:
        raise MonitorError("Summary response did not contain a JSON object")

    try:
        data = json.loads(text[start : end + 1])
    except json.JSONDecodeError as exc:
        raise MonitorError("Summary response was not valid JSON") from exc

    keys = (
        "prior_limitation",
        "contribution",
        "new_capability",
        "significance",
    )
    if not all(clean(data.get(key)) for key in keys):
        raise MonitorError("Summary response was missing a required field")

    return ResearchInsight(
        prior_limitation=clean(data["prior_limitation"]),
        contribution=clean(data["contribution"]),
        new_capability=clean(data["new_capability"]),
        significance=clean(data["significance"]),
        source=f"Abstract-only AI summary ({model})",
    )


def ai_summary(
    match: Match, config: dict[str, Any], api_key: str
) -> ResearchInsight:
    """Ask the Responses API to paraphrase the abstract into four short fields."""

    settings = config["summaries"]
    model = os.getenv("OPENAI_MODEL", "").strip() or settings["model"]
    abstract = clean(match.paper.abstract)
    if not abstract:
        return _NO_ABSTRACT

    instructions = (
        "Use only the supplied abstract as evidence. Do not use outside "
        "knowledge, infer content from the title, or claim a clinical benefit "
        "that the abstract does not state. Return one concise English sentence "
        "for each field: prior_limitation, contribution, new_capability, and "
        "significance. If evidence is missing, write 'Not stated in the "
        "available abstract.' Return only a JSON object."
    )
    payload = {
        "model": model,
        "instructions": instructions,
        "input": abstract[: int(settings["max_abstract_chars"])],
        "max_output_tokens": int(settings["max_output_tokens"]),
        "store": False,
    }
    response = request_json(
        "https://api.openai.com/v1/responses",
        method="POST",
        payload=payload,
        headers={"Authorization": f"Bearer {api_key}"},
        retries=2,
    )
    return _parse_json_summary(_response_text(response), model)


def summarize_research(
    match: Match, config: dict[str, Any]
) -> ResearchInsight:
    """Use the optional AI summary, then fall back to deterministic rules."""

    settings = config["summaries"]
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if settings.get("use_openai_when_available", True) and api_key:
        try:
            return ai_summary(match, config, api_key)
        except Exception as exc:
            print(
                f"AI summary failed for {match.paper.title}: {clean(exc)}; "
                "using the abstract-only rule-based summary."
            )
    return rule_based_summary(match)
