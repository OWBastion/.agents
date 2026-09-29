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
- `workshop-agent` remains the public distribution repository for
  Workshop-domain skills; it is not replaced by this workspace-local set.
- The existing `Bastion/skills/` files remain repository-local and were not
  rewritten as part of this migration.

## Skill activation

A skill's `description` is its activation contract, visible before the body loads. Write it as: what the skill does; use when (task surfaces, changed artifacts, failure signals); also use when (indirect situations and natural user wording); do NOT use for (adjacent tasks or other skills' scope). Procedure lives in the skill; policy lives in `.github/docs/` and is referenced, not copied. If two skills activate on the same ordinary prompt, clarify their boundary rather than relying on ordering. See `.github/docs/documentation.md`.

## Migrated skills

The following skills were moved from the global skills store into
`.agents/skills/` so they are available from this workspace without depending
on global installation state:

- `add-workshop-event` — add or adjust Bastion random events.
- `remove-workshop-event` — retire Bastion random events with validation gates.
- `session-skill-maintainer` — review recent Bastion sessions and maintain
  reusable skill procedures.
- `ow-balance-notes-writer` — format Overwatch-AI-PVE balance notes.
- `ow-changelog-sync` — check hero changes against player-facing changelog coverage.
- `ow-contract-guard` — validate Workshop source and protocol invariants.
- `ow-fandom-hero-data` — collect structured hero data from Overwatch Fandom.
- `ow-hero-change-pipeline` — run the hero-change review workflow.
- `ow-module-metrics-sync` — synchronize module metrics in documentation.
- `ow-workshop-loops` — design and review Workshop loops for safety and cost.

The `ow-*` skills retain their declared Overwatch-AI-PVE scope. Use them only
when the task's source and contracts match that workflow.

## Layout

```text
owbastion/
├── AGENTS.md                 # workspace routing and cross-repository rules
├── .agents/
│   ├── README.md             # shared skill ownership and usage
│   └── skills/               # workspace-wide reusable procedures
├── Bastion/                  # released Workshop source and builds
├── owbastion.codes/          # platform, Portal, and business state
├── qqbot/                    # QQ protocol and notifications
└── ocrkit/                   # stateless screenshot recognition
```

When a skill is relevant, use its workspace path (for example,
`.agents/skills/add-workshop-event/SKILL.md`) and then follow the repository's
own routing and validation rules.
