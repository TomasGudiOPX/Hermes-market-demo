---
name: openix-method
description: "Openix: plan AI with evidence; supervise propose→approve."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [methodology, ai-adoption, planning, human-in-the-loop, workflow, evidence, openix, supervised-agent]
---

# Método Openix — Evidence-Driven AI Adoption

The user (Tomás @ Openix) applies this method when planning where/how/when to apply AI. Load it whenever they say "use the Método Openix", "our method", "the methodology", or ask to plan an AI/automation project that must be justified with evidence before scaling.

## Thesis

Access to AI is no longer the advantage. The advantage is deciding **where** to apply it, **how** to redesign process/data/controls, and **when** to scale — always against evidence. Three ordering questions: **¿Dónde?** (problem + result), **¿Cómo?** (process, data, controls), **¿Cuándo?** (scale only against evidence).

## Six stages (a loop, not a linear sequence)

`Encontrar → Medir → Evaluar → Diseñar → Implementar → Decidir` — each **Decidir** feeds the next **Encontrar**. Technology scales *after* evidence, not before.

| # | Stage | Question / key points |
|---|-------|----------------------|
| 01 | Encontrar | ¿Qué problema importa? Select problem + result, **not the tool**. |
| 02 | Medir | ¿Cuál es la línea base? Time/errors/cost. No baseline = can't prove the AI improved anything. |
| 03 | Evaluar | ¿Es viable y conveniente? IA is viable when the bottleneck is **interpret/classify/redact/generate** — NOT calculation, exactness, or an already-clear process. |
| 04 | Diseñar | ¿Qué prueba mínima alcanza? Minimal process+tech change. Filters: **Alcance / Solución / Control / Resultado**. Metric + success threshold defined **before** starting. |
| 05 | Implementar | ¿Funciona en contexto real? Prepare → Probar → Autorizar. Scope-limited, reversible, real users, active metrics, residual risk accepted. |
| 06 | Decidir | ¿Qué hacemos con la evidencia? Explicit next move (see table below). |

**Decidir table:** ¿Genera valor medible? → sí continúa / no **Detener**. ¿Puede operarse con control? → sí continúa / no **Ajustar**. ¿La evidencia justifica escalar? → sí **Escalar** / no **Mantener**.

## The two decisions (the core distinction)

- **IA gate — per task/output:** `GO` · `GO-WITH-CAVEATS` · `NO-GO` · `INSUFFICIENT EVIDENCE` — is this output ready to use?
- **Human Decidir — per loop:** `Escalar` · `Ajustar` · `Mantener` · `Detener` — do we invest more?

> **La IA propone. La persona decide.** The IA gate is per-task; the human Decidir is per-loop. Confusing them = letting the AI scale alone — exactly what the method prevents.

## Progression (where AI fits)

`manual → script → automation → workflow → workflow+IA → agente supervisado`. Add AI only when the bottleneck is interpret/classify/redact/generate; sometimes the right tool is a checklist/spreadsheet/script or *none*. Excess AI is also a problem.

## Early failure modes (pitfalls to flag)

1. **Start with the tool** — "we want to use AI" defines no result.
2. **Automate a confused process** — speed amplifies errors, rework, exceptions.
3. **Scale a demo** — tech responding ≠ value, adoption, or operation.

Building faster doesn't fix these; it *accelerates waste*.

## What IA is good at vs weak at

Good: language/writing, classify/compare, summarize long docs, drafts/first versions, generate options. Weak: exact data, missing context, private/sensitive data, serious-consequence decisions, unverifiable output. **Rule:** if you can't verify output against evidence, don't depend on it.

## Supervised workflow pattern (the implementation shape)

When the method lands on "workflow con IA" or "agente supervisado", use the propose/approve/execute pattern. Core loop: **read-only context → agent drafts structured evidence → human reviews/corrects (gate) → agent proposes action (ledger-only) → human explicitly approves → executor runs through validated modules → read-back + traceability + metrics.** See `references/supervised-workflow-pattern.md` for the 7-stage loop, the approval-ledger architecture, and Hermes↔project-MCP wiring.

## User preferences (embed these)

- Drive supervised workflows from the Hermes/Telegram session via the project's **own MCP endpoint** (Hermes native MCP client) — **no separate web admin UI** unless asked.
- Plans are usually requested **in writing first** (no code/repo changes) before implementation.
- This user works in Spanish source material; keep canonical Spanish terms (Encontrar/Medir/…, "La IA propone. La persona decide.", Hechos/Hipótesis/Riesgos/Validaciones) verbatim in plans.
