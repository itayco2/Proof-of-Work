![David icon](icon.png)

# David: a small fine-tune measured against a frontier model

## What you build

A QLoRA fine-tune of a small open model on one narrow task, measured against a frontier API model
on a held-out set that was frozen before any model saw it. The deliverable is one table: the base
small model, the same model after fine-tuning, and at least one frontier model, all scored on the
same examples, each row carrying a 95% interval and a cost per 1,000 requests.

What you earn is the right to say which way the comparison went and why, and to defend the way it
was set up: one frozen split under every row, with equal effort spent on both prompts. A win and a
loss both hold up on those terms.

## Why it gets interviews

Fine-tuning appears in 2 of the 11 AI engineer postings surveyed for this repo, and both ask for
judgment rather than mechanics. GitLab's posting wants an engineer who understands "when a smaller
fine-tuned model outperforms". That is a comparison question, and most candidates answer it from
intuition. You answer it with measurements on a frozen set.

The recruiting sources push the same way. Landed's portfolio guide says "Numbers beat claims."
Conectia's list of red flags in LLM engineer hiring includes "No numbers. Can't quote a latency, a
cost per request, an eval score, an error rate from anything they built." A comparison table with
intervals and a cost ratio is the direct answer to that objection.

Skills on display: fine-tuning judgment, eval design, cost measurement.

## How it works

```
  dataset
     |
     v
  dedupe + split  -->  train (3,000+)      dev (200)      held-out (1,000+, frozen, hashed)
                            |                                        ^
                            |                                        |
  base model  ------------- | ----- zero-shot and few-shot ----------+
     |                      |                                        |
     |  QLoRA <-------------+                                        |
     v                                                              |
  fine-tuned model  ---------------------------------------------- --+
                                                                    |
  frontier model  ------- the identical prompt --------------------- +
                                                                    |
                                                                    v
                                     table: metric, 95% interval, $ per 1,000 requests
```

The split is frozen and deduplicated first, before a single model runs. Fine-tuning is very good at
memorising, so one example that appears in training and again in the held-out set turns the score
into a lookup and you will not notice from the number alone. You remove exact duplicates and near
duplicates across splits, write the hashes into `data/split.json`, and commit that file. After that
the held-out set is read-only. Every later result refers to the same rows, which is what makes the
base, fine-tuned and frontier numbers comparable at all.

The honest outcome may be that David lost. Published work goes both ways: LoRA Land reports small
fine-tunes beating GPT-4 on average across 310 fine-tunes, and the SemEval-2024 clinical inference
work reports fine-tuned models that did not. A losing table is still a strong portfolio result when
you publish it with the error analysis and a clear reason, because the skill on show is the judgment
of when fine-tuning is worth the effort. The failure mode that kills the project is a hidden result,
or a leak that was never checked.

## The numbers

The headline is a comparison: the fine-tuned small model against the frontier model on 1,000 or more
held-out examples, each with a 95% bootstrap interval, plus the ratio of their costs per 1,000
requests. Two rows and one ratio.

Reference points from published work, so you know what a plausible result looks like:

- LoRA Land trained 310 models and reports that "4-bit LoRA fine-tuned models outperform base
  models by 34 points and GPT-4 by 10 points on average" (April 2024).
- An enterprise search relevance labeler (January 2026) distilled a small model that came out "on
  par with or better than the teacher LLM" at "17 times" the throughput and "19 times more
  cost-effective".
- The counterexample, SemEval-2024 clinical natural language inference, where fine-tuned models
  "did not produce more accurate results than GPT-4".

Frontier list prices per million tokens (September 2026), for the cost side of the table: Claude
Opus 5 $5 in and $25 out, Sonnet 5 $2 and $10, Haiku 4.5 $1 and $5, GPT-5 $1.25 and $10, Gemini
3.1 Pro $2 and $12. At 600 input and 20 output tokens per request, 1,000 requests through Opus 5
costs about $3.50 and the same traffic through GPT-5 costs about $0.95. Your fine-tuned model's
figure comes from its measured throughput on the hardware you served it on, not from a list price.

## Free and local

The whole build runs at no cost. Training goes on Colab's free T4, where Unsloth's notebooks are
built to run and where it claims "2× faster" training with "70% less VRAM", or on Apple Silicon with
`mlx-lm`, or on a local NVIDIA GPU. Pick a base model your hardware can hold: the Qwen3 dense family
is Apache 2.0 and starts at 0.6B, and 0.6B to 4B is the right range for 16 GB of RAM or a free T4.

For the frontier side without a card on file, use the Gemini API free tier, or the largest model
Ollama can run on the machine. The free tier covers the Flash and Flash-Lite classes; Gemini 3.1 Pro
sits on the paid tier. A local 8B model is a weaker Goliath than Opus 5, so label the row for what it
is and say so beside the table. A beaten 8B baseline is not a beaten frontier model. The honest
headline on the free path is "beats a Flash-class or local 8B baseline". A headline that names a
frontier model belongs to the paid path.

## Time and money

One to two weeks, most of it on the data and the eval rather than the training.

The paid path is about $40 to $100. A rented RTX 4090 is $0.34 an hour on RunPod's community cloud
and $0.74 an hour secure (September 2026), so twenty hours of rental is $7 to $15 and you can afford
to throw runs away. Frontier baselines are the other half: at the token sizes above, 2,000 examples is
1.2M input and 40,000 output tokens, which is about $7.00 on Opus 5, $2.80 on Sonnet 5 and $1.90 on
GPT-5 per model per full baseline run, and you will run baselines more than once.

The free path is $0: Colab's free T4 or `mlx-lm` locally, a public labelled dataset, and the Gemini
free tier or a local model as the baseline.

## What to publish

The comparison table with a 95% interval on every row. The frozen split and its hashes, plus the
exact baseline prompts, so a reader can check you did not tilt the comparison. The training log with
loss per step. An error analysis over 50 misses, grouped into named failure classes. The throughput
and cost measurement for the local model beside the API's price. `PREFLIGHT.md` with every defect you
hit and the number that exposed it. A 30 to 60 second recording of the fine-tuned model serving
requests.

## Interview questions it answers

1. How did you prevent leakage between training and held-out data?
2. Is the win significant, and how did you compute the intervals?
3. What is the cost ratio and how did you measure throughput?
4. When would you not fine-tune?
5. What did the error analysis show about where the small model fails?

## Sources

- LoRA Land, 310 fine-tuned models: https://arxiv.org/abs/2405.00732
- Enterprise search relevance labeler, January 2026: https://arxiv.org/abs/2601.03211
- SemEval-2024 clinical natural language inference: https://arxiv.org/abs/2404.00484
- Unsloth, speed and VRAM claims, free Colab notebooks: https://github.com/unslothai/unsloth
- Qwen3 dense model family and licence: https://qwenlm.github.io/blog/qwen3/
- RunPod GPU pricing: https://www.runpod.io/pricing
- Claude API pricing: https://platform.claude.com/docs/en/about-claude/pricing
- OpenAI API pricing: https://developers.openai.com/api/docs/pricing
- Gemini API pricing and free tier: https://ai.google.dev/gemini-api/docs/pricing
- GitLab AI engineer posting: https://job-boards.greenhouse.io/gitlab/jobs/8556658002
- Landed, AI engineer portfolio projects: https://github.com/landedjobs/ai-engineer-portfolio-projects
- Conectia, how to hire LLM engineers: https://conectia.pro/en/blog/how-to-hire-llm-engineers
- The 11 postings and the practitioners quoted here: [WHY-THESE-FIVE.md](../../WHY-THESE-FIVE.md)
