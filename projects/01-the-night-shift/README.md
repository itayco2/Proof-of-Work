![The Night Shift icon](icon.png)

# The Night Shift, a coding agent scored on SWE-bench

## What you build

An agent that takes a GitHub issue, reproduces the failure inside a container holding that
repository at the commit before the fix, edits the code, runs the tests and writes a patch. The
benchmark's own tests grade the patch, resolved or not resolved. You run the agent over all 50
instances of SWE-bench Verified-mini and publish the resolved rate with a 95% interval, plus the
dollars and minutes an instance costs, one row per backend.

What people remember is the recording: the agent taking a real issue in your own repository from
first read to an open pull request, next to a table where your number sits beside published numbers
from named systems.

## Why it gets interviews

Agents, tool calling and orchestration appear in 10 of the 11 job postings
[read for this repo](../../WHY-THESE-FIVE.md). Orpex states the bonus outright: "Bonus if you've
built agent tooling in the open." Dover has candidates screen-share their work, and the screen it
describes is "a short-lived repo with a broken agent pipeline", with an interviewer asking what cost
guardrails they added.

Four skills come out of this build at once: writing an agent loop, sandboxing it, scoring it on a
frozen public set, and reporting cost per task. You also get a defensible answer to the question a
good interviewer asks about any benchmark score, which is how much of it is noise.

## How it works

```
GitHub issue
     |
     v
container: the repo at the parent commit, tests installed
     |
     v
the loop:  read -> run -> edit -> test
           one bash tool, a step cap of 60, a cost cap and a time cap per instance
     |
     v
patch  ->  grader: the benchmark's own tests
     |
     v
resolved or not resolved, plus one saved transcript per instance
     |
     v
failure taxonomy over the transcripts
```

One bash tool does the work of a toolbox. mini-SWE-agent is "Just 100 lines of python" and reports
">74% on SWE-bench verified" with frontier models, and every action it takes is a shell command, so
there is no separate edit tool or search API to keep in agreement with the model's idea of it. The
transcript is then the whole state, which is what makes a failed run readable afterwards. A step cap
of 60 plus a cost cap and a wall-clock cap per instance turn a loop that could run forever into a
unit of work with a known ceiling, and every cap is a number you can defend out loud.

The score needs an interval because 50 instances is a small sample. Near a 50% resolved rate the
95% Wilson interval on 50 instances runs from 37% to 63%, about 13 points either side, so 44% and
52% on that set are one result reported twice. Seven points is the standard error on that sample,
and quoting it as the interval halves the noise band you report. Publishing the interval keeps the
comparison honest, and it is why the useful experiment holds the scaffold fixed and changes one
thing at a time, usually the model.

## The numbers

Your headline is the resolved rate on all 50 Verified-mini instances, the method behind its 95%
interval, and the cost per instance, one row per backend. Every figure below belongs to the people
who measured it and is linked under Sources. The numbers you get are yours to publish.

- mini-SWE-agent, 100 lines of Python, reports above 74% on the full 500-instance Verified set with
  frontier models.
- A 2025 survey of the SWE-bench leaderboards collects the open scaffolds of the Claude 3.5 Sonnet
  era, OpenHands with CodeAct v2.1 and Agentless-1.5. Read their resolved rates off the survey, and
  their loops off their repositories.
- Published cost per instance for bash-only scaffolds is not available from swebench.com any more,
  so there is no figure to sit beside. Log your own dollars per instance and publish that.

The claim this project earns is narrow, and worth saying exactly: same scaffold, cheaper model,
measured on the same 50. Fifty instances leave a 95% Wilson interval about 13 points either side of
50%, so a two-point difference is not a finding.

Expect a local 7 to 14B coding model to score far below the API numbers above. Run a 10-instance
slice first, read the transcripts, then run the 50 and report whatever it is. A low local score with
a taxonomy of why it failed is a better interview than a high score you cannot explain.

## Free and local

Docker on x86 Linux or macOS. Verified-mini is the 50-instance subset of Verified, built to keep the
same difficulty distribution, and its images need about 5 GB against the 130 GB of the full set.
Lite (300 test instances) and Verified (500) are the bigger sets; this project stays on the 50. The
scaffold reaches a model through a model string, so an Ollama coding model runs the same code path
as the API. Grade either with the benchmark's free cloud grader, which returns results within 20
minutes and needs a key you request once with `sb-cli gen-api-key <email>`, or locally with Epoch
AI's slimmed images, 30 GiB for the whole Verified set instead of 189 GiB, MIT licensed. The
official evaluation code asks for "at least 120GB free space", so check your disk before you choose
the local grader.

## Time and money

Three to four weeks. The API path costs what your per-instance cap allows. Claude prices
(September 2026): Sonnet 5 at $2 per million input tokens and $10 per million output, Haiku 4.5 at
$1 and $5, with batch requests half price, so the bill follows the token counts you log per
instance. Budget $100 to $300 for three to five passes over 50 instances as a planning estimate,
then replace it with your measured cost after the first pass. Cloud grading is free. The local path
costs nothing and takes longer per instance, so its scarce resource is wall-clock time: time one
instance, then multiply by 50 before you start a full pass. Local grading is quick either way, since
Epoch AI measured about 8 seconds a sample and 62 to 70 minutes for the full 500 on 32 cores.

## What to publish

- The results table: resolved rate with its 95% interval and the method that produced it, cost per
  instance, minutes per instance, one row per backend, dated.
- The failure taxonomy, each cause with its count before and after the fix you made for it.
- The pull request the agent opened on your own repository.
- PREFLIGHT.md: every defect, the number that exposed it, the fix, the number after.
- The 30 to 60 second recording, linked from the top of the README.
- The step cap, the cost cap, the time cap and the grading command, so a reader can rerun all of it.

## Interview questions it answers

1. What is the noise band on 50 instances, and what claim does that allow?
2. How do you sandbox the agent and cap its cost?
3. What were the top failure causes, and what did fixing them change?
4. What does an issue cost on each backend?
5. How would you scale grading to the full set?

## Sources

- SWE-bench evaluation reference (500 Verified instances, `--instance_ids` for a subset, disk and
  runtime): https://www.swebench.com/SWE-bench/reference/harness/
- SWE-bench Lite dataset card (300 test rows, 23 dev):
  https://huggingface.co/datasets/princeton-nlp/SWE-bench_Lite
- SWE-bench Verified-mini dataset card (50 instances, about 5 GB against 130 GB, same difficulty
  distribution): https://huggingface.co/datasets/MariusHobbhahn/swe-bench-verified-mini
- Epoch AI on slimmed SWE-bench images (30 GiB against 189 GiB, about 8 seconds a sample, 62 to 70
  minutes on 32 cores, MIT): https://epoch.ai/latest/swebench-docker
- mini-SWE-agent on SWE-bench, including free cloud grading within 20 minutes:
  https://mini-swe-agent.com/latest/usage/swebench/
- mini-SWE-agent repository ("Just 100 lines of python", ">74% on SWE-bench verified"):
  https://github.com/SWE-agent/mini-swe-agent/
- Community reproduction of the bash-only leaderboard, February 2026, published after the official
  cost table went offline: https://dev.to/kyoma_1234/how-a-002call-model-scored-782-on-swe-bench-verified-beating-every-model-on-the-leaderboard-4bm3
- Survey of the SWE-bench leaderboards, 2025 (the scaffolds it collects include OpenHands with
  CodeAct v2.1 and Agentless-1.5): https://arxiv.org/pdf/2506.17208
- Claude pricing, September 2026: https://platform.claude.com/docs/en/about-claude/pricing
- Orpex, Applied AI Engineer posting:
  https://jobs.ashbyhq.com/orpex/af6f5f29-edf0-49e2-8664-faea7fe3ba5d
- Dover on hiring AI engineers for startups: https://www.dover.com/blog/how-to-hire-ai-engineer-startups
- The 11 postings and the practitioners quoted here: [WHY-THESE-FIVE.md](../../WHY-THESE-FIVE.md)
