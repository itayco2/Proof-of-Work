# Why these five

The five projects in this repo were chosen from hiring research. Interviewers and recruiters describe what they check for. Job postings list requirements. Existing portfolio-project lists repeat the same handful of ideas without differentiating anyone. The counts below come from eleven job postings, read in full, and the quotations from the people named beside them. The published measurements in the last table come from the papers and model cards listed under Sources.

## What hiring sources say they look for

1. Robert Ardell, [KORE1](https://www.kore1.com/llm-engineer-interview-questions/), technical recruiter, asks candidates "How do you know your system is good?" The senior answer: "a few hundred real inputs with graded outputs... on every prompt change and every model version bump."
2. [Eugene Yan](https://eugeneyan.com/writing/how-to-interview/), Anthropic, asks three questions in one breath: "How did you measure model performance over time, as it was retrained or updated? When model performance breached predefined thresholds, how did you respond? How did you collect the initial evaluation data and build the eval harness?"
3. [Chirag Hasija](https://chiraghasija.cc/posts/how-to-interview-ai-engineer-role-2026/), who has sat on both sides of the interview loop for two years: "That is not an eval. That is vibes." On cost: "A feature that works but costs $2 per request and takes 30 seconds does not ship."
4. [Conectia](https://conectia.pro/en/blog/how-to-hire-llm-engineers), an engineering staffing firm: "Production leaves numbers on people." Its red flag: "All demos, no operations. Every project reached 'it works'; none reached month three."
5. [Digital Applied](https://www.digitalapplied.com/blog/ai-developer-hiring-skills-that-matter-2026), in its 2026 hiring checklist: "Ask: 'What was your recall@10?'" On résumés heavy with framework names: "LangChain + Pinecone resume... increasingly, a yellow flag."
6. [KORE1](https://www.kore1.com/hire-rag-engineers-2026/) again, on its ideal take-home test: "a small, provided codebase with a broken or naive RAG pipeline... prove it improved."
7. [Landed](https://github.com/landedjobs/ai-engineer-portfolio-projects), an AI-jobs platform: "One production project with proper evals beats five tutorial clones." And: "Reviewers won't clone — they click."
8. [Dover](https://www.dover.com/blog/how-to-hire-ai-engineer-startups), a recruiting firm, has candidates screen-share their repo and asks: "Why did they pick that model size? How did they spot hallucinations? What cost guardrails did they add?"
9. [Marina Wyss](https://www.dataexpert.io/blog/ultimate-guide-ai-engineering-portfolios), an AI engineering coach and former Amazon hiring panelist: "These standard chatbot tutorials and RAG follow-alongs simply aren't complex enough."
10. [Orpex](https://jobs.ashbyhq.com/orpex/af6f5f29-edf0-49e2-8664-faea7fe3ba5d), in its Applied AI Engineer posting: "Bonus if you've built agent tooling in the open."

## What the postings list

Eleven postings for AI Engineer, Applied AI Engineer and LLM Engineer were read in full in September 2026, from associate to senior, not a random sample. They are [Hasbro](https://job-boards.greenhouse.io/hasbro/jobs/4250645009), [Culture Amp](https://job-boards.greenhouse.io/cultureamp/jobs/8184634), [Splitero](https://job-boards.greenhouse.io/splitero/jobs/5162723008), [WITHIN](https://job-boards.greenhouse.io/agencywithin/jobs/5056863007), [Future](https://job-boards.greenhouse.io/future/jobs/4683133005), [GitLab](https://job-boards.greenhouse.io/gitlab/jobs/8556658002), [Implicit](https://job-boards.greenhouse.io/implicit/jobs/8039713), [Phizenix](https://job-boards.greenhouse.io/phizenix/jobs/5398766008), [Rackner](https://job-boards.greenhouse.io/rackner/jobs/4717776005), [Orpex](https://jobs.ashbyhq.com/orpex/af6f5f29-edf0-49e2-8664-faea7fe3ba5d) and [Exadel](https://builtin.com/job/associate-ai-engineer/7105658). The counts in the table below are of those eleven.

| Skill | Postings (of 11) |
|---|---|
| Evals, evaluation frameworks, regression testing | 11 |
| RAG, retrieval, vector search, embeddings | 10 |
| Agents, tool calling, orchestration | 10 |
| Cloud, deployment, containers | 10 |
| Python | 9 |
| Prompt and system-prompt engineering | 8 |
| Observability, tracing, monitoring | 6 |
| Serving, latency and cost | 5 |
| Guardrails, safety, adversarial testing | 5 |
| Fine-tuning | 2 |

Both fine-tuning mentions ask for judgment. One posting wants a candidate who knows "when a smaller fine-tuned model outperforms" a frontier API.

## What every list already has

Chat-with-your-PDF is the second project on [Careery](https://careery.pro/blog/ai-careers/ai-engineer-project-ideas)'s list and the first on [Upskillist](https://www.upskillist.com/blog/10-ai-portfolio-examples-impress-recruiters/)'s, and none of the versions publishes a retrieval number. The generic chatbot or GPT wrapper is a named red flag: [Landed](https://github.com/landedjobs/ai-engineer-portfolio-projects) lists "GPT-4 wrapper, no original work" among the patterns that get a candidate rejected on sight. A to-do app with GPT is CRUD with an API call attached; [Careery](https://careery.pro/blog/ai-careers/ai-engineer-project-ideas) puts it plainly: "A todo app with GPT doesn't prove AI engineering skills." Titanic, MNIST and IMDB notebooks are what [Let's Data Science](https://letsdatascience.com/blog/the-ml-portfolio-that-actually-gets-you-hired-in-2026) calls "zero signal." They are coursework. A résumé full of framework names is, to Conectia, being "fluent in the names of orchestration libraries, vague on what broke when they used them." Prompt engineering as a headline skill is dated: a 2024 [Hacker News hiring thread](https://news.ycombinator.com/item?id=39605588) said flatly, "Prompt engineering was novel 15 months ago."

Careery's own project list makes the same point about all six: "originality is overrated," and a well-built clone beats a poorly-built original. Measurement makes the difference.

## What makes a project credible

The same checklist recurs, source after source:

- a live URL or a short recording ([Landed](https://github.com/landedjobs/ai-engineer-portfolio-projects))
- the problem, approach and result in the README's first 200 words ([Let's Data Science](https://letsdatascience.com/blog/the-ml-portfolio-that-actually-gets-you-hired-in-2026))
- an eval table (Landed)
- cost per unit and p50/p95 latency (Landed; [Conectia](https://conectia.pro/en/blog/how-to-hire-llm-engineers))
- a failure write-up (Conectia)
- tests, a Dockerfile or a Makefile, and real commit history (Let's Data Science; [Simon Willison](https://simonwillison.net/2025/Oct/7/vibe-engineering/))
- three to six pinned repos (Landed)

## How the five map onto that

| Project | Skills it proves | Headline number | Published number it sits beside |
|---|---|---|---|
| Fixer | Agents, sandboxing, evals, cost per task | Percent of SWE-bench Verified-mini (50 instances) resolved, and dollars per instance | mini-SWE-agent reports above 74% on the full 500-instance Verified set with frontier models; the open scaffolds of the Claude 3.5 Sonnet era are collected in a 2025 leaderboard survey, which carries their resolved rates |
| Scholar | Orchestration, context engineering, faithfulness evals, prompt-injection defence | Citation precision and recall on a 50-question set; minutes and dollars per report | ALCE citation recall and precision for ChatGPT: 73.6 and 72.5 on ASQA, 51.1 and 50.0 on ELI5 |
| Concierge | Streaming, latency engineering, tool use, conversation evals | p50 and p95 from end of speech to first audio; task completion over 30 scripted conversations | Hosted speech-to-speech p50 of 1,064 ms on Gemini Live and 1,253 ms on OpenAI Realtime; a text agent at 85% task completion against 31 to 51% for voice agents on clean audio |
| Librarian | Retrieval engineering, serving, cost, evals | recall@10 and nDCG@10 on 200 or more labelled questions, before and after each retrieval step; p95 latency; dollars per query | bge-small-en-v1.5 at 51.68 on MTEB retrieval, averaged over 15 datasets |
| David | Fine-tuning judgment, evals, cost | Small model versus frontier model on a held-out set; cost ratio per thousand requests | 310 fine-tunes on LoRA Land: 4-bit LoRA models beat GPT-4 by 10 points on average (April 2024) |

## Sources

- https://www.kore1.com/llm-engineer-interview-questions/, eval question
- https://eugeneyan.com/writing/how-to-interview/, eval questions
- https://chiraghasija.cc/posts/how-to-interview-ai-engineer-role-2026/, interview advice
- https://conectia.pro/en/blog/how-to-hire-llm-engineers, red flags
- https://www.digitalapplied.com/blog/ai-developer-hiring-skills-that-matter-2026, hiring checklist
- https://www.kore1.com/hire-rag-engineers-2026/, take-home test
- https://github.com/landedjobs/ai-engineer-portfolio-projects, portfolio checklist
- https://www.dover.com/blog/how-to-hire-ai-engineer-startups, screen-share questions
- https://www.dataexpert.io/blog/ultimate-guide-ai-engineering-portfolios, portfolio guide
- https://jobs.ashbyhq.com/orpex/af6f5f29-edf0-49e2-8664-faea7fe3ba5d, job posting
- https://careery.pro/blog/ai-careers/ai-engineer-project-ideas, project ideas
- https://letsdatascience.com/blog/the-ml-portfolio-that-actually-gets-you-hired-in-2026, portfolio advice
- https://news.ycombinator.com/item?id=39605588, hiring thread
- https://simonwillison.net/2025/Oct/7/vibe-engineering/, vibe engineering
- https://job-boards.greenhouse.io/hasbro/jobs/4250645009, job posting
- https://job-boards.greenhouse.io/cultureamp/jobs/8184634, job posting
- https://job-boards.greenhouse.io/splitero/jobs/5162723008, job posting
- https://job-boards.greenhouse.io/agencywithin/jobs/5056863007, job posting
- https://job-boards.greenhouse.io/future/jobs/4683133005, job posting
- https://job-boards.greenhouse.io/gitlab/jobs/8556658002, job posting
- https://job-boards.greenhouse.io/implicit/jobs/8039713, job posting
- https://job-boards.greenhouse.io/phizenix/jobs/5398766008, job posting
- https://job-boards.greenhouse.io/rackner/jobs/4717776005, job posting
- https://builtin.com/job/associate-ai-engineer/7105658, job posting
- https://www.upskillist.com/blog/10-ai-portfolio-examples-impress-recruiters/, portfolio examples
- https://github.com/SWE-agent/mini-swe-agent/, resolved rate
- https://arxiv.org/pdf/2506.17208, leaderboard survey
- https://ar5iv.labs.arxiv.org/html/2305.14627, citation metrics
- https://github.com/virevolai/voice-benchmarks, voice latency
- https://arxiv.org/abs/2603.13686, task completion
- https://huggingface.co/BAAI/bge-small-en-v1.5, retrieval score
- https://arxiv.org/abs/2405.00732, fine-tune comparison
