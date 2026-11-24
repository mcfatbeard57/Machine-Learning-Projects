"""Video topic -> paper topic -> job topic crosswalk + per-source retrieval index.

Labels alone give the trivial identity mapping (math.algebra -> math.algebra).
The useful signal is the *off-diagonal*: e.g. videos the classifier calls
cs.ml_ai whose vocabulary sits closest to soc.economics papers. We get it from
centroid cosine similarity between (source, topic) groups in the shared
hashed feature space.
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Iterable

import numpy as np
import scipy.sparse as sp

from .classifier import TopicClassifier, _with_source
from .corpus import batched

SOURCES = ("video", "paper", "job")


def build(clf: TopicClassifier, records: Iterable[dict], out_dir: str, batch: int = 4096) -> dict:
    out = Path(out_dir); out.mkdir(parents=True, exist_ok=True)
    T, D = len(clf.tax), clf.vec.n_features
    sums = {s: np.zeros((T, D), dtype=np.float32) for s in SOURCES}
    counts = {s: Counter() for s in SOURCES}
    mats: dict[str, list] = {s: [] for s in SOURCES}
    metas = {s: open(out / f"{s}_meta.jsonl", "w") for s in SOURCES}
    try:
        for chunk in batched(iter(records), batch):
            X = clf.vec.transform([r["text"] for r in chunk])          # no src token: pure content
            P = clf.predict_proba([_with_source(r) for r in chunk])
            y = P.argmax(1)
            for s in SOURCES:
                idx = [i for i, r in enumerate(chunk) if r["source"] == s]
                if not idx:
                    continue
                Xs = X[idx]
                mats[s].append(Xs.astype(np.float32))
                for j, i in enumerate(idx):
                    t = int(y[i])
                    counts[s][t] += 1
                    row = Xs.getrow(j)
                    sums[s][t, row.indices] += row.data
                    r = chunk[i]
                    metas[s].write(json.dumps({
                        "id": r["id"], "title": r["title"], "url": r["url"], "topic": clf.tax.ids[t],
                        "prob": round(float(P[i, t]), 4), "meta": r["meta"]}) + "\n")
    finally:
        for f in metas.values():
            f.close()

    for s in SOURCES:
        if mats[s]:
            sp.save_npz(out / f"{s}_X.npz", sp.vstack(mats[s]).tocsr())

    def normed(a):
        n = np.linalg.norm(a, axis=1, keepdims=True)
        return np.divide(a, n, out=np.zeros_like(a), where=n > 0)

    C = {s: normed(sums[s]) for s in SOURCES}
    walk = {"topics": clf.tax.ids, "counts": {s: {clf.tax.ids[k]: v for k, v in counts[s].items()} for s in SOURCES},
            "map": {}}
    v2p, p2j, v2j = C["video"] @ C["paper"].T, C["paper"] @ C["job"].T, C["video"] @ C["job"].T
    for t, tid in enumerate(clf.tax.ids):
        walk["map"][tid] = {
            "papers": _top(v2p[t], clf.tax.ids),
            "jobs_via_papers": _top(p2j[t], clf.tax.ids),
            "jobs_direct": _top(v2j[t], clf.tax.ids),
        }
    np.save(out / "affinity_video_paper.npy", v2p)
    np.save(out / "affinity_paper_job.npy", p2j)
    (out / "crosswalk.json").write_text(json.dumps(walk, indent=1))
    return walk


def _top(row: np.ndarray, ids: list[str], k: int = 3) -> list[list]:
    return [[ids[i], round(float(row[i]), 3)] for i in np.argsort(-row)[:k] if row[i] > 0]


class Index:
    """Topic-filtered sparse retrieval. Fine to a few million rows; beyond that
    swap the matrices for dense embeddings in FAISS/ScaNN, same interface."""

    def __init__(self, out_dir: str):
        d = Path(out_dir)
        self.walk = json.loads((d / "crosswalk.json").read_text())
        self.X, self.meta, self.topic = {}, {}, {}
        for s in SOURCES:
            if (d / f"{s}_X.npz").exists():
                self.X[s] = sp.load_npz(d / f"{s}_X.npz")
                self.meta[s] = [json.loads(l) for l in open(d / f"{s}_meta.jsonl")]
                self.topic[s] = np.array([m["topic"] for m in self.meta[s]])

    def search(self, q: sp.csr_matrix, source: str, topics: list[str], k: int = 5) -> list[dict]:
        if source not in self.X:
            return []
        scores = (self.X[source] @ q.T).toarray().ravel()
        mask = np.isin(self.topic[source], topics)
        scores = np.where(mask, scores, -1.0)
        top = np.argsort(-scores)[:k]
        return [dict(self.meta[source][i], score=round(float(scores[i]), 3)) for i in top if scores[i] > 0]
