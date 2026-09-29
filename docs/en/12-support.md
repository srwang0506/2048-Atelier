# FAQ, development and validation

## Frequently asked questions

**Why does Mac open a lobby while native opens a board?** Desktop v12 opens mode selection; Native 1.0.1 starts in Classic. They have different entry designs, both keeping Classic first.

**Why is there no Mac exe?** `.exe` is the Windows entry and `.command` the Mac launcher. The two share Python game code but prepare platform-specific runtimes. iPhone/iPad use a separate Swift project.

**Why are game labels Chinese if documentation has three languages?** This delivery adds trilingual documentation and READMEs, not a game UI language selector. Translations preserve the actual button names.

**Does autoplay guarantee 32768?** No. Search is bounded and heuristic, with random outcomes. Historical high scores describe specific trials, not a promise for every version or device.

**Why do phone and computer Daily boards differ?** Check edition, date, action order, undo and assistance. Rule fixtures do not imply identical saves or every cross-edition start; Expedition offer shuffling in particular differs by edition.

**Why do tutorial GIFs look slower?** Media is sampled at 12 fps for readability and file size. It is not a display frame-rate recording or benchmark. Expand MP4 for playback controls.

**Why are stars or records different from expected?** Check assistance, undo, par and the mode whose record you are viewing. Undoing a current game does not lower an established best record.

## Source and development

| Path | Purpose |
|---|---|
| `game.py`, `air_ui.py`, `interface_base.py` | Desktop entry and UI |
| `engine.py`, `modes.py`, `persistence.py` | Rules, independent sessions, background saving |
| `ai.py`, `search_native.py` | Search and worker process |
| `expedition.py`, `rescue.py`, `puzzles.py` | Specialized rules and solvers |
| `desktop_start.py`, `platform_paths.py`, `check_runtime.py` | Platform launch, paths, locking, diagnostics |
| `tests/`, `validation/v12/` | Desktop tests and retained evidence |
| `iOS/` | Native Swift project |
| `mobile/` | Touch web project |
| `docs/`, `README*.md` | Unified handbooks and language entry points |

The standalone documentation ZIP contains manuals, media, reference reports and generation tools, **not a runnable game or full native source**. The Windows-with-docs ZIP includes the Windows game/runtime but not the full iOS project. The original game root is the collection of edition projects and releases.

Prepare a desktop environment, then run from the game root:

```sh
python -m unittest discover -s tests
```

Replace `python` with the game interpreter: `.venv/bin/python` on Mac or `.venv\Scripts\python.exe` for Windows source. Portable Windows users should use `check-windows.bat`. Within `mobile/`, use `node --test tests/*.test.js` and `python3 serve.py` for local web development. Native tests, Xcode builds and device checks are documented in its build chapter.

Retain `THIRD_PARTY.md`, `fonts/OFL.txt` and Windows `licenses/` in the complete game. System fonts such as PingFang are read locally, not copied from Mac for Windows distribution. Source visibility does not imply an unstated redistribution license.

## Separate evidence by edition

The retained Desktop v12 report records **90 passing tests**, a six-stage Expedition with 6,098 points/123 moves, real-loss Rescue extraction, font fallback and Windows static package checks. These are earlier v12 results, not new hardware tests performed for this documentation update.

Native 1.0.1 has **38 core/interaction checks and 5,760 mixed operations** in its retained evidence. Web has separate rule/browser checks. None substitutes for another edition.

See [documentation QA](../QA.md) for this pass: local links and anchors, translated chapters, solution routes, GIF/MP4 decoding and frame counts, packaged resources, unchanged Windows runtime files and unchanged player saves. Offline HTML browser visual/interaction acceptance remains incomplete; structural validation is not a claim of successful clicking through the reader.

## Useful bug report

```text
Edition: Mac/Windows v12, Native 1.0.1, or Touch v1
OS / device / CPU architecture:
Installation method and package filename:
Mode, date or chapter:
Exact reproduction steps:
Expected / actual result:
Repeatable?:
AI, undo or mode changes involved?:
Full error / screenshot / relevant log:
```

Back up before investigating save problems and share only a copy you are willing to use for diagnosis. Passwords and signing certificates are unnecessary. Always identify platform and edition so desktop keyboard issues are not confused with mobile gesture behavior.
