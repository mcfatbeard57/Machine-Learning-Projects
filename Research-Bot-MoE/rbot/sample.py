"""Synthetic shards in the real schema, for smoke tests. Not training data."""
from __future__ import annotations

import json
import random
from pathlib import Path

from .taxonomy import Taxonomy

FILLER = ("so today we look at", "the key idea is", "notice that", "which means", "in practice",
          "let us consider", "as a result", "one more example", "this connects to", "remember")
JOB_FILLER = ("we are hiring a", "the successful candidate will", "requirements include", "experience with",
              "join our lab working on", "phd in a related field", "postdoctoral position in", "apply by")


def _doc(rng, kws, filler, n):
    return " ".join(f"{rng.choice(filler)} {rng.choice(kws)}" for _ in range(n))


def _cat(prefix: str) -> str:
    return prefix + "XX" if prefix.endswith((".", "-")) else prefix


def make(out_dir: str, per_topic: int = 40, seed: int = 0) -> dict:
    rng, tax = random.Random(seed), Taxonomy.load()
    out = Path(out_dir); out.mkdir(parents=True, exist_ok=True)
    n = {"video": 0, "paper": 0, "job": 0}
    with open(out / "videos.jsonl", "w") as fv, open(out / "papers.jsonl", "w") as fp, open(out / "jobs.jsonl", "w") as fj:
        for t in tax.topics:
            kws = t["keywords"]
            for i in range(per_topic):
                # 20% of videos borrow vocabulary from a random neighbour topic -> non-trivial crosswalk
                mix = kws + (rng.choice(tax.topics)["keywords"] if rng.random() < 0.2 else [])
                fv.write(json.dumps({"video_id": f"v-{t['id']}-{i}", "title": f"Lecture {i}: {rng.choice(kws)}",
                                     "transcript": "[Music] 0:01 " + _doc(rng, mix, FILLER, 60),
                                     "url": f"https://youtube.com/watch?v=v{t['id']}{i}"}) + "\n")
                fp.write(json.dumps({"id": f"p-{t['id']}-{i}", "title": f"On {rng.choice(kws)} and {rng.choice(kws)}",
                                     "abstract": _doc(rng, kws, FILLER, 25), "categories": [_cat(t["arxiv"][0])],
                                     "url": f"https://arxiv.org/abs/{t['id']}.{i}"}) + "\n")
                fj.write(json.dumps({"id": f"j-{t['id']}-{i}", "title": f"Research Scientist, {rng.choice(kws).title()}",
                                     "description": _doc(rng, kws, JOB_FILLER, 20), "org": "Example University",
                                     "url": f"https://jobs.example.edu/{t['id']}/{i}"}) + "\n")
                n["video"] += 1; n["paper"] += 1; n["job"] += 1
    return n
