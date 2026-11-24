"""Shared topic taxonomy + weak labelling (keyword seeds, arXiv categories)."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

DEFAULT = Path(__file__).with_name("taxonomy.json")


@dataclass
class Taxonomy:
    topics: list[dict]

    @classmethod
    def load(cls, path: str | Path = DEFAULT) -> "Taxonomy":
        return cls(json.loads(Path(path).read_text())["topics"])

    def __post_init__(self):
        self.ids = [t["id"] for t in self.topics]
        self.index = {t: i for i, t in enumerate(self.ids)}
        self.domains = sorted({t["domain"] for t in self.topics})
        self.domain_index = {d: i for i, d in enumerate(self.domains)}
        self.topic_domain = [self.domain_index[t["domain"]] for t in self.topics]
        self._kw = [
            [re.compile(r"\b" + re.escape(k.lower()) + r"\b") for k in t["keywords"]] for t in self.topics
        ]

    def __len__(self) -> int:
        return len(self.ids)

    def from_arxiv(self, categories: list[str] | str | None) -> int | None:
        """Strong label for papers: longest matching arXiv prefix wins."""
        if not categories:
            return None
        cats = categories.split() if isinstance(categories, str) else categories
        best, best_len = None, 0
        for cat in cats[:1] or cats:          # primary category only
            for i, t in enumerate(self.topics):
                for p in t["arxiv"]:
                    if cat.startswith(p) and len(p) > best_len:
                        best, best_len = i, len(p)
        return best

    def keyword_scores(self, text: str) -> list[int]:
        low = text.lower()
        return [sum(len(p.findall(low)) for p in pats) for pats in self._kw]

    def weak_label(self, text: str, min_hits: int = 2, margin: float = 1.5) -> int | None:
        """Label only when one topic clearly dominates; abstain otherwise."""
        s = self.keyword_scores(text)
        order = sorted(range(len(s)), key=s.__getitem__, reverse=True)
        top, second = s[order[0]], s[order[1]]
        if top >= min_hits and top >= margin * max(second, 1e-9):
            return order[0]
        return None
