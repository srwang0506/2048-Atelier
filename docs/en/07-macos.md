# macOS installation and troubleshooting

## Which edition runs on Mac?

Use **Python Desktop v12**. The current delivery is a source folder with a launcher, not a separately packaged `.app`. `iOS/Lumina.xcodeproj` is the iPhone/iPad project; SwiftUI host previews in this manual are not a replacement Mac desktop distribution.

The examples use `~/2048-Atelier`; replace it with your game folder. Create a fresh Python environment on your Mac rather than copying one from another computer.

## This prepared Mac

1. Mount the external drive and open the game folder.
2. Double-click `启动游戏.command` and wait for the window and AI preparation.
3. Choose Classic or resume in the lobby. Terminal output helps diagnose startup failures.
4. Exit normally and let saving finish before ejecting the drive.

Alternatively:

```sh
cd ~/2048-Atelier
.venv/bin/python game.py
```

## First setup on another Mac

Use **64-bit Python 3.12–3.14**, subject to successful installation of the pinned dependencies. In Terminal, enter the actual game directory and run each command:

```sh
python3 --version
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python game.py
```

Check the first output. If `python3` is incompatible, create the environment with an installed compatible interpreter. Initial dependency downloads need a network connection; prepared gameplay and AI do not require a server. Pinned versions are in the [requirements reference](../../reference/desktop-requirements.txt). Use the game's `.venv`, without modifying system Python via `sudo pip`.

If an existing copied `.venv` is unusable, close the game, rename that environment to retain it, then create a new one locally. Keep `data`. Recreate environments across CPU architectures too. The tested development host is an Apple Silicon Mac; this is not a claim of physical testing across every Intel Mac or macOS release.

## Startup troubleshooting

| Symptom | Check and action |
|---|---|
| Path or file missing | Confirm drive mount and folder name; quote paths containing spaces |
| Double-click does not start | Run `/bin/zsh "启动游戏.command"` in Terminal and read the first error |
| Python/package missing | Check version; install requirements with `.venv/bin/python -m pip` |
| `.venv/bin/python` fails | Was it copied from another computer? Preserve it, then recreate locally |
| Another instance is reported | Find and close the existing window normally; do not delete a lock while it runs |
| Manual play works, AI not ready | Allow compilation preparation; retain output if it remains stuck |
| Missing glyphs | Keep `fonts/` and all resources; system PingFang is read locally, not redistributed |
| Save/screenshot failure | Check game-folder write access, disk space and drive connection; saves are in `data/` |

If macOS flags the download, verify its source and integrity and follow the system's per-item opening flow. Do not disable system protection globally. Existing windows do not load new source automatically; exit and relaunch after updates.
