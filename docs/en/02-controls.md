# Desktop quick start and controls

This chapter applies to **Mac / Windows Desktop v12**. Both platforms use the same game controls.

## Your first game

1. Launch the game to open 「选择玩法」 (mode selection). 「经典与挑战」 is the default page; the large Classic card is on the left.
2. Select 「经典」. Scores are at the top, with a 4×4 board in the center.
3. Use arrows, WASD or a mouse drag on the board. A move slides the whole board; you cannot drag individual tiles.
4. Merge equal numbers and keep space available. Try a few manual moves before requesting a hint.
5. Click the mode title or press B to return. 「精选玩法」 contains Expedition and Rescue. 「继续当前局」 resumes the current board. Each mode retains its own progress.

## Keyboard reference

| Key | During play |
|---|---|
| Arrows / WASD | Slide; manual input can take over from AI |
| Space | Start / pause autoplay |
| Z | Undo |
| Shift+Z / Y | Redo |
| H | Request a hint |
| Enter | One AI move |
| C | Toggle Coach; an actual analysis counts as assistance |
| R | Open Replay |
| B | Mode lobby |
| N | Restart the current mode; complete a confirmation if shown |
| T / M | Toggle appearance / sound |
| F / P | Fullscreen / save screenshot |
| F1 | Rules and control help |
| Esc | Close a panel, leave fullscreen or pause, depending on state |

Inside Replay, Left/Right step between frames, Home selects the beginning, End selects the current final frame and Space plays/pauses. Focus the game window before using shortcuts. Buttons also work with a mouse. Desktop touch depends on the OS and SDL input device support; it has not been validated on every touchscreen computer.

## Undo, Replay and restart are different

**Undo** restores board, score, move count and random state. **Redo** restores the undone action. Making a different move after Undo creates a new branch and discards the previous redo branch. Up to 100 actions are retained; saved history survives restart. Assistance flags remain after Undo.

**Replay** only views history. **原局重试** restarts the fixed Puzzle/Rescue challenge. **新开一局** replaces the current game of that mode, keeping other modes. Restarting Daily retries its current challenge date; use the lobby to enter today's challenge.

## Settings and display

The round settings button at the upper right contains AI quality, playback speed, light/dark appearance, sound, animation, fullscreen, records and help. AI thinking quality and autoplay speed are separate settings. 「冲分」 skips step-by-step animations; choose normal/slow speed with animation enabled to watch transitions.

P saves a file in [the local exports folder](06-saves.md), rather than the clipboard. Screenshot failures show a message without intentionally exiting; filenames avoid same-second overwrites. Close normally and let saving finish before disconnecting an external drive.
