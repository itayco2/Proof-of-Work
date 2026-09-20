# Librarian: master prompt

Paste this into Claude Code in an empty repository. Answer the interview, approve the plan, then work
one phase at a time.

## Goal

Build Librarian, a retrieval system over about one million chunks of real text with a search page,
where every retrieval step is measured on a labelled question set.

Done when: recall@10 and nDCG@10 are reported on at least 200 labelled questions for four
configurations (BM25, dense, hybrid, hybrid plus rerank), p95 latency is under 500 ms on the final
configuration at 1,000,000 chunks, and a cost per query is logged for each backend.

On the local path there is no API key, so the cost and latency logs cover the local backend only and
the API row of every results table reads `not run (no key)` instead of an estimate. The 500 ms gate
splits there too: retrieval p95 under 500 ms, with the cross-encoder step timed and reported on its
own line. A whole reranked configuration under 500 ms is the API or GPU path, not the CPU one.

Nothing in this build is finished by describing it. Each phase ends with a command I can run and a
number it prints.

## Interview me first

Ask me these one at a time, in this order, and stop after the last one:

1. Which provider path: `api` or `local`? If `api`, which provider?
2. How much RAM and free disk do I have, and is there a GPU?
3. Which corpus: a Wikipedia subset, arXiv abstracts, CourtListener opinions, Project Gutenberg, or
   my own text?
4. Confirm the first target size of 100,000 chunks and the final size of 1,000,000, or give me
   different ones.
5. Where does it run: localhost only, Fly, Railway, or Hugging Face Spaces?
6. What is the budget cap in dollars?
7. What is the time budget in weeks?
8. What language is the UI in?

Then write three files and stop for my approval before any other code: `SPEC.md` with the files and
interfaces this build needs and what is out of scope, `PLAN.md` with the phases below turned into
checkable steps, and a `CLAUDE.md` under 200 lines holding the commands, the gate and the rules I
cannot derive from reading the code.

The provider interface here covers three kinds of model call: embedding a chunk or a query, scoring a
query and candidate pair with a reranker, and the single generation call over the top results.

## Provider abstraction

Build one interface for every model call and at least two backends behind it: the API I chose in the interview, and Ollama for the local path. One switch selects the backend: the environment variable `MODEL_BACKEND` (`api` or `local`), overridden by a `--backend` flag. Model names, endpoints and prices live in one config file, never at call sites. The eval, the cost log and the latency log run unchanged on both backends, and every results table has one row per backend. On the local path, run `ollama list` before choosing a model and pick the largest model that fits the RAM I told you about; if nothing suitable is installed, tell me the `ollama pull` command and stop. Expect the local path to score lower and run slower. Say so in the README beside the numbers; never hide it.

## Phases

Seven phases. One commit per checkpoint, and no phase starts before the previous one is committed.

### Phase 1: skeleton

Do: write a `Makefile` with the targets `setup`, `gate`, `test`, `ingest`, `index`, `eval`, `bench`
and `serve`. Write `scripts/gate.py` that checks the Python version, checks that `sqlite3` can load
extensions and names the fix when it cannot, imports every dependency, opens the database, loads the
embedding model, builds a 10-document smoke index in a temporary directory and answers one query from
it. Add one unit test so `make test` has something to run.

sqlite-vec is a loadable extension, and the python3 that ships with macOS is built without extension
loading, so on that interpreter `sqlite3.Connection` has no `enable_load_extension` method at all. The
gate looks for that method before anything else reaches the vector store, and when it is missing it
tells me to rebuild the venv from a python.org or Homebrew interpreter instead of failing later inside
`make index`.

Done when: `make gate` passes on a clean checkout, the 10-document smoke index answers 1 query in
under 1 second, and the gate's output names the extension-loading check.

Verify: `make gate`.

Checkpoint: commit "skeleton".

### Phase 2: ingest 100k

Do: download and parse the corpus I chose. Chunk it to about 300 tokens, with the document title
prepended to every chunk, and store the chunk text, its source id and its position in the document.
Add `make stats`, which prints the chunk count, the number of empty chunks and a length histogram. If
the raw corpus does not fit the free disk I named, stream it or take a slice, and say which in the
README.

Done when: 100,000 chunks are stored, 0 are empty, and the chunk-length histogram is in the README.

Verify: `make ingest N=100000 && make stats`.

Checkpoint: commit "100k chunks".

### Phase 3: two retrievers and fusion

Do: build BM25 over the chunks with SQLite FTS5 or Postgres full-text search, and dense retrieval
with bge-small locally or the API embeddings. Make `make index` build both indexes over whatever is
already ingested, and print how long each took. Fuse the two ranked lists with reciprocal rank
fusion. Make `make bench` sample queries and print the median and p95 for each retriever and for the
fusion.

Done when: each retriever returns 10 results for 100 sampled queries, with a median under 200 ms at
100,000 chunks.

Verify: `make index && make bench`.

Checkpoint: commit "hybrid".

### Phase 4: the labelled set and the first table

Do: generate two questions per sampled chunk with the model. Add a `review` command that shows each
question beside the chunk it came from and records my accept or reject, and store the accepted pairs
as JSONL with the chunk id as the correct answer. Implement recall@k and nDCG@k, each with a unit
test on a toy case whose value I can check by hand.

Done when: 200 accepted questions exist, the metric unit tests pass, and the eval table has 3 rows
(BM25, dense, hybrid).

Verify: `make eval`.

Checkpoint: commit "eval set and first table".

### Phase 5: reranker

Do: run a cross-encoder over the top 20 fused results and cut to 10. Raise on NaN scores instead of
sorting them. Tune the shortlist size on the eval set and record every size you tried with the metric
it produced. Extend `make bench` to time the reranked configuration end to end as its own row, and
record p50 and p95 of that final configuration at 100,000 chunks before Phase 6 grows the corpus.

Done when: the eval table has 4 rows and the rerank row differs from the hybrid row on at least 1
metric.

Verify: `make eval`.

Checkpoint: commit "rerank".

### Phase 6: scale and serve

Do: ingest and index the full corpus. Build a single-page search UI with a query box, the top results
showing source and score, the latency of that query, and the eval table with the date each row was
produced. Measure p50 and p95 over 200 queries. Log the cost per query for each backend.

Done when: 1,000,000 chunks are indexed, the page serves at localhost, and p95 is under 500 ms on the
final configuration on the API path, or under 500 ms for retrieval with the rerank step timed on its
own line on the local path.

Verify: `make serve` in one terminal and `make bench` in another.

Checkpoint: commit "1M and serving".

### Phase 7: credibility and hosting

Do: everything in the credibility layer below. If I chose hosting, deploy there and put the live URL
in the README.

Done when: the README states the headline number in its first 200 words and links a recording of at
least 30 seconds.

Verify: every step of the final verification below.

Checkpoint: tag `v1.0`.

## Credibility layer

These are phases, not extras. The build is not done until every one of them exists:

- `eval/`: the eval set, a runner, and the metric code, with a unit test for each metric on a toy case where the answer is known by hand.
- The eval table in the README: one row per configuration and per backend, every metric, and the date it was produced.
- `cost.md`: cost and latency per unit of work, p50 and p95, per backend, with the token counts and the dated prices they came from.
- `PREFLIGHT.md`: every defect found on the way, one row each, as *what was wrong, the number that showed it, the fix, the number after*. A build with an empty PREFLIGHT.md did not look hard enough.
- The README: the headline number in its first 200 words, the command that reproduces it, and one sentence on what the number does not prove.
- A 30 to 60 second screen recording of the thing working, linked from the README.

## Out of scope

Answer synthesis beyond one model call over the top results. Multilingual corpora. A chat interface.
Accounts or authentication. More than a million chunks. Anything that needs a GPU. If you think one
of these is needed to hit the goal, say so and stop rather than building it.

## Rules

- No number goes into the README without the command that reproduces it, named beside the number.
- Keys live in `.env`, loaded at startup and listed in `.env.example` with empty values. `.env` is in `.gitignore` from the first commit. Never print a key.
- Before any run that could cost more than a tenth of my budget, stop and tell me the estimate.
- Score on a frozen public set where one exists. Grade with something that is not the model being graded. Publish the split and the baseline prompts.
- Never fake, estimate or extrapolate a result. If a run fails, the failure and its number go into `PREFLIGHT.md`.
- Keep every phase green before starting the next: `make gate` passes and the phase's checkpoint is committed.
- If a phase fails twice in a row, stop, write down what was learned, and ask me before a third attempt.
- Prefer the thinnest dependency that does the job. No framework whose only role is to hide a loop you could write in fifty lines.
- One commit per checkpoint, with a plain message that names the number it produced.

## Final verification

1. Clone the repo fresh into a new folder. `make setup && make gate` passes with no manual step beyond copying `.env.example` to `.env`.
2. One end-to-end run produces the headline number, and the README shows that same number next to the command that produced it.
3. Every claim in the README has its reproduction command, every row in the eval table has a date, and `PREFLIGHT.md` has at least one row.
4. `git log` shows one commit per checkpoint, and `git log -p | grep -i "sk-\|api_key="` finds nothing.
5. Tell me the three numbers I should say first in an interview about this project, and where each one came from.
