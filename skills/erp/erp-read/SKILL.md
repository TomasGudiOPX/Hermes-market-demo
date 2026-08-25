---
name: erp-read
description: "Query Odoo ERP records via search, get, and list."
version: 1.1.0
author: Tomas JG, Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [odoo, erp, mcp, query, read-only, xml-rpc]
    related_skills: [cart-actions, cart-erp-stock, cart-erp-customer, cart-erp-reconcile, erp-aggregate, odoo-mcp]
---

# ERP Read — Query Odoo

## Overview

Query the Odoo ERP (`odoo` MCP server) read-only: search, fetch, and list records. Odoo is the marketplace's system of record for inventory, accounting, contacts, and CRM. Runs as the scoped `mcp_reader` user in YOLO `read` mode — write tools are present but rejected.

## When to Use

- Look up a partner, product, invoice, journal entry, or lead.
- Enrich marketplace context with ERP ground truth (stock, price, customer history).
- List which models are available (`list_models`).

**Don't use for:** aggregations/BI (`erp-aggregate`), or cross-system joins (the `cart-erp-*` bridge skills).

## Prerequisites

- `odoo` MCP server registered (see `odoo-mcp` skill): instance `odoo.openix.net.ar`, db `odoo_prod`, user `mcp_reader` (read-only), YOLO `read`.
- Tools appear as `mcp__odoo__<tool>`.

## Tools

| Tool | Purpose |
|---|---|
| `search_records` | query with optional `domain`, `fields`, `limit`, `offset`, `order` |
| `get_record` | one record by `model` + `record_id` |
| `list_models` | all models enabled for MCP access |

## Domain syntax

Odoo domain = list of triples: `[["is_company","=",true]]`, `[["name","ilike","acme"]]`. Model names are technical (`res.partner`, `product.product`), not display labels.

## Common models

- Contacts: `res.partner`, `res.partner.bank`, `res.country`, `res.currency`
- Products: `product.product`, `product.template`, `product.category`, `product.pricelist`
- Inventory: `stock.quant`, `stock.warehouse.orderpoint`, `stock.lot`, `stock.move.line`, `stock.picking`
- Sales/accounting: `sale.order`, `account.move`, `account.move.line`, `account.journal`, `account.payment`, `account.invoice.report`
- CRM: `crm.lead`, `crm.stage`, `crm.tag`
- Mail/activity: `mail.message`, `mail.activity`, `mail.followers`

Note: **`sale.order` now exists** (Sales app installed). Order data lives in `sale.order`; customer invoices live in `account.move` (`move_type='out_invoice'`).

## Procedure

1. Identify the model (technical name) and the filter.
2. Call `search_records` (or `get_record` for a known id).
3. Read the `records` + `total`. Respect the read-only contract.

**Completion criteria:** records returned and understood; no write tool called.

## Pitfalls

- Write tools (`create_record`, `update_record`, etc.) exist but return "access denied" in read mode — expected.
- Field names are technical (`partner_id`, `list_price`, `qty_available`); verify against `list_models` / `get_record` when unsure.
- For join keys between the two systems, see `references/cart-erp-join-keys.md`.

## Verification

- [ ] Correct technical model name used.
- [ ] Domain triples valid; results match the filter.
- [ ] No write tool called.
