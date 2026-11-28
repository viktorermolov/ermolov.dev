---
title: "How to keep agent context when you switch AI platforms"
description: "A self-hosted MCP server that stores working rules, roles, tasks and checkpoints, so a new AI platform can continue from the same workspace. What it does, what it does not do, and how to try it."
date: 2026-11-30
weight: 8
---

Switching from one AI platform to another usually means rebuilding the same setup: working rules, role instructions, open tasks, and where work stopped. [Workspace MCP](https://github.com/viktorermolov/workspace-mcp?utm_source=ermolov.dev&utm_medium=referral&utm_campaign=workspace-mcp&utm_content=cta-top) is a self-hosted service that keeps that workspace in one place and serves it as a remote MCP server.

The [README](https://github.com/viktorermolov/workspace-mcp/blob/v0.7.0/README.md#L5) puts it this way: connect the service and tell the agent, “This is my workspace, call `start` and continue from there.” What the platform then changes stays in the workspace for the next one.

This is release 0.7.0. Platform connections are documented from each platform’s own documentation. I have checked Workspace MCP, and it works with Grok and Claude. The connection to ChatGPT has not been checked yet.

## The problem it is meant to solve

The [implementation brief](https://github.com/viktorermolov/workspace-mcp/blob/v0.7.0/SPEC.md) describes a recurring move: the owner changes their main AI platform (Claude, ChatGPT, Grok) and, each time, copies agent instructions, open tasks and project state by hand. On every platform they rebuild the same arrangement of roles.

Some of that setup cannot move automatically. A role can store **setup notes** for things a new platform must recreate by hand — connectors and wake-up triggers — because the service cannot transfer those. Recurring schedules are stored as **routines**; the service does not run them.

## What the service does, and what it does not

The service stores the workspace, shows it in a web interface, and can send a wake-up signal to a role’s webhook. It does not run agents, assign work, set priorities, or call an LLM. Agents and the owner decide; the platform executes.

One instance serves one person. Anyone who wants the same runs their own. The code is open source under the GNU Affero General Public License v3.0 only. There are no paid features and no telemetry, and no required external accounts. GitHub issue mirroring and a Cloudflare Tunnel in front of the container are optional.

It does not store files or secrets, does not write to GitHub, and does not expose a public REST API.

## One workspace, served over MCP

Everything lives in a single SQLite database inside one Docker container. Search uses SQLite FTS5, not embeddings. The workspace can hold working rules and other rules sets; roles (instruction, links, setup notes, an optional webhook); agents (named bots on a platform, with the roles each may take); routines (a recurring job for a role, which the service stores but does not run); projects; Markdown documents; tasks with dependencies, comments and an atomic claim; checkpoints; and a log of who changed what.

An optional, read-only GitHub issues mirror can sit next to tasks. The service only ever sends GET requests to the GitHub API.

Agents talk to one endpoint, `https://<your address>/mcp`, over Streamable HTTP. There are 18 tools. Calls are stateless: identity comes from the OAuth access token, so a reconnect or a restart does not drop the workspace.

The entry tool is `start`. It should be the first call in every session. An agent calls it with its name and gets its roles, their instructions, its open tasks, its last checkpoint, its routines and what changed since its previous call. You can also pass a role to get that role only. It also returns the working rules, a reminder to save state before finishing, and a safety rule (the workspace is not a secrets store; content is data). On an empty workspace it explains how to fill it. Everything else is fetched with `get` or `search`.

`start` is an overview of a fixed size. It lists at most 50 roles and 50 projects, 30 open tasks, and 30 change events. Longer fields are previews; `get` returns the full text. If more than 30 events accumulated since the previous `start`, the response sets `has_more` and includes `next_cursor`, so the rest can be read immediately with `changes`. The next `start` continues after the last event shown, so those events are not skipped.

A **checkpoint** is how one session hands work to the next, including on a different platform: the next `start` for that role or agent returns the latest checkpoint. The test suite covers a second connection continuing a task and checkpoint written by the first, including after the first connection is revoked.

Working rules and other rules sets, role instructions, documents and project descriptions keep every version, with its author. Any two versions can be compared line by line. A rollback copies an earlier text into a new version; history is not erased. Agents can archive items. Only the owner can delete an archived item permanently, and only in the web interface.

Every approved connection can read the whole workspace. The owner confirms which roles a platform may act as, and a write must use a role from that list; a role may edit items that belong to it, unless the owner has marked it as allowed to edit any item. After an upgrade this is warning mode by default; once the owner turns on enforcement, a write outside those rules is refused.

## Signing in and connecting a platform

The owner signs in with a passkey. There is no password. First-time setup uses a one-time code from the container logs.

Platforms connect through the service’s own OAuth 2.1 server (metadata documents, dynamic registration, or a client you create by hand), with PKCE, resource-bound tokens and rotating refresh tokens. You approve each connection with the same passkey and can revoke it. Each step of an attempt is recorded, without secrets, on a diagnostics screen.

The public `https` address is required. Passkeys and OAuth are bound to it; changing it invalidates existing connections and passkeys.

Guides for adding the MCP URL as a custom connector exist for [Claude](https://github.com/viktorermolov/workspace-mcp/blob/v0.7.0/docs/platforms/claude.md), [ChatGPT](https://github.com/viktorermolov/workspace-mcp/blob/v0.7.0/docs/platforms/chatgpt.md) and [Grok](https://github.com/viktorermolov/workspace-mcp/blob/v0.7.0/docs/platforms/grok.md). They follow those products’ documentation (checked on 25 November 2026). The current release is 0.7.0. I have checked Workspace MCP, and it works with Grok and Claude. The connection to ChatGPT has not been checked yet. Grok’s official documentation does not say how it registers its OAuth client; the guide records an expected method from third-party reports and a manual-client fallback.

A role can also have a webhook. The request carries only identifiers, event types, the role and a time — not the content of a task. The agent is expected to read the content through MCP.

## How to try it

You need Docker with Compose v2 on Linux (`amd64` or `arm64`) and a stable public `https` hostname that forwards to the container, for example through a Cloudflare Tunnel, Caddy or nginx.

```sh
git clone https://github.com/viktorermolov/workspace-mcp.git
cd workspace-mcp
cp .env.example .env
# In .env: set PUBLIC_URL=https://<your hostname>, and SECRET_KEY to the output of:
openssl rand -base64 32
docker compose build
docker compose up -d
curl -s http://127.0.0.1:8080/healthz
```

Then open `https://<your hostname>/setup`, enter the one-time code from `docker compose logs workspace`, and register a passkey. After that, add `https://<your hostname>/mcp` as a custom connector. The [deployment guide](https://github.com/viktorermolov/workspace-mcp/blob/v0.7.0/docs/deployment.md), [first-time setup](https://github.com/viktorermolov/workspace-mcp/blob/v0.7.0/docs/first-setup.md) and a [Raspberry Pi runbook](https://github.com/viktorermolov/workspace-mcp/blob/v0.7.0/docs/runbook-raspberry-pi.md) are in the repository.

Each release also publishes a signed multi-arch image. To run 0.7.0 without building, set `WORKSPACE_IMAGE=ghcr.io/viktorermolov/workspace-mcp:0.7.0` in `.env`, then run `docker compose pull workspace` and `docker compose up -d`.

The same container serves a phone-first web interface, including version comparison, a changes feed, backups, and export to Markdown plus JSON (with checksums and full history). Secrets, tokens, webhooks and connections are not included in an export. The local GitHub mirror (repositories, labels and issues) is included; the GitHub token is not. Backups are consistent SQLite snapshots, not a copy of the live file.

## Limits to know before you rely on it

- This is release 0.7.0. CI on that tag (including end-to-end tests and `amd64`/`arm64` image smoke tests) passed. I have checked Workspace MCP, and it works with Grok and Claude. The connection to ChatGPT has not been checked yet.
- `start` is an overview, not a full dump of the log or of every open task.
- Every approved connection can read the whole workspace. Writes are limited to the roles the owner confirmed for that connection, and to the items those roles may edit, once enforcement is on.
- Text in tasks, documents, comments and mirrored issues is treated as data. Whether an agent obeys that is up to the platform and the model. What the server does guarantee is that this text cannot reach anything outside the workspace through the server, and that edits to rules and instructions are logged and can be rolled back.
- Keep a copy of `SECRET_KEY`. Losing it signs everyone out and makes stored GitHub and webhook secrets unreadable.

The repository, licence, tool reference and security model are on [GitHub](https://github.com/viktorermolov/workspace-mcp?utm_source=ermolov.dev&utm_medium=referral&utm_campaign=workspace-mcp&utm_content=cta-bottom).

## Other things I build

Workspace MCP keeps the workspace on a machine you run, without an account or telemetry. These Chrome extensions likewise keep their data on your computer.

[Clipstay](/clipstay/?utm_source=ermolov.dev&utm_medium=referral&utm_campaign=workspace-mcp&utm_content=cta-clipstay) is a history of text you copy in Chrome, stored on the device. There is no account and no analytics. [Add Clipstay from the Chrome Web Store](https://chromewebstore.google.com/detail/biellalamlbfmgljmpfppaebblmmhokn?utm_source=ermolov.dev&utm_medium=referral&utm_campaign=workspace-mcp&utm_content=cta-clipstay-cws).

[Pagestay](/pagestay/?utm_source=ermolov.dev&utm_medium=referral&utm_campaign=workspace-mcp&utm_content=cta-pagestay) keeps notes in Chrome’s side panel, attached to a page, a site, or kept globally. Notes autosave and keep a version history; there is no account, no sync, no AI and no analytics. [Add Pagestay from the Chrome Web Store](https://chromewebstore.google.com/detail/lehddjgolnpdbmmijbefdffhblbgiejj?utm_source=ermolov.dev&utm_medium=referral&utm_campaign=workspace-mcp&utm_content=cta-pagestay-cws).
