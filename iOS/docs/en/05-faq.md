# Troubleshooting and reporting a problem

## A swipe or button does nothing

Check for a sheet, alert, reward choice or finished game. A direction must change the board to count as a move. Start the gesture inside the board and swipe far enough. At most two moves queue during animation; more rapid input is not accumulated. On narrow screens the lightbulb is the Hint control.

If 准备棋盘… (Preparing board) never finishes, note any built-in resource error. Try closing and reopening; developers should check packaged resources. Do not uninstall unbacked-up progress just to troubleshoot.

## Why does play continue after 2048?

Classic and Daily allow larger tiles. Puzzle checks its own target, Sprint checks the move limit, and Expedition checks stage points. Their ending conditions differ.

## I merged tiles, but Rescue did not complete

The normal new tile spawns after the merge. Rescue counts empty cells after that spawn. Three spaces immediately after merging may become two. Only Expedition has Freeze and Flow to suppress spawning.

## Why is this an assisted game?

A hint request, autoplay, or opening Rescue replay before winning marks assistance, even if you ignore the advice. Undo and import do not remove it. A previously earned manual best remains, but subsequent scores from this run belong to assisted records.

## Why did I miss three stars?

Three stars require no assistance, no undo and completion at or below par. Par is not the maximum allowed move count. Unassisted completion with an undo earns at most two; assisted completion earns one. Restart the puzzle for a fresh three-star attempt.

## Why did AI stop, or why can it still lose?

AI pauses at rewards, the end of a game, menus and manual intervention. Restart it after closing a menu. Finite-time search and heuristic evaluation do not guarantee endless survival in a random game. Deep mode grants more search time, not a proof of global optimality. You choose Expedition rewards yourself.

## Why are Expedition powers disabled?

Freeze requires 5 energy, no cooldown, no active freeze and a legal slide. Swap requires enough energy and two occupied, different-valued tiles. Powers also wait for the current animation. Energy is capped at 12. A six-move cooldown means six valid directional moves, not six seconds.

## Why does a friend's Daily board differ?

Compare local dates, mode, version and moves already made. Different time zones can produce different dates. Matching board states require matching action sequences, not just the date. There is no live synchronization. Yesterday's open game does not automatically become today's; select Daily again.

## Import failed or older progress appeared

| Symptom | What to check |
| --- | --- |
| 存档格式不正确 / Invalid format | Use a complete, unmodified export from this native app; desktop, Windows and PWA files differ |
| 超过 24 MB / Too large | Limit is 24,000,000 bytes; preserve the original instead of deleting arbitrary JSON fields |
| 已从备用存档恢复 / Restored backup | Primary was missing or corrupt; the previous readable version may omit the latest action |
| Import opens Classic | Expected behavior; choose the saved mode from the selector |
| Both devices have new progress | Import replaces everything; export both first and choose which to keep |
| 保存失败 / Save failed | Check free storage, attempt an export and retain the complete error message |

Do not repeatedly restart and overwrite your only useful state while investigating a save failure.

## Sound, haptics or animation seem wrong

Check app settings, system volume, silent mode and audio output. The implementation uses an ambient audio category that can mix with other audio. Haptics depend on hardware; some iPads do not support the same feedback. Reduce motion can come from the app or system. Tutorial GIFs are sampled demonstrations and cannot measure an iPhone's refresh rate. Hardware audio, haptics and animation still need device testing.

## How do I install this on an iPhone or iPad?

A source ZIP, Xcode project or macOS preview is not an installable IPA. A full Xcode installation, matching SDK and signing setup are required. No TestFlight invitation has been delivered. Follow [Installation](06-build.md).

## English or Japanese UI? Windows? Multiplayer?

This documentation is available in Chinese, English and Japanese; the current native interface remains Chinese. There is no language-switch button. Earlier Python desktop, Windows and PWA editions remain separate; this handbook does not claim they are iOS apps or share save formats. The native edition has no multiplayer, cloud leaderboard or automatic cloud synchronization.

## A useful bug report

Copy these fields and describe the exact action that triggers the issue.

| Field | Example information |
| --- | --- |
| App version | 1.0.1 Native and build number |
| Device and OS | iPhone / iPad model and iOS / iPadOS version |
| Mode and position | Puzzle 03, or Expedition stage 2 |
| Reproduction | Launch → select mode → swipe left → undo → observed result |
| Expected versus actual | What should happen, and what happened instead |
| Frequency | Every time, or approximately how often |
| Relevant state | AI, Reduce motion, keyboard, Split View |
| Evidence | Screenshot / recording, complete error; optionally a backup you are comfortable sharing |

There is no built-in ticket submission button or designated public support email for this project. Send the report to your project maintainer. See [Release and validation](09-release.md) for known boundaries.
