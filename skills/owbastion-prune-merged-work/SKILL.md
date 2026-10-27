---
name: owbastion-prune-merged-work
description: >
  Clean up finished work across every repository in the OWBastion workspace:
  local branches, worktrees (including `.claude/worktrees` and `.worktrees`),
  remote leftover branches, stray default checkouts, and task-created temporary
  files. Decides "merged" from GitHub PR state, so squash and rebase merges are
  handled. Use when the user asks to clean up, prune, or tidy branches or
  worktrees, remove merged or stale branches, reset local checkouts to
  `origin/main`, or free the workspace after a batch of PRs merged. Also use
  when the user says "清理分支", "清理 worktree", "删掉已合并的", "收尾", or
  complains that an earlier cleanup missed something. Do NOT use to clean code
  (that is `owbastion-reclaim-entropy`), to decide whether an open PR should be
  closed, or to delete branches in repositories outside this workspace.
---

# OWBastion Prune Merged Work

Remove only work that GitHub shows as finished, across all workspace repositories in one pass, and leave everything else in place with a stated reason.

Authority: the user's request, `.github/docs/pr-delivery.md` for authorization boundaries, and each repository's `AGENTS.md`. Deletion goes to the Trash or through Git commands that the classification below allows.

## Inventory

Run the read-only inventory from the workspace root:

```bash
python3 -I .agents/skills/owbastion-prune-merged-work/scripts/inventory.py .
```

It visits every child Git repository, runs `git fetch --prune`, and loads PR state with `gh pr list` once per repository. It reports every `refs/heads/*` branch (including branches without a worktree), every `origin/*` branch, every worktree, and each default checkout.

Why a script: earlier cleanups scanned one or two repositories, or only branches with worktrees, and the user had to ask again. Scan everything every time.

## Classification

A branch is finished only by its PR state on GitHub, matched by repository and head ref:

- **Tip authored after the PR closed**, whatever the PR state: keep. Long-lived branches such as owbastion.com `next` carry closed or merged PRs, get rebased, and keep moving; author dates survive the rebase.
- **Merged** (`mergedAt` is set): delete. A tip rewritten after the merge (for example by a local rebase) does not keep the branch.
- **Closed without merge**: delete.
- **Open PR**: keep.
- **No PR**: delete only when the tip is contained in `origin/<default>` or in another remote branch. Otherwise keep and report it with its last commit date. A "backup" name does not keep a branch that is contained elsewhere.

Do not use `git branch --merged`, merge-base, or ancestry against `main` to decide merged state, because squash merges break all three.

Judge whether a branch is old or new by its last commit, not its first.

## Actions

Apply them in this order for each repository. Push only with explicit refspecs, never with an implicit current branch.

1. **Worktrees marked `delete`.** Make sure no other session uses the path (the script checks process working directories). Move the directory to the Trash with `trash <path>`, then run `git -C <repo> worktree prune`.
2. **Worktrees marked `keep` because of uncommitted files.** Read the listed paths. If they are only a regenerable tool cache (for example `.wright/`), treat the worktree as clean and apply step 1. Never remove a worktree that holds uncommitted task output. Report it instead.
3. **Default checkouts marked `reset`.** These are on the default branch or on a finished branch; a checkout on a kept branch stays as it is. The user's cleanup request authorizes moving each one back to `origin/<default>` and discarding its uncommitted files. Keep them recoverable: `git stash push -u -m "prune-merged-work <date>"`, then `git switch <default>` and `git merge --ff-only origin/<default>`. If local `<default>` has commits that `origin` does not have, stop for that repository and ask.
4. **Local branches marked `delete`.** Run `git branch -D <branch>` after steps 1–3 free any checkout that held it.
5. **Remote branches marked `delete-remote`.** List them and get the user's approval in this run before `git push origin --delete <branch>`.
6. **Temporary files.** Move to the Trash the untracked paths in the workspace and in `/tmp` that were clearly created by agent tasks for this workspace (task-named scratch directories, repro directories, logs, screenshots) and are not in use. Report anything ambiguous instead of moving it.

## Report

Give one table per repository with each deleted item and each kept item and its reason. List the stash entries you created, the remote branches you deleted or that still wait for approval, and any `no PR, unique commits` branch for the user to decide.
