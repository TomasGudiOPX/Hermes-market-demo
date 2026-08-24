#!/usr/bin/env python3
"""
Hermes Skills Sync Utility
Keeps local custom skills in sync with a remote git repository.

Usage:
  python3 skills_sync.py status [options]
  python3 skills_sync.py push   [options]
  python3 skills_sync.py pull   [options]
  python3 skills_sync.py list

Options:
  --repo=URL           Git repo URL (default: https://github.com/TomasGudiOPX/Hermes-market-demo.git)
  --clone_dir=PATH     Where to clone (default: /tmp/hermes-skills-sync)
  --branch=NAME        Git branch (default: main)
"""
import os, sys, hashlib, subprocess, shutil
from pathlib import Path

SKILLS_DIR = Path(os.environ.get("HERMES_HOME", str(Path.home() / ".hermes"))) / "skills"
BUNDLED_MANIFEST = SKILLS_DIR / ".bundled_manifest"
DEFAULT_REPO = "https://github.com/TomasGudiOPX/Hermes-market-demo.git"
DEFAULT_BRANCH = "main"
DEFAULT_CLONE_DIR = Path("/tmp/hermes-skills-sync")


def get_bundled_names():
    names = set()
    if BUNDLED_MANIFEST.exists():
        for line in BUNDLED_MANIFEST.read_text().strip().splitlines():
            if ":" in line:
                name, _ = line.split(":", 1)
                names.add(name.strip())
    return names


# Skills from these sources are excluded (they're managed separately)
EXCLUDED_PREFIXES = ("gstack",)  # gstack plugin suite — managed by gstack-upgrade

def is_excluded(name):
    """Check if a skill should be excluded from sync."""
    for prefix in EXCLUDED_PREFIXES:
        if name.startswith(prefix):
            return True
    return False


def get_custom_skills():
    bundled = get_bundled_names()
    custom = []
    if not SKILLS_DIR.exists():
        return custom
    for top_dir in sorted(SKILLS_DIR.iterdir()):
        if not top_dir.is_dir() or top_dir.name.startswith("."):
            continue
        # Case 1: root-level skill (SKILL.md directly inside top_dir)
        if (top_dir / "SKILL.md").exists() and top_dir.name not in bundled:
            if is_excluded(top_dir.name):
                continue
            custom.append({
                "category": "",
                "name": top_dir.name,
                "path": str(top_dir),
                "relative": top_dir.name,
            })
            continue
        # Case 2: category dir with skills inside
        for skill_dir in sorted(top_dir.iterdir()):
            if not skill_dir.is_dir() or skill_dir.name.startswith("."):
                continue
            if skill_dir.name in bundled:
                continue
            if is_excluded(skill_dir.name):
                continue
            if not (skill_dir / "SKILL.md").exists():
                continue
            custom.append({
                "category": top_dir.name,
                "name": skill_dir.name,
                "path": str(skill_dir),
                "relative": f"{top_dir.name}/{skill_dir.name}",
            })
    return custom


def file_hash(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def hash_directory(dir_path):
    hashes = {}
    if not Path(dir_path).exists():
        return hashes
    for root, dirs, files in os.walk(dir_path):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for fname in files:
            if fname.startswith("."):
                continue
            full = Path(root) / fname
            rel = str(full.relative_to(dir_path))
            hashes[rel] = file_hash(full)
    return hashes


def run(cmd, cwd=None):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
    return r.returncode, r.stdout.strip(), r.stderr.strip()


def ensure_clone(repo_url, clone_dir, branch):
    if (clone_dir / ".git").exists():
        code, _, err = run(f"git pull origin {branch}", cwd=str(clone_dir))
        if code != 0:
            print(f"  Pull failed: {err}")
    else:
        clone_dir.parent.mkdir(parents=True, exist_ok=True)
        code, _, err = run(f"git clone --branch {branch} {repo_url} {clone_dir}")
        if code != 0:
            print(f"  Clone failed: {err}")
            return False
    return True


def status(args):
    repo_url = args.get("repo", DEFAULT_REPO)
    clone_dir = Path(args.get("clone_dir", DEFAULT_CLONE_DIR))
    branch = args.get("branch", DEFAULT_BRANCH)

    print("=" * 60)
    print(f"  Skills Sync - Status Check")
    print(f"  Local:  {SKILLS_DIR}")
    print(f"  Remote: {repo_url}")
    print("=" * 60)

    custom = get_custom_skills()
    print(f"\n  Custom skills found locally: {len(custom)}")

    if not ensure_clone(repo_url, clone_dir, branch):
        print("\n  Could not access remote repo. Showing local skills only.")
        for s in custom:
            print(f"    {s['relative']}")
        return

    repo_skills_dir = clone_dir / "skills"
    repo_skills = set()
    if repo_skills_dir.exists():
        for top_dir in repo_skills_dir.iterdir():
            if not top_dir.is_dir() or top_dir.name.startswith("."):
                continue
            # Case 1: root-level skill (SKILL.md directly inside)
            if (top_dir / "SKILL.md").exists():
                repo_skills.add(top_dir.name)
                continue
            # Case 2: category with skills inside
            for skill_dir in top_dir.iterdir():
                if skill_dir.is_dir() and (skill_dir / "SKILL.md").exists():
                    repo_skills.add(f"{top_dir.name}/{skill_dir.name}")

    local_names = {s["relative"] for s in custom}
    only_local = local_names - repo_skills
    only_repo = repo_skills - local_names
    in_both = local_names & repo_skills

    drifted = []
    for s in custom:
        if s["relative"] in in_both:
            lh = hash_directory(s["path"])
            rh = hash_directory(str(repo_skills_dir / s["relative"]))
            if lh != rh:
                all_keys = set(lh) | set(rh)
                diffs = []
                for key in sorted(all_keys):
                    if lh.get(key) != rh.get(key):
                        if key not in rh:
                            diffs.append(f"  + {key} (local only)")
                        elif key not in lh:
                            diffs.append(f"  - {key} (repo only)")
                        else:
                            diffs.append(f"  ~ {key} (modified)")
                drifted.append((s["relative"], diffs))

    print(f"\n  Summary:")
    print(f"    In sync:       {len(in_both) - len(drifted)}")
    print(f"    Drifted:       {len(drifted)}")
    print(f"    Local only:    {len(only_local)}")
    print(f"    Repo only:     {len(only_repo)}")

    if only_local:
        print(f"\n  Skills only in local (not yet pushed):")
        for name in sorted(only_local):
            print(f"    {name}")

    if only_repo:
        print(f"\n  Skills only in repo (not yet local):")
        for name in sorted(only_repo):
            print(f"    {name}")

    if drifted:
        print(f"\n  Skills with content drift:")
        for name, diffs in drifted:
            print(f"    {name}")
            for d in diffs[:5]:
                print(f"      {d}")
            if len(diffs) > 5:
                print(f"      ... and {len(diffs) - 5} more")

    if not only_local and not only_repo and not drifted:
        print("\n  Everything is in sync!")


def push(args):
    repo_url = args.get("repo", DEFAULT_REPO)
    clone_dir = Path(args.get("clone_dir", DEFAULT_CLONE_DIR))
    branch = args.get("branch", DEFAULT_BRANCH)

    print("=" * 60)
    print(f"  Skills Sync - Push to Remote")
    print(f"  Remote: {repo_url}")
    print("=" * 60)

    if not ensure_clone(repo_url, clone_dir, branch):
        print("  Could not access remote repo.")
        return

    custom = get_custom_skills()
    print(f"\n  Custom skills to push: {len(custom)}")

    repo_skills_dir = clone_dir / "skills"
    repo_skills_dir.mkdir(parents=True, exist_ok=True)

    pushed, updated, unchanged = 0, 0, 0
    for s in custom:
        dest = repo_skills_dir / s["relative"]
        lh = hash_directory(s["path"])
        rh = hash_directory(str(dest)) if dest.exists() else {}

        if lh == rh:
            unchanged += 1
            continue

        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(s["path"], dest, ignore=shutil.ignore_patterns(".*"))
        pushed += 1
        if rh:
            updated += 1
        label = "updated" if rh else "new"
        print(f"  {label:>10}  {s['relative']}")

    print(f"\n  New: {pushed - updated}  Updated: {updated}  Unchanged: {unchanged}")

    if pushed == 0:
        print("  Everything already in sync - nothing to push.")
        return

    run("git add -A", cwd=str(clone_dir))
    code, out, err = run('git commit -m "Sync custom skills from local"', cwd=str(clone_dir))
    if code != 0:
        combined = "\n".join(x for x in [out, err] if x)
        print(f"\n  Commit failed: {combined}")
        return

    code, out, err = run(f"git push origin {branch}", cwd=str(clone_dir))
    if code == 0:
        print(f"\n  Pushed {pushed} skill(s) to {repo_url}")
    else:
        print(f"\n  Push failed: {err}")


def pull(args):
    repo_url = args.get("repo", DEFAULT_REPO)
    clone_dir = Path(args.get("clone_dir", DEFAULT_CLONE_DIR))
    branch = args.get("branch", DEFAULT_BRANCH)

    print("=" * 60)
    print(f"  Skills Sync - Pull from Remote")
    print(f"  Remote: {repo_url}")
    print("=" * 60)

    if not ensure_clone(repo_url, clone_dir, branch):
        print("  Could not access remote repo.")
        return

    repo_skills_dir = clone_dir / "skills"
    if not repo_skills_dir.exists():
        print("  No skills/ directory found in repo.")
        return

    local_bundled = get_bundled_names()
    installed, updated, unchanged = 0, 0, 0
    for top_dir in sorted(repo_skills_dir.iterdir()):
        if not top_dir.is_dir() or top_dir.name.startswith("."):
            continue
        # Case 1: root-level skill (SKILL.md directly inside)
        if (top_dir / "SKILL.md").exists():
            if top_dir.name in local_bundled:
                continue
            rel = top_dir.name
            dest = SKILLS_DIR / top_dir.name
            rh = hash_directory(str(top_dir))
            lh = hash_directory(str(dest)) if dest.exists() else {}
            if rh == lh:
                unchanged += 1
                continue
            if dest.exists():
                shutil.rmtree(dest)
            shutil.copytree(top_dir, dest, ignore=shutil.ignore_patterns(".*"))
            installed += 1
            label = "updated" if lh else "new"
            print(f"  {label:>10}  {rel}")
            continue
        # Case 2: category with skills inside
        for skill_dir in sorted(top_dir.iterdir()):
            if not skill_dir.is_dir() or skill_dir.name.startswith("."):
                continue
            if not (skill_dir / "SKILL.md").exists():
                continue
            if skill_dir.name in local_bundled:
                continue

            rel = f"{top_dir.name}/{skill_dir.name}"
            dest = SKILLS_DIR / top_dir.name / skill_dir.name
            rh = hash_directory(str(skill_dir))
            lh = hash_directory(str(dest)) if dest.exists() else {}

            if rh == lh:
                unchanged += 1
                continue

            if dest.exists():
                shutil.rmtree(dest)
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(skill_dir, dest, ignore=shutil.ignore_patterns(".*"))
            installed += 1
            if lh:
                updated += 1
            label = "updated" if lh else "new"
            print(f"  {label:>10}  {rel}")

    print(f"\n  New: {installed - updated}  Updated: {updated}  Unchanged: {unchanged}")
    if installed == 0:
        print("  Everything already in sync - nothing to pull.")
    else:
        print(f"\n  Installed {installed} skill(s) locally.")


def list_skills(args):
    custom = get_custom_skills()
    print(f"Custom skills ({len(custom)}):")
    for s in custom:
        print(f"  {s['relative']}")
    bundled = get_bundled_names()
    print(f"\nBundled skills: {len(bundled)} (not synced)")


if __name__ == "__main__":
    args = {}
    for a in sys.argv[2:]:
        if a.startswith("--"):
            k, _, v = a[2:].partition("=")
            args[k] = v
    cmd = sys.argv[1] if len(sys.argv) > 1 else None
    if cmd == "status":
        status(args)
    elif cmd == "push":
        push(args)
    elif cmd == "pull":
        pull(args)
    elif cmd == "list":
        list_skills(args)
    else:
        print(__doc__)