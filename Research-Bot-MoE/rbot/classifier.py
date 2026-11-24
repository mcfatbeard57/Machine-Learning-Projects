"""Streaming topic classifier shared by videos, papers and jobs.

Why one model: the crosswalk video-topic -> paper-topic -> job-topic is only
meaningful if all three are scored in the same label space.

Training is out-of-core (HashingVectorizer + SGD partial_fit), so it scales to
8M transcripts on one box:
  pass 1  papers with arXiv categories (strong labels) + keyword-seeded videos/jobs
  pass 2+ self-training: add unlabelled docs the model is confident about
"""
from __future__ import annotations

import pickle
from typing import Iterable, Iterator

import numpy as np
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.linear_model import SGDClassifier

from .corpus import batched
from .taxonomy import Taxonomy

N_FEATURES = 2 ** 18


def vectorizer() -> HashingVectorizer:
    return HashingVectorizer(
        n_features=N_FEATURES, ngram_range=(1, 2), alternate_sign=False,
        stop_words="english", norm="l2", lowercase=True,
    )


def _with_source(r: dict) -> str:
    # Source token lets the linear model absorb register differences
    # (spoken transcript vs abstract vs job ad) without a separate model each.
    return f"__src_{r['source']} " + r["text"]


class TopicClassifier:
    def __init__(self, tax: Taxonomy):
        self.tax = tax
        self.vec = vectorizer()
        self.clf = SGDClassifier(loss="log_loss", alpha=1e-6, class_weight=None, random_state=0)
        self.classes = np.arange(len(tax))
        self.fitted = False

    # ---- labelling -------------------------------------------------------
    def seed_label(self, r: dict) -> int | None:
        if r["source"] == "paper":
            y = self.tax.from_arxiv(r["meta"].get("categories"))
            if y is not None:
                return y
        return self.tax.weak_label(r["text"])

    # ---- training --------------------------------------------------------
    def _fit_batch(self, texts: list[str], ys: list[int]) -> None:
        if not texts:
            return
        X = self.vec.transform(texts)
        self.clf.partial_fit(X, np.asarray(ys), classes=self.classes)
        self.fitted = True

    def fit_stream(self, records: Iterable[dict], batch: int = 4096,
                   self_train_threshold: float | None = None) -> dict:
        """One pass. If threshold is set and the model is fitted, unlabelled docs
        predicted above it are used as pseudo-labels."""
        stats = {"seen": 0, "seed": 0, "pseudo": 0, "skipped": 0}
        for chunk in batched(iter(records), batch):
            texts, ys, unl = [], [], []
            for r in chunk:
                stats["seen"] += 1
                y = self.seed_label(r)
                if y is None:
                    unl.append(r)
                else:
                    texts.append(_with_source(r)); ys.append(y); stats["seed"] += 1
            if self_train_threshold is not None and self.fitted and unl:
                P = self.predict_proba([_with_source(r) for r in unl])
                for r, p in zip(unl, P):
                    if p.max() >= self_train_threshold:
                        texts.append(_with_source(r)); ys.append(int(p.argmax())); stats["pseudo"] += 1
                    else:
                        stats["skipped"] += 1
            else:
                stats["skipped"] += len(unl)
            self._fit_batch(texts, ys)
        return stats

    # ---- inference -------------------------------------------------------
    def predict_proba(self, texts: list[str]) -> np.ndarray:
        """texts must already carry the __src_ token (see _with_source)."""
        return self.clf.predict_proba(self.vec.transform(texts))

    def classify(self, records: Iterable[dict], batch: int = 4096, top_k: int = 3) -> Iterator[dict]:
        for chunk in batched(iter(records), batch):
            P = self.predict_proba([_with_source(r) for r in chunk])
            for r, p in zip(chunk, P):
                top = np.argsort(-p)[:top_k]
                yield {
                    "id": r["id"], "source": r["source"], "title": r["title"], "url": r["url"],
                    "topic": self.tax.ids[top[0]], "prob": round(float(p[top[0]]), 4),
                    "top": [[self.tax.ids[i], round(float(p[i]), 4)] for i in top],
                    "meta": r["meta"],
                }

    def classify_query(self, text: str, source: str = "video") -> np.ndarray:
        return self.predict_proba([f"__src_{source} {text}"])[0]

    # ---- io --------------------------------------------------------------
    def save(self, path: str) -> None:
        with open(path, "wb") as f:
            pickle.dump({"clf": self.clf, "topics": self.tax.topics}, f)

    @classmethod
    def load(cls, path: str) -> "TopicClassifier":
        with open(path, "rb") as f:
            d = pickle.load(f)
        obj = cls(Taxonomy(d["topics"]))
        obj.clf, obj.fitted = d["clf"], True
        return obj
