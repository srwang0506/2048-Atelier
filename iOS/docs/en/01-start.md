# Getting started and controls

For LUMINA Native 1.0.1, the iPhone / iPad project. Updated 2026-09-29. **The current app interface is in Chinese.** This English manual translates and identifies those controls; it does not imply that an English interface or an in-app language selector exists.

## Your first game

1. If you received source code, start with [Installation and building](06-build.md). A source ZIP cannot be installed directly on an iPhone. This delivery does not include a signed IPA or a TestFlight invitation.
2. Launch opens **Classic 2048**, restoring its saved game when available. Other modes retain their progress, but the app does not automatically reopen the last non-Classic mode.
3. Swipe left, up, right or down **inside the board**. A swipe moves the entire board; you do not drag an individual tile.
4. Equal tiles merge. Watch the score and move counter change.
5. Tap the mode title and downward chevron to choose another mode. Classic appears first.
6. Leaving the app requests a save. Before uninstalling or moving devices, also export a backup yourself.

## Find every control

| Chinese label / location | English meaning | What it does |
| --- | --- | --- |
| 经典 2048, or another title at the top | Current mode | Opens the six-mode selector; changing mode saves and stops AI |
| Slider icon at top right | Settings | Appearance, feedback, motion, AI, records and backups |
| 本局得分 | Current score | Total earned by merges, not the largest tile; undo restores it |
| 手动最高 / 辅助最高 | Manual / assisted best | Highest score for this mode and category; undo does not lower the record |
| 步数 / 剩余步数 | Moves / moves left | Valid directional moves; Expedition powers do not use a move |
| Curved-back arrow | Undo | Restores the previous action, within the combined 100-entry history |
| 提示 or lightbulb icon | Hint | Requests advice; requesting it immediately marks the game assisted |
| 走这一步 | Play this step | Executes the suggestion on the hint card |
| 自动玩 / 暂停 | Autoplay / pause | Starts or stops repeated AI decisions |
| Ellipsis | More | Redo, restart, select mode; extra puzzle or rescue entries when relevant |
| 手动局 / 辅助局 at bottom | Manual / assisted game | The category of the current run; once assisted, it stays assisted |
| 完成 / 知道了 / 取消 | Done / OK / cancel | Closes the relevant sheet, alert or operation |

On a small screen the hint may use an icon instead of text. Scroll below the board or down the side panel to see objectives, abilities, hints and results.

## Touch and keyboard

Make a clear horizontal or vertical swipe inside the board. A diagonal swipe uses the axis with the larger displacement. Very short gestures may be ignored. External keyboards support arrow keys and **A = left, W = up, D = right, S = down**. Other keyboard shortcuts are not implemented; do not assume Cmd+Z performs undo.

At most two swipes are queued while a move animation is running. Extra rapid input is not stored indefinitely. For precise play, let each move settle. Opening a sheet, displaying an alert or restart confirmation, or going to the background clears queued moves and stops AI. After returning, move manually or tap Autoplay again.

To swap in Expedition, tap 交换, then two occupied tiles with different values. Tap the first selected tile again to deselect it. Tap 取消 to leave selection mode.

## Undo, redo and restart

**Undo / 撤销一步** restores the board, random generator, score, move count and Expedition state. Repeating the same move after undo gives the same random result rather than rerolling it. Freeze and swap each create an undo entry too.

**Redo / 重做一步** is in the ellipsis menu. A new valid action after undo discards the old redo branch. Choosing an initial Expedition ability or a between-stage reward clears history: you cannot undo into the previous stage to choose another reward.

**Restart / 重新开始** asks for confirmation and replaces only the current mode's active game. Classic, Sprint and Expedition get a new random start; Puzzle and Rescue reset the selected challenge. Daily restarts the date currently being played, even if that is yesterday. To open today's Daily game, choose 每日同局 from the mode selector again. Best scores and earned puzzle stars remain.

## iPhone and iPad layouts

Narrow layouts stack the title, scores, board, controls and details. Wide layouts place the board on the left and information on the right. Short landscape layouts scroll the detail panel. The iPad layout responds to available window width; this is not simultaneous play in two independent windows. Rotation and Split View transitions still require physical-device acceptance testing.

## Settings reference

| Chinese setting | Options / default | Effect |
| --- | --- | --- |
| 外观 | 跟随系统 system, 浅色 light, 深色 dark | System is the default |
| 声音 | Sound, on by default | Move and merge sounds, subject to system audio conditions |
| 轻触反馈 | Haptics, on by default | Requires suitable device hardware; some iPads provide no such feedback |
| 减少动态效果 | Reduce motion, off by default | Reduces tile effects; the system accessibility preference also applies |
| 思考强度 | 灵敏 responsive / 深度思考 deep | Responsive is the default; deep gives search more time |
| 自动游玩节奏 | Autoplay pacing, 0.20–1.50 s, default 0.42 s | A pacing setting, not a guaranteed end-to-end interval |

## Accessibility

Board cells expose row, column and value, including empty cells. The board offers four directional accessibility actions; swap targets are selectable controls. Current spoken labels are Chinese. Enable Reduce motion when helpful. VoiceOver end-to-end use, very large text and hardware keyboard focus have not yet been verified on an iOS device. Report concrete steps using the [support template](05-faq.md).

Continue with [Rules for all six modes](02-rules.md), or watch the [animated tutorials](07-gallery.md).
