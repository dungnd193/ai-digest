---
title: 'DivInit: diverse query initialization beats parallel sampling in agentic search'
date: '2026-06-17T18:47:43+07:00'
lang: en
slug: divinit-diverse-query-initialization-beats-parallel-sampling-in-agentic-search
categories:
- Research
tags:
- agentic search
- retrieval
- multi-hop QA
- DivInit
- research
summary: This paper identifies first-turn query redundancy as the cause of diminishing
  returns when scaling breadth in agentic search, since parallel rollouts tend to
  issue near-identical opening queries and retrieve overlapping evidence. The authors
  introduce DivInit, a training-free method that samples multiple first-query candidates
  from a single call, selects k diverse seeds, and runs them as parallel trajectories.
  Across five open-weight models and eight benchmarks, DivInit delivers average gains
  of five to seven points on multi-hop QA at matched compute. The approach is attractive
  because it requires no retraining and applies broadly to retrieval-augmented agents.
draft: false
---

## The Hidden Tax of Scaling Breadth in Agentic Search

When you give a retrieval-augmented agent more compute, the intuitive move is to scale *breadth*: spin up several parallel rollouts, let each explore the question its own way, and aggregate the evidence they bring back. More trajectories, more coverage, better answers. That's the theory.

In practice, the returns flatten out fast. You double the number of parallel runs and the answer barely improves. The compute is real; the gains are not. This paper pins down why — and the culprit is almost embarrassingly simple.

## The problem is the first query

Parallel rollouts are supposed to diversify the search. But they tend to *converge on the very first move*. Given the same question, independently sampled trajectories overwhelmingly issue near-identical opening queries. And when the opening queries are the same, the retrieved evidence overlaps heavily.

This is the core insight: **first-turn query redundancy** is the bottleneck. You can run eight trajectories in parallel, but if seven of them open with effectively the same search, you've paid for eight rollouts and bought roughly the coverage of two. The breadth is nominal. Under the hood, the agents are crowding into the same corner of the retrieval space before they've had a chance to differentiate.

This reframes the diminishing-returns curve. The problem was never that parallelism doesn't help — it's that naive parallelism wastes most of its budget re-fetching evidence it already has. The redundancy is concentrated at turn one, where it does the most damage, because the opening query anchors everything downstream.

## DivInit: diversify the seed, not the sampler

The fix follows directly from the diagnosis. If the failure is redundant opening queries, then force the openings apart before you commit compute to full trajectories.

DivInit does exactly this, in three steps:

1. **Sample candidates from a single call.** Instead of launching k full rollouts and hoping they diverge, generate multiple first-query candidates up front from one model call.
2. **Select k diverse seeds.** From that candidate pool, pick a set of opening queries chosen for their diversity — distinct angles on the question rather than k restatements of the same search.
3. **Run the diverse seeds as parallel trajectories.** Each selected seed becomes the entry point for its own rollout, so the parallelism now starts from genuinely different positions in the evidence space.

The conceptual shift is small but consequential. Standard parallel sampling diversifies by *luck* — it relies on stochastic decoding to push trajectories apart, and at the critical first turn, decoding rarely cooperates. DivInit diversifies by *construction*. It moves the diversity decision to the one place where it pays off most and makes it explicit instead of leaving it to sampling temperature.

Crucially, this is **training-free**. There's no fine-tuning, no reward model, no new objective. You're reshaping how the agent is initialized, not what it learned. That keeps the method portable across whatever retrieval-augmented agent you already have.

## What the evaluation shows

The authors test the method across five open-weight models and eight benchmarks. On multi-hop QA — the setting where coverage of distinct evidence matters most, because the answer depends on chaining facts that no single query is likely to surface — DivInit delivers average gains of **five to seven points at matched compute**.

The "matched compute" qualifier is the part to dwell on. This isn't a story about spending more to get more. The comparison holds the budget fixed and changes only how that budget is allocated at the first turn. The same number of trajectories, the same retrieval calls — but seeded to diverge rather than left to collide. The gains come from spending the existing budget on non-overlapping evidence instead of redundant fetches.

That multi-hop is where the method shines is consistent with the diagnosis. Single-hop questions can often be answered from one good query, so opening-query redundancy costs little. Multi-hop questions need several independent pieces of evidence, and that's precisely where seven near-identical first queries leave the agent starved for the facts it actually needs.

## Why this matters beyond the benchmark

Two things make DivInit broadly attractive.

First, **it's free to adopt**. No retraining means no data pipeline, no compute spent on fine-tuning, and no risk of degrading a model's other capabilities. If you're running a retrieval-augmented agent today, the method slots in as a change to the initialization stage.

Second, **it generalizes**. Because the technique targets a structural property of parallel agentic search — redundant openings — rather than a quirk of any one model, it applies broadly across retrieval-augmented agents. The result replicating across five models and eight benchmarks supports that breadth rather than a single lucky configuration.

There's a more general lesson worth taking away. When scaling a dimension of inference stops paying off, the reflexive response is to question whether that dimension matters. DivInit suggests a better first question: *is the scaling actually buying diversity, or just repetition?* Parallelism only helps to the extent that the parallel branches do different things. Spend your diversity budget where the branches first diverge — the opening move — and the rest of the breadth you're already paying for starts to earn its keep.

## Sources
- https://arxiv.org/abs/2606.17209
