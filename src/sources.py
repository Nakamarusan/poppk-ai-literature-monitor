"""Clients for Europe PMC, Crossref, and arXiv."""

from __future__ import annotations

import datetime as dt
import os
import random
import time
from typing import Any
from urllib.parse import quote, urlencode
from xml.etree import ElementTree as ET

from .core import (
    Paper,
    clean,
    crossref_date,
    normalize_doi,
    parse_date,
    request,
    request_json,
)


def _contact_email() -> str:
    return os.getenv("CONTACT_EMAIL", "").strip()


def fetch_europe_pmc(
    config: dict[str, Any], since: dt.date, until: dt.date
) -> list[Paper]:
    """Fetch bibliographic metadata and abstracts from Europe PMC."""

    terms = " OR ".join(
        f'"{term}"' for term in config["search"]["database_terms"]
    )
    query = f"({terms}) AND FIRST_IDATE:[{since} TO {until}]"
    params = {
        "query": query,
        "format": "json",
        "resultType": "core",
        "pageSize": "1000",
        "sort": "FIRST_IDATE_D desc",
    }
    if email := _contact_email():
        params["email"] = email

    url = (
        "https://www.ebi.ac.uk/europepmc/webservices/rest/search?"
        + urlencode(params)
    )
    # Europe PMC occasionally returns a short-lived 503. A fifth attempt, with
    # the shared Retry-After-aware backoff, avoids treating a brief outage as a
    # persistent source failure.
    results = request_json(url, retries=5).get("resultList", {}).get("result", [])

    papers: list[Paper] = []
    for item in results:
        title = clean(item.get("title"))
        source_id = clean(item.get("id") or item.get("pmid"))
        if not title or not source_id:
            continue

        authors = [
            clean(author.get("fullName"))
            for author in item.get("authorList", {}).get("author", [])
            if clean(author.get("fullName"))
        ]
        publication_type = item.get("pubType") or item.get(
            "pubTypeList", {}
        ).get("pubType", [])
        if isinstance(publication_type, list):
            publication_type = ", ".join(map(clean, publication_type))

        source = clean(item.get("source") or "MED")
        papers.append(
            Paper(
                sources=["Europe PMC"],
                source_ids=[f"{source}:{source_id}"],
                title=title,
                authors=authors,
                venue=clean(item.get("journalTitle")),
                date=clean(
                    item.get("firstPublicationDate")
                    or item.get("electronicPublicationDate")
                    or item.get("pubYear")
                ),
                doi=normalize_doi(item.get("doi") or ""),
                url=(
                    f"https://europepmc.org/article/"
                    f"{quote(source)}/{quote(source_id)}"
                ),
                abstract=clean(item.get("abstractText")),
                publication_type=clean(publication_type),
            )
        )
    return papers


def fetch_crossref(
    config: dict[str, Any], since: dt.date, until: dt.date
) -> list[Paper]:
    """Fetch journal articles and posted content registered with Crossref."""

    source_config = config["sources"]["crossref"]
    rows = max(1, min(int(source_config.get("rows_per_query", 150)), 1000))
    date_filter = f"from-created-date:{since},until-created-date:{until}"
    papers: list[Paper] = []

    for query in config["search"]["crossref_queries"]:
        for content_type in ("journal-article", "posted-content"):
            params = {
                "query.bibliographic": query,
                "filter": f"{date_filter},type:{content_type}",
                "rows": str(rows),
                "sort": "created",
                "order": "desc",
            }
            if email := _contact_email():
                params["mailto"] = email

            data = request_json(
                "https://api.crossref.org/works?" + urlencode(params)
            )
            for item in data.get("message", {}).get("items", []):
                title_values = item.get("title", [])
                title = clean(
                    title_values[0]
                    if isinstance(title_values, list) and title_values
                    else title_values
                )
                doi = normalize_doi(item.get("DOI") or "")
                if not title or not doi:
                    continue

                authors = [
                    clean(
                        " ".join(
                            part
                            for part in (
                                author.get("given", ""),
                                author.get("family", ""),
                            )
                            if part
                        )
                    )
                    for author in item.get("author", [])
                ]
                venues = item.get("container-title", [])
                venue = clean(
                    venues[0] if isinstance(venues, list) and venues else venues
                )
                published = next(
                    (
                        crossref_date(item[field])
                        for field in (
                            "published-online",
                            "published",
                            "published-print",
                            "created",
                        )
                        if isinstance(item.get(field), dict)
                        and crossref_date(item[field])
                    ),
                    "",
                )

                papers.append(
                    Paper(
                        sources=["Crossref"],
                        source_ids=[doi],
                        title=title,
                        authors=authors,
                        venue=venue,
                        date=published,
                        doi=doi,
                        url=f"https://doi.org/{doi}",
                        abstract=clean(item.get("abstract")),
                        publication_type=clean(item.get("type")),
                    )
                )
            # Stay below Crossref's polite request rate.
            time.sleep(0.2)

    return papers


def build_arxiv_query(
    config: dict[str, Any], since: dt.date, until: dt.date
) -> str:
    """Build a narrow query that is filtered on the arXiv server."""

    pk_terms = config["search"]["database_terms"]
    ai_terms = config["terms"]["ai"]
    pk_clause = " OR ".join(f'all:"{term}"' for term in pk_terms)
    ai_clause = " OR ".join(f'all:"{term}"' for term in ai_terms)
    date_clause = (
        f"submittedDate:[{since:%Y%m%d}0000 TO {until:%Y%m%d}2359]"
    )
    return f"({pk_clause}) AND ({ai_clause}) AND {date_clause}"


def fetch_arxiv(
    config: dict[str, Any], since: dt.date, until: dt.date
) -> list[Paper]:
    """Fetch abstracts from arXiv.

    arXiv is optional because shared GitHub-hosted runner IPs can receive HTTP
    429 responses. The monitor records such failures internally without adding
    them to the user-facing report.
    """

    source_config = config["sources"]["arxiv"]
    max_results = max(
        1, min(int(source_config.get("max_results", 50)), 200)
    )
    params = {
        "search_query": build_arxiv_query(config, since, until),
        "start": "0",
        "max_results": str(max_results),
        "sortBy": "submittedDate",
        "sortOrder": "descending",
    }

    jitter = max(0, int(source_config.get("jitter_seconds", 60)))
    if jitter:
        time.sleep(random.uniform(0, jitter))

    user_agent = "poppk-ai-literature-monitor/6.0"
    if email := _contact_email():
        user_agent += f" (mailto:{email})"

    payload = request(
        "https://export.arxiv.org/api/query?" + urlencode(params),
        accept="application/atom+xml",
        headers={"User-Agent": user_agent},
        retries=1,
    )
    root = ET.fromstring(payload)
    namespace = {
        "atom": "http://www.w3.org/2005/Atom",
        "arxiv": "http://arxiv.org/schemas/atom",
    }

    papers: list[Paper] = []
    for entry in root.findall("atom:entry", namespace):
        title = clean(entry.findtext("atom:title", "", namespace))
        url = clean(entry.findtext("atom:id", "", namespace))
        published = clean(entry.findtext("atom:published", "", namespace))
        date = parse_date(published)
        if not title or not url or (date and not since <= date <= until):
            continue

        arxiv_id = url.rstrip("/").split("/")[-1]
        papers.append(
            Paper(
                sources=["arXiv"],
                source_ids=[arxiv_id],
                title=title,
                authors=[
                    clean(author.findtext("atom:name", "", namespace))
                    for author in entry.findall("atom:author", namespace)
                ],
                venue="arXiv",
                date=published,
                doi=normalize_doi(
                    entry.findtext("arxiv:doi", "", namespace)
                ),
                url=url.replace("http://", "https://"),
                abstract=clean(
                    entry.findtext("atom:summary", "", namespace)
                ),
                publication_type="preprint",
            )
        )
    return papers
