# Skills Sync: commit identity and temp clone recovery

Use this when `skills_sync.py push` copies skill changes into the temp clone but git commit fails, commonly with `Identidad del autor desconocido` / missing `user.name` or `user.email`.

## Durable lesson

Do not trust a follow-up `skills_sync.py status` alone after a failed push. The script may compare local skills to the dirty temp clone and report `Everything is in sync` even though the remote branch did not advance.

## Recovery pattern

1. Configure a non-secret git identity if missing:

```bash
git config --global user.name 'Hermes Agent'
git config --global user.email 'hermes-agent@users.noreply.local'
```

2. Inspect the temp clone used by the script:

```bash
git -C /tmp/hermes-skills-sync status --short --branch
git -C /tmp/hermes-skills-sync diff --cached --stat
```

3. If changes are staged there, commit and push from the temp clone directly:

```bash
cd /tmp/hermes-skills-sync
git commit -m 'chore: sync Hermes QA workflow skills'
git push origin main
```

4. Verify the remote branch actually advanced and matches local HEAD:

```bash
git -C /tmp/hermes-skills-sync rev-parse HEAD
git -C /tmp/hermes-skills-sync ls-remote origin refs/heads/main | cut -f1
git -C /tmp/hermes-skills-sync status --short --branch
```

## Reporting

Report the final commit SHA and explicitly say whether the remote SHA matched local HEAD. If the temp clone remains dirty or remote SHA differs, do not report the sync as complete.