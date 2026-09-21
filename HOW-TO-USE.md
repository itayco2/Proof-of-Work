# How to use a master prompt

Each project in this repo ships a guide and a `PROMPT.md`. The prompt is the build. You paste it
into Claude Code as your first message, answer an interview, approve the spec it writes, then work
through phases that each end in a number you can check. This page is the mechanics of that, on an
API key or free and local. [Why these five](WHY-THESE-FIVE.md) covers the choice of projects.

|  | Project | Prompt |
|---|---|---|
| <img src="assets/the-night-shift-128.png" width="56"> | [The Night Shift](projects/01-the-night-shift/) | [PROMPT.md](projects/01-the-night-shift/PROMPT.md) |
| <img src="assets/citation-needed-128.png" width="56"> | [Citation Needed](projects/02-citation-needed/) | [PROMPT.md](projects/02-citation-needed/PROMPT.md) |
| <img src="assets/hello-world-128.png" width="56"> | [Hello, World](projects/03-hello-world/) | [PROMPT.md](projects/03-hello-world/PROMPT.md) |
| <img src="assets/needle-in-a-haystack-128.png" width="56"> | [Needle in a Haystack](projects/04-needle-in-a-haystack/) | [PROMPT.md](projects/04-needle-in-a-haystack/PROMPT.md) |
| <img src="assets/david-vs-goliath-128.png" width="56"> | [David vs Goliath](projects/05-david-vs-goliath/) | [PROMPT.md](projects/05-david-vs-goliath/PROMPT.md) |

## Install Claude Code

Claude Code runs in your terminal. Install it and sign in with your Claude account by following the
quickstart: https://code.claude.com/docs/en/quickstart. A working `claude` command inside an empty
folder is the whole setup.

The prompts are plain Markdown, so they also work as a first message in Cursor or Codex; save the
`CLAUDE.md` the build writes as `AGENTS.md` there, so the rules survive a new session.

## Start in an empty folder

A fresh folder with its own git history keeps the phase commits readable, and a clean clone is what
the prompt's final verification checks at the end.

```bash
mkdir night-shift && cd night-shift && git init
```

Copy a project's `PROMPT.md` from the table above into that folder. Read its guide first if you have
not already; it says what the build measures and how long it tends to take.

## Paste the prompt

Start Claude Code in that folder:

```bash
claude
```

Paste the whole of `PROMPT.md` as your first message, including the rules and the final
verification at the bottom. Those sections are what stop a build from ending at "it works". Do not
summarise the prompt and do not feed it one phase at a time.

The first thing that happens is an interview. Nothing is written yet.

## Answer the interview

The questions arrive one at a time and each one changes the build: the provider path (`api` or
`local`), how much RAM the machine has and whether it has a GPU, which corpus or dataset, a budget
cap in dollars, how many weeks you have, the language of the interface. Answer concretely.
"Whatever you think" gets you a spec built on guesses about your hardware and your budget.

Then it writes three files and stops: `SPEC.md`, what gets built and what the numbers have to be;
`PLAN.md`, the phases; and `CLAUDE.md`, under 200 lines, the rules it re-reads at the start of every
session. Read all three before anything else happens. This is the cheapest moment to change your
mind, so cut a phase, swap the dataset or lower a target now. Edit the files yourself where that is
faster than explaining. When they say what you want, say "go".

## One phase at a time

Every phase carries four labels. Do is the work. Done when is the condition, and it ends in a
number. Verify is the command that produces that number. Checkpoint is the commit.

Run the Verify command yourself and read what it prints before you say "next". A phase that reports
no number is not finished, whatever the transcript claims. Commit at each checkpoint, with the
number in the message, so you can go back to the last state that measured well.

When a phase goes wrong twice, stop instead of trying a third time in the same session. Run
`/clear`, then start the phase again, putting what you learned into the first message. Anthropic's
own guidance is to clear context between tasks rather than carry a long session forward:
https://code.claude.com/docs/en/best-practices.

## Free and local

Every project runs with no API key at all. Install Ollama (https://ollama.com) and Python 3.11 or
newer, then pull a model sized for the machine you have.

| RAM | Pull |
|---|---|
| 8 GB | a 3 to 4B model |
| 16 GB | an 8B model |
| 32 GB or more | a 14 to 32B model |

The prompt runs `ollama list` before it picks anything and takes the largest installed model that
fits the RAM you named in the interview. If nothing suitable is installed, it prints the
`ollama pull` command you need and stops.

What each build uses on this path:

- The Night Shift: an Ollama coding model behind the agent scaffold, with Docker for the sandbox.
- Citation Needed: keyless web search and a small entailment model on CPU as the citation grader.
- Hello, World: faster-whisper for speech to text, Ollama for the reply, Kokoro for the voice.
- Needle in a Haystack: local embeddings, SQLite full-text and vector search, and a local reranker.
- David vs Goliath: Colab's free T4, which needs a Google account, or Apple Silicon for the fine-tune.

Scores come out lower here and turns take longer. The bill is $0 for what the build calls. Claude
Code itself needs a paid Claude plan, or you can paste the prompts into another agent's free tier.
The eval, the cost log and the latency log run unchanged on both backends, and every results table
gets one row per backend, so the gap between them is on the page instead of hidden.

## With an API

One key from Anthropic, OpenAI or Gemini covers the model calls in all five builds. Two of them
take a second key, and one needs a GPU: Citation Needed for search, Tavily or Brave, unless you use
the keyless path; Hello, World for hosted speech to text and voice; and David vs Goliath for rented
GPU time or Colab, with the hours and cost in its guide.

Keys live in `.env`, loaded at startup and listed in `.env.example` with empty values. `.env` goes
into `.gitignore` in the first commit, and nothing ever prints a key. The final verification greps
your own history for one before you publish.

Give the interview a budget cap in dollars. Before any run that could cost more than a tenth of
that cap, the build stops and shows you its estimate first. Each guide gives the project's expected
range with dated prices.

## When it is done

A finished build is one a stranger can check:

- The README states the headline number in its first 200 words, beside the command that reproduces
  it, and one sentence on what the number does not prove.
- The eval table has one row per configuration and per backend, each with the date it was produced.
- `PREFLIGHT.md` holds every defect you hit: what was wrong, the number that showed it, the fix,
  the number after.
- A 30 to 60 second screen recording of the thing working, linked from the README.
- The repo pinned on your GitHub profile.
- One paragraph for LinkedIn that says what the reader is looking at and gives the number, with the
  link on its own line at the end.

## Add your number

`RESULTS.md` in this repo collects what readers measured: one row each, the repo linked, the
headline number exactly as that README states it. Open a pull request adding yours. None of those
rows are ours. We ran none of these builds, and the reference numbers in the guides belong to the
people who published them, linked where they appear.

## If something breaks

Run `make gate` in the built project first. It runs the checks that project depends on and names
the one that failed: Docker and the dataset (The Night Shift), search and the entailment model
(Citation Needed), the speech pipeline (Hello, World), the database and the index (Needle in a
Haystack), the GPU or MLX runtime (David vs Goliath).

Then read your own `PREFLIGHT.md`. A defect you fixed once tends to return after a refactor, and
the row tells you which number catches it.

If the prompt is at fault rather than your machine, open an issue here with the phase name, the
Verify command you ran and the number it printed. A phase that cannot reach its number on a 16 GB
laptop is a defect in the prompt.
