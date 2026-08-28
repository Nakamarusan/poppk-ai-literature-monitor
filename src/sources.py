"""Literature-database clients."""
from __future__ import annotations

import datetime as dt
import os
import time
from typing import Any
from urllib.parse import quote, urlencode
from xml.etree import ElementTree as ET

from .core import Paper, clean, date_parts, normalize_doi, parse_date, request, request_json


def fetch_europe_pmc(config: dict[str, Any], since: dt.date, until: dt.date) -> list[Paper]:
    terms = " OR ".join(f'"{term}"' for term in config["search_terms"])
    query = f"({terms}) AND FIRST_IDATE:[{since.isoformat()} TO {until.isoformat()}]"
    params = {"query": query, "format": "json", "resultType": "core", "pageSize": "1000",
              "sort": "FIRST_IDATE_D desc"}
    email = os.getenv("CONTACT_EMAIL", "").strip()
    if email:
        params["email"] = email
    endpoint = "https://www.ebi.ac.uk/europepmc/webservices/rest/search?" + urlencode(params)
    data = request_json(endpoint)
    papers: list[Paper] = []
    for item in data.get("resultList", {}).get("result", []):
        title = clean(item.get("title"))
        source_id = clean(item.get("id") or item.get("pmid"))
        if not title or not source_id:
            continue
        authors = [clean(author.get("fullName"))
                   for author in item.get("authorList", {}).get("author", [])
                   if clean(author.get("fullName"))]
        pub_type = item.get("pubType") or item.get("pubTypeList", {}).get("pubType", [])
        if isinstance(pub_type, list):
            pub_type = ", ".join(map(clean, pub_type))
        source = clean(item.get("source") or "MED")
        papers.append(Paper(
            ["Europe PMC"], [f"{source}:{source_id}"], title, authors,
            clean(item.get("journalTitle")),
            clean(item.get("firstPublicationDate") or item.get("electronicPublicationDate") or item.get("pubYear")),
            normalize_doi(item.get("doi") or ""),
            f"https://europepmc.org/article/{quote(source)}/{quote(source_id)}",
            clean(item.get("abstractText")), clean(pub_type)))
    return papers


def fetch_crossref(config: dict[str, Any], since: dt.date, until: dt.date) -> list[Paper]:
    date_filter = f"from-created-date:{since.isoformat()},until-created-date:{until.isoformat()}"
    papers: list[Paper] = []
    for query in config["crossref_queries"]:
        for content_type in ("journal-article", "posted-content"):
            params = {
                "query.bibliographic": query,
                "filter": date_filter + f",type:{content_type}",
                "rows": "150", "sort": "created", "order": "desc",
            }
            email = os.getenv("CONTACT_EMAIL", "").strip()
            if email:
                params["mailto"] = email
            data = request_json("https://api.crossref.org/works?" + urlencode(params))
            for item in data.get("message", {}).get("items", []):
                titles = item.get("title", [])
                title = clean(titles[0] if isinstance(titles, list) and titles else titles)
                doi = normalize_doi(item.get("DOI") or "")
                if not title or not doi:
                    continue
                authors = [clean(" ".join(value for value in (author.get("given", ""), author.get("family", "")) if value))
                           for author in item.get("author", [])]
                containers = item.get("container-title", [])
                venue = clean(containers[0] if isinstance(containers, list) and containers else containers)
                published = ""
                for key in ("published-online", "published", "published-print", "created"):
                    if isinstance(item.get(key), dict) and (published := date_parts(item[key])):
                        break
                papers.append(Paper(["Crossref"], [doi], title, authors, venue, published, doi,
                                    f"https://doi.org/{doi}", clean(item.get("abstract")),
                                    clean(item.get("type"))))
            time.sleep(0.2)
    return papers


def fetch_arxiv(config: dict[str, Any], since: dt.date, until: dt.date) -> list[Paper]:
    search = " OR ".join(f'all:"{term}"' for term in config["search_terms"])
    params = {"search_query": search, "start": "0", "max_results": "200",
              "sortBy": "submittedDate", "sortOrder": "descending"}
    payload = request("https://export.arxiv.org/api/query?" + urlencode(params),
                      accept="application/atom+xml")
    root = ET.fromstring(payload)
    ns = {"a": "http://www.w3.org/2005/Atom", "x": "http://arxiv.org/schemas/atom"}
    papers: list[Paper] = []
    for entry in root.findall("a:entry", ns):
        title = clean(entry.findtext("a:title", "", ns))
        url = clean(entry.findtext("a:id", "", ns))
        published = clean(entry.findtext("a:published", "", ns))
        day = parse_date(published)
        if not title or not url or (day and not since <= day <= until):
            continue
        arxiv_id = url.rstrip("/").split("/")[-1]
        authors = [clean(author.findtext("a:name", "", ns)) for author in entry.findall("a:author", ns)]
        papers.append(Paper(["arXiv"], [arxiv_id], title, authors, "arXiv", published,
                            normalize_doi(entry.findtext("x:doi", "", ns)),
                            url.replace("http://", "https://"),
                            clean(entry.findtext("a:summary", "", ns)), "preprint"))
    return papers
