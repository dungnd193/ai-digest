---
title: Relational Structural Causal Models for Generalizable Causal Reasoning
date: '2026-06-16T18:15:59+07:00'
lang: en
slug: relational-structural-causal-models-for-generalizable-causal-reasoning
categories:
- AI Research / Causal Inference
tags:
- causal-inference
- structural-causal-models
- machine-learning
- research
- generalization
summary: This paper extends Pearl's structural causal models to relational settings
  where the objects and their relationships vary, enabling causal reasoning that generalizes
  to unseen combinations of objects. The authors show that causal and observational
  queries over novel object combinations are not identifiable without additional assumptions,
  then introduce relational causal graphs with symbolic identification criteria, including
  under unobserved confounding. They propose relational neural causal models, a provably
  correct method that outperforms non-relational baselines on simulated traffic scenes.
  The work is a meaningful theoretical contribution toward compositional, generalizable
  causal inference, though its near-term practical impact remains research-stage.
draft: false
---

Causal inference has a long-standing tension at its core. Pearl's structural causal models (SCMs) give us a rigorous language for reasoning about interventions and counterfactuals, but they assume a fixed set of variables. Define the model over variables `A`, `B`, and `C`, and that is the world you can reason about. The moment the world contains different objects, or the same objects arranged in a new configuration, the model has nothing to say. For domains that are inherently relational — scenes full of objects whose number and relationships shift from one instance to the next — this is a serious limitation.

A recent line of work tackles this head-on by extending structural causal models to relational settings, where both the objects and the relationships among them vary. The goal is ambitious: causal reasoning that *generalizes to unseen combinations of objects*, rather than reasoning that is locked to the specific entities present at training time.

## Why fixed-variable SCMs fall short

The classical SCM is a closed system. Its causal graph enumerates a specific set of nodes, and identification results — the theorems that tell us whether a causal query can be computed from observational data — are stated over that fixed graph. This is exactly what you want when the system under study has stable, named variables.

It breaks down when the entities are interchangeable and combinatorial. Consider a scene composed of several objects that interact. Train on scenes with one arrangement of objects, then ask a causal question about a scene containing a combination you never observed. A non-relational SCM cannot transfer: it has no representation of "an object of this type" as opposed to "this particular object." Each new combination is, formally, a new model.

What you want instead is a model that captures the causal mechanism *at the level of object types and relationships*, so that the same mechanism applies regardless of which specific objects instantiate it. That is the compositional promise: learn the pieces once, recombine them freely.

## Generalization is not free

The first substantive result in this work is a negative one, and it is worth dwelling on. Causal and observational queries over *novel* object combinations are **not identifiable without additional assumptions**.

This matters because it punctures an intuition. One might hope that if you learn the right relational mechanism, generalization to new combinations follows automatically. It does not. There is genuine ambiguity: multiple underlying models can agree on everything you have observed yet disagree on queries about unseen configurations. Without further structure or assumptions, those queries are underdetermined.

Establishing this up front is what makes the rest of the contribution principled rather than heuristic. If you skip the identifiability analysis, you risk building a method that appears to generalize on benchmarks while having no guarantee — and no characterization of *when* it can possibly work.

## Relational causal graphs and symbolic identification

To make identification tractable, the authors introduce **relational causal graphs** equipped with **symbolic identification criteria**. The shift from "graph over concrete variables" to "graph over relational structure" is the key move: the criteria are stated symbolically, so they apply to whole families of object combinations rather than a single instantiation.

Crucially, the identification analysis extends to the case of **unobserved confounding** — the situation where hidden common causes link variables, which is precisely where naive causal inference goes most wrong. Handling confounding symbolically, in the relational setting, is what gives the framework teeth. It means the criteria can tell you whether a query over a novel combination is identifiable even when not everything relevant is observed.

In other words, the framework does two things at once:

- It tells you *which* causal queries over unseen object combinations are answerable, given stated assumptions.
- It does so at the symbolic, relational level, so the answer transfers across configurations instead of being recomputed per instance.

## Relational neural causal models

Theory that characterizes identifiability needs a companion method that actually estimates the quantities. Here that is **relational neural causal models**, presented as a **provably correct** approach — meaning it is designed to respect the identification criteria rather than merely fit data and hope for the best.

The combination is the point. A purely neural model might generalize empirically but offer no guarantee that its answers correspond to valid causal quantities. A purely symbolic framework characterizes what is answerable but does not estimate it from data. Pairing them yields a method whose correctness is tied to the identification theory, while still being learnable.

Empirically, the relational neural causal models are evaluated on **simulated traffic scenes** and **outperform non-relational baselines**. Traffic is a natural testbed for this kind of claim: scenes vary in the number of agents and their spatial and interactive relationships, so generalizing to unseen combinations is exactly the challenge. Beating non-relational baselines is the expected signature of a method that has captured mechanism at the relational level rather than memorizing specific configurations.

## What this is, and what it is not

It is worth being precise about the significance. This is a **theoretical contribution** toward compositional, generalizable causal inference. Its strengths are conceptual clarity and rigor: it formalizes relational SCMs, proves that naive generalization is not identifiable, supplies symbolic criteria (including under confounding), and backs them with a provably correct estimation method validated in simulation.

What it is not — at least not yet — is a deployed practical tool. The evaluation is on simulated scenes, and the near-term practical impact remains **research-stage**. The honest framing is that this advances the foundations: it tells us what compositional causal reasoning *can* look like and under what assumptions it is well-posed, while the path to messy real-world systems is still ahead.

## Why it matters anyway

The broader significance is that it connects two threads the field has largely kept separate. Causal inference brings rigor about interventions and counterfactuals but assumes a static variable set. Compositional and relational modeling brings generalization across varying objects but typically without causal guarantees. By extending SCMs into relational territory — and being upfront about the identifiability barriers — this work sketches what a unification could look like.

For practitioners building systems in inherently relational domains, the takeaways are immediate even before the methods mature:

- Generalizing causal claims to unseen object combinations is *not* automatic; expect to need explicit additional assumptions, and know that without them your queries may be underdetermined.
- Identification, including under unobserved confounding, can be reasoned about symbolically at the relational level rather than re-derived for every configuration.
- Methods that are tied to identification criteria buy you correctness guarantees that a freely-fit neural model does not provide.

The compositional dream — learn causal mechanisms over object types once, then reason about any arrangement of them — is still a dream in practice. But this work makes it a more rigorous one, with a clear map of which parts are answerable and which require us to bring assumptions to the table.

## Sources
- https://arxiv.org/abs/2606.14892
