![Needle in a Haystack icon](icon.png)

# Needle in a Haystack, RAG at scale, as a live product

## What you build

A retrieval system over about a million chunks of real, messy, permissively licensed text. The
corpus is your choice: a subset of English Wikipedia (7,242,247 articles, CC BY-SA 4.0, a dump over
25 GB compressed), arXiv metadata under CC0, CourtListener's bulk opinions under the Public Domain
Mark, or Project Gutenberg's 79,431 free eBooks. The arXiv metadata has two routes: the Kaggle
dataset, which needs a free Kaggle account and an API token on disk before `make ingest` will
download anything, or arXiv's own OAI-PMH feed, which needs no account.

Two indexes run over the same chunks, one keyword and one vector. Their ranked lists are fused, a
cross-encoder reorders the shortlist, and a search page answers a typed question and prints the
latency of that query next to the results.

Beside the system sits what the interview question below is asking for: a labelled question set of at
least 200 questions, and a table that reports recall@10 and nDCG@10 for each retrieval step in turn,
one row per step and per backend.

The demo is a page that answers a hard question over a huge corpus in under half a second on the API
or GPU path, with the measurement on it. The local budget is retrieval p95 under 500 ms, with the
rerank step timed on its own line.

## Why it gets interviews

Retrieval appears in 10 of the 11 job postings behind this repo, read in full in September 2026 (the
table is in [WHY-THESE-FIVE.md](../../WHY-THESE-FIVE.md)). Interviewers have a standard probe for
it. Digital Applied's 2026 hiring checklist states it as an instruction to the interviewer: "Ask:
'What was your recall@10?' Any production RAG system has a recall metric." KORE1 describes its ideal
take-home as a provided codebase with a naive RAG pipeline where the ask is to "improve retrieval
quality and prove it improved."

This project is that take-home at a different scale. The same KORE1 piece suggests handing a
candidate 500 to 5,000 documents and 30 labelled query-answer pairs; this build is a million chunks
and 200 questions. It puts four things on the table at once: retrieval engineering, serving inside a
latency budget, cost per query, and evals that were run rather than described.

## How it works

```
corpus
  |
  v
chunker  (~300 tokens, document title prepended to every chunk)
  |
  +--> BM25 index    (SQLite FTS5 or Postgres full text) --+
  |                                                        +--> RRF fusion --> reranker --> search page
  +--> dense index   (bge-small, or API embeddings) -------+        (top 20 -> top 10)

labelled questions --> eval runner --> recall@10 and nDCG@10 table --> the same page
```

The title goes on the front of every chunk because a chunk taken from the middle of a document no
longer names its own subject. Cut a Wikipedia article at 300 tokens and the paragraph about the
second world war says "he" and "the campaign" and never says which general or which campaign. BM25
cannot match a word that is not in the text, and the embedding of a subject-less paragraph lands
somewhere generic. Prepending the title costs a few tokens per chunk and puts the subject back into
both indexes.

The reranker sees a short shortlist for a reason. A cross-encoder scores the query against each
candidate text, which is far more accurate than comparing two vectors and far slower, so it runs on
twenty candidates and not on a million. That also means it can only reorder what it is handed: any
document the fusion step missed is gone before the reranker starts, which is why recall of the
fusion step is measured separately. Handing it a wider shortlist is not a free upgrade either. A
longer shortlist hands the cross-encoder more near-misses to promote and costs more time per query,
so shortlist size is a parameter to tune on the eval set, with every size you tried written down.

## The numbers

The headline is recall@10 and nDCG@10 on 200 or more labelled questions, with one row per retrieval
configuration: BM25 alone, dense alone, the two fused, and fused plus reranked. Beside them go p95
latency and dollars per query.

One published reference point says roughly where a dense row lands. The bge-small-en-v1.5 model card
puts the model at 51.68 on MTEB retrieval, averaged over 15 datasets. Different corpora, so treat it
as an order of magnitude and not a target.

The shape to expect is a staircase: dense retrieval alone lowest, hybrid above it, hybrid plus
reranking above that. Your own four rows are the only figures for your corpus that mean anything, and
they are the deliverable.

The local path scores a little lower and indexes much slower. Time your own embedding rate on the
first 10,000 chunks and multiply it out before you start the full run; on a laptop CPU the million
takes hours. Generation for the one answer call goes through Ollama. Hosting is optional on this
path.

## Free and local

sentence-transformers running bge-small on CPU handles the embeddings. SQLite FTS5 gives you BM25,
and sqlite-vec holds the vectors with no index to build or tune. Do not assume brute force is fast
enough at full scale: in the benchmark in its own release post, a million float vectors missed the
author's 100 ms target at every dimension he tried, 192-dimension vectors taking 192 ms and
3,072-dimension ones 8.52 seconds, while binary quantization came back in 124 ms. Measure it on your
own machine in Phase 3 and keep binary quantization in reserve. Postgres with pgvector is the
alternative, and the author of one vector-database survey reports an HNSW index build crashing at a
million vectors on his 16 GB machine, so on 16 GB start with brute force and measure before adding an
index. A local cross-encoder does the reranking, and on CPU it is the slowest step in a query, so the
budget on this path is retrieval p95 under 500 ms with the rerank step timed and reported on its own
line; a whole reranked query under half a second is the API or GPU path. Ollama writes the answer.
Ship a localhost demo and a screen recording instead of a URL.

Expect one silent failure. A cross-encoder can return NaN scores for a batch and then sort nothing,
so the reranked row in your table quietly equals the hybrid row and looks like a null result. The
prompt makes the build raise on NaN rather than sort it.

## Time and money

Two to three weeks. On the API path, $30 to $80. A million chunks at about 300 tokens each is 300
million tokens, which is about $6 on OpenAI's text-embedding-3-small at $0.02 per million tokens
(September 2026).
Voyage charges the same $0.02 per million for voyage-4-lite and gives the first 200 million tokens
free, so two thirds of that corpus embeds for nothing there and the rest costs cents (September
2026). Hosting is $1.94 a month for a 256 MB Fly machine or $7.78 for 1 GB, $5 a month on Railway's
Hobby plan, or free on Hugging Face Spaces at 2 vCPU and 16 GB (September 2026). The local path
costs $0 and buys indexing hours instead.

## What to publish

- The eval table, on the search page and in the README, with the date each row was produced.
- p50 and p95 at 100,000 chunks and again at 1,000,000, so the reader sees what scale changed.
- Cost per query on each backend, with the token counts and dated prices behind it.
- `PREFLIGHT.md`: every defect, the number that exposed it, the fix, the number after.
- A 30 to 60 second recording of one real query.
- The live URL, if you hosted it.

## Interview questions it answers

1. How did you build the labelled set, and how do you know the labels are right?
2. What was recall@10 before and after reranking, and why did the shortlist size matter?
3. What did p95 look like at 100,000 chunks versus a million, and what changed?
4. What does a query cost on each backend?
5. What broke silently, and how did you catch it?

## Sources

- https://en.wikipedia.org/wiki/Wikipedia:Database_download, dump size and licence
- https://en.wikipedia.org/wiki/Wikipedia:Size_of_Wikipedia, article count
- https://www.kaggle.com/datasets/Cornell-University/arxiv, arXiv metadata under CC0
- https://www.kaggle.com/docs/api, the account and API token the Kaggle download needs
- https://info.arxiv.org/help/oa/index.html, arXiv's OAI-PMH feed, the route with no account
- https://wiki.free.law/c/courtlistener/help/api/bulk-data/bulk-legal-data, bulk opinions and licence
- https://www.gutenberg.org/, eBook count
- https://huggingface.co/BAAI/bge-small-en-v1.5, the MTEB retrieval score for bge-small
- https://alexgarcia.xyz/blog/2024/sqlite-vec-stable-release/index.html, brute-force latency at 1M vectors
- https://seanpedersen.github.io/posts/vector-databases/, pgvector HNSW at 1M vectors on 16 GB
- https://developers.openai.com/api/docs/pricing, embedding price
- https://docs.voyageai.com/docs/pricing, embedding and rerank prices, free allowance
- https://fly.io/pricing/, machine prices
- https://railway.com/pricing, Hobby plan price
- https://huggingface.co/pricing, Spaces free tier
- https://www.digitalapplied.com/blog/ai-developer-hiring-skills-that-matter-2026, the recall@10 question
- https://www.kore1.com/hire-rag-engineers-2026/, the retrieval take-home
- The 11 postings behind the skill counts, with their URLs: [WHY-THESE-FIVE.md](../../WHY-THESE-FIVE.md)
