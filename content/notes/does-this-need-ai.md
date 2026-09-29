---
title: "Does this actually need AI?"
description: "How to decide whether a workflow needs a language model: start from representative inputs and a baseline, then let quality, cost and failure modes decide."
date: 2026-09-29
weight: 1
---

Most conversations about AI start with the tool. A better starting point is the work: what comes in, what should come out, and how you would know the result is right. Once that is written down, the question of whether a model belongs in the system usually answers itself.

## Start with representative inputs

Before choosing any approach, collect real examples of the inputs the system will see. Not the three tidy ones that come to mind first, but a sample that includes the awkward cases: incomplete forms, scanned documents, messages that mix two requests, data in the wrong field.

For each example, write down the output you would expect. This small set becomes the reference for every decision that follows. It shows how varied the inputs really are, and it gives you something concrete to measure against instead of a demo that happens to go well.

## Build a baseline first

With examples in hand, try the simplest solution that could work. For many workflows that is a deterministic one:

- routing by a known field, sender or keyword;
- validation rules and lookups against existing data;
- templates for predictable responses;
- a conventional integration between two systems that already have APIs.

If the baseline handles most of the examples correctly, it is often the right answer. It is faster, cheaper to run, easier to test and easier to explain when something goes wrong. The remaining cases may be rare enough for a person to handle.

## Where a model earns its place

Language models are useful where the input is genuinely variable and rules would never keep up: free-form messages, documents with inconsistent layouts, classification that depends on meaning rather than keywords, or drafting text that a person will review.

In those cases, test a model against the same examples as the baseline. Look at three things together:

- **Useful output.** How often is the result correct enough to use without rework?
- **Errors.** When it is wrong, how is it wrong? A missing field that a person can spot is very different from a confident, plausible mistake.
- **Cost.** What does each run cost in model usage, latency and review time, at the volume you actually expect?

A model that is slightly more accurate than a rule, but much more expensive and harder to predict, may not be the better choice.

## Design for the cases it gets wrong

If a model does make the cut, the system around it matters as much as the model itself. Structured outputs that can be validated, confidence thresholds, and a clear path to human review turn an impressive prototype into something a business can rely on.

Keep the evaluation examples after launch. When inputs change, a prompt is edited or a model version is updated, run them again. That turns "it seems fine" into a measurable check.

## The decision in short

Use AI when the variability of the input is the real problem and the measured quality justifies the cost and operational complexity. Use conventional software when a rule, lookup or integration solves the problem reliably. Often the best system combines both: deterministic steps for everything predictable, and a model only where judgment on unstructured input is needed.
