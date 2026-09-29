---
name: owbastion-verify-change
description: >
  Independently falsify whether a material OWBastion change someone else
  implemented is actually correct and complete. Use in PR review or an assigned
  QA role for gameplay behavior, state lifecycle, random-event selection,
  platform API or data contract, submission/review/grant, QQ command, or
  screenshot-recognition changes; when a public or authoritative API, schema,
  protocol, or generated contract is replaced, migrated, or retired and
  surviving capabilities must be checked; when the user asks to verify or prove
  a change, or whether a fix is really complete or ready to merge; or when a
  regression escaped coverage and its fix needs re-checking. Do NOT use to
  re-check your own implementation in the same task, and do not spawn a
  subagent to run it on your own work. Also do not use as a routine test
  runner, to diagnose why coverage missed a defect, for mechanical changes fully
  covered by normal gates, to approve a design before implementation, or to
  decide whether a test should exist. Return VERIFIED, NOT VERIFIED, or
  INCONCLUSIVE.
---

# OWBastion Verify Change

The reviewer or QA pass for a material change whose acceptance needs independent falsification, not a rerun of tests written with the implementation.

Authority: `.github/docs/verification-and-acceptance.md`, `.github/docs/testing-policy.md`, and `.github/docs/issue-readiness.md` (contract continuity), then the owning repository's `AGENTS.md`. This skill is a procedure, not a second policy. It checks correctness only; whether a mechanism should exist is `.github/docs/engineering-quality.md`.

Why: a green suite can agree with a wrong expectation, and a replaced boundary can leave legacy tests passing while the new one drops capabilities. A check helps only if it constrains the change from outside.

## Procedure

The steps are an order of reasoning; one decisive check may settle several.

1. **Claim.** State the exact observable behavior that should hold, for example "a player who leaves mid-event has the event's effects and HUD handles cleaned up", not "cleanup is improved". If it cannot be made concrete, the result is `INCONCLUSIVE` until the contract is clarified.
2. **Independent authority.** Find what defines correct behavior outside the implementation: an accepted contract or Issue, reproducible in-game or build behavior, the platform's published contract, an established reference, reviewed evidence, or the accepted pre-migration contract. With none, do not infer correctness from the code or its new tests; report `INCONCLUSIVE` and name the missing contract.
3. **Smallest decisive falsification.** Pick the narrowest check that would fail if the claim were false: a focused test, a minimal input, a real-flow reproduction, or a before/after comparison. Where practical, temporarily invert or remove the key change and confirm the check fails; then restore it. Do not add permanent production scaffolding for this.
4. **Compare.** Compare observed behavior with the authority, and pre- with post-change behavior where meaningful. Ask whether a plausible wrong implementation would also pass what you collected. A missing historical baseline does not invalidate a check the current contract can decide; record it if it matters.

## Boundary migrations

When a change replaces, hides, or retires an authoritative boundary, derive claims from the accepted pre-migration contract, not from the replacement or its companion tests. Account for each capability as preserved, approved removal or change, or transferred to a named owner (`.github/docs/issue-readiness.md`), and verify preserved capabilities through the replacement boundary itself. A check through a retired or compatibility-only path cannot support `VERIFIED`.

## Verdict

- `VERIFIED` — behavior matches the independent authority and the check would catch a plausible wrong implementation.
- `NOT VERIFIED` — behavior conflicts with the contract, shows a material unexpected difference, or silently drops a surviving capability.
- `INCONCLUSIVE` — the authority or checks cannot tell correct from incorrect, or surviving scope is unclear.

If not `VERIFIED`, say what contract, check, or change would resolve it. Never report `VERIFIED` only because existing tests are green.

Verification output is task-local. Keep logs, reports, and minimized inputs ephemeral; if a regression deserves permanent coverage, report it as a candidate for the owning repository's existing test structure.

```text
Claim: <falsifiable behavior>
Authority: <independent contract or source>
Surface: <decisive check>
Observation: <result or comparison>
Verdict: VERIFIED | NOT VERIFIED | INCONCLUSIVE
Limitations: <material uncertainty, or none>
Repository test candidate: <only if durable coverage should be considered>
```
