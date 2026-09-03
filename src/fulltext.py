"""Locate and extract legally available full text for selected papers."""
from __future__ import annotations

import io
import os
import re
from dataclasses import dataclass, field
from typing import Any, Iterable
from urllib.parse import quote, urlencode
from xml.etree import ElementTree as ET

from .core import (
    MonitorError,
    Paper,
    clean,
    normalize_doi,
    normalize_pmcid,
    normalize_title,
    request_json,
    request_response,
)

try:
    from bs4 import BeautifulSoup
except ImportError:  # pragma: no cover
    BeautifulSoup = None  # type: ignore[assignment]

try:
    from pypdf import PdfReader
except ImportError:  # pragma: no cover
    PdfReader = None  # type: ignore[assignment]

EPMC_BASE = "https://www.ebi.ac.uk/europepmc/webservices/rest"
UNPAYWALL_BASE = "https://api.unpaywall.org/v2"
PAYWALL_PHRASES = (
    "purchase access",
    "buy this article",
    "institutional access",
    "sign in to access",
    "subscribe to read",
    "access through your institution",
)
SECTION_PRIORITY = (
    "introduction",
    "background",
    "methods",
    "materials and methods",
    "results",
    "discussion",
    "conclusion",
    "conclusions",
)


@dataclass(frozen=True)
class FullTextDocument:
    text: str
    url: str
    source: str
    sections: list[str] = field(default_factory=list)
    license: str = ""


@dataclass(frozen=True)
class FullTextCandidate:
    url: str
    source: str
    media_type: str = ""
    license: str = ""


def _clip_text(value: str, limit: int) -> str:
    value = clean(value)
    return value if len(value) <= limit else value[:limit].rstrip() + " …"


def _element_text(element: ET.Element | None) -> str:
    if element is None:
        return ""
    return clean(" ".join(element.itertext()))


def _unique(values: Iterable[str]) -> list[str]:
    output: list[str] = []
    for value in values:
        value = clean(value)
        if value and value not in output:
            output.append(value)
    return output


def extract_jats_xml(payload: bytes, max_chars: int) -> tuple[str, list[str], str]:
    """Extract readable sections from JATS XML without reproducing references."""
    try:
        root = ET.fromstring(payload)
    except ET.ParseError as exc:
        raise MonitorError("Open full-text XML could not be parsed") from exc

    license_text = ""
    for node in root.findall(".//license"):
        license_text = _element_text(node)
        if license_text:
            break

    body = root.find(".//body")
    if body is None:
        body = root

    blocks: list[str] = []
    section_names: list[str] = []
    for section in body.findall(".//sec"):
        title = _element_text(section.find("title"))
        title_key = title.casefold()
        if title_key.startswith(("reference", "bibliograph")):
            continue
        paragraphs = [
            _element_text(paragraph)
            for paragraph in section.findall(".//p")
        ]
        paragraphs = [paragraph for paragraph in paragraphs if paragraph]
        if not paragraphs:
            continue
        if title:
            section_names.append(title)
            blocks.append(f"## {title}")
        blocks.extend(paragraphs)
        if sum(len(block) for block in blocks) >= max_chars:
            break

    if not blocks:
        blocks = [
            _element_text(paragraph)
            for paragraph in body.findall(".//p")
            if _element_text(paragraph)
        ]

    text = _clip_text("\n\n".join(blocks), max_chars)
    return text, _unique(section_names), license_text


def extract_html(payload: bytes, max_chars: int) -> tuple[str, list[str]]:
    if BeautifulSoup is None:
        raise MonitorError("beautifulsoup4 is required to extract HTML full text")
    soup = BeautifulSoup(payload, "html.parser")
    for element in soup.select(
        "script, style, nav, header, footer, aside, form, noscript, svg"
    ):
        element.decompose()
    container = soup.find("article") or soup.find("main") or soup.body or soup
    blocks: list[str] = []
    sections: list[str] = []
    for element in container.find_all(["h1", "h2", "h3", "h4", "p"]):
        text = clean(element.get_text(" ", strip=True))
        if not text:
            continue
        if element.name in {"h1", "h2", "h3", "h4"}:
            if text.casefold().startswith(("reference", "bibliograph")):
                break
            sections.append(text)
            blocks.append(f"## {text}")
        elif len(text) >= 30:
            blocks.append(text)
        if sum(len(block) for block in blocks) >= max_chars:
            break
    text = _clip_text("\n\n".join(blocks), max_chars)
    lowered = text.casefold()
    if len(text) < 1_200 or any(phrase in lowered for phrase in PAYWALL_PHRASES):
        raise MonitorError("The HTML page did not contain usable open full text")
    return text, _unique(sections)


def extract_pdf(
    payload: bytes, max_chars: int, max_pages: int
) -> tuple[str, list[str]]:
    if PdfReader is None:
        raise MonitorError("pypdf is required to extract PDF full text")
    try:
        reader = PdfReader(io.BytesIO(payload))
        if reader.is_encrypted:
            try:
                reader.decrypt("")
            except Exception as exc:  # pragma: no cover
                raise MonitorError("The open PDF is encrypted") from exc
        pages: list[str] = []
        for page in reader.pages[:max_pages]:
            text = clean(page.extract_text() or "")
            if text:
                pages.append(text)
            if sum(len(item) for item in pages) >= max_chars:
                break
    except MonitorError:
        raise
    except Exception as exc:
        raise MonitorError("The open PDF could not be parsed") from exc
    text = _clip_text("\n\n".join(pages), max_chars)
    if len(text) < 1_200:
        raise MonitorError("The open PDF did not contain enough extractable text")
    sections = [
        heading.title()
        for heading in SECTION_PRIORITY
        if re.search(rf"(?im)^\s*{re.escape(heading)}\s*$", text)
    ]
    return text, sections


def _source_id_candidates(paper: Paper) -> list[str]:
    ids: list[str] = []
    if paper.pmcid:
        ids.append(normalize_pmcid(paper.pmcid))
    for source, source_id in zip(paper.sources, paper.source_ids):
        if source.casefold() != "europe pmc":
            continue
        raw = clean(source_id)
        if ":" in raw:
            _, raw = raw.split(":", 1)
        if raw.upper().startswith(("PMC", "PPR")):
            ids.append(raw.upper())
    return _unique(ids)


def _match_europe_pmc_record(
    paper: Paper, records: list[dict[str, Any]]
) -> dict[str, Any] | None:
    doi = normalize_doi(paper.doi)
    title = normalize_title(paper.title)
    for record in records:
        if doi and normalize_doi(record.get("doi") or "") == doi:
            return record
    for record in records:
        if normalize_title(record.get("title") or "") == title:
            return record
    return records[0] if len(records) == 1 else None


def lookup_europe_pmc(paper: Paper) -> tuple[str, list[FullTextCandidate], bool]:
    """Find Europe PMC identifiers and legal full-text links for one paper."""
    candidates: list[FullTextCandidate] = []
    pmcid = normalize_pmcid(paper.pmcid)
    open_access = bool(paper.is_open_access)

    queries: list[str] = []
    doi = normalize_doi(paper.doi)
    if doi:
        queries.append(f'DOI:"{doi}"')
    for source, source_id in zip(paper.sources, paper.source_ids):
        if source.casefold() == "europe pmc" and source_id:
            if ":" in source_id:
                src, ext_id = source_id.split(":", 1)
                queries.append(f'EXT_ID:"{ext_id}" AND SRC:{src}')
            else:
                queries.append(f'EXT_ID:"{source_id}"')

    for query in _unique(queries):
        params = {
            "query": query,
            "format": "json",
            "resultType": "core",
            "pageSize": "5",
        }
        data = request_json(f"{EPMC_BASE}/search?{urlencode(params)}", retries=2)
        records = data.get("resultList", {}).get("result", [])
        record = _match_europe_pmc_record(paper, records)
        if not record:
            continue
        pmcid = normalize_pmcid(record.get("pmcid") or pmcid)
        open_access = open_access or clean(record.get("isOpenAccess")).upper() == "Y"
        links = record.get("fullTextUrlList", {}).get("fullTextUrl", [])
        for link in links if isinstance(links, list) else []:
            url = clean(link.get("url"))
            if not url:
                continue
            availability = clean(link.get("availability"))
            style = clean(link.get("documentStyle"))
            site = clean(link.get("site")) or "Europe PMC linked full text"
            if "open" in availability.casefold() or open_access:
                candidates.append(FullTextCandidate(url, site, style, availability))
        break

    for identifier in _source_id_candidates(paper):
        if identifier.startswith("PMC") and not pmcid:
            pmcid = identifier
    if pmcid:
        candidates.insert(
            0,
            FullTextCandidate(
                f"{EPMC_BASE}/{quote(pmcid)}/fullTextXML",
                "Europe PMC open full-text XML",
                "xml",
            ),
        )
        candidates.insert(
            1,
            FullTextCandidate(
                f"https://europepmc.org/articles/{quote(pmcid)}",
                "Europe PMC",
                "html",
            ),
        )
    else:
        for identifier in _source_id_candidates(paper):
            if identifier.startswith("PPR"):
                candidates.insert(
                    0,
                    FullTextCandidate(
                        f"{EPMC_BASE}/{quote(identifier)}/fullTextXML",
                        "Europe PMC preprint full-text XML",
                        "xml",
                    ),
                )
    return pmcid, candidates, open_access


def lookup_unpaywall(paper: Paper) -> list[FullTextCandidate]:
    doi = normalize_doi(paper.doi)
    email = clean(os.getenv("CONTACT_EMAIL"))
    if not doi or "@" not in email:
        return []
    data = request_json(
        f"{UNPAYWALL_BASE}/{quote(doi, safe='')}?" + urlencode({"email": email}),
        retries=2,
    )
    if not data.get("is_oa"):
        return []
    locations = []
    best = data.get("best_oa_location")
    if isinstance(best, dict):
        locations.append(best)
    for location in data.get("oa_locations", []) or []:
        if isinstance(location, dict):
            locations.append(location)
    candidates: list[FullTextCandidate] = []
    for location in locations:
        source = clean(location.get("host_type") or "Unpaywall open-access copy")
        license_name = clean(location.get("license"))
        pdf_url = clean(location.get("url_for_pdf"))
        landing_url = clean(location.get("url"))
        if pdf_url:
            candidates.append(FullTextCandidate(pdf_url, source, "pdf", license_name))
        if landing_url:
            candidates.append(FullTextCandidate(landing_url, source, "html", license_name))
    return candidates


def arxiv_candidates(paper: Paper) -> list[FullTextCandidate]:
    if not any(source.casefold() == "arxiv" for source in paper.sources):
        return []
    arxiv_id = ""
    for source, source_id in zip(paper.sources, paper.source_ids):
        if source.casefold() == "arxiv":
            arxiv_id = re.sub(r"v\d+$", "", clean(source_id), flags=re.I)
            break
    if not arxiv_id:
        match = re.search(
            r"arxiv\.org/(?:abs|pdf|html)/([^?#/.]+(?:\.\d+)?)", paper.url
        )
        arxiv_id = match.group(1) if match else ""
    if not arxiv_id:
        return []
    return [
        FullTextCandidate(
            f"https://arxiv.org/html/{quote(arxiv_id)}", "arXiv HTML", "html"
        ),
        FullTextCandidate(
            f"https://arxiv.org/pdf/{quote(arxiv_id)}.pdf", "arXiv PDF", "pdf"
        ),
    ]


def _candidate_key(candidate: FullTextCandidate) -> str:
    return candidate.url.rstrip("/").casefold()


def _extract_candidate(
    candidate: FullTextCandidate, settings: dict[str, Any]
) -> FullTextDocument:
    max_chars = int(settings.get("max_chars", 60_000))
    max_pages = int(settings.get("max_pdf_pages", 40))
    max_bytes = int(settings.get("max_bytes", 20_000_000))
    response = request_response(
        candidate.url,
        accept="application/xml,text/xml,text/html,application/pdf;q=0.9,*/*;q=0.1",
        retries=2,
        timeout=int(settings.get("timeout_seconds", 45)),
        max_bytes=max_bytes,
    )
    content_type = response.content_type.casefold()
    media_type = candidate.media_type.casefold()
    if (
        "pdf" in content_type
        or media_type == "pdf"
        or response.final_url.lower().endswith(".pdf")
    ):
        text, sections = extract_pdf(response.body, max_chars, max_pages)
    elif (
        "xml" in content_type
        or media_type == "xml"
        or "fulltextxml" in candidate.url.casefold()
    ):
        text, sections, xml_license = extract_jats_xml(response.body, max_chars)
        return FullTextDocument(
            text=text,
            url=response.final_url or candidate.url,
            source=candidate.source,
            sections=sections,
            license=candidate.license or xml_license,
        )
    else:
        text, sections = extract_html(response.body, max_chars)
    return FullTextDocument(
        text=text,
        url=response.final_url or candidate.url,
        source=candidate.source,
        sections=sections,
        license=candidate.license,
    )


def enrich_with_open_full_text(
    paper: Paper, config: dict[str, Any]
) -> FullTextDocument | None:
    """Use open full text when it can be located and extracted legally."""
    settings = config.get("full_text", {})
    if not settings.get("enabled", True):
        return None

    candidates: list[FullTextCandidate] = []
    try:
        pmcid, epmc_candidates, open_access = lookup_europe_pmc(paper)
        paper.pmcid = paper.pmcid or pmcid
        paper.is_open_access = paper.is_open_access or open_access
        candidates.extend(epmc_candidates)
    except Exception as exc:
        print(f"Europe PMC full-text lookup failed for {paper.title}: {clean(exc)}")

    candidates.extend(arxiv_candidates(paper))
    if settings.get("use_unpaywall", True):
        try:
            candidates.extend(lookup_unpaywall(paper))
        except Exception as exc:
            print(f"Unpaywall lookup failed for {paper.title}: {clean(exc)}")

    seen: set[str] = set()
    minimum_chars = int(settings.get("minimum_chars", 1_200))
    for candidate in candidates:
        key = _candidate_key(candidate)
        if not candidate.url or key in seen:
            continue
        seen.add(key)
        try:
            document = _extract_candidate(candidate, settings)
        except Exception as exc:
            print(
                f"Open full-text candidate failed for {paper.title} "
                f"[{candidate.source}]: {clean(exc)}"
            )
            continue
        if len(document.text) < minimum_chars:
            continue
        paper.is_open_access = True
        paper.full_text_url = document.url
        paper.full_text = document.text
        paper.full_text_source = document.source
        paper.full_text_sections = document.sections
        paper.full_text_license = document.license
        return document
    return None
