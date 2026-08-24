---
name: cart-erp-stock
description: "Validate marketplace stock against Odoo inventory."
version: 1.0.0
author: Tomas JG, Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [cart, erp, odoo, stock, inventory, integration, bridge]
    related_skills: [cart-actions, cart-read, erp-read]
---

# Cart ↔ ERP Stock Bridge

## Overview

Cross-check the marketplace's product `stock` (cart_workflow `get_product` / `list_products`) against Odoo's real inventory (`product.product.qty_available`, `stock.quant`, `stock.warehouse.orderpoint`). This is what makes the cart's deferred `stock_adjust` / `retire_product` actions meaningful: Odoo holds the ground truth.

## When to Use

- A marketplace product is at/out of stock, and you need the ERP's real on-hand quantity.
- Before proposing a `stock_adjust` / `retire_product` cart action.

**Don't use for:** partner lookups (`cart-erp-customer`) or order reconciliation (`cart-erp-reconcile`).

## Join key

Marketplace `name` ↔ Odoo `product.product.name` today; the durable key is a **SKU** (`product.product.default_code` ↔ a future marketplace `sku`). Current seed data has zero name overlap — expect no-match until a shared SKU exists.

## Procedure

1. Read the marketplace product (`list_products` / `get_product`) — note `name`, `stock`, `isActive`.
2. Search Odoo `product.product` by normalized `name` (or `default_code` if present).
3. If matched: compare marketplace `stock` vs Odoo `qty_available`; report the delta and the reorder rule (`stock.warehouse.orderpoint`).
4. If no match: report "no ERP match for '<name>'" and recommend adding a SKU.

**Completion criteria:** for each product, either a matched stock delta or an explicit no-match.

## Pitfalls

- Marketplace "Ceramic Coffee Set" has `stock: 0` — a real trigger, but no matching Odoo product yet.
- `qty_available` is on-hand; `stock.quant` is the raw quantity. Use `qty_available` for a storefront view.
- Don't fabricate a match; no-match is the honest answer until keys align.

## Verification

- [ ] Both systems queried for the same product.
- [ ] Stock delta reported (or explicit no-match).
- [ ] Reorder rule surfaced where relevant.
