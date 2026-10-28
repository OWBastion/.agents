# OWBastion workspace agent skills

This directory is the workspace-local home for reusable agent procedures shared
by the independent repositories under `owbastion/`.

The workspace root is a router, not a monorepo. Git state, source ownership,
tests, and commits remain in each child repository. Start with the root
[`AGENTS.md`](../AGENTS.md), then read the nearest repository-local
`AGENTS.md` before editing code.

## Ownership boundary

- `.agents` owns reusable procedures for work spanning the Bastion ecosystem.
- Each child repository owns its source, contracts, tests, documentation, and
  repository-specific skills.
- `overwatch-ai-skills` remains the public distribution repository for
  portable Overwatch and Workshop skills; this workspace-local set does not
  replace it.
- `Bastion/skills/` remains repository-local.

## Skill activation

A skill's `description` is its activation contract, visible before the body loads. Write it as: what the skill does; use when (task surfaces, changed artifacts, failure signals); also use when (indirect situations and natural user wording); do NOT use for (adjacent tasks or other skills' scope). Procedure lives in the skill; policy lives in `.github/docs/` and is referenced, not copied. If two skills activate on the same ordinary prompt, clarify their boundary rather than relying on ordering. See `.github/docs/documentation.md`.

## Governance skills

Domain-neutral procedures that apply policy from `.github/docs/`:

- `owbastion-reclaim-entropy` — post-hoc simplification and load-bearing investigations.
- `owbastion-verify-change` — independent falsification of another author's material change.
- `owbastion-test-design-review` — test necessity, stability, and duplication review.

## Workflow skills

- `owbastion-issue-loop` — pick ready Issues, deliver each through its own PR
  and independent review, and pause or stop cleanly.
- `owbastion-prune-merged-work` — remove merged or closed branches, worktrees,
  and task leftovers across all workspace repositories, judged by GitHub PR
  state.

## Tool skills

- `wright` — decide when and how to use the `wright` CLI for Workshop and
  OverPy correctness, rule cost, symbol and rule flow, and compilation.

## Editorial skills

- `owbastion-log-writer` — write or revise Chinese development logs and release
  notes using the workspace author's sentence patterns and player-facing voice;
  Portal contracts remain owned by the platform repository. Use this for Portal
  prose.

## Asset skills

- `owbastion-title-badge` — generate unified title badge icons for owbastion.com
  (prompt, magenta-background original, watermark/background removal); outputs
  belong to `owbastion-assets`.

## Layout

```text
owbastion/
├── AGENTS.md                 # workspace routing and cross-repository rules
├── .github/                  # organization policy and routing
├── .agents/
│   ├── README.md             # shared skill ownership and usage
│   └── skills/               # workspace-wide reusable procedures
├── Bastion/                  # released Workshop source and builds
├── owbastion.codes/          # platform, Portal, and business state
├── qqbot/                    # QQ protocol and notifications
└── ocrkit/                   # stateless screenshot recognition
```

When a skill is relevant, use its workspace path (for example,
`.agents/skills/owbastion-verify-change/SKILL.md`) and then follow the repository's
own routing and validation rules.
