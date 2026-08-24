# Hermes Market Demo — Skills

Custom Hermes Agent skills for the marketplace bot (**Marketplacebot**). This repo is the version-controlled home of the skills that live locally in `~/.hermes/skills/`, kept in sync with the `skills-sync` skill.

## What's here

### `cart-workflow/` — the marketplace bot's actions

Standard operating procedures for every action the bot can take through the `cart_workflow` MCP server, under a supervised action workflow (**propose → human approve → execute → read-back**).

- **`cart-actions`** — canonical action catalog, state machine, and routing table.
- **`cart-workflow/cart-read`** — read-only context + catalog.
- **`cart-workflow/cart-propose`** — propose a write action (ledger-only).
- **`cart-workflow/cart-decide`** — human approval gate (approve / reject / correct).
- **`cart-workflow/cart-execute`** — executor + read-back.
- **`cart-workflow/cart-ledger`** — approval-ledger reporting.

### `skills-sync/` — the sync mechanism

Keeps these (and all other custom) skills in sync with this repo:

```bash
python3 skills/skills-sync/scripts/skills_sync.py status   # drift check
python3 skills/skills-sync/scripts/skills_sync.py push     # backup local → repo
python3 skills/skills-sync/scripts/skills_sync.py pull     # restore repo → local
python3 skills/skills-sync/scripts/skills_sync.py list     # show custom skills
```

### Other custom skills

The repo also carries the machine's other custom skills (Openix method, Odoo MCP, Polymarket, etc.), because `skills-sync` syncs all non-bundled skills.

## The supervised action workflow

`read-only context → brief → propose (ledger-only) → human gate → execute → read-back`

- **State machine:** `proposed → approved | rejected → executed | failed`.
- **Action kinds:** `note`, `followup_task` (executable); `stock_adjust`, `retire_product` (deferred).

> **La IA propone. La persona decide.**
