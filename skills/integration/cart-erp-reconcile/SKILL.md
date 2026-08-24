---
name: cart-erp-reconcile
description: "Reconcile marketplace orders with Odoo invoices."
version: 1.0.0
author: Tomas JG, Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [cart, erp, odoo, orders, invoices, integration, bridge]
    related_skills: [cart-actions, cart-read, erp-read, cart-erp-customer]
---

# Cart ↔ ERP Order Reconciliation

## Overview

Match a marketplace order (cart_workflow `get_order` / `list_orders`) to its Odoo accounting record. Since `sale.order` isn't installed, the ERP side is `account.move` (customer invoice, `move_type='out_invoice'`) + `account.move.line`.

## When to Use

- "Did this marketplace order get invoiced in Odoo?"
- Detecting orders with no invoice, or total/line mismatches between store and ERP.

**Don't use for:** stock checks (`cart-erp-stock`) or partner lookups (`cart-erp-customer`).

## Join key

Order reference ↔ invoice `ref` / `invoice_origin`; fallback = total + date + partner. This is design-only until (a) the customer join works (`cart-erp-customer`) and (b) invoices are actually created in Odoo.

## Procedure

1. Read the marketplace order (`get_order`) — capture id, `totalCents`, `status`, items, `createdAt`.
2. Search Odoo `account.move` (customer invoices) by partner + date window + total.
3. If matched: compare totals and line items; report any discrepancy.
4. If no match: report "no invoice in Odoo for order <id>" — reconciliation is pending, not failed.

**Completion criteria:** matched invoice + delta, or an explicit "no Odoo invoice yet".

## Pitfalls

- No `sale.order` — don't search it; use `account.move` (`move_type='out_invoice'`).
- Totals are in different units/currencies — normalize cents vs Odoo's currency before comparing.
- The current demo has one order ("Ceramic Coffee Set" x12) and no invoices — expect no-match.

## Verification

- [ ] Order read; ERP invoice searched by the right model.
- [ ] Totals normalized before comparison.
- [ ] Match or explicit no-match reported.
