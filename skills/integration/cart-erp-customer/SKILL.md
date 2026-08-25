---
name: cart-erp-customer
description: "Match marketplace users to Odoo partners by externalId."
version: 1.1.0
author: Tomas JG, Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [cart, erp, odoo, customer, crm, integration, bridge]
    related_skills: [cart-actions, cart-read, erp-read, cart-erp-reconcile]
---

# Cart ↔ ERP Customer Bridge

## Overview

Build a "customer 360": link a marketplace user (cart_workflow `get_user_profile`) to an Odoo partner (`res.partner`) and pull their ERP history — invoices (`account.move`), payments (`account.payment`), CRM leads (`crm.lead`).

## When to Use

- "Who is this marketplace user in our ERP?" / customer-360 enrichment.
- Enriching a support interaction with the customer's ERP history.

**Don't use for:** stock checks (`cart-erp-stock`) or order reconciliation (`cart-erp-reconcile`).

## Join key

`externalId` — marketplace user `externalId` (unmasked) ↔ Odoo `res.partner.ref` (Internal Reference), falling back to `res.partner.email` (the seed sets `externalId = email`). Email stays masked in `get_user_profile`; `externalId` is the stable, unmasked join key.

## Procedure

1. `get_user_profile` for the marketplace user — capture `id`, `role`, `externalId` (email stays masked).
2. `search_records` `res.partner` by `ref` = `externalId`; if empty, fall back to `email` = `externalId`.
3. If matched: pull `account.move` (invoices), `account.payment`, `crm.lead` for that partner.
4. If not matched (no partner with that ref/email): report "no ERP partner for externalId '<id>'" explicitly.

**Completion criteria:** a linked partner + history, or an explicit "no partner for externalId" finding.

## Pitfalls

- `get_user_profile` masks the email by design; use `externalId` for the join — never try to reverse the mask.
- The seed sets `externalId = email` as a placeholder; a durable external id would live in `res.partner.ref`.
- The partner join is the prerequisite for order reconciliation (`cart-erp-reconcile`).

## Verification

- [ ] Marketplace user read; `externalId` captured.
- [ ] Odoo partner matched (or blocker reported).
- [ ] ERP history (invoices/payments/leads) attached where matched.
