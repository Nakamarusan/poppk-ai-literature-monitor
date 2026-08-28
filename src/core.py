"""Shared models, matching rules, persistence, and HTTP helpers."""
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
SPACE = re.compile(r"\s+")
TAG = re.compile(r"<[^>]+>")
DOI_PREFIX = re.compile(r"^(?:https?://(?:dx\.)?doi\.org/|doi:\s*)", re.I)
ARXIV_VERSION = re.compile(r"v\d+$", re.I)


class MonitorError(RuntimeError):
    pass


@dataclass
class Paper:
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
        digest = hashlib.sha256(normalize_title(self.title).encode()).hexdigest()[:24]
        return "title:" + digest

    def keys(self) -> list[str]:
        keys = [self.title_key()]
        doi = normalize_doi(self.doi)
        if doi:
            keys.insert(0, "doi:" + doi)
        for source, source_id in zip(self.sources, self.source_ids):
            if not source_id:
                continue
            sid = source_id.lower()
            if source.lower() == "arxiv":
                sid = ARXIV_VERSION.sub("", sid)
            keys.append(f"source:{source.lower()}:{sid}")
        return list(dict.fromkeys(keys))


@dataclass
class Match:
    paper: Paper
    score: int
    priority: str
    pk_hits: list[str]
    ai_hits: list[str]
    method_hits: list[str]


def clean(value: Any) -> str:
    if value is None:
        return ""
    return SPACE.sub(" ", TAG.sub(" ", html.unescape(str(value)))).strip()


def normalize_title(value: str) -> str:
    value = unicodedata.normalize("NFKC", clean(value)).casefold()
    return SPACE.sub(" ", re.sub(r"[^\w]+", " ", value, flags=re.UNICODE)).strip()


def normalize_doi(value: str) -> str:
    return DOI_PREFIX.sub("", clean(value)).lower().rstrip(". ")


def parse_date(value: str) -> dt.date | None:
    value = clean(value)
    if not value:
        return None
    try:
        return dt.datetime.fromisoformat(value.replace("Z", "+00:00")).date()
    except ValueError:
        pass
    for fmt in ("%Y-%m-%d", "%Y-%m", "%Y"):
        try:
            parsed = dt.datetime.strptime(value, fmt).date()
            return parsed.replace(day=1) if fmt != "%Y-%m-%d" else parsed
        except ValueError:
            continue
    return None


def request(url: str, *, method: str = "GET", payload: dict[str, Any] | None = None,
            headers: dict[str, str] | None = None, accept: str = "application/json",
            retries: int = 4) -> bytes:
    request_headers = {
        "Accept": accept,
        "User-Agent": "poppk-ai-literature-monitor/1.0 (+https://github.com/Nakamarusan/poppk-ai-literature-monitor)",
    }
    if headers:
        request_headers.update(headers)
    body = None
    if payload is not None:
        body = json.dumps(payload, ensure_ascii=False).encode()
        request_headers["Content-Type"] = "application/json"
    last: Exception | None = None
    for attempt in range(max(1, retries)):
        try:
            req = Request(url, data=body, headers=request_headers, method=method)
            with urlopen(req, timeout=45) as response:
                return response.read()
        except HTTPError as exc:
            last = exc
            retryable = exc.code == 429 or 500 <= exc.code < 600
            if not retryable or attempt + 1 == retries:
                detail = clean(exc.read().decode(errors="replace"))[:500]
                raise MonitorError(f"HTTP {exc.code}: {detail or exc.reason}") from exc
        except (URLError, TimeoutError, OSError) as exc:
            last = exc
            if attempt + 1 == retries:
                raise MonitorError(f"Network error: {clean(exc)}") from exc
        time.sleep(min(2 ** attempt, 20))
    raise MonitorError(str(last))


def request_json(url: str, **kwargs: Any) -> Any:
    try:
        return json.loads(request(url, **kwargs).decode())
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise MonitorError("Invalid JSON response") from exc


def date_parts(value: Any) -> str:
    try:
        parts = value["date-parts"][0]
        year = int(parts[0])
        month = int(parts[1]) if len(parts) > 1 else 1
        day = int(parts[2]) if len(parts) > 2 else 1
        return dt.date(year, month, day).isoformat()
    except (KeyError, IndexError, TypeError, ValueError):
        return ""


def merge(target: Paper, incoming: Paper) -> None:
    existing = list(zip(target.sources, target.source_ids))
    for pair in zip(incoming.sources, incoming.source_ids):
        if pair not in existing:
            target.sources.append(pair[0])
            target.source_ids.append(pair[1])
    if len(incoming.abstract) > len(target.abstract):
        target.abstract = incoming.abstract
    for name in ("authors", "venue", "date", "doi", "url", "publication_type"):
        if not getattr(target, name) and getattr(incoming, name):
            setattr(target, name, getattr(incoming, name))


def deduplicate(papers: Iterable[Paper]) -> list[Paper]:
    records: list[Paper] = []
    index: dict[str, int] = {}
    for paper in papers:
        matches = {index[key] for key in paper.keys() if key in index}
        if matches:
            position = min(matches)
            merge(records[position], paper)
        else:
            position = len(records)
            records.append(paper)
        for key in records[position].keys():
            index[key] = position
    return records


def term_hits(text: str, terms: Sequence[str]) -> list[str]:
    hits: list[str] = []
    for term in terms:
        pattern = re.compile(term[3:], re.I) if term.startswith("re:") else re.compile(re.escape(term), re.I)
        if pattern.search(text):
            hits.append(term.removeprefix("re:"))
    return hits


def screen(paper: Paper, config: dict[str, Any]) -> Match | None:
    title, abstract = clean(paper.title), clean(paper.abstract)
    combined = f"{title} {abstract}"
    excluded_text = f"{paper.publication_type} {title}".lower()
    if any(term.lower() in excluded_text for term in config["exclude_terms"]):
        return None
    pk, ai, method = (term_hits(combined, config[name])
                      for name in ("pk_terms", "ai_terms", "method_terms"))
    if not pk or not ai:
        return None
    methodological_ai = {term.lower() for term in config["methodological_ai_terms"]}
    if not method and not any(hit.lower() in methodological_ai for hit in ai):
        return None
    title_hits = sum(len(term_hits(title, config[name]))
                     for name in ("pk_terms", "ai_terms", "method_terms"))
    score = 2 * title_hits + len(pk) + len(ai) + len(method)
    both_in_title = term_hits(title, config["pk_terms"]) and term_hits(title, config["ai_terms"])
    priority = "High" if score >= 14 or both_in_title else "Medium"
    return Match(paper, score, priority, pk, ai, method)


def load_json(path: Path, default: dict[str, Any] | None = None) -> dict[str, Any]:
    if not path.exists() and default is not None:
        return default
    try:
        value = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise MonitorError(f"Cannot read {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise MonitorError(f"Expected an object in {path}")
    return value


def save_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    temp.replace(path)


def already_succeeded_today(state: dict[str, Any], today: dt.date) -> bool:
    raw = clean(state.get("last_success_utc"))
    try:
        value = dt.datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        return False
    if value.tzinfo is None:
        value = value.replace(tzinfo=UTC)
    return value.astimezone(JST).date() == today


def fingerprint(matches: Sequence[Match]) -> str:
    identifiers = sorted(match.paper.keys()[0] for match in matches)
    return hashlib.sha256("\n".join(identifiers).encode()).hexdigest()[:10]
