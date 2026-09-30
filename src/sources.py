"""Metadata-only clients with explicit pagination and retrieval limits."""
from __future__ import annotations

import datetime as dt
import os
import random
import time
from dataclasses import dataclass
from typing import Any
from urllib.parse import quote, urlencode
from xml.etree import ElementTree as ET

from .core import (MonitorError, Paper, clean, crossref_date, normalize_doi,
                   parse_date, request, request_json)


@dataclass
class SourcePage:
    """One API page. A full page is not evidence that a search is exhausted."""
    papers: list[Paper]
    raw_count: int
    total: int
    next_cursor: str | None


class Records(list):
    """Remain compatible with list-based callers while exposing coverage."""
    def __init__(self):
        super().__init__()
        self.pages = 0
        self.raw_count = 0
        self.limited_queries = 0
        self.errors: list[str] = []


def _contact_email() -> str:
    return os.getenv("CONTACT_EMAIL", "").strip()


def _epmc_paper(item: dict[str, Any]) -> Paper | None:
    title = clean(item.get("title"))
    source_id = clean(item.get("id") or item.get("pmid"))
    if not title or not source_id:
        return None
    types = item.get("pubType") or item.get("pubTypeList", {}).get("pubType", [])
    if isinstance(types, list):
        types = ", ".join(map(clean, types))
    source = clean(item.get("source") or "MED")
    # Core responses nest the journal name; journalTitle alone often is absent.
    journal = (item.get("journalInfo", {}).get("journal", {})
               or item.get("journalIssue", {}).get("journal", {}))
    return Paper(
        sources=["Europe PMC"], source_ids=[f"{source}:{source_id}"], title=title,
        authors=[clean(a.get("fullName")) for a in item.get("authorList", {}).get("author", []) if clean(a.get("fullName"))],
        venue=clean(item.get("journalTitle") or journal.get("title")),
        date=clean(item.get("firstPublicationDate") or item.get("electronicPublicationDate") or item.get("pubYear")),
        doi=normalize_doi(item.get("doi") or ""),
        url=f"https://europepmc.org/article/{quote(source)}/{quote(source_id)}",
        abstract=clean(item.get("abstractText")), publication_type=clean(types),
    )


def _crossref_paper(item: dict[str, Any]) -> Paper | None:
    titles = item.get("title", [])
    title = clean(titles[0] if isinstance(titles, list) and titles else titles)
    doi = normalize_doi(item.get("DOI") or "")
    if not title or not doi:
        return None
    venues = item.get("container-title", [])
    published = next((crossref_date(item[key]) for key in
        ("published-online", "published", "published-print")
        if isinstance(item.get(key), dict) and crossref_date(item[key])), "")
    # Registration dates are not publication dates. Do not substitute 'created'.
    return Paper(
        sources=["Crossref"], source_ids=[doi], title=title,
        authors=[clean(" ".join(filter(None, (a.get("given"), a.get("family"))))) for a in item.get("author", [])],
        venue=clean(venues[0] if isinstance(venues, list) and venues else venues),
        date=published, doi=doi, url=f"https://doi.org/{doi}",
        abstract=clean(item.get("abstract")), publication_type=clean(item.get("type")),
    )


def europe_pmc_page(config: dict[str, Any], since: dt.date, until: dt.date,
                    *, cursor: str = "*", historical: bool = False,
                    size: int = 200) -> SourcePage:
    """Use index dates for discovery, publication dates for archive coverage."""
    clauses = [" OR ".join('TITLE_ABS:"' + term.replace('"', '') + '"'
                           for term in config["terms"][group]) for group in ("pk", "ai")]
    field = "FIRST_PDATE" if historical else "FIRST_IDATE"
    query = f"({clauses[0]}) AND ({clauses[1]}) AND {field}:[{since} TO {until}]"
    params = {"query": query, "format": "json", "resultType": "core",
              "pageSize": str(size), "cursorMark": cursor,
              "sort": f"{field}_D desc"}
    if email := _contact_email():
        params["email"] = email
    payload = request_json("https://www.ebi.ac.uk/europepmc/webservices/rest/search?" + urlencode(params), retries=2)
    raw = payload.get("resultList", {}).get("result")
    if not isinstance(raw, list) or "hitCount" not in payload:
        raise MonitorError("Europe PMC returned an invalid search response")
    total = int(payload["hitCount"])
    next_cursor = payload.get("nextCursorMark") if len(raw) >= size else None
    return SourcePage([p for item in raw if (p := _epmc_paper(item))],
                      len(raw), total, next_cursor)


def crossref_page(config: dict[str, Any], since: dt.date, until: dt.date,
                  query: str, content_type: str, *, cursor: str = "*",
                  historical: bool = False, size: int = 150) -> SourcePage:
    field = "pub" if historical else "created"
    params = {"query.bibliographic": query,
              "filter": f"from-{field}-date:{since},until-{field}-date:{until},type:{content_type}",
              "rows": str(size), "cursor": cursor, "sort": "score", "order": "desc"}
    if email := _contact_email():
        params["mailto"] = email
    message = request_json("https://api.crossref.org/works?" + urlencode(params), retries=2).get("message", {})
    raw = message.get("items")
    if not isinstance(raw, list) or "total-results" not in message:
        raise MonitorError("Crossref returned an invalid search response")
    total = int(message["total-results"])
    # Some Crossref cursors do not change between pages. Detect repeated DATA
    # in the caller, rather than incorrectly treating a repeated token as EOF.
    next_cursor = message.get("next-cursor") if len(raw) >= size else None
    time.sleep(0.2)
    return SourcePage([p for item in raw if (p := _crossref_paper(item))],
                      len(raw), total, next_cursor)


def _collect(result: Records, fetch_page, max_pages: int) -> None:
    cursor, received, signatures = "*", 0, set()
    for _ in range(max_pages):
        try:
            page = fetch_page(cursor)
        except Exception as exc:
            result.errors.append(clean(exc))
            return
        result.pages += 1
        result.raw_count += page.raw_count
        received += page.raw_count
        signature = tuple((p.doi, p.title, tuple(p.source_ids)) for p in page.papers)
        if page.raw_count and signature in signatures:
            result.limited_queries += 1
            return
        signatures.add(signature)
        result.extend(page.papers)
        if not page.raw_count or received >= page.total:
            return
        if not page.next_cursor:
            if received < page.total:
                result.limited_queries += 1
            return
        cursor = page.next_cursor
    result.limited_queries += 1


def fetch_europe_pmc(config: dict[str, Any], since: dt.date, until: dt.date) -> Records:
    result = Records()
    limit = int(config["sources"]["europe_pmc"].get("max_pages", 5))
    _collect(result, lambda cursor: europe_pmc_page(config, since, until, cursor=cursor), limit)
    if not result.pages and result.errors:
        raise MonitorError(result.errors[0])
    return result


def fetch_crossref(config: dict[str, Any], since: dt.date, until: dt.date) -> Records:
    settings = config["sources"]["crossref"]
    size = max(1, min(int(settings.get("rows_per_query", 150)), 1000))
    limit = int(settings.get("max_pages", 2))
    result = Records()
    for query in config["search"]["crossref_queries"]:
        for content_type in ("journal-article", "posted-content"):
            _collect(result, lambda cursor: crossref_page(
                config, since, until, query, content_type, cursor=cursor, size=size), limit)
    if not result.pages and result.errors:
        raise MonitorError(result.errors[0])
    return result


def build_arxiv_query(config: dict[str, Any], since: dt.date, until: dt.date) -> str:
    pk = " OR ".join(f'all:"{term}"' for term in config["search"]["database_terms"])
    ai = " OR ".join(f'all:"{term}"' for term in config["terms"]["ai"])
    return f"({pk}) AND ({ai}) AND submittedDate:[{since:%Y%m%d}0000 TO {until:%Y%m%d}2359]"


def fetch_arxiv(config: dict[str, Any], since: dt.date, until: dt.date) -> list[Paper]:
    """Optional preprints; transient failures remain internal to the monitor."""
    settings = config["sources"]["arxiv"]
    params = {"search_query": build_arxiv_query(config, since, until), "start": "0",
              "max_results": str(max(1, min(int(settings.get("max_results", 50)), 200))),
              "sortBy": "submittedDate", "sortOrder": "descending"}
    if jitter := max(0, int(settings.get("jitter_seconds", 60))):
        time.sleep(random.uniform(0, jitter))
    agent = "poppk-ai-literature-monitor/7.0"
    if email := _contact_email():
        agent += f" (mailto:{email})"
    root = ET.fromstring(request("https://export.arxiv.org/api/query?" + urlencode(params),
        accept="application/atom+xml", headers={"User-Agent": agent}, retries=1))
    ns = {"atom": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}
    papers = []
    for entry in root.findall("atom:entry", ns):
        title = clean(entry.findtext("atom:title", "", ns))
        url = clean(entry.findtext("atom:id", "", ns))
        published = clean(entry.findtext("atom:published", "", ns))
        date = parse_date(published)
        if not title or not url or (date and not since <= date <= until):
            continue
        papers.append(Paper(
            sources=["arXiv"], source_ids=[url.rstrip("/").split("/")[-1]], title=title,
            authors=[clean(a.findtext("atom:name", "", ns)) for a in entry.findall("atom:author", ns)],
            venue="arXiv", date=published, doi=normalize_doi(entry.findtext("arxiv:doi", "", ns)),
            url=url.replace("http://", "https://"), abstract=clean(entry.findtext("atom:summary", "", ns)),
            publication_type="preprint"))
    return papers
