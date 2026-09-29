# Windows installation and troubleshooting

## Windows portable edition

Target: **Windows 10/11 on Intel/AMD x64**. This is neither a 32-bit build nor a native ARM64 package; ARM emulation has not been validated. The original is `2048-v12-Windows-x64.zip`. The new `2048-v12-Windows-x64-with-docs.zip` adds the complete trilingual handbook while retaining the same game and runtime.

1. Copy the ZIP to the Windows computer. Right-click → Extract All into a local folder.
2. Open the extracted `2048-Windows` folder and double-click **2048.exe**.
3. Allow a few seconds for initial AI preparation. Manual play is available. No separate Python installation or gameplay network connection is required.
4. Select Classic, try arrow-key moves, then close and reopen to check restoration.
5. Read `README.zh-CN.md / README.en.md / README.ja.md` or `docs/index.html` offline.

Keep the complete structure, including `runtime/`, `fonts/`, level JSON and Python files. **Do not run inside the ZIP or copy only the exe.** Python 3.13.15 and pinned dependencies are included; a different system Python does not need replacement.

## Data is not next to the exe

Paste `%LOCALAPPDATA%\2048-Atelier` into Explorer:

| Folder | Contents |
|---|---|
| `data` | Main `save.json`, backup `save.bak`, process lock |
| `exports` | Screenshots saved with P |
| `logs` | Startup `latest.log`; self-check `diagnostics.json` |
| `cache/numba` | Regenerable AI cache, not player progress |

See [chapter 6](06-saves.md) for backups, updates and migration. Extracting a different game folder does not reset progress in user data.

## Diagnose startup failures

1. Confirm full extraction and Windows 10/11 x64.
2. Open **启动游戏.bat** and retain the first console error.
3. Run **check-windows.bat**. It checks dependency versions, Chinese fonts, twelve puzzles, three practices, temporary storage and background AI. Temporary checks do not modify your personal game. The console pauses for reading.
4. Inspect `%LOCALAPPDATA%\2048-Atelier\logs`. `diagnostics.json` only exists if the report was successfully written; if importing a dependency fails earlier, keep the console output.
5. Use the table, then report version, OS, exact error and reproduction steps.

| Symptom | Action |
|---|---|
| Missing runtime/Python/DLL | Check extraction and extract the original package again; do not obtain individual DLLs from unknown sites |
| Another instance reported | Return to that window; normal exit releases the OS lock. A leftover lock file alone does not mean an active lock |
| Chinese square glyphs | Check bundled `fonts/NotoSansSC-*.otf` and `fonts/OFL.txt`; keep the fonts |
| Only exe startup fails | Use the bat console and latest.log; provide console output when no log exists |
| AI never moves, manual play works | Wait for initial preparation, then use diagnostics for worker/Numba failures |
| Scaling/fullscreen trouble | Return to windowed mode and record display scale and resolution |
| Save or screenshot failure | Check user-folder permissions and disk capacity; no system-folder installation is necessary |
| Update appears unchanged | Close the old window and launch from the new fully extracted folder |

The launcher configures DPI awareness before creating a window; this is not proof of all multi-monitor scaling behavior. If Windows flags the source, verify the package and origin and use the system's per-file handling. Do not globally disable protection or force administrator execution.

## Windows source setup

Portable users can skip this. Source setup needs **64-bit Python 3.12–3.14**. `启动游戏.bat` prefers a bundled runtime, then an existing `.venv`, otherwise finds compatible Python and prepares an environment with pinned dependencies. Initial setup needs networking; prepared launches do not reinstall everything.

Manual Command Prompt example with Python 3.13 installed, from the game directory:

```bat
py -3.13 -m venv .venv
.venv\Scripts\python.exe -m pip install --only-binary=:all: -r requirements.txt
.venv\Scripts\python.exe game.py
```

## Validation status

The original package passed ZIP CRC checks, dependency SHA-256 checks and inspection of 135 x64 PE files and required DLL imports. See the [v12 report](../../reference/desktop-v12-validation.md). **No Windows hardware run has been completed.** Static checks do not validate windows, audio, GPU, scaling or real display frame rate. Desktop clips show the same Python game running on Mac; they are not Windows recordings.
