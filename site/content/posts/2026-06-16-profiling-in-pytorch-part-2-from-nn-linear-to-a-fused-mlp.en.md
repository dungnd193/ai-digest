---
title: 'Profiling in PyTorch (Part 2): from nn.Linear to a fused MLP'
date: '2026-06-16'
lang: en
slug: profiling-in-pytorch-part-2-from-nn-linear-to-a-fused-mlp
categories:
- Engineering / Performance
tags:
- pytorch
- profiling
- kernel-fusion
- performance
- tutorial
summary: This second installment of a PyTorch profiling series walks through optimizing
  an MLP from naively stacked nn.Linear modules to a single fused implementation.
  It uses PyTorch's profiling tools to locate performance bottlenecks and shows how
  kernel fusion cuts overhead and improves throughput. The post is a practical, hands-on
  guide for practitioners optimizing model inference and training. It offers solid
  educational value without being broadly newsworthy.
draft: true
---

This is the second part of a series on profiling PyTorch code. In the first installment we set up the tooling and learned to read a profile; here we put it to work on a concrete optimization. The target is a multilayer perceptron — about as ordinary a building block as deep learning has — and the journey takes it from a naive stack of `nn.Linear` modules to a single fused implementation. Along the way the profiler does what it does best: it tells us where the time actually goes, rather than where we assume it goes.

## The naive MLP

Most of us write an MLP the obvious way. You reach for `nn.Linear`, stack a few of them with activations in between, and wrap the whole thing in `nn.Sequential`:

```python
import torch
import torch.nn as nn

mlp = nn.Sequential(
    nn.Linear(in_features, hidden),
    nn.ReLU(),
    nn.Linear(hidden, hidden),
    nn.ReLU(),
    nn.Linear(hidden, out_features),
)
```

This is correct, readable, and exactly what you want most of the time. It also leaves performance on the table, and the interesting question is *where*. Each `nn.Linear` is its own module with its own forward call. Each activation is another. From PyTorch's point of view, running this MLP means dispatching a sequence of discrete operations, each one launching its own work and handing intermediate results to the next.

That structure is invisible when you only look at wall-clock time. It becomes visible the moment you profile.

## Letting the profiler find the bottleneck

The point of a profiling series is that you don't guess. Instead of reasoning about what *should* be slow, you instrument the model and let the measurements speak. PyTorch's profiling tools let you record a forward pass (or a training step) and then break the runtime down by operation: how many times each kernel ran, how long it took, and how much of the total each one accounts for.

When you profile the naive MLP, a recurring pattern tends to emerge. A meaningful share of the time isn't spent on the actual mathematics — the matrix multiplies that do the real work — but on the overhead that surrounds them. Every separate operation carries a fixed cost: dispatching the call, launching the kernel, reading and writing intermediate tensors. Individually each cost is small. Stacked across many small operations, they add up, and for an MLP with modest layer sizes they can dominate.

This is the core lesson of profiling as a discipline. The bottleneck is rarely where intuition points. You have to look.

## Why fusion helps

Once the profile shows that overhead — not arithmetic — is the limiting factor, the optimization strategy follows naturally. If the cost is per-operation, reduce the number of operations. That is exactly what **kernel fusion** does: it collapses several distinct operations into one, so the work that used to require multiple dispatches and multiple round trips through memory happens in a single pass.

A fused MLP applies the same idea to the whole block. Rather than treating each linear projection and each activation as an isolated module, you express the computation so that the underlying machinery can execute more of it together. The math is unchanged — the same projections, the same activations, the same output. What changes is the *shape* of the work handed to the hardware: fewer kernel launches, fewer intermediate tensors materialized only to be immediately consumed, less fixed overhead per element of useful computation.

The payoff shows up in two ways. Overhead drops, because there is simply less of the per-operation tax to pay. And throughput improves, because the hardware spends a larger fraction of its time on the computation that matters instead of on bookkeeping between steps.

## Measuring the win

Fusion is satisfying in theory, but the series insists on closing the loop. After rewriting the MLP in fused form, you profile again under the same conditions and compare. This is the part practitioners skip at their peril: an optimization is only real if the measurement confirms it. Re-profiling tells you whether the overhead you targeted actually shrank, whether the time really did migrate toward the productive kernels, and whether the change earned its added complexity.

That before-and-after comparison is the whole methodology in miniature:

- **Profile** the current implementation and identify where time is genuinely spent.
- **Form a hypothesis** about the cause — here, per-operation overhead from many small kernels.
- **Change** the implementation to attack that specific cause — here, fusion.
- **Re-profile** to confirm the time moved the way you predicted.

## Takeaways for your own models

The fused MLP is a worked example, but the habits generalize to any inference or training code you want to make faster.

- **Default to clear code, optimize with evidence.** The naive `nn.Linear` stack is the right starting point. Reach for fusion when the profiler justifies it, not before.
- **Distinguish overhead from computation.** Many real-world slowdowns aren't about doing too much math; they're about doing it in too many small pieces. Profiling is how you tell the difference.
- **Fewer, larger operations tend to win.** Reducing the number of distinct kernels — through fusion or otherwise — cuts dispatch cost and memory traffic, which is where throughput is often quietly lost.
- **Always re-measure.** An optimization without a follow-up profile is a guess wearing a confident expression.

None of this requires exotic tooling or a rewrite of your training loop. It requires the willingness to measure first, change second, and measure again. Take the same MLP you already have, profile it, and see whether overhead is eating your throughput — then decide, with data in hand, whether a fused version is worth building.

## Sources
- https://huggingface.co/blog/torch-mlp-fusion
