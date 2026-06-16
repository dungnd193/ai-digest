---
title: Open-weights model distilled from Anthropic's short-lived Fable-5 preview
date: '2026-06-16'
lang: en
slug: open-weights-model-distilled-from-anthropic-s-short-lived-fable-5-preview
categories:
- Open-Source AI
tags:
- open-weights
- distillation
- export-controls
- unverified
- huggingface
summary: A community developer released Qwable-v1, an open-weights Qwen3.6-35B-A3B
  model reportedly distilled from Anthropic's brief Fable-5 preview using 4,659 cleartext
  agentic-coding traces, with the model, GGUF quantizations, and SFT dataset published
  on Hugging Face under AGPL-3.0. The post claims Fable-5 (80.3% SWE-bench Pro) was
  suspended globally after about four days under U.S. export-control directives, and
  that its tool surface (e.g., str_replace_editor) leaked into the distilled weights.
  These are unverified community claims sourced from Reddit and should be treated
  cautiously. If true, it raises notable questions about distillation from preview
  models, export controls, and inadvertent leakage of proprietary tool interfaces.
draft: true
---

Open weights have a way of appearing in places no one planned for. The latest example, if the claims hold up, is a small distilled model that purportedly carries fingerprints of a frontier preview that was pulled offline almost as soon as it appeared. The story is worth examining not because the details are confirmed — they are not — but because of the questions it raises if any part of it is true.

## What was reportedly released

A community developer published a model called **Qwable-v1**, described as an open-weights `Qwen3.6-35B-A3B` checkpoint. According to the release, it was distilled from Anthropic's short-lived **Fable-5** preview using **4,659 cleartext agentic-coding traces**. The author published the model weights, GGUF quantizations for local inference, and the supervised fine-tuning (SFT) dataset on Hugging Face, all under **AGPL-3.0**.

The accompanying post makes several striking claims:

- Fable-5 reportedly scored **80.3% on SWE-bench Pro**.
- The preview was allegedly **suspended globally after about four days**, attributed to **U.S. export-control directives**.
- The model's **tool surface** — including an editing tool named `str_replace_editor` — supposedly **leaked into the distilled weights**.

Before going further, the necessary caveat: **these are unverified community claims, sourced from Reddit.** None of the numbers, the timeline, or the export-control explanation has been independently confirmed. Treat everything that follows as conditional reasoning about a scenario, not reporting on established fact.

## Why distillation from a preview is interesting

Distillation — training a smaller "student" model to imitate the outputs of a larger "teacher" — is a well-worn technique. What makes this case notable is the alleged *source*: a frontier preview that was available only briefly.

A few thousand agentic-coding traces is a small dataset by pretraining standards, but for SFT targeting a specific behavior — agentic coding — it can be enough to transfer a meaningful slice of capability. The implied workflow is straightforward:

1. Collect transcripts of the preview model performing coding tasks (the "traces").
2. Format them as supervised examples.
3. Fine-tune an open base model to reproduce the teacher's behavior.

If the traces were captured in cleartext during the preview window, the suspension of the upstream model would not undo the capture. The data, once collected, outlives the API. That asymmetry — ephemeral access, durable artifacts — is the crux of the whole episode.

## The leaked tool surface

The most technically revealing claim is the alleged leakage of a proprietary **tool interface** into the student weights. Agentic models operate through tools: structured function calls like file editors, shell runners, and search utilities. The way a model is taught to name and invoke those tools is part of its scaffolding.

The named example, `str_replace_editor`, is exactly the kind of artifact that would bleed through distillation. If the teacher's traces contain calls to a specifically named editing tool, a student trained to imitate those traces will learn to emit the same calls — including the tool's name and calling convention. The student doesn't "know" the tool is proprietary; it just reproduces the patterns it was shown.

This is a subtle form of leakage. It isn't weight theft and it isn't a prompt dump. It's **behavioral residue**: the distilled model inadvertently encodes the shape of an interface its creators never published. For anyone reverse-engineering how a frontier agent is wired, that residue is informative.

## The questions worth sitting with

Assume, for the sake of argument, that the core of the story is accurate. Several issues follow.

**Distillation from previews.** Preview access is usually framed as evaluation, not as a training corpus. If a brief window of access is enough to capture transferable agentic capability, the line between "trying a model" and "harvesting a model" becomes thin. Terms of service routinely prohibit using outputs to train competing models, but enforcement against an anonymous community release is a different problem entirely.

**Export controls as a distribution lever.** The claim that a model was withdrawn under export-control directives — if true — points at a tension that compute and policy people have flagged for a while: controls can govern an API endpoint, but they govern *derived artifacts* far less cleanly. A model suspended for policy reasons does not retract whatever was distilled from it during its short life, and an AGPL-3.0 release is designed to propagate freely.

**Inadvertent interface leakage.** The `str_replace_editor` detail is a reminder that proprietary scaffolding can escape through behavior, not just through code or weights. Teams shipping agentic models may need to think about tool naming and calling conventions as potentially observable surface area, recoverable by anyone who can collect enough transcripts.

## Reading this responsibly

It is easy to let a vivid narrative — a frontier model pulled in four days, secret traces, a leaked tool name — substitute for evidence. It shouldn't. The benchmark figure, the suspension, the export-control rationale, and the leakage are all assertions from an unverified community post, and any of them could be wrong, exaggerated, or fabricated.

What makes the episode worth discussing isn't whether this particular release is exactly as described. It's that the *mechanism* is entirely plausible: ephemeral access plus durable capture plus permissive licensing equals artifacts that outlast the conditions of their creation. Whether or not Qwable-v1 is what its author says it is, that mechanism is real, and the governance questions around it are not going away.

So hold the specifics loosely and the structural questions firmly. If a model can be meaningfully distilled from a four-day window of access — and if its weights can quietly carry a competitor's tool interface — then the hard problems aren't about one anonymous upload. They're about what "preview" and "withdrawal" actually mean once outputs are flowing.

## Sources
- https://www.reddit.com/r/LocalLLaMA/comments/1u6zj79/claude_fable_5_distilled/
