---
title: "What makes automation dependable?"
description: "Dependable automation plans for duplicate events, provider outages, retries and inputs that need a person, and makes every failure visible and recoverable."
date: 2026-09-29
weight: 3
---

An automation that works in a demo handles the happy path. An automation a business can rely on also handles everything around it: the event that arrives twice, the provider that is down for an hour, the input nobody anticipated. Most of the engineering effort goes into those cases.

## Expect duplicates

Webhooks are retried, users click twice, and jobs restart after a crash. The same event will eventually be processed more than once.

Design each step to be idempotent: give every unit of work a stable identifier, record what has already been done, and make repeating a step safe. Sending the same notification twice, or creating the same invoice twice, should be prevented by design rather than by luck.

## Expect providers to fail

Every external service is sometimes slow, rate-limited or unavailable. Retries with backoff handle short outages, but they need limits. A retry loop without a ceiling can turn a brief incident into a flood of requests or a queue that never drains.

Distinguish temporary failures from permanent ones. A timeout is worth retrying; an invalid request usually is not. Store enough context with each failed item that it can be retried later without reconstructing it from memory.

## Keep people in the loop where judgment is needed

Some inputs should not be handled automatically: an unusual amount, an ambiguous request, a document the system cannot read with confidence. A dependable automation recognizes these and routes them to a person with the context they need to decide quickly.

This is not a failure of the automation. It is what lets the automated path stay simple and trustworthy for everything else.

## Make failures visible and recoverable

When something goes wrong, the right person should know, and should be able to fix it without reading code. That means:

- alerts for failures that need attention, and silence for ones that recover on their own;
- a clear state for every item: pending, done, retrying, or waiting for a person;
- a way to retry or resolve an item once the cause is fixed;
- logs that record what happened without exposing sensitive data.

## The standard to aim for

An automation should reduce the work of operating a business, including on the days when something goes wrong. If a failure means someone has to dig through logs, guess what was processed and repair data by hand, the automation has moved the work rather than removed it. Planning for duplicates, outages and human judgment from the start is what makes the time savings last.
