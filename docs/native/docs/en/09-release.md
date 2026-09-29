# Release notes, evidence and documentation maintenance

## Versions

Game: **1.0.1 Native**, build 2. Save schema: 1. Documentation revision: 2026-09-29. This handbook describes the current Swift native implementation. Earlier desktop / PWA manuals do not replace these rules or save instructions.

## Main fixes in 1.0.1

- Queued input could continue behind mode sheets, confirmations or background transitions.
- Continuous input postponed saving; a missing primary did not trigger backup recovery.
- Damaged originals could be overwritten; mixed-mode metadata, invalid calendar dates and inconsistent Rescue data could be accepted.
- Sprint's last move valued nonexistent future turns.
- Changing replay routes could leave an out-of-range cursor.
- Choosing a stage reward during animation could retain old actions.
- Keyboard focus and background saving were adjusted; their iOS branches still require SDK and device verification.

The original detailed repair record is [BUGFIXES-1.0.1.md](../../BUGFIXES-1.0.1.md).

## Retained validation evidence

| Check | Result | Boundary |
| --- | --- | --- |
| Core and interaction | 38 passed | macOS host, not iOS device |
| Mixed operations | 5,760 across six modes | Moves, powers, undo, redo and related state |
| Save round trips | 144 | Encoding and decoding |
| Static layouts | Four sizes rendered and inspected | Cannot establish touch behavior or frame rate |
| Expedition AI on 1.0.1 | Six stages, 6,422 points | Fixed seed and reward priority |
| Classic AI | 3,200 moves, 69,592 points, 4096 tile | Historical 1.0 result, not rerun for this documentation |

Logs and images are in `QA/`; the source report is [QA.md](../../QA.md). Swift Testing summaries may count skipped optional checks in their displayed total. The 38 figure counts the core and interaction checks actually executed.

## What tutorial media represents

Nine demonstrations run the actual native GameModel and SwiftUI on macOS. Sampled frames are assembled as videos and converted to GIF. They are instructional captures, **not iPhone / iPad screen recordings, touch tests or frame-rate measurements**. The English strip at the bottom belongs to the recorder, not the app. Midgame checkpoints come from real engine actions rather than invented scores or modified rules. Seeds, methods and scripts are in the [media notes](../media/README.md).

## Still outstanding

No signed IPA, App Store / TestFlight release or completed iOS SDK build. Device animation, system file panels, suspended-state saving, keyboard, VoiceOver, haptics and rotation still need validation. The native UI is currently Chinese; translated manuals do not constitute UI localization. There is no automatic iCloud sync, multiplayer or cloud leaderboard.

## Reading and maintaining the manual

Chinese button names identify controls; translated names explain them. Arrows always mean board direction: ← left, ↑ up, → right, ↓ down. A zero or dot in a board example means an empty cell, not a zero tile. Solution routes must start from a freshly reset matching challenge.

Open `docs/index.html` for offline reading, language selection, chapters, search and animations. Markdown is the editable source. Printing or saving as PDF produces a static document: GIFs cannot animate on paper or in that PDF. Distribute HTML and media together when animation is needed.
