# Concierge: master prompt

Paste this into Claude Code in an empty repository.

## Goal

Build Concierge, a real-time voice agent in the browser that listens, can be interrupted, calls tools
mid-conversation, and books an appointment on a local calendar, with a latency budget measured per
turn.

Done when: p50 and p95 from the end of speech to first audio are reported over 100 turns per backend,
task completion is reported over 30 scripted conversations, and the interruption test passes 20 of
20.

## Interview me first

Ask me all of this in one numbered message, then wait for my answers. Do not write code first.

1. Path: `api` or `local`.
2. RAM, whether this machine has a GPU, and what microphone I am using.
3. The booking domain: restaurant, clinic, barber or meeting room. Whichever I pick, the calendar is
   a local SQLite file with real rows, never a hosted service and never a stub that pretends.
4. Stack: a speech-to-speech API, a pipeline of separate speech-to-text, model and speech-synthesis
   APIs, or fully local.
5. The language spoken in the conversation. Say with the question that on the local path Kokoro has
   voices for English, Japanese, Mandarin, Spanish, French, Hindi, Italian and Portuguese, and that
   any other language means Piper for the local voice or the API path, so I pick the language and the
   voice together.
6. Budget cap in dollars.
7. Time budget, in evenings or days.

Then write three files and stop. `SPEC.md`: what it does, the five timestamps you will record, the
three numbers you will report. `PLAN.md`: the phases below with my answers folded in, and for each
phase the command I will run to check it. `CLAUDE.md`, under 200 lines: the commands, the repository
layout, and the rules that must not be broken. Show me all three and wait for me to say go before
Phase 1.

## Provider abstraction

Build one interface for every model call and at least two backends behind it: the API I chose in the interview, and Ollama for the local path. One switch selects the backend: the environment variable `MODEL_BACKEND` (`api` or `local`), overridden by a `--backend` flag. Model names, endpoints and prices live in one config file, never at call sites. The eval, the cost log and the latency log run unchanged on both backends, and every results table has one row per backend. On the local path, run `ollama list` before choosing a model and pick the largest model that fits the RAM I told you about; if nothing suitable is installed, tell me the `ollama pull` command and stop. Expect the local path to score lower and run slower. Say so in the README beside the numbers; never hide it.

For Concierge that interface covers three kinds of call: speech to text, the model, and speech
synthesis. Each one gets an API backend and a local backend behind the same signature.
`MODEL_BACKEND` switches all three together, and a mixed pipeline such as a hosted speech-to-text
service in front of a local model needs its own flag and its own row in every table. If I answered
`local`, there is no API to put behind the interface, so the second backend is a second local
configuration: a smaller Ollama model, or whisper base against whisper small. Every table carries one
row per backend actually run, and the README says which two they were.

## Phases

### Phase 1: skeleton

Do: a Makefile with `setup`, `gate`, `test`, `serve`, `bench`, `test-interrupt` and `eval` targets.
`make gate` pushes one 5-second WAV through speech to text, the model and synthesis with no
microphone in the loop, and asserts that each component loaded and produced output. Before it loads
anything, the gate checks the binaries pip cannot install for you: Kokoro's phonemizer calls
`espeak-ng`, so look for that binary on the path first and print `brew install espeak-ng` (or the
apt-get line on Linux) when it is missing, instead of failing later inside synthesis with an error
that never names the package. Add one unit test over the timestamp arithmetic so the percentile code
is exercised before any audio exists.

Done when: `make gate` passes and a 5-second WAV becomes a spoken reply WAV. On the `api` path that
happens in under 10 seconds. On the `local` path, write down the seconds you actually got and name the
model that produced it, and leave cutting the number to Phase 6.

Verify: `make gate`.

Checkpoint: "skeleton".

### Phase 2: the browser loop

Do: a page that captures the microphone and streams audio to the server. The detector marks end of
speech, speech to text emits partials while I talk, the model streams, synthesis streams back, and
the page plays audio as chunks arrive rather than waiting for the file. One log line per turn
carrying all five timestamps.

Done when: 10 consecutive turns in the browser complete with all five timestamps in the log, one line
per turn. On the `api` path every one of those turns is under 3 seconds. On the `local` path, write
down the turn time you actually got, name the model that produced it, and leave cutting it to Phase 6.
Also measure the page's playback buffer here, once, because Phase 3 may have to borrow that number.

Verify: `make serve`, then a 10-turn session in the browser with the log attached to the checkpoint
commit.

Checkpoint: "loop".

### Phase 3: the latency bench

Do: record five timestamps per turn, end of speech, speech-to-text final, first token, first audio
byte and first audio played, into one line of structured output. Then a bench mode that replays 100
fixed utterances through the same server path with no microphone, so the number is repeatable and does
not depend on me talking. Build the 100 once by running a list of written utterances through the local
speech synthesis and committing the WAVs, and reuse that same generator for the eval set in Phase 5.
Feed each WAV to the server at real-time pace with a tail of silence on the end, so the detector fires
on it the way it fires on a microphone and end of speech is a measured timestamp. First audio played
happens in the page, so the bench either drives the page in a headless browser or reports the first
four timestamps and adds the playback buffer measured in Phase 2, labelled in the table as the Phase 2
number it is.

Done when: a per-stage p50 and p95 table over 100 turns exists, with one row per backend.

Verify: `make bench`.

Checkpoint: "measured".

### Phase 4: interruption and tools

Do: barge-in cancels synthesis, cancels the model turn and flushes the queued audio in the page.
Tools for checking availability, booking and cancelling against the SQLite calendar, callable
mid-conversation. Then a test that injects a new utterance at a known offset during a reply and
measures wall-clock time from its first sample to the last sample the player emitted, at offsets that
include the first 200 ms of a reply and the middle of a tool call. That test runs in headless Chrome
started with `--use-fake-device-for-media-capture` and `--use-file-for-fake-audio-capture` pointed at
the injected utterance, and the page logs the timestamp of the last sample it writes to output;
`make test-interrupt` starts the browser, runs the 20 attempts and reads that log. The booking half of
the phase gets its own test under `make test`: it drives one booking end to end and asserts the row in
the SQLite calendar, before and after.

Done when: 20 of 20 interruptions stop the audio within 300 ms and one booking round trip changes a
row in the calendar.

Verify: `make test-interrupt && make test`.

Checkpoint: "interrupt and book".

### Phase 5: conversation eval

Do: 30 scripted conversations whose user turns are audio files generated from the scripts, so the
same input runs on both backends. Completion is judged by reading the calendar afterwards and
comparing it to what the script asked for. Never ask a model whether the conversation succeeded.

Done when: the completion rate over 30 conversations is reported per backend, with each failure
listed by what actually went wrong.

Verify: `make eval`.

Checkpoint: "eval".

### Phase 6: cut the latency

Do: work the stages the bench says are slowest. Smaller synthesis chunks, the detector's silence
threshold, prompt caching, a smaller model where the eval still holds. Change one thing at a time and
re-run the bench after each change so every gain has an owner.

Done when: p50 is lower than the Phase 3 number, and both numbers are in the README beside the change
that moved it.

Verify: `make bench`.

Checkpoint: "faster".

### Phase 7: credibility

Do: everything in the credibility layer below. The recording is the demo, so record a real
conversation that includes one interruption and one booking.

Done when: the README's first 200 words carry p50 and the completion rate and link a recording of at
least 30 seconds.

Verify: the final verification below, all 5 steps.

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

Telephony and phone numbers. More than one speaker in the room. Wake words. Coping with background
noise beyond what the detector gives you. More than one booking domain. Anything that needs a GPU on
the API path.
If I ask for one of these later, it is a second project and it starts with its own interview.

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
4. `git log` shows one commit per checkpoint, and `git log -p | grep -iE "sk-[A-Za-z0-9]{16}|api_key=.+"` finds nothing.
5. Tell me the three numbers I should say first in an interview about this project, and where each one came from.
