# Supervised Workflow Pattern (propose → approve → execute)

The implementation shape for "workflow con IA" / "agente supervisado" in the Método Openix. Domain-agnostic loop, then a concrete reference architecture.

## Canonical 7-stage loop (from the "Populorum" talk proposal)

1. **Trigger event** — recover context **read-only** (DB/CRM/calendar/external sources).
2. **Agent drafts a brief** — explicitly separate *Hechos confirmados / Fuentes / Hipótesis (≤3 falsables) / Riesgos / Validaciones pendientes*, plus a 90s brief, discovery questions, candidate next-step, desired next step, and the **no-fit condition**.
3. **Human gate #1** — reviews, corrects hypotheses, decides what to explore. No promise of price/scope/term before evidence.
4. **Authorized capture** — bounded, consent-based input (test/anonymized transcript). No live assistance/coaching.
5. **Agent builds structured evidence** — `Problema / Proceso / Impacto / Stakeholders / Restricciones / Compromisos / Próximo paso / Riesgos / Validaciones` + a provisional SIPOC for the human to correct.
6. **Human gate #2 + action proposal** — agent *proposes* note/tasks/status/decision but **cannot** write business data by inference, change stage/owner/amount/date, send messages, or commit price/scope/term.
7. **Approved + traceable write** — execute *only* the authorized action, **read back** the result, report created IDs, persist approval + IDs.

Two decisions overlay every loop: IA gate per output (`GO / GO-WITH-CAVEATS / NO-GO / INSUFFICIENT EVIDENCE`) and human Decidir per loop (`Escalar / Ajustar / Mantener / Detener`).

## Reference architecture (concrete — cart project / tech-evaluation repo)

- **Approval ledger** — one append-only `PendingAction` table: `kind` (note / followup_task / stock_adjust / retire_product), `payload Json` (Zod-discriminated-union per kind), `source`, `status` `proposed→approved/rejected→executed/failed`, `decidedBy` (explicit human identity, never inferred), `reason`, `resultRef`, timestamps. No separate metrics store initially (YAGNI).
- **MCP tools (on-project endpoint)**:
  - read-only context tools: `list_orders`, `get_order`, `get_cart`, `get_user_profile` (masked), `list_reviews`, plus existing product tools.
  - `propose_action` — ledger-only write (the *only* agent write; validated per kind).
  - approval tools: `list_actions`, `get_action`, `approve_action`, `reject_action`, `correct_action`.
- **Executor** — the only writer. Maps approved `kind`+`payload` → existing validated business modules (same code paths as normal admin ops, never raw SQL), then reads back → `resultRef`. Transactional; failure → `status=failed`.
- **Security invariants** — MCP read/propose-only on business data; write only via executor on explicit approve; ledger append-only; per-kind Zod validation blocks out-of-scope actions; `decidedBy` explicit.
- **Metrics** — trigger→brief→approved→executed times; % events with owner+next-step+due; corrections/rejections; proposed→approved→executed conversion by cohort.

## Wiring Hermes to the project MCP (native client — "from here" without a web UI)

The project ships a streamable-http MCP endpoint (e.g. `apps/api/src/engine/mcp/` at `/mcp`, Bearer `MCP_API_TOKEN`). Hermes connects as a native MCP client via `~/.hermes/config.yaml`:

```yaml
mcp_servers:
  cart_workflow:
    url: "http://127.0.0.1:8080/mcp"   # or the deployed https URL
    headers:
      Authorization: "Bearer <MCP_API_TOKEN>"
    timeout: 180
    connect_timeout: 60
```

- Prereq: `pip install mcp` (HTTP client support), then restart Hermes. Tools appear as `mcp_<server>_<tool>` (e.g. `mcp_cart_workflow_approve_action`).
- **Behavioral rule (the human gate when the agent drives MCP):** the agent calls `approve_action`/`reject_action` **only** on the user's explicit instruction in chat — the user is the relationship owner, the agent is the executor.
- The repo's `mcp-config.example.json` is the equivalent client template for external MCP clients (Claude/Cursor).
