import torch

from rbot import cli
from rbot.bot import ResearchBot
from rbot.moe import MoEConfig, MoELM
from rbot.taxonomy import Taxonomy


def test_taxonomy_labels():
    tax = Taxonomy.load()
    assert tax.ids[tax.from_arxiv(["cs.LG", "math.ST"])] == "cs.ml_ai"
    assert tax.ids[tax.from_arxiv("stat.ML")] == "cs.ml_ai"            # longest prefix beats 'stat.'
    assert tax.ids[tax.from_arxiv(["stat.ME"])] == "math.probability_stats"
    assert tax.weak_label("the galaxy and the black hole and dark matter") == tax.index["physics.astro_cosmo"]
    assert tax.weak_label("hello world") is None


def test_moe_domain_routing_learns():
    torch.manual_seed(0)
    m = MoELM(MoEConfig(d_model=32, n_heads=2, n_layers=1, ctx=16, n_experts=4, d_ff=64, domain_coef=1.0))
    opt = torch.optim.AdamW(m.parameters(), 1e-2)
    x = torch.randint(0, 256, (8, 16)); dom = torch.tensor([0, 1, 2, 3] * 2)
    for _ in range(60):
        _, loss, _ = m(x, x, dom); opt.zero_grad(); loss.backward(); opt.step()
    _, _, routes = m(x, x, dom)
    top1 = routes[0][..., 0].mode(dim=1).values                        # dominant expert per sequence
    assert (top1 == dom).float().mean() >= 0.75


def test_end_to_end(tmp_path):
    d, w = tmp_path / "data", tmp_path / "work"
    paths = ["--videos", f"{d}/videos*", "--papers", f"{d}/papers*", "--jobs", f"{d}/jobs*", "--work", str(w)]
    cli.main(["sample", "--out", str(d), "--per-topic", "15"])
    cli.main(["train-clf", *paths, "--batch", "128"])
    cli.main(["build", *paths, "--batch", "128"])
    cli.main(["train-moe", *paths, "--steps", "3", "--d-model", "32", "--layers", "1", "--ctx", "32"])
    r = ResearchBot(str(w)).ask("black hole and gravitational wave telescope", k=3, generate=10)
    assert r["topics"][0][0] == "physics.astro_cosmo"
    assert r["expert_domain"] == "physics"
    assert r["videos"] and r["papers"] and r["jobs"]
    assert all(h["topic"].startswith("physics") for h in r["videos"])
