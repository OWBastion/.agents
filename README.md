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

## Migrated skills

The following skills were moved from the global Codex skill directory into
`.agents/skills/` so they are available from this workspace without depending
on global installation state:

- `add-workshop-event` — add or adjust Bastion random events.
- `remove-workshop-event` — retire Bastion random events with validation gates.
- `session-skill-maintainer` — review recent Bastion sessions and maintain
  reusable skill procedures.

The `ow-*` skills were intentionally not migrated: their descriptions target
the separate `Overwatch-AI-PVE` repository rather than this Bastion workspace.

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
