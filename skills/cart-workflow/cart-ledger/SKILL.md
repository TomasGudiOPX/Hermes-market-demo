---
name: cart-ledger
description: "Inspect the approval ledger and its metrics."
version: 1.0.0
author: Tomas JG, Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [cart, marketplace, ledger, metrics, report, mcp]
    related_skills: [cart-actions, cart-decide, cart-execute]
---

# Cart Ledger — Approval Ledger Reporting

## Overview

Read the append-only approval ledger via `list_actions`, `get_action`, and `get_action_metrics`. Counters are derived from the ledger; there is no separate metrics store.

## When to Use

- "What's pending / approved / rejected?" → `list_actions` with an optional status filter.
- Inspecting one action's full record → `get_action` (by UUID).
- Reporting totals (proposed / approved / rejected / executed / failed) → `get_action_metrics`.

**Don't use for:** proposing (`cart-propose`) or deciding (`cart-decide`).

## Procedure

1. Choose the reporting goal: overview → `list_actions`; drill-down → `get_action`; counters → `get_action_metrics`.
2. Call the tool with the right filters (status, limit).
3. Present results: for each action, id + kind + status + `decidedBy` + `resultRef`.
4. Keep metrics honest: cite counters as derived-from-ledger, not as a realtime dashboard.

**Completion criteria:** requested actions/counters returned and presented with ids + status.

## Pitfalls

- The ledger is append-only: no tool edits or deletes a row.
- `get_action_metrics` counts the ledger; a `0` is meaningful (no actions yet), not an error.

## Verification Checklist

- [ ] Correct reporting tool used for the goal.
- [ ] Ids and statuses cited exactly as returned.
- [ ] No write tool called.
