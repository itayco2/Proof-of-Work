# Contributing

Two kinds of change are welcome here: a result you measured, and a correction to a prompt or a guide.

## Add a result

If you finished one of the five builds, the row belongs on the board. Open a pull request that adds
one line to [RESULTS.md](RESULTS.md) and changes nothing else. The five columns are:

- Project, the folder name, one of `01-fixer`, `02-scholar`, `03-concierge`, `04-librarian`,
  `05-david`.
- Date, the date you produced the number, as `2026-09-21`.
- Path, `api` or `local`, whichever the run used.
- Model, the model or models behind the number, with your own repo linked from this cell. The link is
  the point of the row, since it is where a reader checks the claim.
- Headline number, copied from your README rather than restated. If your README reports an interval,
  bring the interval.

Your repo needs a README that names the number in its first screen and the command that reproduces
it. A row whose repo has neither gets a comment asking for both, not a rejection.

One row per run. A second configuration of the same build is a second row, and a corrected number
replaces the row it corrects.

## Fix a prompt or a guide

Run `make setup` once, then `make test` before you open the pull request. The fast tier takes under a
second and checks that every guide still has its nine sections in order, every prompt its eight
blocks, every phase a measurable `Done when:`, and every relative link a file at the other end.
`make gate` adds the external links and takes under a minute.

One change per pull request, and say in the description which phase or which line you changed and
why. A fix to a number needs the source URL in the same pull request; a number without a source
comes back out. Quotations are verbatim, so a tidied quotation is a defect.

The contracts the tests encode are deliberate. If a fix needs a contract to change, say so in the
description and change the test in the same pull request, so the change is visible rather than
silent.

## What is not accepted

- A sixth project. Five is the point of the repo, and the choice of five is argued from hiring
  research in [WHY-THESE-FIVE.md](WHY-THESE-FIVE.md). A better fifth project is a fair argument;
  another folder is not.
- Reference implementations. The prompts exist so that you and Claude Code write the code in your own
  repository, under your own name. Working code in this repo would turn every row on the results
  board into a fork of one solution.
- Anything a reader cannot reach. A source behind a paywall, a login or a free trial cannot be
  checked by the person reading the guide, so it does not earn a citation here. Prices and figures
  quoted from vendor pages are fine, dated, with the page linked.
- Marketing. No vendor comparison written to sell a vendor, and no link to a course or a product.

## Licences

The scripts and tests are MIT ([LICENSE](LICENSE)). The guides, prompts and icons are CC BY 4.0
([LICENSE-CONTENT](LICENSE-CONTENT)). A pull request puts your contribution under the same licence as
the file it touches, and you keep the copyright in what you wrote.
