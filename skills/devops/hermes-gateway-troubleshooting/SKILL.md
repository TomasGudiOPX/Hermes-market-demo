---
name: hermes-gateway-troubleshooting
description: "Debug Hermes gateway adapters that hang connecting."
version: 1.0.0
metadata:
  hermes:
    tags: [hermes, gateway, telegram, discord, messaging, debugging, logs]
    related_skills: [hermes-agent]
---

# Hermes Gateway Troubleshooting

Diagnosing and verifying Hermes' messaging gateway and its per-platform adapters
(Telegram, Discord, Slack, WhatsApp, Signal, …). Covers the failure modes that
are NOT obvious from the console and are easy to misdiagnose as a hang.

## The #1 trap: the console is not the real log

Hermes routes log records by level: **WARNING and above go to the console/stdout,
while INFO (and DEBUG) go to the log files under `~/.hermes/logs/`.** This means
the "success" lines for a gateway adapter — which are INFO level — never appear
on stdout.

Concrete symptom: you start `hermes gateway run` and the last thing on stdout is

    [Telegram] Connecting to Telegram (attempt 1/8)…

then nothing. It looks like it's hanging. **It is usually not hanging** — the
adapter finished connecting a few seconds later, and the confirmation was logged
to a file:

    [Telegram] Connected to Telegram (polling mode)
    gateway.run: ✓ telegram connected

So before declaring a hang, read the files. Never diagnose gateway startup from
`hermes gateway run > /tmp/x.log 2>&1` alone.

## Where the logs actually are

    ~/.hermes/logs/gateway.log   # gateway + adapter lifecycle (the one you want)
    ~/.hermes/logs/agent.log     # superset incl. per-message agent activity
    ~/.hermes/logs/errors.log    # WARNING+ rolled up
    ~/.hermes/logs/gateway-exit-diag.log      # written on clean shutdown
    ~/.hermes/logs/gateway-shutdown-diag.log  # shutdown state dump
    ~/.hermes/logs/gateway_faulthandler.log   # blocked-loop stack dumps

Resolve the real home from `$HERMES_HOME` — never hardcode `~/.hermes`.

## Verification workflow (in this order)

1. **Read the log file, not stdout.** Grep for the confirmation line:
   `grep -iE "connected|polling" ~/.hermes/logs/gateway.log | tail`. Confirm you
   see `Connected to <platform> (polling mode)` and `✓ <platform> connected`.
2. **Confirm the process is alive** (`ps` on the gateway PID) and that it holds a
   live connection: `cat /proc/net/tcp | awk 'NR>1 && $4=="01"'` should show an
   ESTABLISHED socket to the platform (e.g. api.telegram.org = 149.154.x.x:443).
   Decode `/proc/net/tcp` remote addresses as little-endian hex (6EA69A95 → 95.9A.A6.6E → 149.154.166.110).
3. **Prove delivery with a real message.** The only end-to-end proof is a message
   the user receives. If the user has already started a DM with the bot, send one
   via the platform API from the shell (see `references/telegram-setup.md` for the
   curl form); check the response `"ok":true`.
4. Only if the file log shows a *genuine* timeout/error do you start the deeper
   network/process investigation below.

## When it IS a real connect stall

If `gateway.log` shows the adapter retrying (`Connect attempt N/8 failed/timed out`)
rather than a clean `Connected`, investigate the network path:

- **Broken IPv6 is a classic.** `getent hosts api.telegram.org` may return an IPv6
  (AAAA) address while the host has no working IPv6 route. Force-test each family:
  `curl -4 …` vs `curl -6 …`. If IPv4 works and IPv6 fails, the adapter's httpx
  connect to the IPv6 address can stall.
- **Fallback IP transport.** Hermes' Telegram adapter normally discovers fallback
  IPv4 IPs (or falls back to seed IPs `149.154.166.110` / `149.154.167.220`) and
  connects with a hostname-preserving transport. To force the plain
  `api.telegram.org` path: `HERMES_TELEGRAM_DISABLE_FALLBACK_IPS=true`.
  Bounded discovery: `HERMES_TELEGRAM_FALLBACK_DISCOVERY_TIMEOUT` (seconds, default 5).
- **Reproduce with httpx directly** in the gateway venv (same library the adapter
  uses) to isolate whether it's the app or the network:
  `venv/bin/python3 -c "import httpx; print(httpx.get('https://api.telegram.org/bot<TOKEN>/getMe', timeout=8).status_code)"`.
  If that returns 200 instantly, the network is fine and the "hang" is elsewhere
  (most likely the false-hang trap above — go back to the log file).
- **Get a real stack** with py-spy when the loop is genuinely wedged:
  `venv/bin/pip install py-spy && venv/bin/py-spy dump --pid <PID>`. An idle main
  thread in `select`/`run_forever` plus idle worker threads usually means the
  gateway already reached its serving loop (i.e. startup finished), not a hang.

## Setup quick reference (per-platform)

Secrets go in `~/.hermes/.env`; the pattern is consistent across platforms:

    <PLATFORM>_BOT_TOKEN=<token>
    <PLATFORM>_ALLOWED_USERS=<comma-separated user IDs>   # allowlist; deny all others
    <PLATFORM>_HOME_CHANNEL=<chat id>                    # cron delivery target

The platform SDK must be installed in the Hermes venv (e.g. `python-telegram-bot`
for Telegram, `discord.py` for Discord) or the adapter won't import. Check with
`hermes doctor` (lists them under "Required Packages" / optional). Then:

    hermes gateway run          # foreground
    hermes gateway install      # user service (needs logind session OR linger)
    sudo hermes gateway install --system   # boot-time system service (needs sudo)

## Persistence gotchas

- `sudo hermes gateway install --system` needs a sudo password — non-interactive
  shells often don't have one, so this may need the user to run it themselves.
- A user-level service (`hermes gateway install`) requires a logind session or
  lingering. On a headless host reached via `su`, `systemctl --user` fails with
  "Operation not permitted" and `XDG_RUNTIME_DIR` may point at the wrong uid —
  meaning the user service can't start until `sudo loginctl enable-linger $USER`.
- Only ONE gateway may poll a given platform (Telegram enforces a single
  getUpdates consumer). Stop the manual/background gateway before starting the
  service, or the second one gets "Conflict: terminated by other getUpdates request".

## Pitfalls

- Treating stdout as the whole story and chasing a "hang" that isn't there. Read
  `~/.hermes/logs/gateway.log` first; it is the single biggest time-saver here.
- `write_file`/`patch` tools refuse to edit `~/.hermes/.env` (protected credential
  file). Edit it via a terminal heredoc/Python instead.
- Don't confuse the bot's *user ID* with a chat ID: the DM chat id equals the user
  id, but group chat ids are negative (`-100…`).
- A stale `XDG_CACHE_HOME`/`XDG_CONFIG_HOME` pointing at another user's home breaks
  `uv` (→ "Failed to initialize cache … Permission denied") during Hermes'
  auto-update recovery. That's an environment issue, separate from gateway health.

See `references/telegram-setup.md` for the end-to-end Telegram walkthrough with
exact commands.
