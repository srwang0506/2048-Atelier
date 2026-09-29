# AI assistance, records and saved progress

## Hint versus autoplay

提示 (Hint) computes a suggestion without making the move. The card shows a direction or power; 走这一步 (Play this step) executes it. You may instead make your own move. 自动玩 (Autoplay) repeatedly decides and acts; 暂停 (Pause) stops it.

Manual swipes, undo, redo, changing modes, opening settings, alerts, backgrounding and choosing stage abilities stop autoplay. Closing a menu does not restart it: tap Autoplay again.

Requesting a hint immediately marks the game **assisted**, even if ignored. Starting autoplay does too. Opening Rescue replay before winning also marks assistance. Stopping AI, undoing, or exporting and importing cannot remove that flag. A restarted game begins unassisted again.

## What the algorithms actually do

| Mode | Method | Interpretation |
| --- | --- | --- |
| Classic and Daily | Expectimax probability search | Compares moves and random spawn outcomes; favors space, merge opportunities, orderly values and a large corner tile |
| Sprint | Probability search bounded by remaining moves | Does not value fictional turns beyond the limit; the last move compares immediate points |
| Expedition | Probability search with ability effects | Includes score and spawn effects; swap and freeze use additional heuristics, not exhaustive optimization of every build |
| Puzzle and Rescue | Breadth-first search with complete random state | Explores shorter routes first and returns a reproducible shortest solution when found, within a time budget |

Classic search uses precomputed row tables, repeated-state caching, iterative deepening and a cutoff for very low-probability branches. “优先 / 备选” means preferred / alternative in this search ranking, **not a win probability or guaranteed score**. Normal random modes do not inspect the future random sequence to cheat. Fixed Puzzle and Rescue searches intentionally use their deterministic state to find reproducible solutions.

灵敏 (Responsive) normally budgets about 0.14 seconds; 深度思考 (Deep) about 0.55 seconds. These are search budgets, not guaranteed full turn latency. Puzzle and Rescue receive at least about one second. Deeper search can cost more battery and still does not guarantee a globally optimal decision. An unfinished search is different from exhausting the permitted search space without a solution. Retry or undo when appropriate.

## Learning from the assistant

Try a hint in Classic, compare its choice with your own, then follow it. Slow autoplay makes decisions easier to observe. Expedition stops at reward selection; choose a reward and start autoplay again. For a manual record, avoid assistance from the start.

Retained host evidence includes a Classic run of 3,200 moves, 69,592 points and a 4096 tile from version 1.0. Expedition was rerun on 1.0.1: six stages, 138 actions, 6,422 points. These are specific seeded runs, not device performance figures, average win rates or promised scores.

## Records and stars

Each mode has separate manual and assisted best scores. Daily records cover the mode as a whole, not a separate daily leaderboard. Undo can reduce the current score without reducing a previously earned record. Puzzle stars retain the best rating for each puzzle; a later one-star finish does not replace three stars. There are no online leaderboards, account-based record merging, friend matches or server statistics.

## What autosave contains

Current sessions, boards and random states, scores, move counts, assistance flags, undo/redo history, Expedition abilities, best puzzle stars, personal Rescue challenges, records and settings. Each non-Daily mode has one active session. Daily retains seven saved dates, and the personal Rescue archive holds six entries.

Ordinary changes are coalesced into a write scheduled after about 280 ms; continuous play does not postpone saving indefinitely. Backgrounding requests an immediate write. Abrupt system termination, lack of storage or device failure can still affect the latest save, so export important progress too. Writes are atomic and retain the previous readable save as a backup. If the primary is missing or corrupt, loading tries the backup; an unreadable original is preserved separately before replacement.

## Exporting a backup

1. Open the top-right settings button.
2. Under 进度 (Progress), tap 导出进度备份 (Export progress backup).
3. Choose a destination in the system file panel. The default name resembles `LUMINA-2026-09-29.json`.
4. Confirm that the file exists in Files before uninstalling or migrating.
5. For multiple exports on one day, add a device name or time to avoid replacing your only copy.

The export includes all mode progress, settings and records, not just the current game. Saving the file to iCloud Drive or sending it through AirDrop is **manual file transfer**, not automatic iCloud synchronization by the app.

## Import and migration

Install a runnable native app on the destination device. Open Settings → 导入进度备份 (Import progress backup), then choose the JSON. The app validates size, structure, board values, random state and challenges before asking 用备份替换本机进度？ (Replace local progress with this backup?). Confirming **replaces all local mode progress, records and settings**; it does not merge the devices. Export the destination's existing progress first.

After import, Classic appears first; switch modes to continue another session. Invalid files or files larger than 24,000,000 bytes are rejected. Native JSON is incompatible with Python desktop, Windows and PWA saves. Renaming a file to `.json` does not convert it.

## Local data and privacy scope

Gameplay and AI run locally, with no server dependency, login requirement or advertising SDK. Saves live in the app sandbox under `Application Support/Lumina`. Players should use the import/export controls rather than edit internal files. Backups contain game state and preferences, not the developer's signing account. Sharing a backup also shares its records and unfinished boards; choose recipients accordingly.

See [Troubleshooting](05-faq.md) for errors, sound issues and installation problems.
