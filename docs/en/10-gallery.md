# Seventeen animated demonstrations

Eight desktop clips plus nine native clips, all from the actual game code. Each GIF was made by decoding its delivered MP4. Sampling at 12 fps serves instruction, not display performance measurement. GIFs start paused in HTML; play them or expand MP4. Markdown viewers usually loop GIFs automatically.

## Mac / Windows Desktop v12 controls

Captured from the real Python/pygame renderer on Mac using SDL dummy and an isolated temporary profile. Windows shares this code, but these are not Windows hardware recordings. Silent; no personal player save was used.

### Lobby: Classic first and featured modes

Switch from Classic/Challenges to Featured, return and enter Classic. B returns to the lobby during play.

![Lobby: Classic first and featured modes](../media/10-desktop-lobby.gif)

[GIF](../media/10-desktop-lobby.gif) · [MP4 · 6.00 s](../media/10-desktop-lobby.mp4) · [PNG](../media/10-desktop-lobby-poster.png)

### Classic: move, undo and redo

A real seed-42 opening: left, down, left, up, right, then undo and redo. Board, score and move count restore together.

![Classic: move, undo and redo](../media/11-desktop-classic.gif)

[GIF](../media/11-desktop-classic.gif) · [MP4 · 7.00 s](../media/11-desktop-classic.mp4) · [PNG](../media/11-desktop-classic-poster.png)

### AI analysis, one step and Replay

The actual worker computes direction analysis. Preview left, execute one AI move, then review history without changing the current board.

![AI analysis, one step and Replay](../media/12-desktop-ai-replay.gif)

[GIF](../media/12-desktop-ai-replay.gif) · [MP4 · 8.50 s](../media/12-desktop-ai-replay.mp4) · [PNG](../media/12-desktop-ai-replay-poster.png)

### Puzzle: reach 64 in two moves

Puzzle 01 from its original state: up, up, then the actual three-star result. Contains the solution.

![Puzzle: reach 64 in two moves](../media/13-desktop-puzzle.gif)

[GIF](../media/13-desktop-puzzle.gif) · [MP4 · 5.33 s](../media/13-desktop-puzzle.mp4) · [PNG](../media/13-desktop-puzzle-poster.png)

### Expedition: choose an ability and gain energy

A seed-13 opening, Battery Core selection, moves, energy and the rules panel. This is stage-one instruction, not a full six-stage run.

![Expedition: choose an ability and gain energy](../media/14-desktop-expedition.gif)

[GIF](../media/14-desktop-expedition.gif) · [MP4 · 8.00 s](../media/14-desktop-expedition.mp4) · [PNG](../media/14-desktop-expedition-poster.png)

### Rescue: three moves and route comparison

Practice 01: right, up, up creates three empty cells. Open comparison after success and step through. Contains the solution.

![Rescue: three moves and route comparison](../media/15-desktop-rescue.gif)

[GIF](../media/15-desktop-rescue.gif) · [MP4 · 6.83 s](../media/15-desktop-rescue.mp4) · [PNG](../media/15-desktop-rescue-poster.png)

### Daily: fixed date, undo and redo

Created by the production daily_game function for 2026-09-29. Demonstrates moves, undo and redo; invalid directions do not add moves.

![Daily: fixed date, undo and redo](../media/16-desktop-daily.gif)

[GIF](../media/16-desktop-daily.gif) · [MP4 · 6.67 s](../media/16-desktop-daily.mp4) · [PNG](../media/16-desktop-daily-poster.png)

### Sprint: track the move allowance

A real seed-42 Sprint opening, five moves, undo and redo. This explains the counter, not the move-60 result.

![Sprint: track the move allowance](../media/17-desktop-sprint.gif)

[GIF](../media/17-desktop-sprint.gif) · [MP4 · 7.50 s](../media/17-desktop-sprint.mp4) · [PNG](../media/17-desktop-sprint-poster.png)

## Native iPhone / iPad controls (Mac host preview)

These nine GIFs are converted from sampled videos of the actual native code running. The MP4 source videos are included. Capture platform: macOS native preview, **not iPhone / iPad screen recording or a device FPS test**. The English bottom strip is a tutorial annotation. The HTML reader can pause animations; Markdown viewers usually loop them. MP4 uses H.264. Expand the video player in the HTML reader or download it for separate playback. All media is local and works offline.

### Classic: slide, merge and spawn

Continue a real seed-42 game from midgame. Watch the entire board slide, equal values merge, the score rise and a new tile appear. The bottom strip identifies directions.

![Classic: slide, merge and spawn](../native/docs/media/01-classic.gif)

Try keeping your largest tile near a corner. A slide without a merge still spawns a tile.

[GIF](../native/docs/media/01-classic.gif) · [MP4 · 6.08 s](../native/docs/media/01-classic.mp4) · [PNG](../native/docs/media/01-classic-poster.png)

### Undo and redo: restore the same spawn

Make one move, undo it, then redo. The board, score and counter change together.

![Undo and redo: restore the same spawn](../native/docs/media/02-undo-redo.gif)

Redo is in the ellipsis menu. The random state is restored too; this is not a reroll.

[GIF](../native/docs/media/02-undo-redo.gif) · [MP4 · 5.58 s](../native/docs/media/02-undo-redo.mp4) · [PNG](../native/docs/media/02-undo-redo-poster.png)

### AI: hint, follow, autoplay and pause

Request a hint, follow it, run autoplay, then pause.

![AI: hint, follow, autoplay and pause](../native/docs/media/03-ai.gif)

The footer changes from manual to assisted. Pausing does not clear the assisted flag.

[GIF](../native/docs/media/03-ai.gif) · [MP4 · 11.5 s](../native/docs/media/03-ai.mp4) · [PNG](../native/docs/media/03-ai-poster.png)

### Expedition: draft and opening moves

Begin a seed-42 expedition, choose Battery Core and make several valid moves.

![Expedition: draft and opening moves](../native/docs/media/04-expedition-draft.gif)

Multiple merged pairs earn more energy. Distinguish the stage target from cumulative score.

[GIF](../native/docs/media/04-expedition-draft.gif) · [MP4 · 7.25 s](../native/docs/media/04-expedition-draft.mp4) · [PNG](../native/docs/media/04-expedition-draft-poster.png)

### Expedition: freeze and swap

Continue from an actually played position with 12 energy. Freeze, select two different values to swap, then make two moves.

![Expedition: freeze and swap](../native/docs/media/05-expedition-powers.gif)

Active powers leave the move counter unchanged. Frozen moves do not spawn a new tile.

[GIF](../native/docs/media/05-expedition-powers.gif) · [MP4 · 6.42 s](../native/docs/media/05-expedition-powers.mp4) · [PNG](../native/docs/media/05-expedition-powers-poster.png)

### Puzzle: make 64 in two moves

Puzzle 01 from its reset state: up, then up, reaching 64.

![Puzzle: make 64 in two moves](../native/docs/media/06-puzzle.gif)

Contains the solution. No hint or undo is used, so the result earns three stars.

[GIF](../native/docs/media/06-puzzle.gif) · [MP4 · 4.67 s](../native/docs/media/06-puzzle.mp4) · [PNG](../native/docs/media/06-puzzle-poster.png)

### Rescue: a failed move and a recovery route

Practice A Glimmer of Hope: left reproduces the original blocked outcome. Restart, then right, up, up.

![Rescue: a failed move and a recovery route](../native/docs/media/07-rescue.gif)

Compare the outcomes. Success requires at least three empty cells after spawning. This shows actual challenge actions, not a full Classic recording.

[GIF](../native/docs/media/07-rescue.gif) · [MP4 · 7.58 s](../native/docs/media/07-rescue.mp4) · [PNG](../native/docs/media/07-rescue-poster.png)

### Daily: same date, same restart

Use the fixed demonstration date 2026-09-29, make three moves, then restart.

![Daily: same date, same restart](../native/docs/media/08-daily.gif)

The two initial tiles match the opening. No network synchronization is involved.

[GIF](../native/docs/media/08-daily.gif) · [MP4 · 5.83 s](../native/docs/media/08-daily.mp4) · [PNG](../native/docs/media/08-daily-poster.png)

### Sprint: final three moves

A real seed-42 Sprint is advanced to move 57, then the last three moves and result are captured.

![Sprint: final three moves](../native/docs/media/09-sprint.gif)

Remaining moves fall from 3 to 0. This is not a timer, and there is no move 61.

[GIF](../native/docs/media/09-sprint.gif) · [MP4 · 5.58 s](../native/docs/media/09-sprint.mp4) · [PNG](../native/docs/media/09-sprint-poster.png)

[Media / 媒体 / メディア](../native/docs/media/README.md)
