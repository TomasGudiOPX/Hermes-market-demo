---
name: cart-actions
description: "Canonical catalog of the marketplace bot's actions."
version: 1.0.0
author: Tomas JG, Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [cart, marketplace, actions, supervised, workflow, mcp, approval, human-in-the-loop]
    related_skills: [cart-read, cart-propose, cart-decide, cart-execute, cart-ledger, skills-sync, erp-read, erp-aggregate, cart-erp-stock, cart-erp-customer, cart-erp-reconcile]
---

# Cart Actions — Standard Operating Procedure

## Overview

The marketplace bot (this Hermes on Telegram) acts on the cart domain through the `cart_workflow` MCP server under a supervised action workflow: **read-only context → structured brief → propose (ledger-only) → human gate → execute → read-back**. This skill is the canonical reference for every action the bot can take and the invariants that govern them.

## When to Use

- Whenever the bot is asked to do anything in the marketplace/cart domain.
- To look up which tool/action applies and its invariant before acting.

**Don't use for:** generic Hermes tasks unrelated to cart/marketplace.

## Prerequisites

- `cart_workflow` MCP server registered (see memory: `hermes mcp add cart_workflow --url <url> --auth header`; token is user-relayed and rotatable, never stored).
- Tools appear as `mcp__cart_workflow__<tool>`.

## Action catalog

| Group | Tools | Nature | Invariant |
|---|---|---|---|
| Read context | `list_orders`, `get_order`, `get_cart`, `get_user_profile`, `list_reviews` | read | never mutate; email masked |
| Catalog | `list_products`, `get_product`, `search_products` | read | read-only |
| Propose | `propose_action` | ledger-only write | writes only to ledger |
| Decide | `approve_action`, `reject_action`, `correct_action` | ledger write + (on approve) execute | explicit `decidedBy`; only on user instruction |
| Ledger report | `list_actions`, `get_action`, `get_action_metrics` | read (ledger) | read-only |

## State machine

`proposed → approved | rejected → executed | failed`

Kinds: `note`, `followup_task` = executable (slice 0); `stock_adjust`, `retire_product` = deferred.

## The loop (La IA propone. La persona decide.)

1. Trigger event → `cart-read` (read-only context)
2. Draft brief → `cart-propose` (ledger-only)
3. Human gate → `cart-decide` (explicit approve/reject/correct)
4. Execute + read-back → `cart-execute`
5. Report + metrics → `cart-ledger`

## Routing table

| Need | Skill |
|---|---|
| Gather context read-only | `cart-read` |
| Propose a write | `cart-propose` |
| Approve / reject / correct | `cart-decide` |
| Execute + read-back | `cart-execute` |
| Inspect the ledger | `cart-ledger` |
| Sync skills to the repo | `skills-sync` |
| Change marketplace code | `marketplace-deploy` |

### ERP & integration (cart ↔ Odoo)

| Need | Skill |
|---|---|
| Query Odoo records | `erp-read` |
| Aggregate ERP metrics | `erp-aggregate` |
| Validate stock vs ERP | `cart-erp-stock` |
| Match user ↔ ERP partner | `cart-erp-customer` |
| Reconcile order ↔ invoice | `cart-erp-reconcile` |

## Security invariants (hard rules)

- Read tools: read-only on business data.
- `propose_action`: ledger-only.
- Writes execute only via the executor, only on explicit approve, through existing modules (no raw SQL).
- `decidedBy` is an explicit human identity from chat — never inferred.
- Never call `approve_action` / `reject_action` / `correct_action` without the user's explicit instruction.

## Pitfalls

- Confusing the IA gate (`GO` / `GO-WITH-CAVEATS` / `NO-GO` / `INSUFFICIENT EVIDENCE`, per output) with the human Decidir (`Escalar` / `Ajustar` / `Mantener` / `Detener`, per loop).
- Letting the agent decide on its own — the human gate is the point.

## Verification Checklist

- [ ] Every cart action maps to exactly one skill.
- [ ] Invariants honored (read-only, ledger-only, explicit decider, explicit approve).
- [ ] Read-back confirmed before claiming a write succeeded.
