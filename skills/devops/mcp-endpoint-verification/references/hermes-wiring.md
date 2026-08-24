# Wiring a verified MCP endpoint into Hermes (operational gotchas)

The canonical config shape lives in the bundled `hermes-agent` skill →
`references/native-mcp.md`. This file captures the operational details that doc
doesn't cover, learned from a real two-bot flow (devops handoff a `URL` +
`Bearer token` → this agent connects to the deployed `/mcp`).

## Add the server — use the CLI, never hand-edit config

`~/.hermes/config.yaml` is write-protected from the agent. Both the `patch` tool
and shell `echo`/heredoc into `config.yaml` are refused ("Refusing to write to
Hermes config file" / a hardline blocklist error). Only the CLI writes MCP config:

```bash
hermes mcp add <name> --url https://<host>/mcp --auth header
```

## The add command is interactive

Drive it with `terminal(pty=true, background=true)` then `process submit` per
prompt (do NOT pipe answers — the token prompt is a masked secret prompt):

1. `Does this server require authentication? [Y/n]` → submit Enter (default Y)
2. `API key / Bearer token:` (masked) → submit the token
3. `Enable all N tools? [Y/n/select]` → submit Enter (default = all)

On success it prints `Saved '<name>' to ~/.hermes/config.yaml (N/N tools enabled)`
and `Start a new session to use these tools.`

## Where the secret lands

The token is written to `~/.hermes/.env` as `MCP_<NAME>_API_KEY` (NAME uppercased,
non-alphanumerics → `_`). `config.yaml` stores only the interpolation:

```yaml
mcp_servers:
  <name>:
    url: "https://<host>/mcp"
    headers:
      Authorization: "Bearer ${MCP_<NAME>_API_KEY}"
    enabled: true
```

The secret stays out of `config.yaml`. If a handoff already includes a `Bearer `
prefix, strip it — the header template adds its own, and `Bearer Bearer …` → 401.

## Verify before restarting

```bash
hermes mcp list           # registered + enabled?
hermes mcp test <name>    # connects via Hermes's own client + lists discovered tools
```

`hermes mcp test` proves token + connection + discovery in one shot (e.g.
"✓ Connected (827ms)" + "✓ Tools discovered: 15").

## Activation requires a gateway restart — from OUTSIDE

Tools surface as `mcp_<name>_<tool>` only after a gateway restart (no hot-reload).
The gateway **blocks self-restart from inside**: the terminal tool refuses
`systemctl restart` / `systemd-run … restart` / `hermes gateway restart` when
issued from within the running gateway (SIGTERM would kill the turn and lose the
reply). Run from a separate shell:

```bash
hermes gateway restart            # or: systemctl --user restart hermes-gateway.service
```

The chat drops ~30s. A per-session `/model` override is persisted and rehydrated
on restart, so a mid-session model switch survives the bounce — no need to fear
reverting to a stale broken `model.default` in `config.yaml`.

## Exercise a tool to prove it *functions*, not just that it's listed

A `tools/list` 200 only proves a tool is *exposed*, not that the write/approve
path works. Call one tool over the same StreamableHTTP JSON-RPC:

```python
# after initialize: rpc("tools/call", {"name": "propose_action",
#                                      "arguments": {"payload": {...}}})
# result text lives in msg["result"]["content"][0]["text"]  (a JSON-encoded string)
```

For the full probe (initialize + `tools/list` + optional `call`), see
`scripts/probe_streamable_http.py` in this skill.
