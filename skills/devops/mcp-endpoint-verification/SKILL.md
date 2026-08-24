---
name: mcp-endpoint-verification
description: "Verify a remote MCP server's tools, auth, and state."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [mcp, verification, debugging, streamable-http, tools]
    related_skills: [hermes-agent]
---

# MCP Endpoint Verification

Probe a remote Model Context Protocol (MCP) server over StreamableHTTP — without
Hermes or a full MCP client — to answer: does the endpoint respond, does my token
work, and **exactly which tools does it currently expose?**

Use this when:
- A deployer/bot reports an MCP endpoint "is live" and you must confirm the tools
  it *actually* serves (e.g. "are my new write/approve tools deployed yet, or
  still just the read-only ones?").
- Debugging a Hermes `mcp_servers` entry that connects but surfaces no/partial
  tools.
- Confirming a bearer token works before wiring it into `~/.hermes/config.yaml`.

## Quick probe

`scripts/probe_streamable_http.py` (stdlib only, zero deps):

```bash
python3 scripts/probe_streamable_http.py <URL> <TOKEN>
```

It runs an MCP `initialize` handshake then `tools/list`, prints the server
identity and the full list of tool names. Pass URL and bearer token as args —
never hardcode the token into the script or commit it anywhere.

## Hand-rolled curl (one-liner sanity check)

```bash
curl -sS -X POST "$URL" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-03-26","capabilities":{},"clientInfo":{"name":"probe","version":"0"}}}'
```

## Pitfalls

- **SSE responses, not bare JSON.** StreamableHTTP servers reply with
  `event: message` + `data: {…}` lines. Parse every line starting with `data:`
  and `json.loads` the payload — a single `json.loads(body)` on the raw body
  fails with "Expecting value: line 1 column 1".
- **Session id is optional.** A stateless server may return no
  `mcp-session-id` header at all (initialize still works, `tools/list` follows
  fine without it). If a header *is* returned, echo it back as `Mcp-Session-Id`
  on every subsequent request.
- **Send the SSE Accept header** — `Accept: application/json,
  text/event-stream` — or the handshake may 406.
- **Enumerate, don't assume.** A server can handshake HTTP 200 while exposing
  only a subset of its tools (e.g. read-only tools but not the write/approve
  tools). The only reliable check is the `tools/list` output, not the handshake.

## Related

- Hermes-native connection/config: `hermes-agent` skill →
  `references/native-mcp.md`. Add a server with
  `hermes mcp add <name> --url <url> --auth header`, test with
  `hermes mcp test <name>`, then restart the gateway to discover tools as
  `mcp_<server>_<tool>`.
