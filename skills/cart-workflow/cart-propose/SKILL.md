---
name: cart-propose
description: "Record a proposed write action in the approval ledger."
version: 1.0.0
author: Tomas JG, Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [cart, marketplace, propose, ledger, supervised, mcp, workflow]
    related_skills: [cart-actions, cart-read, cart-decide]
---

# Cart Propose — Ledger-Only Action Proposal

## Overview

Draft structured evidence (`InterventionBrief` / `InterventionRecord`) and record a *proposed* write action into the append-only approval ledger via `propose_action`. This is the only "write" the agent performs, and it writes to the ledger only — never business data.

## When to Use

- After `cart-read`, when a bounded write is warranted (a customer note or a follow-up task).
- The agent must propose without mutating business state.

**Don't use for:** executing a write (`cart-execute`) or deciding (`cart-decide`).

## Action kinds

| kind | status | payload (validated per kind) |
|---|---|---|
| `note` | executable | `userId` + `orderId`? + `content` |
| `followup_task` | executable | `title` + `owner` + `dueAt` |
| `stock_adjust` | deferred | executor rejects (`ACTION_KIND_NOT_SUPPORTED`) |
| `retire_product` | deferred | executor rejects (`ACTION_KIND_NOT_SUPPORTED`) |

## Procedure

1. Draft the `InterventionBrief`: Hechos confirmados / Fuentes / Hipótesis (≤3 falsable) / Riesgos / Validaciones pendientes + next step with **owner + due date**.
2. Draft the `InterventionRecord`: Problema / Proceso / Impacto / Stakeholders / Restricciones / Compromisos / Próximo paso / Riesgos / Validaciones.
3. Choose the smallest `kind` that covers the next step.
4. Build the payload matching the `kind`'s discriminated-union schema.
5. Call `propose_action`. Confirm a `PendingAction` row (`status=proposed`) is returned and no business data changed.
6. Report the proposal + its id to the user for decision.

**Completion criteria:** a proposed action id exists; business data unchanged; brief/record fields populated.

## Pitfalls

- Unknown or out-of-scope `kind` → `propose_action` returns a validation error and stores nothing.
- Never infer owner/amount/date — leave missing fields explicit (`INSUFFICIENT EVIDENCE`) rather than guessing.
- Slice 0 has no financial mutation: never propose `stock_adjust`/`retire_product` expecting execution.

## Verification Checklist

- [ ] Kind is `note` or `followup_task` (slice 0).
- [ ] Payload matches the kind's schema.
- [ ] A proposed action id is recorded; no business write occurred.
- [ ] Brief/record drafted with owner + next step + due date where known.
