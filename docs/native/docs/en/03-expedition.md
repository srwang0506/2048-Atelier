# Expedition: stages, energy and all nine abilities

## A complete expedition

Start by choosing one of three abilities: 连击引擎 (Combo Engine), 蓄能核心 (Battery Core), or 豪赌协议 (Gambit Protocol). Each stage requires its own score target within a limited number of valid moves. The top score is cumulative; the stage progress bar measures **current score minus the score at stage entry**.

| Stage | In-app name / meaning | Stage target | Base moves | With Reserve I / II |
| --- | --- | --- | --- | --- |
| 1 | 启程 / Departure | 100 | 26 | 30 / 34 |
| 2 | 蓄势 / Gathering Momentum | 260 | 34 | 38 / 42 |
| 3 | 回响 / Resonance | 520 | 42 | 46 / 50 |
| 4 | 临界 / Threshold | 900 | 46 | 50 / 54 |
| 5 | 跃迁 / Leap | 1400 | 52 | 56 / 60 |
| 6 | 终章 / Finale | 2200 | 60 | 64 / 68 |

After each of the first five stages, play pauses for a three-choice reward. Add an ability or upgrade one to rank II. Maxed-out abilities are excluded from offers. Your board, total score, abilities and energy carry forward. If more than one tile is occupied, one smallest tile is removed to create space; ties use the first cell in reading order from top left.

Unused moves and excess target score do not carry into the next stage. Choosing a reward resets combo streak, freeze duration, cooldown and undo/redo history. Stage six completes the expedition. Hitting the target on the final allowed move wins the stage; otherwise, running out of moves or having neither a legal slide nor an available power loses.

## Energy and active powers

Each merged pair earns one energy, capped at **12**. Battery Core adds more per pair. Sliding without merging earns none. Energy exists only in Expedition.

| Power | Base cost | How to use it | Effect |
| --- | --- | --- | --- |
| 凝时 / Freeze | 5 energy | Tap 凝时 · 5 | Suppress spawning on the next two valid moves; set a six-move cooldown |
| 交换 / Swap | 6 energy | Tap 交换, then two occupied tiles with different values | Exchange positions without merging or spawning |

Neither power spends a directional move or awards points directly; each does create an undo entry. You cannot swap empty cells or equal-valued tiles. Freeze requires sufficient energy, zero cooldown, no active freeze and at least one legal slide. It cannot rescue an already immovable board directly; a swap sometimes can.

Freeze duration and cooldown decrease only on valid directional moves. Waiting, invalid swipes and swaps do not advance them. If Flow also suppresses spawning during a frozen move, that move still consumes one freeze charge. Stage transitions reset freeze and cooldown.

## Exact ability reference

| In-app name / translation | Rank I | Rank II | Conditions |
| --- | --- | --- | --- |
| 连击引擎 / Combo Engine | +25% per streak layer | +40% per layer | Starts with the second consecutive merging move; at most four bonus layers |
| 蓄能核心 / Battery Core | +1 extra energy per merged pair | +2 extra per pair | Total 2 / 3 per pair including base; capped at 12 |
| 豪赌协议 / Gambit Protocol | Score ×2; 4-spawn chance 30% | Score ×2.5; 4-spawn chance 40% | Higher score comes with more 4 tiles |
| 角落增幅 / Corner Amplifier | +50% of corner merge output values | +100% | Uses the destination of a merge, not its starting cell |
| 共鸣回路 / Echo Circuit | +50% of base score when at least two pairs merge | +100% | Applied once per move, even with three or four pairs |
| 空间回流 / Spatial Flow | No spawn with at least three merged pairs | No spawn with at least two | Passive effect, no energy cost |
| 从容节拍 / Measured Tempo (Reserve) | +4 moves per stage | +8 per stage | Applies immediately; II means +8 total, not +4 plus another +8 |
| 折跃透镜 / Warp Lens | Swap costs 4 | Swap costs 3 | Freeze still costs 5 |
| 凝时晶体 / Freeze Crystal | Freeze lasts three valid moves | Lasts four | Cooldown stays six valid moves |

A combo streak counts successive **moves with a merge**, not the number of pairs within one move. A valid non-merging slide breaks it. Invalid swipes and active powers neither advance nor break it.

## Score calculation

Let G be base merge points, C the corner bonus and E the Echo bonus:

`Move score = (G + C + E) × combo multiplier × gambit multiplier`

The final number is rounded to the nearest integer, with exact halves rounded to the nearest even integer. Example: G = 24, an 8 is merged into a corner, at least two pairs merge, and you have Corner I, Echo I, Combo I on the second successive merging move, plus Gambit I. Score is `(24 + 4 + 12) × 1.25 × 2 = 100`.

Combo I gives multipliers 1, 1.25, 1.50, 1.75 and 2 over the first five consecutive merging moves, then stays at 2. Combo II gives 1, 1.40, 1.80, 2.20 and 2.60, then stays at 2.60.

## Three practice approaches

**Energy control:** Battery plus Warp gives more opportunities to rearrange tiles. Energy beyond 12 is lost; consider a useful power before another large energy gain.

**Multiple merges:** Echo plus Flow rewards preparing two or more simultaneous pairs with both points and space. Do not destroy a stable board merely to chase a trigger.

**Multipliers:** Combo plus Gambit can reach stage targets quickly, but more 4 tiles and the need to maintain a streak make planning harder. Gambit is a tradeoff, not a free score multiplier.

Rewards offer only three choices at a time, so no combination is guaranteed. AI can use powers during play, but stage rewards are always chosen by the player. Watch the [Expedition demonstrations](07-gallery.md).
