#!/usr/bin/env python3
"""Read-only inventory of branches and worktrees in every workspace repository.

Usage: python3 -I inventory.py [WORKSPACE_ROOT]

Prints one tab-separated row per branch, worktree, and default checkout:
repo, kind, name, verdict, reason. It runs `git fetch --prune` and `gh pr list`;
it never deletes or moves anything.
"""

import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def run(args, cwd=None, check=True):
    result = subprocess.run(args, cwd=cwd, capture_output=True, text=True)
    if check and result.returncode != 0:
        raise RuntimeError(f"{' '.join(args)}: {result.stderr.strip()}")
    return result.stdout.rstrip()


def git(repo, *args, check=True):
    return run(["git", "-C", str(repo), *args], check=check)


def repo_slug(repo):
    url = git(repo, "remote", "get-url", "origin", check=False)
    match = re.search(r"github\.com[:/]([^/]+/[^/]+?)(?:\.git)?$", url)
    return match.group(1) if match else None


def default_branch(repo, slug):
    ref = git(repo, "symbolic-ref", "--short", "refs/remotes/origin/HEAD", check=False)
    if ref:
        return ref.removeprefix("origin/")
    return run(["gh", "repo", "view", slug, "--json", "defaultBranchRef", "-q", ".defaultBranchRef.name"])


def pulls_by_head(slug):
    raw = run([
        "gh", "pr", "list", "--repo", slug, "--state", "all", "--limit", "1000",
        "--json", "number,state,mergedAt,closedAt,headRefName,headRefOid,updatedAt",
    ])
    pulls = {}
    for pr in sorted(json.loads(raw), key=lambda p: p["updatedAt"]):
        current = pulls.get(pr["headRefName"])
        if current is None or current["state"] != "OPEN":
            pulls[pr["headRefName"]] = pr
    return pulls


def worktrees(repo):
    entries, entry = [], {}
    for line in git(repo, "worktree", "list", "--porcelain").splitlines() + [""]:
        if not line:
            if entry:
                entries.append(entry)
            entry = {}
            continue
        key, _, value = line.partition(" ")
        entry[key] = value or True
    return entries


def summarize(status_lines):
    paths = [line[3:] for line in status_lines]
    more = f" (+{len(paths) - 3} more)" if len(paths) > 3 else ""
    return ", ".join(paths[:3]) + more


def process_cwds():
    out = run(["lsof", "-a", "-d", "cwd", "-Fn"], check=False)
    return [Path(line[1:]) for line in out.splitlines() if line.startswith("n")]


def in_use(path, cwds):
    return any(cwd == path or path in cwd.parents for cwd in cwds)


def is_ancestor(repo, commit, ref):
    return subprocess.run(
        ["git", "-C", str(repo), "merge-base", "--is-ancestor", commit, ref],
        capture_output=True,
    ).returncode == 0


def authored_after(repo, tip, closed_at):
    # Author dates survive rebases, so only genuinely new work counts.
    authored = git(repo, "log", "-1", "--format=%aI", tip)
    return datetime.fromisoformat(authored) > datetime.fromisoformat(closed_at)


def contained_elsewhere(repo, branch, tip, default):
    if is_ancestor(repo, tip, f"origin/{default}"):
        return f"origin/{default}"
    for ref in git(repo, "for-each-ref", "--contains", tip, "--format=%(refname:short)", "refs/remotes/origin").splitlines():
        if ref not in ("origin", "origin/HEAD", f"origin/{branch}"):
            return ref
    return None


def classify(repo, branch, tip, default, pulls):
    pr = pulls.get(branch)
    if pr and pr["state"] == "OPEN":
        return "keep", f"open PR #{pr['number']}"
    if pr and pr["headRefOid"] != tip and authored_after(repo, tip, pr["closedAt"]):
        return "keep", f"new commits after PR #{pr['number']} ({pr['state'].lower()})"
    if pr and pr["mergedAt"]:
        note = "" if pr["headRefOid"] == tip else ", tip differs from PR head"
        return "delete", f"merged PR #{pr['number']}{note}"
    if pr:
        return "delete", f"closed unmerged PR #{pr['number']}"
    holder = contained_elsewhere(repo, branch, tip, default)
    if holder:
        return "delete", f"no PR, contained in {holder}"
    return "keep", "no PR, unique commits"


def inventory(repo, cwds):
    slug = repo_slug(repo)
    if not slug:
        yield repo.name, "repo", "-", "skip", "origin is not a GitHub remote"
        return
    git(repo, "fetch", "--prune", "--quiet", "origin")
    default = default_branch(repo, slug)
    pulls = pulls_by_head(slug)
    verdicts = {}

    for line in git(repo, "for-each-ref", "--format=%(refname:short)\t%(objectname)\t%(committerdate:short)", "refs/heads").splitlines():
        branch, tip, date = line.split("\t")
        if branch == default:
            continue
        verdict, reason = classify(repo, branch, tip, default, pulls)
        verdicts[branch] = verdict
        yield slug, "branch", branch, verdict, f"{reason}; last commit {date}"

    for line in git(repo, "for-each-ref", "--format=%(refname:short)\t%(objectname)", "refs/remotes/origin").splitlines():
        ref, tip = line.split("\t")
        branch = ref.removeprefix("origin/")
        if branch in ("HEAD", default, "origin"):
            continue
        verdict, reason = classify(repo, branch, tip, default, pulls)
        if verdict == "delete":
            verdict = "delete-remote"
        yield slug, "remote", branch, verdict, reason

    main_path = Path(git(repo, "rev-parse", "--show-toplevel")).resolve()
    for entry in worktrees(repo):
        path = Path(entry["worktree"]).resolve()
        branch = str(entry.get("branch", "")).removeprefix("refs/heads/") or "(detached)"
        dirty = git(path, "status", "--porcelain", check=False).splitlines() if path.exists() else []
        if path == main_path:
            if branch != default and verdicts.get(branch) != "delete":
                yield slug, "checkout", str(path), "keep", f"on kept branch {branch}"
                continue
            notes = [] if branch == default else [f"on finished {branch}, switch to {default}"]
            if dirty:
                notes.append(f"uncommitted: {summarize(dirty)}")
            ahead = git(repo, "rev-list", "--count", f"origin/{default}..{default}", check=False)
            if ahead not in ("", "0"):
                notes.append(f"local {default} {ahead} commits ahead of origin")
            yield slug, "checkout", str(path), "reset" if notes else "ok", "; ".join(notes) or f"clean on {default}"
            continue
        if entry.get("prunable") or not path.exists():
            yield slug, "worktree", str(path), "prune", "directory missing"
        elif dirty:
            yield slug, "worktree", str(path), "keep", f"uncommitted on {branch}: {summarize(dirty)}"
        elif in_use(path, cwds):
            yield slug, "worktree", str(path), "keep", f"a process has its cwd inside; {branch}"
        elif verdicts.get(branch, "keep") == "delete" or branch == "(detached)" and is_ancestor(repo, "HEAD", f"origin/{default}"):
            yield slug, "worktree", str(path), "delete", f"clean; {branch}"
        else:
            yield slug, "worktree", str(path), "keep", f"branch {branch} is kept"


def main():
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    cwds = process_cwds()
    repos = sorted(p for p in root.iterdir() if (p / ".git").is_dir())
    print("repo\tkind\tname\tverdict\treason")
    for repo in repos:
        try:
            for row in inventory(repo, cwds):
                print("\t".join(row))
        except RuntimeError as error:
            print(f"{repo.name}\trepo\t-\terror\t{error}")


if __name__ == "__main__":
    main()
