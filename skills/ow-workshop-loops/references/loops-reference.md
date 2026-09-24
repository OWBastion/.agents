# Loops Reference

## Action Cheat Sheet

| Action | Category | What it repeats | Required guardrail | Primary failure mode |
| --- | --- | --- | --- | --- |
| [Loop](https://workshop.codes/wiki/articles/loop) | Rule loop | Entire rule actions | `Wait` before repeating | Infinite same-frame recursion |
| [Loop If](https://workshop.codes/wiki/articles/loop+if) | Rule loop | Entire rule when expression is true | `Wait` before looping | High-frequency repeated execution |
| [Loop If Condition Is True](https://workshop.codes/wiki/articles/loop+if+condition+is+true) | Rule loop | Entire rule while conditions stay true | `Wait` before looping | Waitless crash risk under multi-player load |
| [Loop If Condition Is False](https://workshop.codes/wiki/articles/loop+if+condition+is+false) | Rule loop | Entire rule while conditions are false | `Wait` before looping | Busy-looping on persistent false condition |
| [While](https://workshop.codes/wiki/articles/while) | Action loop | Nested action block | In-loop `Wait` and `End` | Unbounded action spam |
| [End](https://workshop.codes/wiki/articles/end) | Loop terminator | Ends `While`/`For` scope | Must exist for each loop scope | Accidental large loop body |
| [For Global Variable](https://workshop.codes/wiki/articles/for+global+variable) | Indexed loop | Bounded range with global index | Bounded stop + sane step | Large one-tick burst |
| [For Player Variable](https://workshop.codes/wiki/articles/for+player+variable) | Indexed loop | Bounded range with player index | Bounded stop + sane step | Per-player burst scaling |
| [Wait](https://workshop.codes/wiki/articles/wait) | Throttling | Delays continuation | Use in self-repeating loops | Server overload from waitless loops |

## Common Pitfalls

- Waitless rule loops or `While` loops can execute hundreds of actions in one frame.
- `For` loops with unstable stop values or wrong step direction can create near-unbounded execution.
- Expensive conditions first (`Distance`, large array predicates) multiply evaluation cost.
- Many heavy loops activating on match start can spike server load before players stabilize.

## Stability Mapping

Loop-specific mapping from [Improve your code's server stability](https://workshop.codes/wiki/articles/improve-your-codes-server-stability):

| Stability recommendation | Loop implication | Practical fix |
| --- | --- | --- |
| Waitless loops | Self-repeating loops can crash server | Add `Wait(>=0.016)` in every repeating path |
| Condition ordering | Expensive loop gates evaluated too often | Put cheap/high-selectivity checks first |
| Too many actions in one frame | Loop body can burst too many actions | Insert micro-batching waits |
| Too many startup conditions | Opening tick checks all rules | Defer loops by spawn/time/living-player gates |
| Sparse condition evaluation | Constant heavy checks waste budget | Use low-frequency `Wait + If + Loop` pattern |
| De-sync expensive actions | Same-tick synchronization causes spikes | Offset waits by slot or shard |

## Minimal Snippets

Rule-loop throttle:

```opy
Wait(0.200, Ignore Condition);
Loop If Condition Is True;
```

While-loop throttle:

```opy
While(condition);
    // actions
    Wait(0.016, Ignore Condition);
End;
```

For-loop micro-batching:

```opy
For Global Variable(i, 0, Count Of(Global.items), 1);
    // actions
    If(Modulo(Global.i, 20) == 0);
        Wait(0.016, Ignore Condition);
    End;
End;
```
