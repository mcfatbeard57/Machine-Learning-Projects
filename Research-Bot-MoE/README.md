# Research-Bot-MoE

Ask a research question. Get the matching **YouTube lectures**, **papers** and **research jobs**, routed through a **Mixture-of-Experts LM trained from scratch on the transcripts**.

```
question ─► topic classifier ─► topics ─► crosswalk ─► paper topics ─► job topics
                                   │                         │               │
                                   ▼                         ▼               ▼
                          MoE expert (domain)          paper index      job index
                          + video index
```

## Pieces

| File | What it does |
| -- | -- |
| `rbot/taxonomy.json` | One shared label space (20 topics, 9 domains). Domain = MoE expert. arXiv prefixes give papers strong labels; keywords seed weak labels for videos/jobs. |
| `rbot/corpus.py` | Streams JSONL(.gz) shards, cleans transcripts (`[Music]`, timestamps). Never loads 8M videos into RAM. |
| `rbot/classifier.py` | Out-of-core topic classifier (hashing + SGD `partial_fit`). Pass 1 = seeds, passes 2+ = self-training. Same model scores all three sources. |
| `rbot/crosswalk.py` | Video→paper→job topic map from centroid similarity (finds off-diagonal links, not just identity), plus topic-filtered retrieval index. |
| `rbot/moe.py` | Byte-level decoder, every FFN a top-2 MoE. One expert per domain; a domain-guided routing loss uses classifier labels so experts specialise by field. Load-balancing loss included. |
| `rbot/sources.py` | Fetchers: arXiv, OpenAlex, USAJobs, any RSS/Atom job feed, CSV dumps. |
| `rbot/bot.py` | The bot. Steers the router toward the question's domain at generation time. |

## Run

```bash
pip install -r requirements.txt
python -m rbot.cli sample                       # synthetic shards in data/ (smoke test only)
python -m rbot.cli train-clf                    # topic classifier
python -m rbot.cli build                        # crosswalk + index in work/index
python -m rbot.cli train-moe --steps 2000       # MoE LM on transcripts
python -m rbot.cli ask "how do eigenvalues relate to markov chains" --generate 200
python -m pytest -q tests
```

Real data:

```bash
# your transcripts: data/videos-00000.jsonl.gz ... {"video_id","title","transcript","url"}
python -m rbot.cli fetch arxiv "cat:math.*" --n 50000 --out data/papers-math.jsonl
python -m rbot.cli fetch openalex "clinical trial" --n 20000 --out data/papers-med.jsonl
USAJOBS_KEY=... USAJOBS_EMAIL=... python -m rbot.cli fetch usajobs research --out data/jobs-usa.jsonl
python -m rbot.cli fetch rss "https://feed1.xml,https://feed2.xml" --out data/jobs-rss.jsonl
```

## Reality check

- **"All research jobs" does not exist as one feed.** Coverage = sum of adapters. LinkedIn/Indeed/Glassdoor forbid scraping, so they're excluded. Add university HR feeds, EURAXESS, jobs.ac.uk etc. as RSS or CSV.
- **Training an LLM from scratch on 8M transcripts is a multi-GPU job.** Defaults here are tiny (CPU smoke test; output is gibberish until trained properly). At scale: bigger `MoEConfig`, BPE tokenizer, FSDP. A cheaper alternative that usually wins: a pretrained base + one LoRA adapter per domain, same router.
- **Retrieval** is sparse hashing — fine to a few million rows. For 8M, swap in dense embeddings + FAISS behind `Index.search`.
- **Taxonomy** is a starter. Replace with OpenAlex's ~4.5k topics for finer mapping; keep ids stable once trained.
