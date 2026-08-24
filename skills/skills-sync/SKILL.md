---
name: skills-sync
description: "Keep local custom Hermes skills in sync with a git repository."
version: 1.0.0
author: Tomas JG
license: MIT
platforms: [linux, macos]
metadata:
  hermes:
    tags: [Skills, Git, Sync, GitHub, Repository, Hermes]
    related_skills: []
---

# Skills Sync — Custom Hermes Skills Repository

Keep your **custom** Hermes skills in a git repository for sharing, version control,
and multi-machine sync. Detects drift, pushes local changes, and pulls remote updates.

## What Gets Synced

Only **custom skills** (those not in the bundled manifest) are synced.
Bundled skills (shipped with Hermes) are skipped automatically.
Gstack plugin skills (any skill starting with `gstack`) are also excluded —
they're managed by the gstack plugin suite via `gstack-upgrade`.

### Exclusion List

| Excluded | Reason |
|----------|--------|
| Bundled skills (72) | Shipped with Hermes, maintained by the team |
| `gstack-*` skills (53) | Managed by gstack plugin suite |

## Prerequisites

- Git installed and configured with push access to the remote repo
- A GitHub (or other git host) repository to store skills
- The `skills_sync.py` helper script (bundled with this skill at `scripts/skills_sync.py`)

### Setup

```bash
git config --global user.name "Your Name"
git config --global user.email "your-email@example.com"
git config --global credential.helper store
```

### Private repo access with a dedicated deploy key

When syncing from a private skills repo over SSH, first verify whether the private key is actually present. A public key or SHA256 fingerprint only identifies a key; it cannot authenticate. If no usable private key exists, generate a dedicated repo deploy key, give the user the public key to add in GitHub, then clone/pull with `core.sshCommand` pinned to that key.

```bash
mkdir -p ~/.ssh && chmod 700 ~/.ssh
ssh-keygen -t ed25519 -C "hermes-skills-sync@$(hostname)" -f ~/.ssh/hermes_skills_sync_ed25519 -N ""
chmod 600 ~/.ssh/hermes_skills_sync_ed25519
ssh-keygen -lf ~/.ssh/hermes_skills_sync_ed25519.pub -E sha256
cat ~/.ssh/hermes_skills_sync_ed25519.pub

# After the user adds it as a GitHub deploy key:
GIT_SSH_COMMAND="ssh -i ~/.ssh/hermes_skills_sync_ed25519 -o IdentitiesOnly=yes -o StrictHostKeyChecking=accept-new" \
  git ls-remote git@github.com:OWNER/REPO.git

git clone git@github.com:OWNER/REPO.git ~/.hermes/sources/REPO
cd ~/.hermes/sources/REPO
git config core.sshCommand "ssh -i ~/.ssh/hermes_skills_sync_ed25519 -o IdentitiesOnly=yes -o StrictHostKeyChecking=accept-new"
```

See `references/git-auth-pitfalls.md` for the public-key-vs-private-key trap and the safe deploy-key install flow.

## Commands

The sync utility is at `scripts/skills_sync.py` relative to this skill directory.

### status — Check drift

```bash
python3 scripts/skills_sync.py status
```

Shows what's in sync, what's drifted, what's only local, and what's only in the repo.

### push — Backup local skills to repo

```bash
python3 scripts/skills_sync.py push
```

Copies all custom skills to the repo, commits, and pushes.

### pull — Install skills from repo to local

```bash
python3 scripts/skills_sync.py pull
```

Copies skills from the repo into the local Hermes installation.

### list — Show custom skills

```bash
python3 scripts/skills_sync.py list
```

## Options

| Option | Default | Description |
|--------|---------|-------------|
| `--repo=URL` | `https://github.com/TomasGudiOPX/Hermes-market-demo.git` | Git repo URL |
| `--clone_dir=PATH` | `/tmp/hermes-skills-sync` | Temp clone directory |
| `--branch=NAME` | `main` | Git branch |

## Agent Workflow

1. Determine intent: status check, push (backup), or pull (restore)
2. Verify git credentials work: `git ls-remote <repo_url>` when the same URL/auth mode will be used by the sync operation. If a direct HTTPS probe fails in a non-interactive session but `skills_sync.py push` succeeds and a fresh `skills_sync.py status` reports everything in sync, treat the script's post-push status as the verification signal and report the HTTPS probe caveat separately.
3. Run the appropriate command
4. After push, verify the remote branch SHA advanced and run a fresh `status` check with the same repo URL/auth mode; see `references/post-push-verification.md`
5. If commit fails because git identity is missing, or push output is ambiguous, recover from the temp clone and verify SHA as described in `references/commit-identity-and-temp-clone-recovery.md`
6. Report results: what synced, what skipped, final remote SHA or verified in-sync status, and any errors

## Repository Structure

```
repo/
├── README.md
├── skills/
│   ├── software-development/
│   │   ├── qa-openspec/
│   │   │   └── SKILL.md
│   │   └── ...
│   └── productivity/
│       └── ...
└── scripts/
    └── skills_sync.py
```

## Pitfalls

- **Bundled skills are never overwritten** — the sync skips skills in the bundled manifest
- **Hidden files skipped** — any file starting with `.` is ignored (sessions, caches, curator state)
- **No conflict resolution** — last-write-wins. Use git branching for collaborative editing
- **Temp clone cleared on reboot** — `/tmp/` is ephemeral; the script does a fresh clone each time
- **Push output is not final proof** — always verify the remote branch SHA and run a fresh status check after push; a dirty temp clone or missing git identity can leave staged changes unpushed even when output looks successful
- **HTTPS auth may be non-interactive** — if HTTPS prompts fail, look for an existing SSH remote/deploy key and run status/push with `GIT_SSH_COMMAND` pinned to that private key