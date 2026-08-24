---
name: cart-decide
description: "Approve, reject, or correct a proposed action for the user."
version: 1.0.0
author: Tomas JG, Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [cart, marketplace, approve, reject, correct, human-in-the-loop, mcp]
    related_skills: [cart-actions, cart-propose, cart-execute]
---

# Cart Decide — Human Approval Gate

## Overview

Apply the human's explicit decision to a proposed action via `approve_action`, `reject_action`, or `correct_action`. Records the decision with an explicit `decidedBy` (human identity from chat, never inferred) + reason. On approve, triggers the executor (see `cart-execute`).

## When to Use

- The user has **explicitly** instructed approve / reject / correct on a proposed action.

**Don't use for:**

- Deciding on the agent's own judgment — NEVER decide without explicit user instruction.
- Proposing (`cart-propose`) or executing (`cart-execute`).

## Procedure

1. Confirm the user's instruction is explicit (e.g. "approve action X" / "reject X because…").
2. Resolve the action id (from `list_actions` / `get_action` or the prior proposal).
3. Capture the human identity for `decidedBy` from the chat author — never a guessed identity.
4. Capture a `reason` (mandatory on reject/correct; recommended on approve).
5. Call `approve_action` / `reject_action` / `correct_action` with `actionId` + `decidedBy` + `reason`.
6. Report the resulting status (approved/rejected) to the user. On approve, note that execution proceeds (`cart-execute`).

**Completion criteria:** decision recorded with explicit `decidedBy` + reason; status reflected; no decision recorded without a decider.

## Pitfalls

- Decision missing `decidedBy` → validation error, nothing recorded.
- Never decide on the agent's behalf — the human gate's integrity depends on it.
- `correct_action` replaces a proposed payload; confirm the corrected payload with the user before submitting.

## Verification Checklist

- [ ] User instruction explicit.
- [ ] `decidedBy` = real human identity from chat.
- [ ] `reason` present (mandatory for reject/correct).
- [ ] Only one decision tool called per action; status matches.
