---
name: erp-aggregate
description: "Aggregate Odoo records for business metrics."
version: 1.0.0
author: Tomas JG, Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [odoo, erp, aggregate, metrics, bi, mcp]
    related_skills: [erp-read, cart-actions]
---

# ERP Aggregate — Business Metrics

## Overview

Compute server-side aggregations over Odoo records via `aggregate_records` (groupby + aggregates). Turn the ERP ledger into numbers: revenue by country/partner, CRM pipeline by stage, stock value.

## When to Use

- "How much revenue by country?" — group `account.move` by `partner_id` / country.
- "What's the CRM pipeline by stage?" — group `crm.lead` by `stage_id`.
- "Total stock value?" — aggregate `product.product` / `stock.quant`.

**Don't use for:** plain record lookups (`erp-read`).

## Tools

`aggregate_records(model, groupby, aggregates?, domain?, order?, limit?, offset?)`

## Procedure

1. Pick the model + the field to `groupby` (e.g. `partner_id`, `stage_id`, `country_id`).
2. Pick `aggregates` (Odoo aggregate names: `sum`, `avg`, `count`, `min`, `max`) over a numeric field.
3. Call `aggregate_records` and read the grouped result.

**Completion criteria:** grouped numbers returned; each group labeled.

## Pitfalls

- `groupby` must be a real field on the model; aggregates must name a numeric field.
- `count` counts records in the group; use `sum` for money/quantity.
- Results reflect current ERP data — label the source model and date.

## Verification

- [ ] `groupby` field exists on the model.
- [ ] Aggregate names valid; numbers make sense.
- [ ] Source (model + date) stated with the result.
