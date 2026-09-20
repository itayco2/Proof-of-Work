# Fixer: master prompt

Paste this into a coding agent in an empty repository. Work one phase at a time and stop at every
checkpoint.

## Goal

Build Fixer, a coding agent that takes a GitHub issue, reproduces it in a container, patches, runs
the tests and opens a pull request, scored on SWE-bench Verified-mini.

Done when: the resolved rate on all 50 Verified-mini instances is reported per backend with a 95%
interval and a cost per instance, and 1 real issue on a repo of mine is fixed end to end with a
recording.

## Interview me first

Ask me all of this in one message, numbered, and wait for my answers before writing any code.

1. Path: `api` or `local`.
2. Machine: whether Docker is installed and running, free disk in GB, RAM in GB.
3. Scaffold: fork mini-SWE-agent's loop, or write your own with the same single bash tool.
4. The model or models, one per backend. On the local path, name two Ollama models of different
   size: those are the two backends, and an API backend is an addition for when a key exists.
5. Grading: the benchmark's free cloud grader, or local Docker images. For the cloud grader, confirm
   you hold its key, which `sb-cli gen-api-key <email>` sends to that address.
6. Budget cap in dollars.
7. Time budget per week.
8. A repository of mine with an open issue, for the live demo in Phase 6: whether `gh` is
   authenticated there or a token with repo scope sits in `.env`, and the commands that install its
   dependencies and run its tests.

Tell me when my answers conflict with each other, for example the local path on 8 GB of RAM, or
local grading of the full set on 20 GB of free disk, and say what you recommend instead.

Then write three files and stop for my approval: `SPEC.md` (what it does, the 50 instances, the
metric, the two backends), `PLAN.md` (the phases below with my answers filled in and the caps set to
numbers) and a `CLAUDE.md` under 200 lines holding the commands, the caps, the repository layout and
one line per mistake worth not repeating.

## Provider abstraction

Build one interface for every model call and at least two backends behind it: the API I chose in the interview, and Ollama for the local path. One switch selects the backend: the environment variable `MODEL_BACKEND` (`api` or `local`), overridden by a `--backend` flag. Model names, endpoints and prices live in one config file, never at call sites. The eval, the cost log and the latency log run unchanged on both backends, and every results table has one row per backend. On the local path, run `ollama list` before choosing a model and pick the largest model that fits the RAM I told you about; if nothing suitable is installed, tell me the `ollama pull` command and stop. Expect the local path to score lower and run slower. Say so in the README beside the numbers; never hide it.

## Phases

A phase ends at its checkpoint commit. Nothing from the next phase starts before that commit exists.

Before any run of N instances, multiply the minutes one instance took in Phase 1 by N, divided by
the number of workers. If that total is more than a tenth of my weekly time budget, stop and tell me
the estimate before starting. On the local path this is the cap that binds, because the dollars are
zero.

### Phase 1: skeleton

Do: write the Makefile with the targets setup, gate, test, run, grade, taxonomy and demo. `make
gate` checks four things and prints one line for each: Docker starts a container, the Verified-mini
dataset downloads and holds 50 rows, one instance's container starts with the repository at the
expected commit, and the configured model answers one short message on the selected backend. Write
one unit test for the instance loader, over a fixture row, with no network and no container.
Done when: `make gate` passes and 1 instance runs end to end and writes a patch file, right or
wrong, in under 15 minutes, with its wall-clock minutes written to the run log.
Verify: `make gate && make test && make run N=1`
Checkpoint: commit "skeleton".

### Phase 2: the loop

Do: the agent loop with exactly one bash tool, executed inside the container; a step cap of 60; a
cost cap and a wall-clock cap per instance, both read from the config file; a transcript per
instance saved under `runs/`, one JSON line per step with the command, the output, the token counts
and the running cost. When any cap is hit, stop that instance and write the reason into its
transcript.
Done when: 5 instances run with a transcript and a patch each, all 5 patches apply cleanly with
`git apply`, and each instance has its stop reason recorded. On the API backend, at least 1 of the 5
is also graded as resolved.
Verify: `make run N=5 && make grade`
Checkpoint: commit "loop".

### Phase 3: the first table

Do: run all 50 instances and grade them. Compute the resolved rate with a 95% binomial interval,
naming the method you used (Wilson or Clopper-Pearson) beside the number. Log cost and wall-clock
minutes per instance, p50 and p95. Write the table into the README with its date and the command
that produced it.
Done when: the table exists with the interval, and all 50 instances have a row in the per-instance
results file.
Verify: `make run N=50 && make grade`
Checkpoint: commit "table".

### Phase 4: the failure taxonomy

Do: read 20 failed transcripts. Classify each one as wrong file, no reproduction, tests not run,
step cap hit, tool error or other, and count the classes. Fix the top two causes in the loop, one
change at a time. Re-run the 50 and re-grade.
Done when: 2 taxonomy rows have a before and after count and the new table is in the README.
Verify: `make taxonomy && make run N=50 && make grade && make taxonomy`
Checkpoint: commit "taxonomy".

### Phase 5: the second backend

Do: the same loop on the other backend, local if the first was the API and the reverse. With no key,
both backends are local: the second is the other Ollama model from the interview, selected by its
name in the config file, and the API row is an addition for the day a key exists. Change the backend
config and nothing else. Run a 10-instance slice first and show me its numbers before spending
anything, dollars or hours, on the full set.
Done when: the table has a second row over 50 instances with its cost and its time.
Verify: `make run N=10 MODEL_BACKEND=local && make grade`, then `make run N=50
MODEL_BACKEND=local && make grade`, with `api` in place of `local` when the API backend is the
second one, or the second model's name in the config when both backends are local
Checkpoint: commit "two backends".

### Phase 6: the live demo

Do: build the demo container from that repository's own setup and test commands, the ones I gave you
in the interview, and run the agent on the real issue inside it. Open the pull request from its
patch on the host with `gh`, never from inside the sandbox, with a summary of the transcript in the
description: the commands it ran, the tests it ran, and what it changed. Record 30 to 60 seconds of
the run.
Done when: 1 pull request exists and the recording is linked from the README.
Verify: `make demo`, then the pull request URL, with its checks green.
Checkpoint: commit "demo".

### Phase 7: credibility

Do: every item in the credibility layer below.
Done when: the README's first 200 words carry the resolved rate with its interval and the cost per
instance.
Verify: `make setup && make gate && make test` in a fresh clone, then the final verification below,
step by step.
Checkpoint: commit, then tag `v1.0`.

## Credibility layer

These are phases, not extras. The build is not done until every one of them exists:

- `eval/`: the eval set, a runner, and the metric code, with a unit test for each metric on a toy case where the answer is known by hand.
- The eval table in the README: one row per configuration and per backend, every metric, and the date it was produced.
- `cost.md`: cost and latency per unit of work, p50 and p95, per backend, with the token counts and the dated prices they came from.
- `PREFLIGHT.md`: every defect found on the way, one row each, as *what was wrong, the number that showed it, the fix, the number after*. A build with an empty PREFLIGHT.md did not look hard enough.
- The README: the headline number in its first 200 words, the command that reproduces it, and one sentence on what the number does not prove.
- A 30 to 60 second screen recording of the thing working, linked from the README.

## Out of scope

Build none of this, and stop and tell me if one of them starts to look necessary: monorepo support;
the full Lite or Verified sets; a web UI; more than 4 parallel workers; a GPU; any model routing
beyond the two backends.

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
4. `git log` shows one commit per checkpoint, and `git log -p -- . ':!.env.example' | grep -iE "sk-[A-Za-z0-9]|api_key=.+"` finds nothing.
5. Tell me the three numbers I should say first in an interview about this project, and where each one came from.
