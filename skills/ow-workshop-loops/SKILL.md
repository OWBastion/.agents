---
name: ow-workshop-loops
description: Design, review, and optimize Overwatch Workshop loop logic (Rule Loop, While, For) with safe Wait usage, bounded iteration, and server-load safeguards. Use when implementing loop behavior, diagnosing waitless loop crash risk, or choosing loop strategy for performance-sensitive rules.
license: AGPL-3.0-only
compatibility: Designed for Agent Skills-compatible coding agents, including Codex and Claude Code. Requires local filesystem access to the skill folder. No network access or extra system packages are required.
metadata:
  author: Teakowa
  version: "1.0.1"
  canonical_spec: "https://agentskills.io/specification"
  target_products: "Codex, Claude Code"
---

# OW Workshop Loops

## Overview
Use this skill to design loop logic that is safe under multiplayer load and clear to maintain.

Focus on three loop forms:

- Rule loops (`loop`, `Loop If`, `Loop If Condition Is True`, `Loop If Condition Is False`)
- While loops (`While ... End`)
- For loops (`For Global Variable`, `For Player Variable`)

Use this workflow when you need to:

- choose the correct loop form for behavior and cost
- prevent waitless loop crashes
- batch expensive actions in large iterations
- review existing rules for loop stability risks

## Quick Start
1. Identify whether the task is indefinite repetition, condition-scoped repetition, or bounded iteration.
2. Pick the loop style with the decision guide below.
3. Apply the matching safe template from `Patterns`.
4. Run a review pass with `Safety Guardrails` and `Review Checklist` before shipping.

Primary references:

- [How to use loops](https://workshop.codes/wiki/articles/how-to-use-loops)
- [Improve your code's server stability](https://workshop.codes/wiki/articles/improve-your-codes-server-stability)

## Loop Selection Guide
Use this guide to select one loop type quickly.

| Situation | Preferred loop | Why |
| --- | --- | --- |
| Repeat an entire rule over time until rule conditions change | Rule loop | Lowest ceremony and direct rule-level retry |
| Repeat a subset of actions while a runtime condition stays true | While loop | Keeps scoped action blocks together |
| Iterate over array items or numeric ranges with known bounds | For loop | Explicit index progression and finite termination |

Choose a different approach when:

- the action count per tick is high and cannot be batched
- loop termination is unclear or depends on unstable external state
- a high-cost condition must be reevaluated every tick without throttling

## Patterns

### Rule Loop Template
When to use:

- repeat a rule in short intervals
- condition is already expressed in rule `conditions`

When not to use:

- loop body needs branch-local repetition only (use `While`)
- iteration target is a finite array/range (use `For`)

Minimum safe template:

```opy
rule("Pulse effect while Interact is held")
{
    event
    {
        Ongoing - Each Player;
        All;
        All;
    }

    conditions
    {
        Is Button Held(Event Player, Button(Interact)) == True;
    }

    actions
    {
        Small Message(Event Player, Custom String("Pulse"));
        Wait(0.200, Ignore Condition);
        Loop If Condition Is True;
    }
}
```

Safety floor:

- add `Wait(...)` before loop continuation
- keep wait at or above `0.016`
- avoid heavy queries in the same rule without extra throttling

Related actions:

- [Loop](https://workshop.codes/wiki/articles/loop)
- [Loop If](https://workshop.codes/wiki/articles/loop+if)
- [Loop If Condition Is True](https://workshop.codes/wiki/articles/loop+if+condition+is+true)
- [Loop If Condition Is False](https://workshop.codes/wiki/articles/loop+if+condition+is+false)
- [Wait](https://workshop.codes/wiki/articles/wait)

### While Loop Template
When to use:

- repeat only part of the action sequence
- require explicit begin/end scope around repeated actions

When not to use:

- rule-level repetition is sufficient
- iteration is better represented by index traversal

Minimum safe template:

```opy
rule("Track movement trail while Ability 1 is held")
{
    event
    {
        Ongoing - Each Player;
        All;
        All;
    }

    conditions
    {
        Is Button Held(Event Player, Button(Ability 1)) == True;
    }

    actions
    {
        Play Effect(All Players(All Teams), Ring Explosion, Color(Red), Position Of(Event Player), 8);
        While(Is Button Held(Event Player, Button(Ability 1)));
            Play Effect(All Players(All Teams), Ring Explosion, Color(White), Position Of(Event Player), 2);
            Wait(0.016, Ignore Condition);
        End;
        Play Effect(All Players(All Teams), Ring Explosion, Color(Red), Position Of(Event Player), 8);
    }
}
```

Safety floor:

- always include `Wait(...)` inside `While`
- always close with `End`
- keep body short or split into helper routines

Related actions:

- [While](https://workshop.codes/wiki/articles/while)
- [End](https://workshop.codes/wiki/articles/end)
- [Wait](https://workshop.codes/wiki/articles/wait)

### For Loop Template
When to use:

- apply actions to each element in a bounded set
- iterate by index with explicit start/stop/step

When not to use:

- loop can become unbounded because stop is unstable
- the body is too expensive for one tick and lacks batching

Minimum safe template:

```opy
variables
{
    player:
        0: index
        1: targets
}

rule("Push enemies in radius")
{
    event
    {
        Ongoing - Each Player;
        All;
        All;
    }

    actions
    {
        Event Player.targets = Players Within Radius(Event Player, 8, Opposite Team Of(Team Of(Event Player)), Surfaces);
        For Player Variable(Event Player, index, 0, Count Of(Event Player.targets), 1);
            Apply Impulse(
                Event Player.targets[Event Player.index],
                Direction Towards(Event Player, Event Player.targets[Event Player.index]),
                15,
                To World,
                Cancel Contrary Motion
            );
        End;
    }
}
```

Batching pattern for large loops:

```opy
For Global Variable(i, 0, Count Of(Global.bigArray), 1);
    // expensive action
    If(Modulo(Global.i, 20) == 0);
        Wait(0.016, Ignore Condition);
    End;
End;
```

Safety floor:

- ensure `Range Stop` is bounded and monotonic relative to `Step`
- avoid large one-tick bursts without batched waits
- keep per-iteration conditions cheap

Related actions:

- [For Global Variable](https://workshop.codes/wiki/articles/for+global+variable)
- [For Player Variable](https://workshop.codes/wiki/articles/for+player+variable)

## Safety Guardrails
- Never ship a self-repeating rule or `While` block without `Wait`.
- Place high-selectivity, low-cost checks before expensive distance/array scans.
- Prefer event player filters (hero/slot) over broad `All` filters with late hero conditions.
- Defer expensive startup loops using spawn/time gates when possible.
- De-sync heavy multi-player work with slot-based offsets to reduce same-tick spikes.
- Split long action chains with short waits if a single frame becomes overloaded.

## Review Checklist
- [ ] Chosen loop type matches problem shape (rule repeat, scoped repeat, bounded iteration).
- [ ] Every rule loop/while loop includes a throttling `Wait`.
- [ ] Every `While` is terminated by `End`.
- [ ] Every `For` loop has bounded stop and sane step direction.
- [ ] No heavy one-tick burst without batching in large iterations.
- [ ] Expensive conditions are not the first gate unless required.
- [ ] Startup path avoids full-load loop activation on first tick.

## Attribution
This skill is a structured rewrite derived from the Workshop.Codes Wiki.

Source references:

- [How to use loops (Workshop.Codes)](https://workshop.codes/wiki/articles/how-to-use-loops)
- [Improve your code's server stability (Workshop.Codes)](https://workshop.codes/wiki/articles/improve-your-codes-server-stability)
