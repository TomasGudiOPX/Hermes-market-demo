---
name: marketplace-deploy
description: "Change marketplace code: validate, push, redeploy handoff."
version: 1.0.0
author: Tomas JG, Hermes Agent
license: MIT
platforms: [linux, macos]
metadata:
  hermes:
    tags: [marketplace, deploy, git, prisma, api, handoff, devops]
    related_skills: [skills-sync, cart-actions, erp-read]
---

# Marketplace Deploy — Code Change → Redeploy Handoff

## Overview

The marketplace app (`tech-evaluation`) is deployed by a **separate devops bot** on a VPS. This Hermes (the marketplace bot) only writes code and pushes; the devops bot builds/deploys. The workflow: **edit → validate → push → verify origin → hand off for redeploy**.

## When to Use

- The user asks for a code change to the marketplace API/web (`tech-evaluation`).
- Adding a field, model, migration, seed change, or contract change.

**Don't use for:** cart/ERP runtime actions (`cart-*`, `erp-*`) — this skill is about *changing the code*.

## Repo facts

- Remote: `git@github.com:TomasGudiOPX/tech-evaluation.git` (local clone `/home/hermes/workspace/marketplace/tech-evaluation`).
- Branch: `cart-update-separate`.
- Yarn workspaces: `@vps-template/api`, `@vps-template/web`, `@vps-template/contracts`.

## Build env quirk (do this first, every session)

The sandbox points `XDG_CONFIG_HOME`/`XDG_CACHE_HOME` at another user's home, which breaks corepack. Before any yarn/prisma command:

```bash
export XDG_CONFIG_HOME="$HOME/.config" XDG_CACHE_HOME="$HOME/.cache" COREPACK_HOME="$HOME/.cache/node/corepack"
```

Use `corepack yarn` (there is no `yarn` shim on PATH; `corepack enable` fails EACCES).

## Procedure

1. **Edit** the code. Typical touch points for a new field:
   - `apps/api/prisma/schema.prisma` (+ a new migration under `apps/api/prisma/migrations/<ts>_<name>/migration.sql`).
   - `packages/contracts/src/*.ts` (types/schemas).
   - `apps/api/src/modules/<x>/<x>.types.ts`, `<x>.controller.ts`, `<x>.service.ts`, `<x>.repository.ts`.
   - `apps/api/src/engine/mcp/mcp.workflow-tools.ts` if an MCP tool should expose the field.
   - `apps/api/prisma/seed.ts` to backfill existing rows.

2. **Regenerate** the Prisma client and rebuild contracts — *before* the API build, or `tsc` sees stale types:
   ```bash
   corepack yarn workspace @vps-template/api prisma:generate   # or: prisma generate
   corepack yarn workspace @vps-template/contracts build
   ```

3. **Build + test**:
   ```bash
   corepack yarn workspace @vps-template/api build    # tsc
   corepack yarn workspace @vps-template/api test     # vitest
   corepack yarn workspace @vps-template/web build
   ```

4. **Fix typed mocks** that break when a type gains a field — `ProductRow`/`StoredUser`/`AuthUser` fixtures in `*.test.ts` (e.g. `cart.service.test.ts`, `reviews/review.service.test.ts`, `auth.service.test.ts`, `roles.guard.test.ts`, `mcp.workflow-tools.test.ts`).

5. **Commit + push**:
   ```bash
   git add -A && git commit -m "feat(scope): <message>"
   git push origin cart-update-separate
   ```

6. **Verify origin** — the deployer only sees what is *pushed*, so committing locally is not enough:
   ```bash
   git rev-list --left-right --count origin/cart-update-separate...cart-update-separate   # expect 0 0
   git ls-remote origin cart-update-separate                                            # SHA must equal local HEAD
   ```

7. **Hand off**: tell the user it's ready to redeploy. If the change adds a schema column or seed data, flag explicitly that devops must run **migrations *and* re-seed** (not just migrate), because the seed backfills the new column on existing rows.

## Pitfalls

- **Deployer ships stale code unless you verify `origin`** — commit + push is not proof; `ls-remote` is.
- **Migrations alone don't backfill** — a new `@unique` column on existing rows needs a seed re-run (or a data migration), or `prisma migrate` fails / rows stay null.
- **Stale-type LSP errors are expected** after editing schema/contracts — they clear only after `prisma generate` + `contracts build`.
- **Test fixtures** for typed rows (`StoredUser`, `AuthUser`, `ProductRow`) must gain the new field or `tsc`/tests fail.
- **ERP join keys** (sku, externalId) live in the `erp-read` skill (its `cart-erp-join-keys.md` reference) — update it whenever a join key changes.

## Verification

- [ ] `prisma generate` + `contracts build` run after schema/contract edits.
- [ ] `api build` clean; `api test` green; `web build` green.
- [ ] Committed and pushed; `rev-list --left-right --count` = `0 0` and `ls-remote` = local HEAD.
- [ ] Handoff message states whether **migrate + seed** (vs migrate only) is required.
