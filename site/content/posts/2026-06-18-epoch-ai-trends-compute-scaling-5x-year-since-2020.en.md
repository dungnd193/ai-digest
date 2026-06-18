---
title: 'Epoch AI trends: compute scaling ~5x/year since 2020'
date: '2026-06-18T17:36:06+07:00'
lang: en
slug: epoch-ai-trends-compute-scaling-5x-year-since-2020
categories:
- Research
tags:
- epoch-ai
- compute
- scaling
- trends
- data
summary: Epoch AI's 'Trends in Artificial Intelligence' tracks frontier scaling metrics,
  showing training compute growing roughly 5x per year since 2020 and the total stock
  of AI chips growing 3.4x per year. Pre-training compute efficiency improves about
  3.0x per year while chip performance per dollar rises 37% per year, and frontier
  data centers now span roughly 500k–1.1M H100-equivalents. These figures provide
  a rigorous, quantitative baseline for understanding the pace and economics of AI
  scaling. The data is widely cited in strategy and policy discussions about compute's
  trajectory.
draft: false
---

## The Numbers Behind the Scaling Story

For years, "AI is scaling fast" has been the kind of claim everyone repeats and no one quantifies. Epoch AI's *Trends in Artificial Intelligence* exists to fix that. It tracks the frontier metrics that actually drive the field — how much compute goes into training, how many chips exist to run it, and how efficiently both are improving — and turns the hand-waving into rates you can reason about.

The headline figure is the one worth internalizing first: since 2020, the compute used to train frontier models has grown roughly **5x per year**. That is not a one-off spike. It's a sustained trend, compounding annually, and it reframes how you should think about almost everything downstream.

## What 5x a Year Actually Means

Compounding is easy to underestimate. A 5x annual growth rate doesn't just mean "bigger models." Stretched over a few years, it means training runs that dwarf their predecessors by orders of magnitude. Each generation of frontier model isn't an incremental step up from the last — it sits on a compute budget multiples larger.

This is the single most important lens for reading frontier AI. When a new model arrives with capabilities that feel discontinuous, the compute curve is usually the quiet explanation. The 5x figure gives you a baseline expectation: absent that growth, you'd be surprised by a leap; with it, the leap is roughly what the trend predicts.

It also sets a hard question for anyone forecasting the field. A rate this steep cannot continue indefinitely without running into physical and economic walls — power, capital, chip supply. Knowing the rate is the first step to reasoning about when and how it bends.

## The Inputs: Chips and Efficiency

Training compute is the output. Epoch's data also tracks the inputs that produce it, and they tell a more textured story.

- **The total stock of AI chips is growing about 3.4x per year.** This is the raw industrial capacity of the field — the installed base of accelerators available to do work. Note that it grows more slowly than training compute itself, which implies that frontier runs are claiming a growing share of available compute, concentrating it rather than just riding overall hardware growth.

- **Pre-training compute efficiency is improving roughly 3.0x per year.** This is the algorithmic side: getting the same capability from less compute through better methods, architectures, and training recipes. It means a meaningful chunk of progress comes not from spending more, but from spending smarter.

- **Chip performance per dollar is rising about 37% per year.** This is the economic tailwind. Hardware doesn't just get faster; it gets cheaper per unit of useful work, which steadily lowers the cost floor for any given training run.

Stack these together and you see why the frontier moves so fast. Bigger training runs are powered simultaneously by more chips, better algorithms, and cheaper compute. The 5x training-compute growth is the product of multiple compounding curves pulling in the same direction — not a single lever.

## The Physical Frontier: Data Centers in H100-Equivalents

Abstract growth rates eventually become concrete infrastructure. Epoch's data puts the frontier data center at roughly **500k to 1.1M H100-equivalents**.

Expressing capacity in H100-equivalents is a useful normalization: it lets you compare facilities across different hardware generations on a common unit. And the magnitude is the point. We're talking about clusters whose scale is measured in hundreds of thousands to over a million top-tier accelerators — a scale that carries direct implications for power consumption, capital expenditure, and the physical siting of compute.

This is where the economics stop being a chart and start being buildings, substations, and supply chains. The range itself — spanning roughly a factor of two — also signals that "the frontier" is not a single point but a band of comparably-resourced players.

## Why a Rigorous Baseline Matters

The value of Epoch's work isn't any single number — it's that the numbers are measured rather than asserted. That distinction matters enormously the moment these figures leave research circles.

These trends are now widely cited in strategy and policy discussions about where compute is headed. When questions arise about export controls, energy demand, competitive dynamics, or the feasibility of future capabilities, the conversation increasingly leans on quantitative baselines like these. A shared, rigorous set of growth rates lets people argue about implications instead of arguing about the facts.

For practitioners, the takeaway is to treat these rates as a working model. If you're planning infrastructure, evaluating where capability is likely to be in a couple of years, or stress-testing a forecast, start from the measured trends:

- Training compute: ~5x/year
- AI chip stock: ~3.4x/year
- Pre-training efficiency: ~3.0x/year
- Performance per dollar: +37%/year
- Frontier cluster scale: ~500k–1.1M H100-equivalents

None of these guarantees the future — every compounding curve eventually meets a constraint. But starting from grounded numbers beats starting from intuition. That's the real contribution here: not a prediction, but a measured baseline from which honest predictions can be made.

## Sources
- https://epoch.ai/trends
