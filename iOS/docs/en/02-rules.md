# Complete rules for all six modes

## Shared board rules

The board is 4 × 4, with 16 cells. Each directional move slides all tiles toward that edge. Adjacent equal values merge in pairs. **A tile created by a merge cannot merge again during the same move.**

These examples show one row moving left, before the new tile spawns. A dot means an empty cell.

| Before | After sliding left | Base score |
| --- | --- | --- |
| 2 · 2 · 0 · 0 | 4 · 0 · 0 · 0 | 4 |
| 2 · 2 · 2 · 0 | 4 · 2 · 0 · 0 | 4 |
| 2 · 2 · 4 · 0 | 4 · 4 · 0 · 0 | 4; it does not become 8 yet |
| 2 · 2 · 2 · 2 | 4 · 4 · 0 · 0 | 8 |
| 4 · 4 · 8 · 8 | 8 · 16 · 0 · 0 | 24 |
| 2 · 4 · 8 · 16 | Unchanged | 0; invalid if the entire board is unchanged |

A move is valid when it changes the board. It increments the move counter and normally spawns a new tile in an empty cell: **90% chance of 2, 10% chance of 4**. Expedition abilities can alter this probability or suppress spawning. A slide without a merge still spends a move and spawns a tile, but earns no score. An invalid direction does none of these and does not advance the random generator.

Base score is the sum of all newly merged values. Expedition then applies its bonuses. Score and largest tile are different statistics. A full board with no horizontally or vertically adjacent equal pair has no legal slide. Expedition also checks whether an active power remains available.

## Mode comparison

| In-app name / English name | Goal | Move limit | End condition | Restart |
| --- | --- | --- | --- | --- |
| 经典 2048 / Classic | Bigger tiles and higher score | None | No legal move; 2048 does not stop play | New random game |
| 能力远征 / Expedition | Meet six stage score targets | Per stage | Reach target to advance; complete stage six to win | New expedition |
| 败局重生 / Rescue | Create the required empty cells | Per challenge; practices use 6 | Reach empty-cell goal after spawning | Same challenge |
| 每日同局 / Daily | Play the local date's shared start | None | No legal move | Same date's initial board |
| 谜题剧场 / Puzzle Theatre | Make the target tile | 3–6 per built-in puzzle | Largest tile reaches target | Same puzzle |
| 六十步冲刺 / 60-Move Sprint | Maximize score within 60 moves | 60 | Move 60 or an earlier blocked board | New random game |

## Classic 2048

A new Classic game starts with two tiles. Reaching 2048 does not force a stop: continue toward 4096 and beyond. After losing, undo may let you explore another move. A truly blocked board may also qualify for Rescue extraction.

A useful practice is to keep the largest value near one corner, arrange neighboring values in descending order and preserve empty cells. Before moving, check whether you will pull the largest tile away from its corner. These are strategies, not mandatory rules or a guarantee of winning.

## Daily

The seed is derived from the device's **local calendar date**, formatted `YYYY-MM-DD`. The same date, rules and sequence of actions reproduce the same board. A different route can produce different spawn positions because available cells differ. This is an offline shared-start mode, not a server competition: there is no global leaderboard, synchronized countdown or enforced common time zone.

An open game from yesterday is not erased at midnight. Choose Daily from the mode selector to open today's game. Restarting while still on yesterday's board restarts yesterday. The app retains progress for the most recent seven saved dates. Manual and assisted best scores are recorded across the Daily mode, not as separate leaderboards for each date.

## 60-Move Sprint

Only valid directional moves count. It is **not a 60-second timer**: you can think as long as you like. Play ends at move 60, or earlier if blocked. Undo restores remaining moves, while the historical best score remains.

On the final move, immediate merge score matters because there is no move 61. AI respects that horizon. Earlier in the run, balance immediate points against future opportunities. Reaching 60 moves while the board still has legal moves does not qualify as a blocked-board Rescue source.

## Puzzle Theatre

There are twelve fixed puzzles, targeting 64 through 2048. Open More → 选择谜题 (Choose puzzle). All puzzles are selectable; there is no unlock gate. Each puzzle has a maximum move count and a shorter par. Its random state is deterministic, so repeating the same actions reproduces the same result.

| No. | In-app title / English title | Target | Par | Limit |
| --- | --- | --- | --- | --- |
| 01 | 借一步 / A Step in Advance | 64 | 2 | 3 |
| 02 | 转身 / Turn Around | 64 | 2 | 3 |
| 03 | 留白 / Room to Breathe | 128 | 3 | 4 |
| 04 | 折返 / Double Back | 128 | 3 | 4 |
| 05 | 暗流 / Undercurrent | 256 | 3 | 4 |
| 06 | 挪一寸 / Make a Little Room | 256 | 4 | 5 |
| 07 | 连锁 / Chain Reaction | 512 | 4 | 5 |
| 08 | 破局 / Breakthrough | 512 | 4 | 5 |
| 09 | 回声 / Echo | 1024 | 4 | 5 |
| 10 | 逆风 / Against the Wind | 1024 | 5 | 6 |
| 11 | 归位 / Back in Place | 2048 | 5 | 6 |
| 12 | 最后一线 / The Last Opening | 2048 | 5 | 6 |

- **Three stars:** unassisted, no undo, finished at or below par.
- **Two stars:** unassisted completion within the limit, but over par or with an undo.
- **One star:** completed after using assistance.

Redo does not erase the fact that undo was used. Achieving the target on the last permitted move wins. The best star rating per puzzle is retained. Starting another puzzle replaces the Puzzle mode's current unfinished board; it does not maintain twelve simultaneous unfinished sessions. Exact routes are isolated in the [solutions chapter](08-solutions.md).

## Rescue

The objective is **empty cells**, not a 2048 tile. The goal is checked after sliding, merging **and spawning**. If three empty cells become two after the new tile appears, the three-cell goal is not yet met.

Three built-in practices each require three empty cells within six moves: 一线生机 (A Glimmer of Hope), 腾挪之间 (Room to Maneuver), and 逆转时刻 (Turning Point). In Rescue, open More → 残局档案 (Rescue archive) to choose one. Undo, restart, hints and autoplay remain available.

To extract a challenge from your own game:

1. Reach an actually blocked board in Classic, Daily or Sprint.
2. Tap 寻找这局的另一种结局 (Find another ending) in the result area.
3. Search examines candidate positions in the last ten moves, with at most one empty cell, seeking a verified route to three empty cells within six moves.
4. If found, tap 试着改写这局 (Try a different ending) to start an independent challenge. The source mode's game is retained.
5. Failure to find a challenge means none was confirmed within that search range or time budget, not proof that every earlier position was hopeless.

The personal archive holds up to six challenges. New entries may remove older ones that are not needed by the current challenge. Built-in practices do not consume these slots. Two-route replay is a Rescue feature, not a full video replay of every Classic game.

对照复盘 (Compare routes) shows 原来的路线 (Original route) and 转机路线 (Recovery route). Use 上一步 / 下一步 (Previous / Next); changing route resets to step zero. **Opening replay before winning marks the challenge assisted**, even if you intended only to view the original route, because it initially presents the verified solution. Opening it after winning does not change that completed run's category.

For stage numbers and all abilities, see the [Expedition handbook](03-expedition.md).
