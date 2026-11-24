"""Streaming readers for the three corpora: videos, papers, jobs.

Every record is normalised to {"id", "source", "title", "text", "url", "meta"}.
Files are JSONL or JSONL.gz shards, read lazily, so 8M transcripts never sit in RAM.
"""
from __future__ import annotations

import glob
import gzip
import json
import re
from typing import Iterator

_TS = re.compile(r"\b\d{1,2}:\d{2}(?::\d{2})?\b")          # 12:34 / 1:02:03
_TAGS = re.compile(r"\[(?:music|applause|laughter|inaudible|__)[^\]]*\]", re.I)
_WS = re.compile(r"\s+")

TEXT_FIELDS = {
    "video": ("transcript", "text", "captions"),
    "paper": ("abstract", "text", "summary"),
    "job": ("description", "text", "body"),
}


def clean(text: str) -> str:
    text = _TAGS.sub(" ", text)
    text = _TS.sub(" ", text)
    return _WS.sub(" ", text).strip()


def _open(path: str):
    return gzip.open(path, "rt", encoding="utf-8") if path.endswith(".gz") else open(path, encoding="utf-8")


def shards(pattern: str) -> list[str]:
    files = sorted(glob.glob(pattern, recursive=True))
    if not files:
        raise FileNotFoundError(f"no shards match {pattern!r}")
    return files


def read(pattern: str, source: str, max_chars: int = 20000) -> Iterator[dict]:
    """Yield normalised records. Bad lines are skipped, not fatal."""
    fields = TEXT_FIELDS[source]
    for path in shards(pattern):
        with _open(path) as f:
            for line in f:
                try:
                    r = json.loads(line)
                except json.JSONDecodeError:
                    continue
                body = next((r[k] for k in fields if r.get(k)), "")
                text = clean(f"{r.get('title', '')}. {body}")[:max_chars]
                if len(text) < 20:
                    continue
                yield {
                    "id": str(r.get("id") or r.get("video_id") or r.get("url")),
                    "source": source,
                    "title": r.get("title", ""),
                    "text": text,
                    "url": r.get("url", ""),
                    "meta": {k: r[k] for k in ("categories", "channel", "org", "location", "deadline", "year") if k in r},
                }


def batched(it: Iterator[dict], n: int) -> Iterator[list[dict]]:
    buf: list[dict] = []
    for r in it:
        buf.append(r)
        if len(buf) == n:
            yield buf
            buf = []
    if buf:
        yield buf
