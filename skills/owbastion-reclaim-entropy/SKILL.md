---
name: owbastion-reclaim-entropy
description: >
  OWBastion simplification: find or remove duplicate truth, dead or redundant
  abstractions, obsolete fallbacks or compatibility layers, post-migration
  leftovers, unused consumers, duplicated state/config, or replacement cleanup
  in any OWBastion repository. Use for codebase cleanup, entropy audits,
  migration cleanup, or focused "is this still load-bearing?" investigations.
  Also use when the user asks what can be deleted or simplified, to remove
  leftovers, find bloat or duplicate truth, or clean up after a replacement.
  Do NOT use for routine feature implementation, correctness-only review,
  self-authorizing removal of public, persisted, or compatibility contracts, or
  approving a new mechanism before implementation.
---

# OWBastion Reclaim Entropy

Reduce maintenance obligations; line count is not the objective. This is post-hoc cleanup, not design admission for a proposed mechanism (that is `.github/docs/engineering-quality.md`).

Authority: `.github/docs/entropy-policy.md`, `.github/docs/engineering-quality.md`, `.github/docs/testing-policy.md`, then the owning repository's `AGENTS.md`, which takes precedence. This skill adds an investigation workflow and does not redefine any contract.

> Scanners create candidates; consumer inspection and contract checks justify a cut.

Why: unused-looking code can encode an external contract, a dynamic path, a lifecycle requirement, or a cross-repository consumer. Reachable code can still be accidental duplication.

## Modes

- **Audit** — rank meaningful candidates without editing.
- **Apply** — implement authorized simplifications and verify them.
- **Focused investigation** — decide whether one named abstraction, state, dependency, fallback, or layer is load-bearing.

A review or audit request is not authorization to edit.

## Judging a candidate

- **Obligation**: name what is maintained (API, state, wrapper, fallback, dependency, flag, lifecycle mechanism, fixture, generated artifact, duplicated fact). Deleting lines that just move the obligation elsewhere is not a gain.
- **Dependents**: trace callers far enough to classify the surface as production, test-only, generated, dynamic, or cross-repository. Search strings, config and protocol keys, build and codegen paths, and consumers in sibling OWBastion repositories (Bastion, owbastion.com, qqbot, ocrkit), since a local reference count misses them.
- **Load-bearing reason**: the contract, ownership decision, compatibility requirement, lifecycle need, or live consumer that justifies it. If the cut touches a public or persisted contract, gameplay behavior players rely on, privacy/security control, declared compatibility, or an unresolved ownership decision, route the decision to its owner instead of authorizing it yourself.
- **Net effect**: prefer one canonical owner, removal of obsolete paths, and removal of pass-through layers when concepts, synchronization, dependencies, or lifecycle states go down without equivalent glue appearing elsewhere.

Duplicate truth, pass-through layers, abandoned extension points, one-off generality, migration residue, overlapping lifecycle mechanisms, and support artifacts for removed behavior are places to look, not findings.

## Apply

Stay inside the ownership boundary, remove the obligation end to end (exports, docs, config, tests, generated output), keep unrelated cleanup out, and preserve behavior a real contract requires. Verify the smallest decisive property first, then the repository gates for the affected boundary. Do not weaken tests, diagnostics, or validation to make a deletion pass.

## Output

A few well-supported candidates beat a wishlist. Finding no worthwhile cut is a valid result.

```text
Candidate: <maintenance obligation>
Consumers: <production, dynamic, external, or cross-repository>
Contract: <public/compatibility contract or ownership decision>
Change: <what can be removed or consolidated>
Net effect: <concepts removed and any replacement cost>
Authority: <implementation-level, or owner decision required>
Verify: <smallest decisive check>
```

During review, do not expand the approved PR into cleanup the Issue does not include.
