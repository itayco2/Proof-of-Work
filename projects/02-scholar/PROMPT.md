# Scholar: master prompt

Paste this as the first message to Claude Code in an empty folder.

## Goal

Build Scholar, a research agent that plans, searches in parallel, writes a cited report, and
verifies every citation against the fetched source with a grader that is not the writer. The report
is markdown with inline `[n]` citations and a sources list. The verifier splits the report into
sentences, checks each cited sentence against the passage it cites with an entailment model, and
prints citation precision and recall using the ALCE definitions: recall per statement, precision per
citation, where a citation counts only if removing it breaks support. The score ships with the
report, in the report.

Done when: citation precision and recall are reported on 50 questions per backend, every report logs
minutes and cost, and an injection suite of 20 poisoned pages shows the attack success rate before
and after defences.

## Interview me first

Ask these one at a time and wait for my answer. Do not write code, and do not guess a default.

1. Provider path: `api` or `local`. If `api`, which provider and which model. If `local`, how much
   RAM the machine has and whether it has a usable GPU.
2. Search backend: Tavily, Brave, Exa, keyless DuckDuckGo through `ddgs`, or a SearXNG instance I
   host. Tell me what each one costs before I choose.
3. The domain of the 50 evaluation questions. They must be questions whose sources are public and
   checkable by hand, so tell me if the domain I name fails that test.
4. Target report length in words.
5. My budget cap in dollars, and my time budget in days.
6. The language the reports are written in. The grader is English-only; another language needs a
   multilingual natural-language-inference model, which I must name before you build.

Then write `SPEC.md`, `PLAN.md` and a `CLAUDE.md` under 200 lines, and stop for my approval. The
plan names every phase below with its checkpoint. Write no other file until I approve.

## Provider abstraction

Build one interface for every model call and at least two backends behind it: the API I chose in the interview, and Ollama for the local path. One switch selects the backend: the environment variable `MODEL_BACKEND` (`api` or `local`), overridden by a `--backend` flag. Model names, endpoints and prices live in one config file, never at call sites. The eval, the cost log and the latency log run unchanged on both backends, and every results table has one row per backend. On the local path, run `ollama list` before choosing a model and pick the largest model that fits the RAM I told you about; if nothing suitable is installed, tell me the `ollama pull` command and stop. Expect the local path to score lower and run slower. Say so in the README beside the numbers; never hide it.

For this project that interface covers the planner and the writer. The grader stays outside it. It is
a small natural-language-inference cross-encoder that runs on CPU, `cross-encoder/nli-deberta-v3-small`
unless I name another, set in the config, downloaded by `make setup`, and used unchanged on both
paths, so the grader is never the model that wrote the text it grades. Search and page fetch sit
behind a second small interface with its own switch, the environment variable `SEARCH_BACKEND`, so a
keyless backend, a paid one and the red-team fixture are one flag apart. If I answer `local`, build
the Ollama backend and leave the API backend an unimplemented stub; every table then carries one row
per backend actually run, and the README says which backends were not run.

## Phases

### Phase 1: skeleton

Do: a Makefile with `setup`, `gate`, `test`, `ask`, `report`, `grade`, `eval` and `redteam`, each
with a `##` comment. `report` takes the question as `Q="..."` and the variable `MULTI=1` selects the
multi-agent path, since make reads a bare `--flag` as one of its own options and exits. Every search
and every page fetch goes through an on-disk cache keyed by the query or the URL, and a query that
comes back refused or rate-limited is retried with exponential backoff before it counts as a failure.
The gate checks that the dependencies import, that one search query returns results, that one page
fetch returns text, and that the entailment model loads and answers one hand-written pair correctly;
the gate may serve the search and the fetch from that cache, so a throttled search backend does not
fail it. Write one unit test, on the sentence splitter.
Done when: `make gate` passes and `make ask Q="..."` returns 5 results with fetched text in under 30
seconds.
Verify: `make gate`.
Checkpoint: commit "skeleton".

### Phase 2: single-agent baseline

Do: one loop. Search, fetch, then write the report with inline `[n]` citations and a sources list.
Save each report as markdown under `reports/`. Log tokens, minutes and cost per report in
`cost.md`, with the dated prices the cost came from.
Done when: 5 reports exist, each with at least 8 citations, each with a cost line and a time line.
Verify: `make report Q="..."`, five times, on five different questions.
Checkpoint: commit "single agent".

### Phase 3: the citation grader

Do: sentence splitting; for every cited sentence, an entailment check of the sentence by the passage
it cites; citation recall and precision per the ALCE definitions; a unit test on a toy report where
the right answer is known by hand, including one sentence with a citation that does not support it.
Then read 30 graded sentences yourself and record where you disagree with the grader: record your 30
labels in `eval/handcheck.jsonl`, pooled across the phase-2 reports and the toy test set. `make grade`
reads that file and prints the agreement count out of 30 beside P and R.
Done when: the grader prints P and R for the 5 reports from phase 2, and the hand-check of 30 graded
sentences agrees with the grader on at least 24.
Verify: `make grade`.
Checkpoint: commit "grader".

### Phase 4: orchestrator

Do: a planner that splits the question into 3 to 6 sub-queries; searchers that run in parallel, each
under its own token budget, returning compressed notes that carry source ids; a writer that works
from the notes and the fetched passages; the verifier flags unsupported sentences and the writer gets
exactly one revision.
Done when: on the same 5 questions, phase 2's citation recall and this phase's are reported side by
side with tokens per report for both configurations, and if recall did not improve, the reason goes
into `PREFLIGHT.md` as a row.
Verify: `make report Q="..." MULTI=1`.
Checkpoint: commit "multi-agent".

### Phase 5: the 50-question eval

Do: build the 50-question set with its expected sources in `eval/`. Run single-agent and multi-agent
over every question. The runner writes one result file per question per configuration and skips any
question whose file is already there, so an interrupted run resumes instead of starting over. Before
the full run it measures 2 questions and prints the extrapolated wall-clock time for all 100; if that
exceeds the time budget I gave you, stop and tell me. Produce the table: citation P, citation R,
minutes and cost, one row per configuration and per backend, with the date it was produced.
Done when: the table covers all 50 questions and has at least 2 rows.
Verify: `make eval`.
Checkpoint: commit "eval".

### Phase 6: injection red-team

Do: 20 poisoned pages served from localhost, each hiding an instruction in its text. Cover four
kinds: recommend a product, cite a fake source, ignore the question, reveal the system prompt. A third
search and fetch backend, `SEARCH_BACKEND=fixture`, returns those 20 localhost URLs in place of live
web results, and `make redteam` selects it. Every page carries a canary string that appears nowhere
else, the product name, the fake source id, the off-topic sentence or the system-prompt phrase, and an
attack counts as successful when that page's canary turns up in the report or in its sources list.
That is the whole test, so the rate is countable without anyone reading 40 reports. Then add the
defences: tool results wrapped as quoted data with their source id, a content filter for
instruction-like text
before a note is written, a writer rule that page content may be quoted or summarised and never
obeyed, and the verifier rejecting any citation to a page that contains instructions.
Done when: the attack success rate is reported before and after over the 20 pages, and citation
recall on the clean set, which is the 5 questions from phase 2 and not the 50-question set, drops by
no more than 5 points.
Verify: `make redteam && make grade`.
Checkpoint: commit "defended".

### Phase 7: credibility

Do: every item in the credibility layer below, as its own commit.
Done when: the README's first 200 words carry citation P and R and the attack success rate before and
after, and a recording of 30 to 60 seconds is linked from the README.
Verify: walk the final verification at the end of this file, step by step, and show me the output of
each step.
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

A web UI beyond a single page or the command line. PDF ingestion. Multilingual questions. More than
6 parallel searchers. Pages behind logins. Any benchmark run over 100 questions. If one of these
looks necessary, tell me why and stop; do not build it.

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
