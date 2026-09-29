# Desktop modes and scoring

## The merge rule

On a 4×4 board, slide all tiles as far as possible in one direction. Adjacent equal values merge into double their value. A newly merged tile cannot merge again in the same move. Left-move examples, before the new tile spawns:

| Before | After | Score gained |
|---|---|---:|
| 2, 2, 2, 2 | 4, 4, 0, 0 | 8 |
| 2, 2, 4, 0 | 4, 4, 0, 0 | 4 |
| 4, 0, 4, 4 | 8, 4, 0, 0 | 8 |

A valid move normally spawns a 2 (90%) or 4 (10%) in an empty cell. Invalid moves do not spawn a tile, consume a move or advance randomness. Expedition abilities can change scoring and spawning. A full board is not necessarily lost: adjacent equal values can still merge.

## Classic and Daily

Classic has unlimited moves. Reaching 2048 does not end play; keep going until no legal move remains. A merge awards the resulting value: 8+8 makes 16 and awards 16 base points.

Daily uses a date-based seed. The same date **and action sequence** reproduce spawns; the same date with different moves does not imply the same board. Enter today's challenge through the lobby. Restart keeps the current challenge date. Up to seven saved dates are retained locally, without an older-date picker or online leaderboard.

## 60-Move Sprint

Score as much as possible in 60 valid moves, or until the board becomes immobile. Undo restores the move allowance; invalid directions cost nothing. Manual and assisted best scores are separate and do not contribute to the Classic best. Merely reaching move 60 does not trigger Rescue extraction; a blocked board can.

## Puzzle Theatre: twelve chapters

Each chapter has a fixed board and random state, with targets from 64 to 2048. Shortest solutions take 2–5 moves. The limit is one move above par: 3–6 moves. The side panel shows remaining moves and the next tile value. Retrying the same route reproduces spawns; a different direction changes available spawn locations.

| Completion | Stars |
|---|---|
| No assistance, no undo, finish within par | Three |
| Any other unassisted completion | Two |
| Completion with assistance | One |

Each chapter retains its highest star result. Re-selecting the same unfinished chapter resumes it; 「原局重试」 resets it. Selecting another chapter replaces the current puzzle board but keeps earned stars. AI analysis can show the deterministic next board, solvability within remaining moves and the full route. Solutions are spoilers.

## Rescue: recover space in six moves

When Classic, Daily or Sprint ends because no slide is possible, a background search examines up to ten recent positions. A candidate must have zero or one empty cell and permit recovery to at least three empty cells with continued legal movement within six valid moves. Search preserves full random state, finds a shortest route and verifies it through the real engine before offering a challenge.

Rescue starts as a separate zero-score, zero-move game. The original loss remains intact in its own mode. Retry, undo, hints and autoplay are available. Manual and assisted best move counts are stored separately. Opening 「路线对照」 while the challenge is in progress marks assistance; it compares your route or the original loss with the verified route, step by step. Undo does not clear assistance.

Up to six personal challenges are retained, preserving the current one. Three clearly labelled practice challenges are available, with shortest routes of 3, 5 and 5 moves. Not every loss yields a challenge. Search has a time limit; no result does not prove impossibility.

## Expedition and record categories

Expedition combines six score-target stages, move limits, ability choices and active powers. See [chapter 4](04-expedition.md). Its score is separate from Classic.

Hints, actual Coach analysis, AI single moves and autoplay count as assistance. Undo cannot remove that flag. Modes use different records—stars, score or moves—so multiplied Expedition scores are not directly comparable to Classic. The game cannot detect that you read an external solution; distinguish independent solving from practice with a known route.
