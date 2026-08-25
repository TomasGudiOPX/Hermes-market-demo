---
name: cart-erp-reconcile
description: "Reconcile marketplace orders with Odoo invoices."
version: 1.1.0
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

Match a marketplace order (cart_workflow `get_order` / `list_orders`) to its Odoo record. `sale.order` is now installed (Sales app), so the ERP side is `sale.order` + `account.move` (customer invoice, `move_type='out_invoice'`) + `account.move.line`.

## When to Use

- "Did this marketplace order get invoiced in Odoo?"
- Detecting orders with no invoice, or total/line mismatches between store and ERP.

**Don't use for:** stock checks (`cart-erp-stock`) or partner lookups (`cart-erp-customer`).

## Join key

Order reference ↔ `sale.order.name` / invoice `ref` / `invoice_origin`; fallback = total + date + partner. Prerequisite: the customer join (`cart-erp-customer`, by `externalId`) is wired.

## Procedure

1. Read the marketplace order (`get_order`) — capture id, `totalCents`, `status`, items, `createdAt`.
2. Match the customer via `cart-erp-customer` (`externalId` → partner).
3. Search Odoo `sale.order` (then `account.move` customer invoices) by partner + date window + total.
4. If matched: compare totals and line items; report any discrepancy.
5. If no match: report "no invoice/order in Odoo for order <id>" — reconciliation is pending, not failed.

**Completion criteria:** matched invoice + delta, or an explicit "no Odoo invoice yet".

## Pitfalls

- `sale.order` is installed but empty (0 orders at check time); invoices still live in `account.move` (`move_type='out_invoice'`).
- Totals are in different units/currencies — normalize cents vs Odoo's currency before comparing.
- The demo has no invoices yet — expect no-match until the invoice flow is exercised.

## Verification

- [ ] Order read; ERP record searched by the right model.
- [ ] Totals normalized before comparison.
- [ ] Match or explicit no-match reported.
