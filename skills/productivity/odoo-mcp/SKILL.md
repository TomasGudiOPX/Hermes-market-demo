---
name: odoo-mcp
description: "Query Odoo ERP read-only (scoped mcp_reader) via the Odoo MCP server."
version: 0.2.0
author: Tomás Joaquín Gudiño, Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [odoo, erp, mcp, xml-rpc, read-only]
    related_skills: [hermes-agent, erp-read]
---

# Odoo MCP Skill

Interact with the Odoo ERP instance through the `mcp-server-odoo` MCP server
(https://github.com/ivnvxd/mcp-server-odoo), registered in Hermes as `odoo`.
Its tools are auto-injected into every conversation as `mcp__odoo__*`.

## When to Use

- Search, read, aggregate, or list Odoo records (contacts, products, orders, invoices, leads).
- Answer questions about data in the connected Odoo instance.
- Create/update/delete/post-message — **deferred**: write access is blocked until the licensed module is purchased (see below).
- Don't use for: a different Odoo instance — reconfigure the server first.

## Connection

- Instance: `https://odoo.openix.net.ar/` (database `odoo_prod`).
- Auth: API key for the scoped read-only user **`mcp_reader`** (NOT `admin`), stored in `~/.hermes/config.yaml` → `mcp_servers.odoo.env`.
- Mode: **YOLO `read`** (read-only, vanilla XML-RPC) + `ODOO_LOCALE=es_ES`. Write tools are present but rejected.
- Server runs via `uvx mcp-server-odoo` (requires `uv`/`uvx` on PATH).

## Tools (9) — Hermes name is `mcp__odoo__<tool>`

| Tool | Required args | Optional args |
|---|---|---|
| `search_records` | `model` | `domain`, `fields`, `limit`, `offset`, `order` |
| `get_record` | `model`, `record_id` | `fields` |
| `list_models` | — | — |
| `list_resource_templates` | — | — |
| `create_record` | `model`, `values` | — |
| `update_record` | `model`, `record_id`, `values` | — |
| `delete_record` | `model`, `record_id` | — |
| `post_message` | `model`, `record_id`, `body` | `subtype`, `message_type`, `partner_ids`, `attachment_ids`, `body_is_html` |
| `aggregate_records` | `model`, `groupby` | `aggregates`, `domain`, `order`, `limit`, `offset` |

## How to Use

Call the tools directly, e.g. `mcp__odoo__search_records` with `{"model": "res.partner", "limit": 10}`.
Model names are Odoo **technical names**, not display labels.

Common models: `res.partner` (contacts), `res.users`, `product.product`,
`sale.order`, `purchase.order`, `crm.lead`, `account.move` (invoices/journal entries),
`stock.picking`, `project.task`, `hr.employee`.

> **Verified (2026-08-25):** the Sales app is now installed — `sale.order` is queryable
> (0 orders at check time). Invoices live in `account.move` (`move_type='out_invoice'`).
> Confirmed present: `res.partner`, `product.product` (12 marketplace products with
> `MP-*` `default_code`), `stock.*`, `account.*`, `crm.*`, `mail.*`, and `sale.*`.

Odoo domain is a list of triples: `[["is_company", "=", true]]`, `[["name", "ilike", "acme"]]`.
`aggregate_records` groupby takes a model field, e.g. `"country_id"`; aggregates
use Odoo aggregate names like `sum`, `avg`, `count`.

## Read-Only Hardening (DONE)

- The `mcp_server` module is licensed **OPL-1 (Odoo Proprietary License, paid)** — deferred. It is only required for MCP-level per-model operation control and the write path (standard mode).
- **Live:** the MCP now authenticates as the scoped user **`mcp_reader`** (read-only ACLs on the business models), not `admin`. Odoo's native ACLs are enforced at the XML-RPC layer for whichever user the API key maps to, so the MCP can only read what `mcp_reader` can — even in YOLO `read` mode, no module required.
- **Never** set `ODOO_YOLO=true` against `odoo_prod`, and never use `admin` for the MCP. Write capability stays deferred until the licensed module with per-model ACLs is purchased.

## Enabling Write Access (deferred)

In `read` mode, `create_record`/`update_record`/`delete_record`/`post_message`
return `Access denied: Write operation ... not allowed in read-only YOLO mode`.

Writes require YOLO `true` (full read/write, **no MCP security — do not use
against a production database**):

```bash
# DO NOT run this against odoo_prod — full read/write with no MCP security.
printf 'Y\n' | hermes mcp add odoo --command uvx \
  --env ODOO_URL=https://odoo.openix.net.ar/ ODOO_USER=<scoped-writer> \
  ODOO_API_KEY=<key> ODOO_DB=odoo_prod ODOO_YOLO=true \
  --args mcp-server-odoo
```

Then restart the gateway/agent (MCP config has no hot-reload).

## Verification

- `terminal(command="hermes mcp test odoo")` → "Connected" + 9 tools listed.
- `mcp__odoo__search_records` with `model="res.partner"` → returns `records` + `total`.

## Pitfalls

- API key must be paired with `ODOO_USER` — the server passes the key as the XML-RPC password.
- Standard mode (`ODOO_YOLO=off`) requires the Odoo module **`mcp_server`** — https://apps.odoo.com/apps/modules/18.0/mcp_server (Odoo 18; the mcp-server-odoo README links 19.0 for Odoo 19). Install it, then Settings > MCP Server > Enabled Models to pick per-model access; health check at `/mcp/health`. Standard mode respects Odoo ACLs/record rules and ties each API key to a user — the secure path. Without the module, only YOLO `read`/`true` work against vanilla XML-RPC. The server itself runs **client-side** (uvx on the Hermes host); the only Odoo-side artifact is this module.
- In `read` mode the four write tools still appear but return an access-denied error — expected, not a bug.
- Config changes need a gateway restart (no hot-reload); tools appear in the next session.
- If `uvx` is missing (e.g. `command not found` on connect), install it: `curl -LsSf https://astral.sh/uv/install.sh | sh`.
- `ODOO_LOCALE` is set to `es_ES` on this deployment to localize translated field values.
