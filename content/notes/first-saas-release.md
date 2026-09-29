---
title: "What belongs in a first SaaS release?"
description: "A first SaaS release needs one narrow workflow that solves a real problem, plus the foundations that are costly to retrofit. Keep the rest proportionate."
date: 2026-09-29
weight: 2
---

A first release has one job: put a real workflow in front of real users and learn from how they use it. Scope creep usually comes from trying to anticipate every future need. The better question is which decisions are cheap to change later and which are not.

## One workflow, done properly

Pick the narrowest workflow that solves a real problem for a specific user, and make it work end to end. A person should be able to sign up, do the thing the product exists for, and get a useful result without a workaround.

That usually means leaving out features that feel essential in planning: extensive settings, several user roles, integrations with every tool a customer might use, a polished admin area. Each of these can be added once usage shows it matters.

## Foundations that are expensive to retrofit

Some parts of a SaaS product are hard to change after customers depend on them. These deserve attention from the start, even in a small release.

- **Identity.** How people sign in, how accounts are recovered, and how a user relates to an organization. Changing this later often means migrating every account.
- **Tenant boundaries.** Every query and file should be scoped to the right customer from day one. Adding isolation to a system built without it is slow and risky.
- **Billing foundations.** Even if pricing will change, the product needs a clear idea of who pays, for what, and what happens when a payment fails.
- **Deployment.** A repeatable way to ship changes, with environments and configuration kept out of the code.
- **Observability.** Logs, error reporting and a few meaningful metrics, so problems are visible before a customer reports them.

None of these needs to be elaborate. They need to exist, and they need to be correct.

## Keep the rest proportionate

Beyond those foundations, choose the simplest architecture that supports the workflow. A single well-structured application and one database carry most products a long way. Extra services, queues and abstractions each add operational cost; introduce them when a real constraint appears, not in anticipation of one.

Write down the important decisions and the reasons behind them. A short record of why something was built a certain way is often more valuable to the next stage of the product than an extra layer of architecture.

## What "done" looks like

A first release is ready when the core workflow works reliably for real users, the foundations above are in place, deployment is routine, and you can see what is happening in production. From there, the roadmap can be driven by how the product is actually used rather than by guesses made before launch.
