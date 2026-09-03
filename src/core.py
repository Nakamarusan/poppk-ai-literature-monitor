"""Core data models, scoring, normalization, and HTTP helpers."""

from __future__ import annotations

import datetime as dt
import hashlib
import html
import json
import re
import time
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Sequence
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

UTC = dt.timezone.utc
JST = ZoneInfo("Asia/Tokyo")

_SPACE = re.compile(r"\s+")
_HTML_TAG = re.compile(r"<[^>]+>")
_DOI_PREFIX = re.compile(r"^(?:https?://(?:dx\.)?doi\.org/|doi:\s*)", re.I)
_ARXIV_VERSION = re.compile(r"v\d+$", re.I)


class MonitorError(RuntimeError):
    """Raised when the monitor cannot complete a required operation."""


@dataclass
class Paper:
    """Normalized bibliographic metadata returned by any source."""

    sources: list[str]
    source_ids: list[str]
    title: str
    authors: list[str] = field(default_factory=list)
    venue: str = ""
    date: str = ""
    doi: str = ""
    url: str = ""
    abstract: str = ""
    publication_type: str = ""

    def title_key(self) -> str:
        digest = hashlib.sha256(normalize_text(self.title).encode()).hexdigest()[:24]
        return f"title:{digest}"

    def keys(self) -> list[str]:
        """Return stable identifiers used for de-duplication and seen-state checks."""

        keys: list[str] = []
        if doi := normalize_doi(self.doi):
            keys.append(f"doi:{doi}")

        for source, source_id in zip(self.sources, self.source_ids):
            if not source_id:
                continue
            identifier = source_id.casefold()
            if source.casefold() == "arxiv":
                identifier = _ARXIV_VERSION.sub("", identifier)
            keys.append(f"source:{source.casefold()}:{identifier}")

        keys.append(self.title_key())
        return list(dict.fromkeys(keys))


@dataclass(frozen=True)
class Score:
    """Transparent 0-100 relevance score."""

    pk: int
    ai: int
    method: int
    intersection: int

    @property
    def total(self) -> int:
        return self.pk + self.ai + self.method + self.intersection

    def as_dict(self) -> dict[str, int]:
        return {
            "pk": self.pk,
            "ai": self.ai,
            "method": self.method,
            "intersection": self.intersection,
            "total": self.total,
        }


@dataclass(frozen=True)
class Match:
    """A paper that passed screening, including evidence and score details."""

    paper: Paper
    score: Score
    priority: str
    title_hits: dict[str, list[str]]
    abstract_hits: dict[str, list[str]]

    @property
    def hits(self) -> dict[str, list[str]]:
        return {
            group: list(
                dict.fromkeys(self.title_hits[group] + self.abstract_hits[group])
            )
            for group in ("pk", "ai", "method")
        }


def clean(value: Any) -> str:
    """Remove HTML tags and collapse whitespace."""

    if value is None:
        return ""
    plain = _HTML_TAG.sub(" ", html.unescape(str(value)))
    return _SPACE.sub(" ", plain).strip()


def normalize_text(value: str) -> str:
    """Normalize text for stable matching across punctuation and Unicode variants."""

    value = unicodedata.normalize("NFKC", clean(value)).casefold()
    return _SPACE.sub(" ", re.sub(r"[^\w]+", " ", value)).strip()


def normalize_doi(value: str) -> str:
    return _DOI_PREFIX.sub("", clean(value)).casefold().rstrip(". ")


def parse_date(value: str) -> dt.date | None:
    """Parse common date formats returned by the literature APIs."""

    value = clean(value)
    if not value:
        return None

    try:
        return dt.datetime.fromisoformat(value.replace("Z", "+00:00")).date()
    except ValueError:
        pass

    for format_string in ("%Y-%m-%d", "%Y-%m", "%Y"):
        try:
            parsed = dt.datetime.strptime(value, format_string).date()
            return parsed if format_string == "%Y-%m-%d" else parsed.replace(day=1)
        except ValueError:
            continue
    return None


def phrase_hits(text: str, terms: Sequence[str]) -> list[str]:
    """Find configured phrases after punctuation-insensitive normalization."""

    haystack = f" {normalize_text(text)} "
    hits: list[str] = []
    for term in terms:
        needle = normalize_text(term)
        if needle and f" {needle} " in haystack:
            hits.append(term)
    return hits


def _method_signal(
    method_hits: Sequence[str],
    ai_hits: Sequence[str],
    methodological_ai: set[str],
) -> bool:
    return bool(method_hits) or any(normalize_text(hit) in methodological_ai for hit in ai_hits)


def screen(paper: Paper, config: dict[str, Any]) -> Match | None:
    """Screen one paper and calculate a bounded relevance score.

    Eligibility requires evidence for all three concepts:
    PopPK/pharmacometrics, AI/ML, and methodology. The score measures topical
    relevance only; it is not a quality or validity rating.
    """

    terms = config["terms"]
    excluded_text = normalize_text(f"{paper.publication_type} {paper.title}")
    if any(normalize_text(term) in excluded_text for term in terms["exclude"]):
        return None

    title_hits = {
        group: phrase_hits(paper.title, terms[group])
        for group in ("pk", "ai", "method")
    }
    abstract_hits = {
        group: phrase_hits(paper.abstract, terms[group])
        for group in ("pk", "ai", "method")
    }

    pk_present = bool(title_hits["pk"] or abstract_hits["pk"])
    ai_present = bool(title_hits["ai"] or abstract_hits["ai"])
    methodological_ai = {normalize_text(term) for term in terms["methodological_ai"]}
    method_present = _method_signal(
        title_hits["method"] + abstract_hits["method"],
        title_hits["ai"] + abstract_hits["ai"],
        methodological_ai,
    )
    if not (pk_present and ai_present and method_present):
        return None

    weights = config["scoring"]
    method_in_title = _method_signal(
        title_hits["method"], title_hits["ai"], methodological_ai
    )
    method_in_abstract = _method_signal(
        abstract_hits["method"], abstract_hits["ai"], methodological_ai
    )

    score = Score(
        pk=(weights["pk_title"] if title_hits["pk"] else 0)
        + (weights["pk_abstract"] if abstract_hits["pk"] else 0),
        ai=(weights["ai_title"] if title_hits["ai"] else 0)
        + (weights["ai_abstract"] if abstract_hits["ai"] else 0),
        method=(weights["method_title"] if method_in_title else 0)
        + (weights["method_abstract"] if method_in_abstract else 0),
        intersection=(
            weights["intersection_bonus"]
            if title_hits["pk"] and title_hits["ai"]
            else 0
        ),
    )

    if score.total >= weights["high_threshold"]:
        priority = "High"
    elif score.total >= weights["medium_threshold"]:
        priority = "Medium"
    else:
        priority = "Low"

    return Match(paper, score, priority, title_hits, abstract_hits)


def _merge(target: Paper, incoming: Paper) -> None:
    """Fill missing metadata and retain the longest available abstract."""

    existing_pairs = set(zip(target.sources, target.source_ids))
    for pair in zip(incoming.sources, incoming.source_ids):
        if pair not in existing_pairs:
            target.sources.append(pair[0])
            target.source_ids.append(pair[1])

    if len(incoming.abstract) > len(target.abstract):
        target.abstract = incoming.abstract

    for field_name in ("authors", "venue", "date", "doi", "url", "publication_type"):
        if not getattr(target, field_name) and getattr(incoming, field_name):
            setattr(target, field_name, getattr(incoming, field_name))


def deduplicate(papers: Iterable[Paper]) -> list[Paper]:
    """Merge records that share a DOI, source identifier, or normalized title."""

    records: list[Paper] = []
    key_to_record: dict[str, int] = {}

    for paper in papers:
        positions = {key_to_record[key] for key in paper.keys() if key in key_to_record}
        if positions:
            position = min(positions)
            _merge(records[position], paper)
        else:
            position = len(records)
            records.append(paper)

        for key in records[position].keys():
            key_to_record[key] = position

    return records


def article_id(paper: Paper) -> str:
    """Return the canonical article identifier used in the HTML catalog."""

    if doi := normalize_doi(paper.doi):
        return f"doi:{doi}"
    return paper.title_key()


def fingerprint(matches: Sequence[Match]) -> str:
    identifiers = sorted(article_id(match.paper) for match in matches)
    return hashlib.sha256("\n".join(identifiers).encode()).hexdigest()[:10]


def load_json(path: Path, default: Any | None = None) -> Any:
    if not path.exists() and default is not None:
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise MonitorError(f"Cannot read {path}: {exc}") from exc


def save_json(path: Path, value: Any) -> None:
    """Write JSON atomically so interrupted runs do not corrupt state."""

    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def succeeded_on_jst_date(state: dict[str, Any], date: dt.date) -> bool:
    raw = clean(state.get("last_success_utc"))
    try:
        value = dt.datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        return False
    if value.tzinfo is None:
        value = value.replace(tzinfo=UTC)
    return value.astimezone(JST).date() == date


def request(
    url: str,
    *,
    method: str = "GET",
    payload: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
    accept: str = "application/json",
    retries: int = 4,
) -> bytes:
    """Make an HTTP request with bounded retries for transient errors."""

    request_headers = {
        "Accept": accept,
        "User-Agent": (
            "poppk-ai-literature-monitor/5.0 "
            "(+https://github.com/Nakamarusan/poppk-ai-literature-monitor)"
        ),
    }
    if headers:
        request_headers.update(headers)

    body = None
    if payload is not None:
        body = json.dumps(payload, ensure_ascii=False).encode()
        request_headers["Content-Type"] = "application/json"

    last_error: Exception | None = None
    for attempt in range(max(1, retries)):
        try:
            with urlopen(
                Request(url, data=body, headers=request_headers, method=method),
                timeout=45,
            ) as response:
                return response.read()
        except HTTPError as exc:
            last_error = exc
            retryable = exc.code == 429 or 500 <= exc.code < 600
            if not retryable or attempt + 1 == retries:
                detail = clean(exc.read().decode(errors="replace"))[:500]
                raise MonitorError(f"HTTP {exc.code}: {detail or exc.reason}") from exc
            retry_after = exc.headers.get("Retry-After", "")
            delay = float(retry_after) if retry_after.isdigit() else 2**attempt
        except (URLError, TimeoutError, OSError) as exc:
            last_error = exc
            if attempt + 1 == retries:
                raise MonitorError(f"Network error: {clean(exc)}") from exc
            delay = 2**attempt
        time.sleep(min(delay, 20))

    raise MonitorError(str(last_error))


def request_json(url: str, **kwargs: Any) -> Any:
    try:
        return json.loads(request(url, **kwargs).decode())
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise MonitorError("Invalid JSON response") from exc


def crossref_date(value: Any) -> str:
    """Convert a Crossref date-parts object into ISO format."""

    try:
        parts = value["date-parts"][0]
        year = int(parts[0])
        month = int(parts[1]) if len(parts) > 1 else 1
        day = int(parts[2]) if len(parts) > 2 else 1
        return dt.date(year, month, day).isoformat()
    except (KeyError, IndexError, TypeError, ValueError):
        return ""
