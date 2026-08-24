# Post-Push Verification for Skills Sync

Use this after any `skills_sync.py push`, especially when the helper prints success but the user expects remote state to be updated.

## Why

A sync push is not complete until the remote branch actually advances and a fresh status check reports no drift. Git helper output can be misleading if commit setup fails, the temp clone is dirty, or authentication differs between HTTPS and SSH.

## Verification sequence

1. Check remote branch SHA after push:

```bash
GIT_SSH_COMMAND="ssh -i <private-key> -o IdentitiesOnly=yes -o StrictHostKeyChecking=accept-new" \
  git ls-remote <repo-url> refs/heads/<branch>
```

2. Check the sync clone is clean and on the expected branch:

```bash
cd /tmp/hermes-skills-sync
git status --short --branch
git log -2 --oneline
```

3. Run a fresh status check using the same remote URL/auth mode used for push:

```bash
GIT_SSH_COMMAND="ssh -i <private-key> -o IdentitiesOnly=yes -o StrictHostKeyChecking=accept-new" \
  python3 scripts/skills_sync.py status --repo=<repo-url> --branch=<branch>
```

Completion criterion:

```text
In sync:       <all custom skills>
Drifted:       0
Local only:    0
Repo only:     0
Everything is in sync!
```

## If push reports success but remote SHA did not advance

Inspect the temp clone:

```bash
cd /tmp/hermes-skills-sync
git status --short --branch
git diff --cached --stat
git log -1 --oneline
```

If changes are staged but not committed, commit with an explicit local identity and push with the same SSH command:

```bash
git -c user.name='Hermes Agent' \
    -c user.email='hermes-agent@users.noreply.github.com' \
    commit -m "Sync custom Hermes skills"

GIT_SSH_COMMAND="ssh -i <private-key> -o IdentitiesOnly=yes -o StrictHostKeyChecking=accept-new" \
  git push origin <branch>
```

Then repeat the verification sequence.

## Auth mode notes

- HTTPS remotes may fail in non-interactive sessions with `could not read Username`.
- Prefer an already configured SSH remote/deploy key when available.
- A public key or fingerprint is not enough; verify the private key works with `git ls-remote`.
