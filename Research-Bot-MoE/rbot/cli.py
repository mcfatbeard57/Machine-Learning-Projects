"""python -m rbot.cli <command> ...  (run from Research-Bot-MoE/)"""
from __future__ import annotations

import argparse
import itertools
import json
import os
from pathlib import Path

from . import corpus, sources


def _all(a):
    """Interleave the three corpora so every SGD batch sees every source."""
    its = [corpus.read(a.videos, "video"), corpus.read(a.papers, "paper"), corpus.read(a.jobs, "job")]
    for group in itertools.zip_longest(*its):
        yield from (r for r in group if r is not None)


def cmd_sample(a):
    from .sample import make
    print(make(a.out, a.per_topic))


def cmd_fetch(a):
    if a.kind == "arxiv":
        recs = sources.arxiv(a.query, a.n)
    elif a.kind == "openalex":
        recs = sources.openalex(a.query, a.n, mailto=os.environ.get("OPENALEX_MAILTO"))
    elif a.kind == "rss":
        recs = itertools.chain.from_iterable(sources.rss(u) for u in a.query.split(","))
    elif a.kind == "usajobs":
        recs = sources.usajobs(a.query, os.environ["USAJOBS_KEY"], os.environ["USAJOBS_EMAIL"])
    else:
        recs = sources.csv_jobs(a.query)
    print(f"wrote {sources.write_jsonl(recs, a.out)} -> {a.out}")


def cmd_train_clf(a):
    from .classifier import TopicClassifier
    from .taxonomy import Taxonomy
    clf = TopicClassifier(Taxonomy.load(a.taxonomy) if a.taxonomy else Taxonomy.load())
    print("pass 1 (seeds):", clf.fit_stream(_all(a), a.batch))
    for i in range(a.self_train):
        print(f"pass {i + 2} (self-train @{a.threshold}):", clf.fit_stream(_all(a), a.batch, a.threshold))
    Path(a.work).mkdir(parents=True, exist_ok=True)
    clf.save(f"{a.work}/classifier.pkl")


def cmd_build(a):
    from .classifier import TopicClassifier
    from .crosswalk import build
    clf = TopicClassifier.load(f"{a.work}/classifier.pkl")
    walk = build(clf, _all(a), f"{a.work}/index", a.batch)
    print(json.dumps(walk["counts"], indent=1))


def cmd_train_moe(a):
    import torch
    from .moe import MoEConfig, MoELM, doc_stream, train
    from .taxonomy import Taxonomy
    torch.manual_seed(0)
    tax = Taxonomy.load()
    labels = {}
    meta = Path(f"{a.work}/index/video_meta.jsonl")
    if meta.exists():                                # domain labels from the classifier
        for l in open(meta):
            m = json.loads(l)
            labels[m["id"]] = tax.topic_domain[tax.index[m["topic"]]]
    cfg = MoEConfig(n_experts=max(len(tax.domains), a.experts), d_model=a.d_model, n_layers=a.layers, ctx=a.ctx)
    model = MoELM(cfg)
    print(f"{sum(p.numel() for p in model.parameters()) / 1e6:.1f}M params, {cfg.n_experts} experts, "
          f"{len(labels)} domain-labelled videos")

    def windows():
        while True:                                  # epochs over the shards
            yield from doc_stream(corpus.read(a.videos, "video"), labels, cfg.ctx)

    train(model, windows(), a.steps, a.batch, a.lr)
    torch.save({"config": model.config_dict(), "state": model.state_dict()}, f"{a.work}/moe.pt")


def cmd_ask(a):
    from .bot import ResearchBot, render, to_json
    bot = ResearchBot(a.work)
    qs = [a.question] if a.question else iter(lambda: input("research> "), "")
    for q in qs:
        r = bot.ask(q, a.k, a.generate)
        print(to_json(r) if a.json else render(r), "\n")


def main(argv=None):
    p = argparse.ArgumentParser(prog="rbot")
    sub = p.add_subparsers(dest="cmd", required=True)

    def data_args(s):
        s.add_argument("--videos", default="data/videos*.jsonl*")
        s.add_argument("--papers", default="data/papers*.jsonl*")
        s.add_argument("--jobs", default="data/jobs*.jsonl*")
        s.add_argument("--work", default="work")
        s.add_argument("--batch", type=int, default=4096)

    s = sub.add_parser("sample"); s.add_argument("--out", default="data"); s.add_argument("--per-topic", type=int, default=40)
    s.set_defaults(f=cmd_sample)

    s = sub.add_parser("fetch")
    s.add_argument("kind", choices=["arxiv", "openalex", "rss", "usajobs", "csv"])
    s.add_argument("query", help="arxiv/openalex query, comma-separated feed URLs, usajobs keyword, or csv path")
    s.add_argument("--n", type=int, default=1000); s.add_argument("--out", required=True)
    s.set_defaults(f=cmd_fetch)

    s = sub.add_parser("train-clf"); data_args(s)
    s.add_argument("--self-train", type=int, default=2); s.add_argument("--threshold", type=float, default=0.8)
    s.add_argument("--taxonomy"); s.set_defaults(f=cmd_train_clf)

    s = sub.add_parser("build"); data_args(s); s.set_defaults(f=cmd_build)

    s = sub.add_parser("train-moe"); data_args(s)
    s.set_defaults(batch=16)
    s.add_argument("--steps", type=int, default=200); s.add_argument("--lr", type=float, default=3e-4)
    s.add_argument("--d-model", type=int, default=256); s.add_argument("--layers", type=int, default=4)
    s.add_argument("--ctx", type=int, default=256); s.add_argument("--experts", type=int, default=0)
    s.set_defaults(f=cmd_train_moe)

    s = sub.add_parser("ask"); s.add_argument("question", nargs="?"); s.add_argument("--work", default="work")
    s.add_argument("-k", type=int, default=5); s.add_argument("--generate", type=int, default=0)
    s.add_argument("--json", action="store_true"); s.set_defaults(f=cmd_ask)

    a = p.parse_args(argv)
    a.f(a)


if __name__ == "__main__":
    main()
