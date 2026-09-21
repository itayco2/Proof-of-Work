# David: master prompt

Paste this into Claude Code in an empty folder. Answer the interview, then work phase by phase.

## Goal

Build David, a fine-tune of a small open model on one narrow task that is compared, honestly,
against a frontier model on a frozen held-out set. The comparison is the product. A high score on a
set you cannot prove was clean is worth nothing, so the split comes before the training.

`Done when:` the table shows the base small model, the fine-tuned small model and at least 1 external
baseline, labelled either as a frontier API model or as a free-tier or local Goliath, on the same
held-out set of at least 1,000 examples, each with a 95% interval and a cost per 1,000 requests, and
the split and baseline prompts are in the repo.

## Interview me first

Ask me these, one message, then wait. Do not write code before I answer.

1. Path: `api` or `local`. `api` means I have a key for a frontier model and a card on file. `local`
   means no key and no spend, so the frontier baseline is the Gemini API free tier or the largest
   model Ollama runs on my machine.
2. Hardware, and how much memory it has: a rented 4090, Colab's free T4, Apple Silicon, or a local
   NVIDIA GPU. This decides the training library and the base model size.
3. The frontier baseline to beat: Opus 5, GPT-5, Gemini Pro, the Gemini free tier, or the largest
   local model. Name the exact model string you will use.
4. The task. Offer me these three, each with a hard metric and a public labelled dataset, and let me
   pick one or name my own:
   - support ticket triage, graded by accuracy over a fixed label set,
   - slot filling from natural-language requests, graded by exact match per slot, from an
     intent-and-slot corpus such as MASSIVE or SNIPS,
   - domain-specific entity extraction, graded by F1 over spans.
   Say which public dataset you would use for each and how many labelled examples it has. Every
   candidate must be plain text and hold at least 4,200 labelled rows, which is 3,000 train plus 200
   dev plus 1,000 held-out. Rule out any set of scanned images, because a 0.6B to 4B text model
   cannot read one. If my own task has no public labelled set, tell me what labelling it needs
   before we start.
5. Base model, sized to the answer to question 2: 0.6B to 4B, with the licence named.
6. The metric: accuracy, F1, or exact match. One primary metric, chosen now, never changed later.
7. My budget cap in dollars, and my time budget in days.

When I have answered, write `SPEC.md` (the task, the dataset, the metric, the target, the split
sizes), `PLAN.md` (the phases below with my answers filled in), and `CLAUDE.md` (under 200 lines:
the commands, the frozen split rule, the metric, the cost model). Then stop and let me read them.

For this project the single model-call interface below covers three callers that must go through it
unchanged: the base model, the fine-tuned model, and the frontier baseline. If the frontier baseline
and the local model reach the eval by different code paths, the comparison is not a comparison.

## Provider abstraction

Build one interface for every model call and at least two backends behind it: the API I chose in the interview, and Ollama for the local path. One switch selects the backend: the environment variable `MODEL_BACKEND` (`api` or `local`), overridden by a `--backend` flag. Model names, endpoints and prices live in one config file, never at call sites. The eval, the cost log and the latency log run unchanged on both backends, and every results table has one row per backend. On the local path, run `ollama list` before choosing a model and pick the largest model that fits the RAM I told you about; if nothing suitable is installed, tell me the `ollama pull` command and stop. Expect the local path to score lower and run slower. Say so in the README beside the numbers; never hide it.

For this project add a third backend, `mlx` (`mlx_lm.server --adapter-path <adapter>`), because the
Apple Silicon fine-tune is an mlx-lm LoRA adapter and Ollama cannot serve one without a fuse and
convert-to-GGUF step. Score the base model and the fine-tuned model through the same backend, `mlx`
on Apple Silicon and Ollama elsewhere, so both local rows share one code path. The config file also
carries the cost basis for a locally served model: one hourly rate for the hardware, dated beside the
API prices, and a cost per 1,000 requests computed from the measured requests per second at that
rate. Use $0.34 an hour for a community-cloud RTX 4090 (RunPod, September 2026) unless I give you a
rate for my own machine. On the free path the marginal cost of a local run is $0, so publish the
throughput and the p50 and p95 latency beside that figure.

## Phases

### Phase 1: skeleton

Do: write the Makefile with targets `setup`, `gate`, `test`, `data`, `baseline`, `train`, `fuse`,
`eval-dev`, `eval` and `serve`. `make setup` installs the dependencies and runs every model pull the
config names, printing each command as it runs it, so a fresh clone needs no manual pull. Write the
gate: it detects the GPU or MLX runtime and prints what it found, downloads the base model, runs one forward pass, loads the dataset, and runs the metric on a
toy case whose answer you worked out by hand. If it finds no local GPU and no MLX runtime and I named
Colab in the interview, it passes and prints that training runs on Colab; the rest of its checks run
on CPU. Write one unit test for the metric on that toy case.
Done when: `make gate` passes and the base model answers 10 examples with the metric printed.
Verify: `make gate`. Checkpoint: "skeleton".

### Phase 2: data and the frozen split

Do: load the dataset, clean it, remove exact duplicates and near duplicates across splits, then
freeze `data/split.json` with a hash per example and a hash of the whole file. Write the leakage
check as code that fails loudly, and run it as part of `make data`.
Done when: train holds at least 3,000 examples, held-out at least 1,000, the duplicate count across
splits is 0, and the leakage report is in the README.
Verify: `make data`. Checkpoint: "split frozen".

### Phase 3: baselines

Do: tune and score both prompts on the 200-example dev slice, the base model zero-shot and few-shot
and then the frontier model with the identical prompt. The held-out set stays untouched until Phase
5. Count the tokens you actually sent and received, and turn them into a cost per 1,000 requests
using the dated prices in the config file, or its hourly rate for a row served locally. A baseline
prompt you tuned for the small model and not for the frontier model is a rigged comparison, so write
both prompts into the repo and spend equal effort on each. Before the first call to any rate-limited
API, work out the request budget: the held-out size times the number of passes it will take, against
that tier's current requests-per-day limit, which for a free tier you read in AI Studio rather than
assume. If it does not fit, chunk the pass across days or fall back to the Ollama baseline, and tell
me which you chose. Done when: the dev baseline table has at least 3 rows, each with the metric and
the cost per 1,000 requests. Verify: `make baseline`. Checkpoint: "baselines".

### Phase 4: fine-tune

Do: QLoRA, with Unsloth or TRL on NVIDIA and `mlx-lm` on Apple Silicon. Run a 200-step smoke run
first and check the loss falls, then the full run. Write a training log with the loss per step, the
hyperparameters, and the wall-clock time. Evaluate on the 200-example dev slice only, never on the
held-out set. On Colab's free T4, where `make train` cannot run, commit the notebook, download the
adapter into `adapters/`, and have `make train` check that adapter's presence and hash instead of
training. That download is a LoRA adapter, which Ollama will not load as it stands, so merge it into
the base weights, convert the merged weights to GGUF with llama.cpp's converter, and `ollama create`
from a Modelfile. That is what `make fuse` does, and on the `mlx` path it prints that there is
nothing to convert. Name in `cost.md` the backend that scored each local row. Done when: the fine-tuned model beats the base model by at least 10 points on the
200-example dev slice, or the dev ceiling you measured is written into `PREFLIGHT.md` and I have told
you to carry that result into the comparison. Verify: `make train && make fuse && make eval-dev`. Checkpoint:
"fine-tuned".

### Phase 5: the comparison

Do: run the base model, the fine-tuned model and the frontier model over the full held-out set in one
pass, so every row of the final table scores the same examples. Compute 95% bootstrap intervals for
every row. Pull 50 misses, read them, and group them into named failure classes with counts. Measure
the fine-tuned model's throughput served locally, in requests per second on named hardware, convert
it at the config's hourly rate, and put that cost per 1,000 requests beside the API's.
Done when: the table carries a 95% interval on every row and the README says in 1 sentence whether
David won, lost or tied.
Verify: `make eval`. Checkpoint: "compared".

### Phase 6: credibility

Do: build the credibility layer below, and a serving demo, a CLI or a single page that hits the
local model and returns an answer. Record it. Done when: the README's first 200 words carry both
scores and the cost ratio, and the recording is linked from the README. Verify: every step of the
Final verification block below, in order, from a fresh clone. Checkpoint: tag `v1.0`.

## Credibility layer

These are phases, not extras. The build is not done until every one of them exists:

- `eval/`: the eval set, a runner, and the metric code, with a unit test for each metric on a toy case where the answer is known by hand.
- The eval table in the README: one row per configuration and per backend, every metric, and the date it was produced.
- `cost.md`: cost and latency per unit of work, p50 and p95, per backend, with the token counts and the dated prices they came from.
- `PREFLIGHT.md`: every defect found on the way, one row each, as *what was wrong, the number that showed it, the fix, the number after*. A build with an empty PREFLIGHT.md did not look hard enough.
- The README: the headline number in its first 200 words, the command that reproduces it, and one sentence on what the number does not prove.
- A 30 to 60 second screen recording of the thing working, linked from the README.

## Out of scope

Full fine-tuning of all weights. Base models above 9B parameters. RLHF and DPO. Vision-language
models, and any dataset whose input is a scanned image rather than text. Any task whose
metric needs a language model as the judge, because then the grader is the thing under test. Serving
at scale, load balancing and autoscaling. More than one task: a second task doubles the work and
adds nothing a reader will check.

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
4. `git log` shows one commit per checkpoint. `.env` never entered the history: `git log --all -- .env` prints nothing. No key was pasted into code either: `git log -p -- . ':!.env.example' | grep -E 'sk-(ant|proj|svcacct)-|sk-[A-Za-z0-9]{40,}|AIza[0-9A-Za-z_-]{35}'` finds nothing. Neither check trips on the empty key names in `.env.example`, or on code that reads a key from the environment.
5. Tell me the three numbers I should say first in an interview about this project, and where each one came from.
