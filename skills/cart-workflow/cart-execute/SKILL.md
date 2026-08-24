---
name: cart-execute
description: "Confirm execution and read-back of an approved action."
version: 1.0.0
author: Tomas JG, Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [cart, marketplace, execute, read-back, executor, mcp, traceability]
    related_skills: [cart-actions, cart-decide, cart-ledger]
---

# Cart Execute — Executor + Read-Back

## Overview

After an approve, the server-side executor runs the approved action through existing business modules (never raw SQL), reads the created/changed entity back, and records `resultRef` + `executedAt` + status. This skill is about verifying the read-back and reporting it — the execution itself happens on approve.

## When to Use

- After `cart-decide` approves an action, to confirm execution and report the created entities + IDs.

**Don't use for:** proposing (`cart-propose`) or deciding (`cart-decide`).

## Procedure

1. After `approve_action` returns executed (or the ledger shows executed), fetch the action via `get_action`.
2. Read `resultRef` (created entity id + summary) and `executedAt`.
3. Verify the entity exists by reading it back (`get_order` / `get_cart` / etc., as appropriate).
4. Report in chat: what was created/changed + resulting IDs + status.
5. On `status=failed`, surface the reason verbatim (e.g. `ACTION_KIND_NOT_SUPPORTED` for `stock_adjust` / `retire_product`).

**Completion criteria:** created entity id confirmed via read-back; `resultRef` matches; status reported.

## Pitfalls

- Deferred kinds (`stock_adjust` / `retire_product`) → `status=failed` with reason; do not retry them.
- `resultRef` is authoritative; don't claim success without reading it back.
- Execution is server-side; this skill verifies + reports — it does not re-run the write.

## Verification Checklist

- [ ] Action status `executed` (or `failed`) recorded.
- [ ] `resultRef` read and entity read-back confirmed.
- [ ] IDs reported to the user.
