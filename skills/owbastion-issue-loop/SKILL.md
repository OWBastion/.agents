---
name: owbastion-issue-loop
description: >
  Run a repeated, self-paced loop that picks ready OWBastion Issues, implements
  each one through a PR, has it independently reviewed, and moves to the next.
  Use when the user starts `/loop` or asks to "work through the ready issues",
  "clear the backlog", "keep implementing issues", or "run the implementation
  loop" in Bastion, owbastion.com, qqbot, or ocrkit. Also use when the user asks
  how a loop should pick, pause, or stop, or says "这一轮完成后先暂停" or
  "停止 loop". Do NOT use for a single named Issue (follow the repository's
  normal Issue workflow), for reviewing someone else's PR outside a loop
  (`owbastion-verify-change`), or for branch cleanup
  (`owbastion-prune-merged-work`).
---

# OWBastion Issue Loop

Deliver ready Issues one or two at a time, each through its own PR and an independent review, without making owner decisions.

Authority: `.github/docs/issue-readiness.md`, `.github/docs/pr-delivery.md`, `.github/docs/verification-and-acceptance.md`, and the owning repository's `AGENTS.md`, which takes precedence. This skill orders the loop; it does not widen what the user authorized.

## Selection

Pick an Issue only when all of these hold:

- It is open and meets the readiness bar in `issue-readiness.md`. Use the repository's readiness label when it has one; label sets differ between repositories, so query them instead of assuming a name.
- Every native `blocked-by` Issue is closed, and it has no open sub-issue.
- It is not labeled as blocked or waiting for a decision or design.

Order: priority label (`p0` first) when the repository has one; at the same priority, bugs before features and tasks; then oldest first.

Work on at most two Issues at a time. Use subagents only inside those Issues (reading code, checking facts, locating a CI failure), not to start a third.

## Each Issue

1. Re-read the Issue, its comments, parent, and linked work. Confirm it is still open and not already implemented.
2. Implement in its own worktree and branch, one Issue per PR. Deliver under the repository's delivery rules.
3. Get an independent review from another session. The reviewer pulls the branch, runs the checks, and verifies against the acceptance criteria with `owbastion-verify-change`. Follow-up rounds check only the previous findings, regressions from their fixes, and new code.
4. Fix only the reported defects. If the second review round still fails, redesign or report the blocker, as `pr-delivery.md` requires.
5. Merge only when the user's loop request authorizes merging, independent review has passed, and all checks are green. Use an explicit squash message whose closing reference matches the delivered scope. Re-read the Issue state just before merging.

## Never

- Merge a release PR, create a tag, or deploy.
- Decide an unresolved product, design, contract, or ownership question. Comment the concrete question on the Issue, apply the repository's blocked or decision label when one exists, and skip it.
- Continue on an Issue that is delivered, blocked, or reassigned.

## Pause and stop

When the user asks to pause or stop, finish the current step and push or commit task-owned work. Leave every worktree that holds uncommitted output in place. Report each Issue's state: PR, review round, checks, and what remains.
