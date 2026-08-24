# Git Authentication Pitfalls

Lessons learned from setting up git access for the skills sync workflow.

## SSH Deploy Keys: Public Key Is Not Enough

For private skill repositories cloned via `git@github.com:OWNER/REPO.git`, a user may provide a public key line (`ssh-ed25519 ...`) or a fingerprint (`SHA256:...`). These identify a key but **cannot authenticate**. The agent needs the matching private key loaded locally or must generate a new dedicated key and ask the user to add its public half as a deploy key.

### Diagnostic pattern

```bash
# See whether any private keys are present or loaded
ls -la ~/.ssh
ssh-add -l -E sha256 || true
ssh -o BatchMode=yes -T git@github.com || true

# Verify a supplied public key matches the claimed fingerprint
tmp=$(mktemp)
printf '%s\n' 'ssh-ed25519 AAAA... comment' > "$tmp"
ssh-keygen -lf "$tmp" -E sha256
rm -f "$tmp"
```

If GitHub says `Permission denied (publickey)` and `ssh-add -l` has no identity with the expected fingerprint, generate a dedicated key instead of retrying the same clone.

### Safe dedicated deploy-key flow

```bash
mkdir -p ~/.ssh && chmod 700 ~/.ssh
ssh-keygen -t ed25519 -C "hermes-skills-sync@$(hostname)" -f ~/.ssh/hermes_skills_sync_ed25519 -N ""
chmod 600 ~/.ssh/hermes_skills_sync_ed25519
chmod 644 ~/.ssh/hermes_skills_sync_ed25519.pub
ssh-keygen -lf ~/.ssh/hermes_skills_sync_ed25519.pub -E sha256
cat ~/.ssh/hermes_skills_sync_ed25519.pub
```

Ask the user to add that public key to the target GitHub repo as a deploy key. Use read-only unless the sync workflow must push. Then verify and clone:

```bash
GIT_SSH_COMMAND="ssh -i ~/.ssh/hermes_skills_sync_ed25519 -o IdentitiesOnly=yes -o StrictHostKeyChecking=accept-new" \
  git ls-remote git@github.com:OWNER/REPO.git

GIT_SSH_COMMAND="ssh -i ~/.ssh/hermes_skills_sync_ed25519 -o IdentitiesOnly=yes -o StrictHostKeyChecking=accept-new" \
  git clone git@github.com:OWNER/REPO.git ~/.hermes/sources/REPO

cd ~/.hermes/sources/REPO
git config core.sshCommand "ssh -i ~/.ssh/hermes_skills_sync_ed25519 -o IdentitiesOnly=yes -o StrictHostKeyChecking=accept-new"
```


## GitHub Fine-Grained PATs vs Classic PATs

**Fine-grained PATs** (`github_pat_*` prefix):
- Authenticate successfully on the API (GET /user returns 200, GET /repos shows `push: true` in permissions)
- **FAIL on `git push`** with HTTP 403: `"Resource not accessible by personal access token"`
- Also fail on the Contents API (PUT /repos/.../contents/...) with the same 403
- The fix: ensure the token has explicit **Contents: Read and write** permission for the target repository
- Even if the API reports `push: true`, the fine-grained token still needs the Contents permission explicitly set

**Classic PATs** (`ghp_*` prefix):
- Work universally for git push when `repo` scope is selected
- Simpler to set up — just check the `repo` scope box
- Recommended for agent/headless use where interactive permission tweaking isn't practical

## Bitbucket API Tokens

**Repository access tokens** (`ATATT3xF` prefix):
- Authenticate for git operations on the specific repo they're scoped to
- **Cannot** list workspaces, create repos, or access workspace-level API endpoints
- All workspace/2.0 API calls return 401: `"Token is invalid, expired, or not supported for this endpoint."`
- Git push to a repo you don't have access to returns: `"You may not have access to this repository or it no longer exists"` (not "invalid token")

**To create a new repo on Bitbucket:**
- You need a **workspace-level API token** (from Workspace Settings → API Tokens, with Workspace write scope)
- Or create the repo manually in the web UI, then use a repo access token for push/pull

## Diagnostic Pattern

When a token fails, test systematically:

```bash
# Step 1: Does the API accept the token?
curl -s -H "Authorization: token <TOKEN>" "https://api.github.com/user" -w "%{http_code}"
# 200 = token valid; 401 = token invalid/expired

# Step 2: Does git push work?
git push <remote> <branch>
# 403 = token valid but missing write/contents permission
# 128 "Authentication failed" = token not accepted by git at all

# Step 3: Does the Contents API work?
curl -s -X PUT -H "Authorization: token <TOKEN>" "https://api.github.com/repos/.../contents/test.txt" ...
# 403 "Resource not accessible" = fine-grained PAT missing Contents: write
```

## Recommended Token Setup for Hermes Agent

1. **GitHub**: Use a classic PAT (`ghp_*`) with `repo` scope
2. **Bitbucket**: Use workspace-level API tokens for repo creation; repo tokens for push-only
3. Store in `~/.git-credentials` with `credential.helper store`:
   ```
   https://<username>:<token>@github.com
   ```
4. Verify with: `git ls-remote https://github.com/<user>/<repo>.git`