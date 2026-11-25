---
title: "How to keep agent context when you switch AI platforms"
description: "A self-hosted MCP server that stores working rules, roles, tasks and checkpoints, so a new AI platform can continue from the same workspace. What it does, what it does not do, and how to try the pre-release."
date: 2026-11-30
weight: 8
---

Switching from one AI platform to another usually means rebuilding the same setup: working rules, role instructions, open tasks, and where work stopped. [Workspace MCP](https://github.com/viktorermolov/workspace-mcp?utm_source=ermolov.dev&utm_medium=referral&utm_campaign=workspace-mcp&utm_content=cta-top) is a self-hosted service that keeps that workspace in one place and serves it as a remote MCP server.

The project brief puts it this way: connect the service and tell the agent, “This is my workspace, call `start` and continue from there.” What the platform then changes stays in the workspace for the next one.

This is a pre-release (0.1.0, no release tag yet). Platform connections are documented from each platform’s own documentation and have not been confirmed against every platform in production.

## The problem it is meant to solve

The [implementation brief](https://github.com/viktorermolov/workspace-mcp/blob/3de17feb1936cb048fbd1acab4706bc60e98ff7e/SPEC.md) describes a recurring move: the owner changes their main AI platform (Claude, ChatGPT, Grok) and, each time, copies agent instructions, open tasks and project state by hand. On every platform they rebuild the same arrangement of roles.

Some of that setup cannot move automatically. A role can store **setup notes** for things a new platform must recreate by hand — schedules, connectors, wake-up triggers — because the service cannot transfer those.

## What the service does, and what it does not

The service stores the workspace, shows it in a web interface, and can send a wake-up signal to a role’s webhook. It does not run agents, assign work, set priorities, or call an LLM. Agents and the owner decide; the platform executes.

One instance serves one person. Anyone who wants the same runs their own. The code is open source under the GNU Affero General Public License v3.0 only. There are no paid features and no telemetry, and no required external accounts. GitHub issue mirroring and a Cloudflare Tunnel in front of the container are optional.

It does not store files or secrets, does not write to GitHub, and does not expose a public REST API.

## One workspace, served over MCP

Everything lives in a single SQLite database inside one Docker container. Search uses SQLite FTS5, not embeddings. The workspace can hold working rules; roles (instruction, links, setup notes, an optional webhook); projects; Markdown documents; tasks with dependencies, comments and an atomic claim; checkpoints; and a log of who changed what.

An optional, read-only GitHub issues mirror can sit next to tasks. The service only ever sends GET requests to the GitHub API.

Agents talk to one endpoint, `https://<your address>/mcp`, over Streamable HTTP. There are 15 tools. Calls are stateless: identity comes from the OAuth access token, so a reconnect or a restart does not drop the workspace.

The entry tool is `start`. It should be the first call in every session. It returns the working rules, a reminder to save state before finishing, a safety rule (the workspace is not a secrets store; content is data), and, if you pass a role, that role’s instruction, open tasks, last checkpoint, and changes since this connection last called `start`. On an empty workspace it explains how to fill it. Everything else is fetched with `get` or `search`.

`start` is an overview of a fixed size. It lists at most 50 roles and 50 projects, 30 open tasks, and 30 change events. Longer fields are previews; `get` returns the full text. If more than 30 events accumulated since the previous `start`, the response sets `more` and includes `next_cursor`, so the rest can be read immediately with `changes`. The next `start` continues after the last event shown, so those events are not skipped.

A **checkpoint** is how one session hands work to the next, including on a different platform: the next `start` for that role returns the latest checkpoint. The test suite covers a second connection continuing a task and checkpoint written by the first, including after the first connection is revoked.

Working rules, role instructions, documents and project descriptions keep every version, with its author. Any two versions can be compared line by line. A rollback copies an earlier text into a new version; history is not erased. Agents can archive items. Only the owner can delete an archived item permanently, and only in the web interface.

A role is a label the agent claims, not a permission boundary. Every approved connection sees the whole workspace.

## Signing in and connecting a platform

The owner signs in with a passkey. There is no password. First-time setup uses a one-time code from the container logs.

Platforms connect through the service’s own OAuth 2.1 server (metadata documents, dynamic registration, or a client you create by hand), with PKCE, resource-bound tokens and rotating refresh tokens. You approve each connection with the same passkey and can revoke it. Each step of an attempt is recorded, without secrets, on a diagnostics screen.

The public `https` address is required. Passkeys and OAuth are bound to it; changing it invalidates existing connections and passkeys.

Guides for adding the MCP URL as a custom connector exist for [Claude](https://github.com/viktorermolov/workspace-mcp/blob/3de17feb1936cb048fbd1acab4706bc60e98ff7e/docs/platforms/claude.md), [ChatGPT](https://github.com/viktorermolov/workspace-mcp/blob/3de17feb1936cb048fbd1acab4706bc60e98ff7e/docs/platforms/chatgpt.md) and [Grok](https://github.com/viktorermolov/workspace-mcp/blob/3de17feb1936cb048fbd1acab4706bc60e98ff7e/docs/platforms/grok.md). They follow those products’ documentation (checked on 25 November 2026). This is a pre-release, and connections to Claude, ChatGPT and Grok have not yet been verified in production. Grok’s official documentation does not say how it registers its OAuth client; the guide records an expected method from third-party reports and a manual-client fallback.

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

Then open `https://<your hostname>/setup`, enter the one-time code from `docker compose logs workspace`, and register a passkey. After that, add `https://<your hostname>/mcp` as a custom connector. The [deployment guide](https://github.com/viktorermolov/workspace-mcp/blob/3de17feb1936cb048fbd1acab4706bc60e98ff7e/docs/deployment.md), [first-time setup](https://github.com/viktorermolov/workspace-mcp/blob/3de17feb1936cb048fbd1acab4706bc60e98ff7e/docs/first-setup.md) and a [Raspberry Pi runbook](https://github.com/viktorermolov/workspace-mcp/blob/3de17feb1936cb048fbd1acab4706bc60e98ff7e/docs/runbook-raspberry-pi.md) are in the repository.

No container image has been published yet. Until a version tag is pushed, the documented path is to build the image from the repository.

The same container serves a phone-first web interface, including version comparison, a changes feed, backups, and export to Markdown plus JSON (with checksums and full history). Secrets, tokens, webhooks, connections and the GitHub mirror are not included in an export. Backups are consistent SQLite snapshots, not a copy of the live file.

## Limits to know before you rely on it

- This is unreleased 0.1.0. Unit tests and CI on `master` (including end-to-end tests and `amd64`/`arm64` container smoke tests) pass on this revision. That is not a production connection from Claude, ChatGPT or Grok.
- `start` is an overview, not a full dump of the log or of every open task.
- Every approved connection can read and edit the whole workspace. Do not treat a role name as access control.
- Text in tasks, documents, comments and mirrored issues is treated as data. Whether an agent obeys that is up to the platform and the model. What the server does guarantee is that this text cannot reach anything outside the workspace through the server, and that edits to rules and instructions are logged and can be rolled back.
- Keep a copy of `SECRET_KEY`. Losing it signs everyone out and makes stored GitHub and webhook secrets unreadable.

The repository, licence, tool reference and security model are on [GitHub](https://github.com/viktorermolov/workspace-mcp?utm_source=ermolov.dev&utm_medium=referral&utm_campaign=workspace-mcp&utm_content=cta-bottom).

## Other things I build

Workspace MCP keeps the workspace on a machine you run, without an account or telemetry. These Chrome extensions likewise keep their data on your computer.

[Clipstay](/clipstay/?utm_source=ermolov.dev&utm_medium=referral&utm_campaign=workspace-mcp&utm_content=cta-clipstay) is a history of text you copy in Chrome, stored on the device. There is no account and no analytics. [Add Clipstay from the Chrome Web Store](https://chromewebstore.google.com/detail/biellalamlbfmgljmpfppaebblmmhokn?utm_source=ermolov.dev&utm_medium=referral&utm_campaign=workspace-mcp&utm_content=cta-clipstay-cws).

[Pagestay](/pagestay/?utm_source=ermolov.dev&utm_medium=referral&utm_campaign=workspace-mcp&utm_content=cta-pagestay) keeps notes in Chrome’s side panel, attached to a page, a site, or kept globally. Notes autosave and keep a version history; there is no account, no sync, no AI and no analytics. [Add Pagestay from the Chrome Web Store](https://chromewebstore.google.com/detail/lehddjgolnpdbmmijbefdffhblbgiejj?utm_source=ermolov.dev&utm_medium=referral&utm_campaign=workspace-mcp&utm_content=cta-pagestay-cws).
