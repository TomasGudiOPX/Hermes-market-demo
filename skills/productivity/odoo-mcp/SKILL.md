---
name: odoo-mcp
description: "Query and manage Odoo ERP via the Odoo MCP server."
version: 0.1.0
author: Tomás Joaquín Gudiño, Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [odoo, erp, mcp, xml-rpc]
    related_skills: [hermes-agent]
---

# Odoo MCP Skill

Interact with the Odoo ERP instance through the `mcp-server-odoo` MCP server
(https://github.com/ivnvxd/mcp-server-odoo), registered in Hermes as `odoo`.
Its tools are auto-injected into every conversation as `mcp_odoo_*`.

## When to Use

- Search, read, aggregate, or list Odoo records (contacts, products, orders, invoices, leads).
- Answer questions about data in the connected Odoo instance.
- Create/update/delete/post-message — only after the server is switched to write mode (see below).
- Don't use for: a different Odoo instance — reconfigure the server first.

## Connection

- Instance: `https://odoo.openix.net.ar/` (database `odoo_prod`).
- Auth: API key for user `admin`, stored in `~/.hermes/config.yaml` → `mcp_servers.odoo.env`.
- Mode: **YOLO `read`** (read-only, vanilla XML-RPC). Write tools are present but rejected.
- Server runs via `uvx mcp-server-odoo` (requires `uv`/`uvx` on PATH).

## Tools (9) — Hermes name is `mcp_odoo_<tool>`

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

Call the tools directly, e.g. `mcp_odoo_search_records` with `{"model": "res.partner", "limit": 10}`.
Model names are Odoo **technical names**, not display labels.

Common models: `res.partner` (contacts), `res.users`, `product.product`,
`sale.order`, `purchase.order`, `crm.lead`, `account.move` (invoices/journal entries),
`stock.picking`, `project.task`, `hr.employee`.

> **Verified via live probe (2026-08-24):** `sale.order` does NOT exist on `odoo_prod` —
> the Sales app is not installed. Use `account.move` (`move_type='out_invoice'`) for
> order/invoice data. `res.partner`, `product.product`, `stock.*`, `account.*`, `crm.*`
> and `mail.*` models were confirmed present.

Odoo domain is a list of triples: `[["is_company", "=", true]]`, `[["name", "ilike", "acme"]]`.
`aggregate_records` groupby takes a model field, e.g. `"country_id"`; aggregates
use Odoo aggregate names like `sum`, `avg`, `count`.

## Enabling Write Access (optional)

In `read` mode, `create_record`/`update_record`/`delete_record`/`post_message`
return `Access denied: Write operation ... not allowed in read-only YOLO mode`.

To allow writes, switch to YOLO `true` (full read/write, **no MCP security — do not
use against a production database**):

```bash
printf 'Y\n' | hermes mcp add odoo --command uvx \
  --env ODOO_URL=https://odoo.openix.net.ar/ ODOO_USER=admin \
  ODOO_API_KEY=<key-from-config.yaml> ODOO_DB=odoo_prod ODOO_YOLO=true \
  --args mcp-server-odoo
```

Then restart the gateway/agent (MCP config has no hot-reload).

## Verification

- `terminal(command="hermes mcp test odoo")` → "Connected" + 9 tools listed.
- `mcp_odoo_search_records` with `model="res.partner"` → returns `records` + `total`.

## Pitfalls

- API key must be paired with `ODOO_USER` — the server passes the key as the XML-RPC password.
- Standard mode (`ODOO_YOLO=off`) requires the paid "MCP Server" Odoo module (apps.odoo.com); without it, only YOLO `read`/`true` work against vanilla XML-RPC endpoints.
- In `read` mode the four write tools still appear but return an access-denied error — expected, not a bug.
- Config changes need a gateway restart (no hot-reload); tools appear in the next session.
- If `uvx` is missing (e.g. `command not found` on connect), install it: `curl -LsSf https://astral.sh/uv/install.sh | sh`.
- `ODOO_LOCALE` (e.g. `es_ES`) is unset by default; set it to localize translated field values.
