---
title: 'Dr-DCI: scaling agentic search via dynamic workspace expansion'
date: '2026-06-16T08:01:00'
lang: en
slug: dr-dci-scaling-agentic-search-via-dynamic-workspace-expansion
categories:
- AI Research
tags:
- agentic-search
- retrieval
- rag
- benchmarks
- research
summary: Dr-DCI is a retriever-steered framework for agentic search that lets an agent
  dynamically pull relevant documents into an evolving local workspace and run shell-executable
  Direct Corpus Interaction operations there, rather than over the full corpus. The
  design combines retriever-level recall with DCI-style precision while staying scalable
  as corpora grow. It reports 71.2% on BrowseComp-Plus (73.3% with context reset)
  and remains effective from 100K to 20M documents, outperforming raw DCI, BM25, and
  trained search-agent baselines while reducing tool calls, time, and cost. The benchmark
  gains and efficiency claims make it a notable contribution to retrieval-augmented
  agents, though results are not yet independently verified.
draft: false
---

Search agents have a scaling problem that does not announce itself until the corpus gets big. The retrieve-then-read loop works fine on a curated index, but the failure modes shift as the document store grows from a demo-sized collection into something that looks like the real world. Dr-DCI is a recent proposal that takes this scaling problem head on, and its core idea is deceptively simple: instead of letting the agent reason over the entire corpus, give it a small, evolving workspace and let it decide what to bring in.

## The tension Dr-DCI is trying to resolve

There are two broad strategies for grounding an agent in a large body of text, and each has a characteristic weakness.

The first is retrieval. A retriever — dense, sparse, or hybrid — is good at *recall*. Throw a query at it and it surfaces candidates from across the whole corpus. But retrieval is coarse. It hands the agent a ranked list and stops there; everything downstream depends on how good that list was, and the agent has limited ability to interrogate the corpus on its own terms.

The second is Direct Corpus Interaction (DCI), where the agent runs shell-executable operations against the documents themselves. This gives *precision*: the agent can grep, filter, slice, and inspect with the exactness of a command line rather than the fuzziness of a similarity score. The catch is scale. Operating directly over the full corpus gets more expensive and more unwieldy as the corpus grows, and what works at a hundred thousand documents does not necessarily survive a jump of two orders of magnitude.

Recall without precision, or precision without scale. Dr-DCI's bet is that you do not have to choose.

## Retriever-steered, workspace-local

The framework is described as *retriever-steered*. The retriever is not the whole story — it is the steering mechanism. Rather than handing back a static result set, the retriever is used to dynamically pull relevant documents into a local workspace that the agent owns. That workspace is the key architectural object. It is small relative to the corpus, it evolves as the task unfolds, and it is where the agent actually does its work.

Inside that workspace, the agent runs DCI operations — the same shell-executable, precise interactions that make DCI attractive — but it runs them over a focused, manageable slice of documents rather than over everything. The retriever supplies recall by deciding what enters the workspace; DCI supplies precision by giving the agent exact operations once the documents are there.

The payoff of this split is scalability. Because the precise, potentially expensive operations happen in a bounded workspace rather than across the entire store, the cost of those operations is largely decoupled from the size of the corpus. The retriever absorbs the scaling pressure; the workspace stays small. That is the structural reason the approach is meant to hold up as corpora grow.

## What the numbers say

On BrowseComp-Plus, Dr-DCI reports **71.2%**, rising to **73.3%** when context reset is used. The context-reset variant is worth flagging on its own: it suggests that periodically clearing accumulated state — rather than letting the agent's context grow monotonically through a long search — is not just a memory-management convenience but something that can improve task outcomes. In a long agentic loop, stale context is a liability, and a clean reset around the evolving workspace appears to help.

The more interesting claim for a practitioner is the range. Dr-DCI is reported to remain effective from **100K to 20M documents** — a 200× spread. Holding performance across that range is precisely the property that distinguishes a method that scales from one that merely works on a benchmark-sized index. Many techniques degrade quietly as the corpus grows; the headline here is that this one is claimed not to.

Against baselines, Dr-DCI is reported to outperform:

- **raw DCI** — the precision-first approach without the retriever steering it,
- **BM25** — the strong, stubbornly competitive sparse-retrieval baseline,
- **trained search-agent baselines** — agents specifically trained for the search task.

And it does so while *reducing tool calls, time, and cost*. This is the part that should catch a builder's attention. Accuracy gains in agentic systems are often bought with more steps — more retrievals, more tool invocations, more wall-clock time, more spend. A result that moves accuracy up *and* the cost curve *down* at the same time is the combination worth caring about, because it points at a genuinely better operating point rather than a different position on the same trade-off frontier.

## Why the architecture, not just the score, is the contribution

It would be easy to read Dr-DCI as one more entry on a leaderboard. The more durable idea is the one in the design: treat the agent's environment as a *dynamic workspace* that the retriever populates, and confine precise operations to that workspace instead of the full corpus.

This reframes the relationship between retrieval and agentic reasoning. In the conventional pipeline, retrieval is a preprocessing step that feeds the agent and then gets out of the way. Here it is an ongoing steering signal, continuously shaping what the agent can see and act on. The workspace becomes the unit of scaling: keep it bounded, and the expensive precise operations stay cheap no matter how large the underlying store gets. That is a clean separation of concerns — recall is the retriever's job, precision is DCI's job, and scalability falls out of keeping them apart.

## The appropriate amount of skepticism

The results are notable, and they are also, by the framework's own framing, **not yet independently verified**. That caveat matters and should temper how the numbers are read. Benchmark gains can be sensitive to evaluation setup; efficiency claims depend heavily on what is being counted and how; and a 200× scalability range is exactly the kind of claim that deserves reproduction before it is treated as settled. The honest summary is that Dr-DCI presents a compelling combination of accuracy and efficiency, with an architecture whose logic is easy to follow — and that the next step is for others to confirm it.

If the results hold, the takeaway for anyone building retrieval-augmented agents is concrete: the corpus is not the workspace. Let a retriever steer a small, evolving local environment, run your precise operations there, and you may get recall, precision, and scale at once — at lower cost than the loop you are running today.

## Sources
- https://arxiv.org/abs/2606.14885
