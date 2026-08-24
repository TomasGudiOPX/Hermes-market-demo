#!/usr/bin/env python3
"""Probe a remote MCP StreamableHTTP endpoint: initialize handshake + tools/list.

Usage:
    python3 probe_streamable_http.py <URL> [TOKEN]

Stdlib only (no dependencies). Prints the server identity and the full list of
tool names currently exposed. Omit TOKEN for an unauthenticated endpoint.

Why: a deployer may report an MCP endpoint "is live" while it only serves a
subset of tools (e.g. read-only but not the write/approve tools). The handshake
HTTP 200 is not proof — the tools/list output is.
"""
import json
import sys
import urllib.error
import urllib.request


def post(url, token, payload, session_id=None):
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
    }
    if token:
        headers["Authorization"] = "Bearer " + token
    req = urllib.request.Request(
        url, data=json.dumps(payload).encode(), headers=headers, method="POST"
    )
    if session_id:
        req.add_header("Mcp-Session-Id", session_id)
    try:
        resp = urllib.request.urlopen(req, timeout=30)
    except urllib.error.HTTPError as e:
        return e.code, None, e.read().decode()
    sid = None
    for k, v in resp.headers.items():
        if k.lower() == "mcp-session-id":
            sid = v
    return resp.status, sid, resp.read().decode()


def parse_sse(body):
    """StreamableHTTP replies are SSE: one JSON object per 'data:' line."""
    out = []
    for line in body.splitlines():
        if line.startswith("data:"):
            out.append(json.loads(line[5:].strip()))
    return out


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    url = sys.argv[1]
    token = sys.argv[2] if len(sys.argv) > 2 else None

    st, sid, body = post(
        url, token,
        {"jsonrpc": "2.0", "id": 1, "method": "initialize",
         "params": {"protocolVersion": "2025-03-26", "capabilities": {},
                    "clientInfo": {"name": "probe", "version": "0.0.1"}}},
    )
    print("[initialize] HTTP %s  session-id=%s" % (st, sid))
    for msg in parse_sse(body):
        res = msg.get("result", {})
        info = res.get("serverInfo")
        if info:
            print("  server: %s v%s (protocol %s)"
                  % (info.get("name"), info.get("version"),
                     res.get("protocolVersion")))

    st2, _, body2 = post(
        url, token,
        {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
        session_id=sid,
    )
    print("[tools/list] HTTP %s" % st2)
    for msg in parse_sse(body2):
        tools = msg.get("result", {}).get("tools", [])
        names = [t.get("name") for t in tools]
        print("  tool count: %d" % len(names))
        for n in names:
            print("    - " + n)


if __name__ == "__main__":
    main()
