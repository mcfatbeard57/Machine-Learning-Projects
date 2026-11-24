"""Fetch papers and research jobs into the JSONL shard format corpus.py reads.

There is no single feed of "all research jobs". Coverage comes from stacking
adapters; each one writes {"id","title","description","url","org","location",...}.
  - USAJobs API (US federal research roles; needs a free API key + email UA)
  - Any RSS/Atom job feed (university HR boards, EURAXESS, jobs.ac.uk,
    AcademicJobsOnline, lab sites). Pass the feed URLs; formats vary per board.
  - A local CSV/JSONL dump you already scraped.
Respect each site's terms of use and robots.txt; most commercial boards
(LinkedIn, Indeed, Glassdoor) forbid scraping, so they are not included.
"""
from __future__ import annotations

import csv
import hashlib
import json
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from typing import Iterator

UA = "research-bot/0.1"
ATOM = "{http://www.w3.org/2005/Atom}"
ARXIV = "{http://arxiv.org/schemas/atom}"


def _get(url: str, headers: dict | None = None, timeout: int = 60) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA, **(headers or {})})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def write_jsonl(records: Iterator[dict], path: str) -> int:
    n = 0
    with open(path, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n"); n += 1
    return n


# ------------------------------------------------------------------ papers
def arxiv(query: str, max_results: int = 1000, page: int = 200, delay: float = 3.0) -> Iterator[dict]:
    """arXiv export API. query e.g. 'cat:math.*' or 'all:transformer'. 3s delay per their policy."""
    for start in range(0, max_results, page):
        q = urllib.parse.urlencode({"search_query": query, "start": start, "max_results": min(page, max_results - start)})
        root = ET.fromstring(_get(f"http://export.arxiv.org/api/query?{q}"))
        entries = root.findall(f"{ATOM}entry")
        if not entries:
            return
        for e in entries:
            cats = [c.get("term") for c in e.findall(f"{ATOM}category")]
            prim = e.find(f"{ARXIV}primary_category")
            if prim is not None and prim.get("term") in cats:
                cats.remove(prim.get("term")); cats.insert(0, prim.get("term"))
            yield {
                "id": e.findtext(f"{ATOM}id", "").rsplit("/", 1)[-1],
                "title": " ".join(e.findtext(f"{ATOM}title", "").split()),
                "abstract": " ".join(e.findtext(f"{ATOM}summary", "").split()),
                "categories": cats,
                "url": e.findtext(f"{ATOM}id", ""),
                "year": e.findtext(f"{ATOM}published", "")[:4],
            }
        time.sleep(delay)


def _openalex_abstract(inv: dict | None) -> str:
    if not inv:
        return ""
    pos = sorted((p, w) for w, ps in inv.items() for p in ps)
    return " ".join(w for _, w in pos)


def openalex(search: str, max_results: int = 1000, mailto: str | None = None) -> Iterator[dict]:
    """OpenAlex works API (cursor paging). Non-arXiv fields (medicine, humanities)
    have no arXiv category, so they get labelled by the classifier instead."""
    cursor, n = "*", 0
    while cursor and n < max_results:
        params = {"search": search, "per-page": 200, "cursor": cursor}
        if mailto:
            params["mailto"] = mailto
        d = json.loads(_get("https://api.openalex.org/works?" + urllib.parse.urlencode(params)))
        for w in d.get("results", []):
            yield {
                "id": w["id"].rsplit("/", 1)[-1],
                "title": w.get("title") or "",
                "abstract": _openalex_abstract(w.get("abstract_inverted_index")),
                "url": w.get("doi") or w["id"],
                "year": w.get("publication_year"),
                "openalex_topic": (w.get("primary_topic") or {}).get("display_name"),
            }
            n += 1
            if n >= max_results:
                return
        cursor = d.get("meta", {}).get("next_cursor")


# -------------------------------------------------------------------- jobs
def usajobs(keyword: str, api_key: str, email: str, pages: int = 5) -> Iterator[dict]:
    """https://developer.usajobs.gov — Authorization-Key header, email as User-Agent."""
    h = {"Authorization-Key": api_key, "User-Agent": email, "Host": "data.usajobs.gov"}
    for page in range(1, pages + 1):
        q = urllib.parse.urlencode({"Keyword": keyword, "ResultsPerPage": 500, "Page": page})
        d = json.loads(_get(f"https://data.usajobs.gov/api/search?{q}", headers=h))
        items = d.get("SearchResult", {}).get("SearchResultItems", [])
        if not items:
            return
        for it in items:
            m = it["MatchedObjectDescriptor"]
            det = m.get("UserArea", {}).get("Details", {})
            yield {
                "id": "usajobs-" + str(m.get("PositionID")),
                "title": m.get("PositionTitle", ""),
                "description": " ".join([det.get("JobSummary", ""), " ".join(det.get("MajorDuties", []) or [])]),
                "url": m.get("PositionURI", ""),
                "org": m.get("OrganizationName", ""),
                "location": m.get("PositionLocationDisplay", ""),
                "deadline": m.get("ApplicationCloseDate", ""),
            }


def rss(url: str) -> Iterator[dict]:
    """Generic RSS 2.0 / Atom job feed."""
    root = ET.fromstring(_get(url))
    items = root.findall(".//item") or root.findall(f".//{ATOM}entry")
    for it in items:
        title = it.findtext("title") or it.findtext(f"{ATOM}title") or ""
        link = it.findtext("link") or ""
        if not link:
            l = it.find(f"{ATOM}link")
            link = l.get("href", "") if l is not None else ""
        desc = it.findtext("description") or it.findtext(f"{ATOM}summary") or it.findtext(f"{ATOM}content") or ""
        yield {
            "id": "rss-" + hashlib.sha1((link or title).encode()).hexdigest()[:16],
            "title": title.strip(), "description": _strip_html(desc), "url": link, "feed": url,
        }


def csv_jobs(path: str, title="title", description="description", url="url") -> Iterator[dict]:
    with open(path, newline="", encoding="utf-8") as f:
        for i, row in enumerate(csv.DictReader(f)):
            yield {"id": row.get("id") or f"csv-{i}", "title": row.get(title, ""),
                   "description": row.get(description, ""), "url": row.get(url, ""),
                   **{k: row[k] for k in ("org", "location", "deadline") if k in row}}


def _strip_html(s: str) -> str:
    import html, re
    return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", s)).split())
