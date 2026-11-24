"""The research bot: question -> topic -> MoE expert -> videos, papers, jobs."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import torch

from .classifier import TopicClassifier
from .crosswalk import Index
from .moe import MoEConfig, MoELM


class ResearchBot:
    def __init__(self, work_dir: str):
        w = Path(work_dir)
        self.clf = TopicClassifier.load(str(w / "classifier.pkl"))
        self.tax = self.clf.tax
        self.index = Index(str(w / "index"))
        self.lm = None
        if (w / "moe.pt").exists():
            ck = torch.load(w / "moe.pt", map_location="cpu", weights_only=False)
            self.lm = MoELM(MoEConfig(**ck["config"]))
            self.lm.load_state_dict(ck["state"])
            self.lm.eval()

    def _topics(self, p: np.ndarray, mass: float = 0.7, k: int = 3) -> list[tuple[str, float]]:
        out, acc = [], 0.0
        top = p.max()
        for i in np.argsort(-p)[:k]:
            if p[i] < 0.5 * top:                     # drop weak tail topics
                break
            out.append((self.tax.ids[i], float(p[i]))); acc += p[i]
            if acc >= mass:
                break
        return out

    def ask(self, question: str, k: int = 5, generate: int = 0) -> dict:
        p = self.clf.classify_query(question)
        topics = self._topics(p)
        tids = [t for t, _ in topics]
        walk = self.index.walk["map"]
        paper_topics = sorted({t for tid in tids for t, _ in walk.get(tid, {}).get("papers", [])} | set(tids))
        job_topics = sorted({t for pt in paper_topics for t, _ in walk.get(pt, {}).get("jobs_via_papers", [])} | set(tids))

        q = self.clf.vec.transform([question])
        domain_p = np.zeros(len(self.tax.domains))
        for i, pi in enumerate(p):
            domain_p[self.tax.topic_domain[i]] += pi
        res = {
            "question": question,
            "topics": [[t, round(s, 3)] for t, s in topics],
            "expert_domain": self.tax.domains[int(domain_p.argmax())],
            "videos": self.index.search(q, "video", tids, k),
            "papers": self.index.search(q, "paper", paper_topics, k),
            "jobs": self.index.search(q, "job", job_topics, k),
        }
        if self.lm is not None and generate > 0:
            # Steer the router toward the chosen domain's expert (log-prior bias).
            bias = torch.zeros(self.lm.c.n_experts)
            bias[: len(domain_p)] = torch.tensor(np.log(domain_p + 1e-3), dtype=torch.float32)
            res["expert_notes"] = self.lm.generate(question + " ", n=generate, expert_bias=bias)
        return res


def render(r: dict) -> str:
    lines = [f"Q: {r['question']}",
             "topics: " + ", ".join(f"{t} ({s:.2f})" for t, s in r["topics"]) + f"  | expert: {r['expert_domain']}"]
    for key in ("videos", "papers", "jobs"):
        lines.append(f"\n{key.upper()}")
        if not r[key]:
            lines.append("  (none indexed for these topics)")
        for h in r[key]:
            extra = f" — {h['meta'].get('org')}" if h.get("meta", {}).get("org") else ""
            lines.append(f"  [{h['score']:.2f}] {h['title']}{extra}  <{h['url']}>  ({h['topic']})")
    if r.get("expert_notes"):
        lines.append("\nEXPERT NOTES (MoE LM)\n  " + r["expert_notes"].replace("\n", " "))
    return "\n".join(lines)


def to_json(r: dict) -> str:
    return json.dumps(r, indent=1, ensure_ascii=False)
