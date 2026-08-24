---
name: cart-erp-customer
description: "Match marketplace users to Odoo partners by email."
version: 1.0.0
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

`email` — marketplace user email ↔ `res.partner.email`. **Blocker:** the marketplace masks the email (e.g. `c*******@example.com`), so the bot cannot match today. Needs an unmasked stable identifier.

## Procedure

1. `get_user_profile` for the marketplace user — capture id + role + masked email.
2. If an unmasked email (or stable id) is available, `search_records` `res.partner` by `email`.
3. If matched: pull `account.move` (invoices), `account.payment`, `crm.lead` for that partner.
4. If not matched (masked / no key): report the blocker explicitly.

**Completion criteria:** a linked partner + history, or an explicit "email masked — cannot match" finding.

## Pitfalls

- `get_user_profile` returns a masked email by design; do not try to reverse it.
- Odoo currently has only 2 demo partners (Administrator, My Company) — no real customers yet.
- The partner join is the prerequisite for order reconciliation (`cart-erp-reconcile`).

## Verification

- [ ] Marketplace user read; join key identified.
- [ ] Odoo partner matched (or blocker reported).
- [ ] ERP history (invoices/payments/leads) attached where matched.
