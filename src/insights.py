"""Create concise interpretations from the available abstract only."""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Any, Iterable

from .core import Match, MonitorError, clean, normalize_text, request_json

_SENTENCE_BOUNDARY = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9(\[\"'])")
_SECTION_PREFIX = re.compile(
    r"^(?:abstract\s+)?(?:background|objectives?|aims?|methods?|results?|"
    r"conclusions?)\s*:\s*",
    re.I,
)
_NOT_STATED = "Not stated in the available abstract."

_LIMITATION_CUES = (
    "however",
    "although",
    "but",
    "remains",
    "remain",
    "lack",
    "limited",
    "limitation",
    "challenge",
    "difficult",
    "manual",
    "resource intensive",
    "time consuming",
    "fails",
    "failed",
    "unable",
    "not established",
    "unknown",
    "barrier",
    "bottleneck",
    "insufficient",
    "restricted",
)
_CONTRIBUTION_CUES = (
    "this study",
    "we propose",
    "we present",
    "we develop",
    "we developed",
    "we introduce",
    "we evaluate",
    "we evaluated",
    "we benchmark",
    "aimed to",
    "objective was",
    "framework",
    "algorithm",
    "method",
    "approach",
)
_CAPABILITY_CUES = (
    "enables",
    "enabled",
    "allows",
    "allowed",
    "can ",
    "could ",
    "supports",
    "supported",
    "provides",
    "improved",
    "outperformed",
    "reduced",
    "achieved",
    "demonstrated",
    "showed",
    "feasible",
    "accurately",
)
_SIGNIFICANCE_CUES = (
    "conclusion",
    "these findings",
    "this approach",
    "this method",
    "may support",
    "could support",
    "clinical",
    "dosing",
    "precision dosing",
    "model informed",
    "reproducibility",
    "interpretability",
    "privacy",
    "multicenter",
    "generaliz",
    "potential",
)


@dataclass(frozen=True)
class ResearchInsight:
    """Four questions presented for every selected paper."""

    prior_limitation: str
    contribution: str
    new_capability: str
    significance: str
    source: str


_NO_ABSTRACT = ResearchInsight(
    prior_limitation="Not stated because no abstract was available.",
    contribution="Not stated because no abstract was available.",
    new_capability="Not stated because no abstract was available.",
    significance="Manual review is required before the paper can be interpreted.",
    source="No abstract available",
)


def _sentences(abstract: str) -> list[str]:
    """Split a structured abstract into readable candidate sentences."""

    text = clean(abstract)
    if not text:
        return []

    parts = _SENTENCE_BOUNDARY.split(text)
    sentences: list[str] = []
    for part in parts:
        sentence = _SECTION_PREFIX.sub("", clean(part))
        if len(sentence) >= 20:
            sentences.append(sentence)
    return sentences


def _cue_score(sentence: str, cues: Iterable[str]) -> int:
    normalized = f" {normalize_text(sentence)} "
    return sum(
        1 + int(len(normalize_text(cue)) >= 12)
        for cue in cues
        if normalize_text(cue) in normalized
    )


def _select_sentence(
    sentences: list[str],
    cues: tuple[str, ...],
    used: set[int],
    *,
    prefer_later: bool = False,
) -> tuple[str, int | None]:
    """Select the strongest unused sentence for one interpretive field."""

    candidates: list[tuple[int, int, int, str]] = []
    for index, sentence in enumerate(sentences):
        if index in used:
            continue
        score = _cue_score(sentence, cues)
        if not score:
            continue
        position = index if prefer_later else -index
        candidates.append((score, position, -len(sentence), sentence))

    if not candidates:
        return _NOT_STATED, None

    selected = max(candidates)
    sentence = selected[3]
    index = sentences.index(sentence)
    return _clip(sentence), index


def _clip(value: str, limit: int = 320) -> str:
    """Keep extracted evidence readable in Issues and article cards."""

    value = clean(value)
    if len(value) <= limit:
        return value
    return value[: limit - 1].rstrip(" ,;:") + "…"


def rule_based_summary(match: Match) -> ResearchInsight:
    """Extract four evidence-bearing sentences without adding new claims."""

    sentences = _sentences(match.paper.abstract)
    if not sentences:
        return _NO_ABSTRACT

    used: set[int] = set()
    limitation, index = _select_sentence(sentences, _LIMITATION_CUES, used)
    if index is not None:
        used.add(index)

    contribution, index = _select_sentence(sentences, _CONTRIBUTION_CUES, used)
    if index is not None:
        used.add(index)

    capability, index = _select_sentence(
        sentences, _CAPABILITY_CUES, used, prefer_later=True
    )
    if index is not None:
        used.add(index)

    significance, _ = _select_sentence(
        sentences, _SIGNIFICANCE_CUES, used, prefer_later=True
    )

    return ResearchInsight(
        prior_limitation=limitation,
        contribution=contribution,
        new_capability=capability,
        significance=significance,
        source="Abstract-only extractive summary",
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
        prior_limitation=_clip(data["prior_limitation"]),
        contribution=_clip(data["contribution"]),
        new_capability=_clip(data["new_capability"]),
        significance=_clip(data["significance"]),
        source=f"Abstract-only AI summary ({model})",
    )


def ai_summary(
    match: Match, config: dict[str, Any], api_key: str
) -> ResearchInsight:
    """Paraphrase only the supplied abstract through the Responses API."""

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
    """Use the optional AI paraphrase, then the extractive fallback."""

    settings = config["summaries"]
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if settings.get("use_openai_when_available", True) and api_key:
        try:
            return ai_summary(match, config, api_key)
        except Exception as exc:
            print(
                f"AI summary failed for {match.paper.title}: {clean(exc)}; "
                "using the abstract-only extractive summary."
            )
    return rule_based_summary(match)
