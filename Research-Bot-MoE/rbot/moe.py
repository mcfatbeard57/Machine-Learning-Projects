"""Mixture-of-Experts language model trained from scratch on transcripts.

- Decoder-only transformer, byte-level vocab (256) so there is no tokenizer to train.
- Every FFN is a sparse MoE layer, top-k routing (Switch/Mixtral style).
- One expert per taxonomy *domain*. The topic classifier's label for each
  transcript gives a domain, and an auxiliary loss nudges the router to send
  that document's tokens to that domain's expert. Experts therefore specialise
  by field (maths, physics, ...) instead of by arbitrary token statistics.
- Standard load-balancing loss keeps any expert from starving.

Defaults are tiny so the smoke test runs on CPU. For 8M videos, scale d_model,
layers and context and run under FSDP/DeepSpeed; the module does not change.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, asdict

import torch
import torch.nn as nn
import torch.nn.functional as F


@dataclass
class MoEConfig:
    vocab: int = 256
    d_model: int = 256
    n_heads: int = 4
    n_layers: int = 4
    ctx: int = 256
    n_experts: int = 8
    top_k: int = 2
    d_ff: int = 512
    dropout: float = 0.0
    lb_coef: float = 0.01        # load-balancing loss weight
    domain_coef: float = 0.1     # domain-guided routing loss weight


class Expert(nn.Module):
    def __init__(self, c: MoEConfig):
        super().__init__()
        self.w1 = nn.Linear(c.d_model, c.d_ff, bias=False)
        self.w3 = nn.Linear(c.d_model, c.d_ff, bias=False)
        self.w2 = nn.Linear(c.d_ff, c.d_model, bias=False)

    def forward(self, x):                      # SwiGLU
        return self.w2(F.silu(self.w1(x)) * self.w3(x))


class MoELayer(nn.Module):
    def __init__(self, c: MoEConfig):
        super().__init__()
        self.c = c
        self.router = nn.Linear(c.d_model, c.n_experts, bias=False)
        self.experts = nn.ModuleList(Expert(c) for _ in range(c.n_experts))

    def forward(self, x, domain=None, expert_bias=None):
        B, T, D = x.shape
        logits = self.router(x)                                      # B,T,E
        if expert_bias is not None:                                  # inference-time steering
            logits = logits + expert_bias.view(1, 1, -1)
        probs = logits.softmax(-1)
        w, idx = probs.topk(self.c.top_k, dim=-1)                    # B,T,k
        w = w / w.sum(-1, keepdim=True)

        flat_x, flat_idx, flat_w = x.reshape(-1, D), idx.reshape(-1, self.c.top_k), w.reshape(-1, self.c.top_k)
        out = torch.zeros_like(flat_x)
        for e, expert in enumerate(self.experts):
            tok, slot = (flat_idx == e).nonzero(as_tuple=True)
            if tok.numel():
                out.index_add_(0, tok, expert(flat_x[tok]) * flat_w[tok, slot].unsqueeze(-1))

        # Switch load-balancing: E * sum_e frac_tokens_e * mean_prob_e
        E = self.c.n_experts
        frac = F.one_hot(idx[..., 0], E).float().mean((0, 1))
        aux = E * (frac * probs.mean((0, 1))).sum() * self.c.lb_coef
        if domain is not None:                                       # -1 = unknown domain
            known = domain >= 0
            if known.any():
                seq_probs = probs.mean(1)[known]                     # B',E
                aux = aux + F.nll_loss(seq_probs.clamp_min(1e-9).log(), domain[known]) * self.c.domain_coef
        return out.view(B, T, D), aux, idx


class Block(nn.Module):
    def __init__(self, c: MoEConfig):
        super().__init__()
        self.n1, self.n2 = nn.RMSNorm(c.d_model), nn.RMSNorm(c.d_model)
        self.attn = nn.MultiheadAttention(c.d_model, c.n_heads, dropout=c.dropout, batch_first=True)
        self.moe = MoELayer(c)

    def forward(self, x, mask, domain=None, expert_bias=None):
        h = self.n1(x)
        a, _ = self.attn(h, h, h, attn_mask=mask, need_weights=False)
        x = x + a
        m, aux, idx = self.moe(self.n2(x), domain, expert_bias)
        return x + m, aux, idx


class MoELM(nn.Module):
    def __init__(self, c: MoEConfig):
        super().__init__()
        self.c = c
        self.tok = nn.Embedding(c.vocab, c.d_model)
        self.pos = nn.Embedding(c.ctx, c.d_model)
        self.blocks = nn.ModuleList(Block(c) for _ in range(c.n_layers))
        self.norm = nn.RMSNorm(c.d_model)
        self.head = nn.Linear(c.d_model, c.vocab, bias=False)
        self.head.weight = self.tok.weight
        self.apply(self._init)

    @staticmethod
    def _init(m):
        if isinstance(m, (nn.Linear, nn.Embedding)):
            nn.init.normal_(m.weight, std=0.02)

    def forward(self, x, y=None, domain=None, expert_bias=None):
        B, T = x.shape
        h = self.tok(x) + self.pos(torch.arange(T, device=x.device))
        mask = torch.triu(torch.full((T, T), float("-inf"), device=x.device), 1)
        aux_total, routes = 0.0, []
        for b in self.blocks:
            h, aux, idx = b(h, mask, domain, expert_bias)
            aux_total = aux_total + aux
            routes.append(idx)
        logits = self.head(self.norm(h))
        loss = None
        if y is not None:
            lm = F.cross_entropy(logits.view(-1, self.c.vocab), y.view(-1))
            loss = lm + aux_total
            self.last_lm_loss = lm.detach()
        return logits, loss, routes

    @torch.no_grad()
    def generate(self, prompt: str, n: int = 200, temperature: float = 0.8, expert_bias=None) -> str:
        self.eval()
        ids = torch.tensor([list(prompt.encode("utf-8", "ignore"))[-self.c.ctx:]], dtype=torch.long)
        for _ in range(n):
            logits, _, _ = self(ids[:, -self.c.ctx:], expert_bias=expert_bias)
            p = (logits[0, -1] / max(temperature, 1e-5)).softmax(-1)
            ids = torch.cat([ids, torch.multinomial(p, 1).view(1, 1)], 1)
        return bytes(ids[0, -n:].tolist()).decode("utf-8", "ignore")

    def config_dict(self) -> dict:
        return asdict(self.c)


# ---------------------------------------------------------------- training
def doc_stream(records, labels: dict[str, int], ctx: int):
    """Yield (x, y, domain) windows. labels: record id -> domain index."""
    for r in records:
        b = r["text"].encode("utf-8", "ignore")
        dom = labels.get(r["id"], -1)
        for s in range(0, max(len(b) - ctx - 1, 0) + 1, ctx):
            w = b[s:s + ctx + 1]
            if len(w) == ctx + 1:
                t = torch.tensor(list(w), dtype=torch.long)
                yield t[:-1], t[1:], dom


def train(model: MoELM, windows, steps: int, batch: int = 16, lr: float = 3e-4, log_every: int = 20, log=print):
    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=0.1, betas=(0.9, 0.95))
    sched = torch.optim.lr_scheduler.LambdaLR(
        opt, lambda s: min(1.0, (s + 1) / 50) * 0.5 * (1 + math.cos(math.pi * min(s / max(steps, 1), 1.0))))
    model.train()
    it, step = iter(windows), 0
    while step < steps:
        xs, ys, ds = [], [], []
        for _ in range(batch):
            try:
                x, y, d = next(it)
            except StopIteration:
                return step
            xs.append(x); ys.append(y); ds.append(d)
        _, loss, _ = model(torch.stack(xs), torch.stack(ys), torch.tensor(ds))
        opt.zero_grad(set_to_none=True)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        opt.step(); sched.step(); step += 1
        if step % log_every == 0:
            log(f"step {step} loss {loss.item():.3f} lm {model.last_lm_loss.item():.3f}")
    return step
