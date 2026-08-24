---
name: cart-read
description: "Read-only cart/order/user/product/review context via MCP."
version: 1.0.0
author: Tomas JG, Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [cart, marketplace, read-only, context, mcp, orders, products, reviews]
    related_skills: [cart-actions, cart-propose]
---

# Cart Read — Read-Only Context

## Overview

Gather the context needed to evaluate a trigger event in the marketplace domain, strictly read-only. Uses the `cart_workflow` MCP server's context tools. Never mutates business data.

## When to Use

- A trigger event needs context: an order with an out-of-stock item, an abandoned cart, a product at/below reorder threshold, or a support message.
- The agent must recover order + items + user profile + product stock + prior orders/notes before drafting a brief.
- Any time you need current cart/order/user/product/review state.

**Don't use for:** proposing or executing a write (`cart-propose` / `cart-execute`), or approving/rejecting (`cart-decide`).

## Prerequisites

- `cart_workflow` MCP server registered (see memory: `hermes mcp add cart_workflow --url <url> --auth header`; token is user-relayed and rotatable, never stored).
- Tools appear as `mcp__cart_workflow__<tool>`.

## Tools

| Tool | Returns |
|---|---|
| `list_orders` | recent orders, newest first |
| `get_order` | one order with its items (by UUID) |
| `get_cart` | current cart for a user (by UUID) |
| `get_user_profile` | user id + role + **masked** email |
| `list_reviews` | reviews for an active product (by UUID) |
| `list_products` | catalog products |
| `get_product` | full product detail (by UUID) |
| `search_products` | name-based, case-insensitive partial match |

## Procedure

1. Identify the trigger entity (order id / user id / product id) from the chat or prior context.
2. Call the minimal set of read tools to recover the facts: order + items, user profile, product stock, prior orders/notes.
3. Assemble *Hechos confirmados* (confirmed facts), labeling the source tool + entity id per fact.
4. Stop at read. Do not call `propose_action` / `approve_action` from this skill.

**Completion criteria:** every fact has a source tool + id; no write tool was called.

## Pitfalls

- `get_user_profile` returns a masked email; never attempt to unmask it.
- Read tools are read-only by contract — don't use them to "check if a write worked" (that read-back belongs to `cart-execute`).
- `list_orders` is newest-first; paginate if the trigger order is older.

## Verification Checklist

- [ ] Only read tools called (no propose/approve/reject/correct).
- [ ] Each recovered fact cites its source tool + entity id.
- [ ] Email kept masked.
