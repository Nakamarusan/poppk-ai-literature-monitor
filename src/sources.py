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
    date_parts,
    normalize_doi,
    normalize_pmcid,
    parse_date,
    request,
    request_json,
)


def fetch_europe_pmc(
    config: dict[str, Any], since: dt.date, until: dt.date
) -> list[Paper]:
    terms = " OR ".join(f'"{term}"' for term in config["search_terms"])
    query = f"({terms}) AND FIRST_IDATE:[{since.isoformat()} TO {until.isoformat()}]"
    params = {
        "query": query,
        "format": "json",
        "resultType": "core",
        "pageSize": "1000",
        "sort": "FIRST_IDATE_D desc",
    }
    email = os.getenv("CONTACT_EMAIL", "").strip()
    if email:
        params["email"] = email
    endpoint = (
        "https://www.ebi.ac.uk/europepmc/webservices/rest/search?"
        + urlencode(params)
    )
    data = request_json(endpoint)
    papers: list[Paper] = []
    for item in data.get("resultList", {}).get("result", []):
        title = clean(item.get("title"))
        source_id = clean(item.get("id") or item.get("pmid"))
        if not title or not source_id:
            continue
        authors = [
            clean(author.get("fullName"))
            for author in item.get("authorList", {}).get("author", [])
            if clean(author.get("fullName"))
        ]
        pub_type = item.get("pubType") or item.get("pubTypeList", {}).get(
            "pubType", []
        )
        if isinstance(pub_type, list):
            pub_type = ", ".join(map(clean, pub_type))
        source = clean(item.get("source") or "MED")
        pmcid = normalize_pmcid(item.get("pmcid") or "")
        open_access = clean(item.get("isOpenAccess")).upper() == "Y"
        papers.append(
            Paper(
                ["Europe PMC"],
                [f"{source}:{source_id}"],
                title,
                authors,
                clean(item.get("journalTitle")),
                clean(
                    item.get("firstPublicationDate")
                    or item.get("electronicPublicationDate")
                    or item.get("pubYear")
                ),
                normalize_doi(item.get("doi") or ""),
                f"https://europepmc.org/article/{quote(source)}/{quote(source_id)}",
                clean(item.get("abstractText")),
                clean(pub_type),
                pmcid=pmcid,
                is_open_access=open_access,
            )
        )
    return papers


def fetch_crossref(
    config: dict[str, Any], since: dt.date, until: dt.date
) -> list[Paper]:
    date_filter = (
        f"from-created-date:{since.isoformat()},"
        f"until-created-date:{until.isoformat()}"
    )
    papers: list[Paper] = []
    for query in config["crossref_queries"]:
        for content_type in ("journal-article", "posted-content"):
            params = {
                "query.bibliographic": query,
                "filter": date_filter + f",type:{content_type}",
                "rows": "150",
                "sort": "created",
                "order": "desc",
            }
            email = os.getenv("CONTACT_EMAIL", "").strip()
            if email:
                params["mailto"] = email
            data = request_json(
                "https://api.crossref.org/works?" + urlencode(params)
            )
            for item in data.get("message", {}).get("items", []):
                titles = item.get("title", [])
                title = clean(
                    titles[0] if isinstance(titles, list) and titles else titles
                )
                doi = normalize_doi(item.get("DOI") or "")
                if not title or not doi:
                    continue
                authors = [
                    clean(
                        " ".join(
                            value
                            for value in (
                                author.get("given", ""),
                                author.get("family", ""),
                            )
                            if value
                        )
                    )
                    for author in item.get("author", [])
                ]
                containers = item.get("container-title", [])
                venue = clean(
                    containers[0]
                    if isinstance(containers, list) and containers
                    else containers
                )
                published = ""
                for key in (
                    "published-online",
                    "published",
                    "published-print",
                    "created",
                ):
                    if isinstance(item.get(key), dict) and (
                        published := date_parts(item[key])
                    ):
                        break
                licenses = item.get("license") or []
                open_access = any(
                    "creativecommons.org" in clean(
                        license_item.get("URL")
                    ).casefold()
                    for license_item in licenses
                    if isinstance(license_item, dict)
                )
                papers.append(
                    Paper(
                        ["Crossref"],
                        [doi],
                        title,
                        authors,
                        venue,
                        published,
                        doi,
                        f"https://doi.org/{doi}",
                        clean(item.get("abstract")),
                        clean(item.get("type")),
                        is_open_access=open_access,
                    )
                )
            time.sleep(0.2)
    return papers


def build_arxiv_search_query(
    config: dict[str, Any], since: dt.date, until: dt.date
) -> str:
    """Build a narrow, server-side date-filtered arXiv query."""
    settings = config.get("arxiv_query", {})
    pk_terms = settings.get("pk_terms") or config["search_terms"]
    ai_terms = settings.get("ai_terms") or [
        "machine learning",
        "artificial intelligence",
        "federated learning",
        "reinforcement learning",
        "neural network",
        "neural ODE",
        "normalizing flow",
        "scientific machine learning",
        "physics-informed",
        "mechanistic machine learning",
    ]
    pk_clause = " OR ".join(f'all:"{term}"' for term in pk_terms)
    ai_clause = " OR ".join(f'all:"{term}"' for term in ai_terms)
    date_clause = (
        f"submittedDate:[{since.strftime('%Y%m%d')}0000 TO "
        f"{until.strftime('%Y%m%d')}2359]"
    )
    return f"({pk_clause}) AND ({ai_clause}) AND {date_clause}"


def fetch_arxiv(
    config: dict[str, Any], since: dt.date, until: dt.date
) -> list[Paper]:
    settings = config.get("arxiv_query", {})
    search = build_arxiv_search_query(config, since, until)
    max_results = max(1, min(int(settings.get("max_results", 50)), 200))
    params = {
        "search_query": search,
        "start": "0",
        "max_results": str(max_results),
        "sortBy": "submittedDate",
        "sortOrder": "descending",
    }

    jitter_seconds = max(0, int(settings.get("jitter_seconds", 60)))
    if jitter_seconds:
        time.sleep(random.uniform(0, jitter_seconds))

    contact = os.getenv("CONTACT_EMAIL", "").strip()
    user_agent = "poppk-ai-literature-monitor/4.0"
    if contact:
        user_agent += f" (mailto:{contact})"
    payload = request(
        "https://export.arxiv.org/api/query?" + urlencode(params),
        accept="application/atom+xml",
        headers={"User-Agent": user_agent},
        retries=1,
    )
    root = ET.fromstring(payload)
    ns = {
        "a": "http://www.w3.org/2005/Atom",
        "x": "http://arxiv.org/schemas/atom",
    }
    papers: list[Paper] = []
    for entry in root.findall("a:entry", ns):
        title = clean(entry.findtext("a:title", "", ns))
        url = clean(entry.findtext("a:id", "", ns))
        published = clean(entry.findtext("a:published", "", ns))
        day = parse_date(published)
        if not title or not url or (day and not since <= day <= until):
            continue
        arxiv_id = url.rstrip("/").split("/")[-1]
        authors = [
            clean(author.findtext("a:name", "", ns))
            for author in entry.findall("a:author", ns)
        ]
        papers.append(
            Paper(
                ["arXiv"],
                [arxiv_id],
                title,
                authors,
                "arXiv",
                published,
                normalize_doi(entry.findtext("x:doi", "", ns)),
                url.replace("http://", "https://"),
                clean(entry.findtext("a:summary", "", ns)),
                "preprint",
                is_open_access=True,
            )
        )
    return papers
