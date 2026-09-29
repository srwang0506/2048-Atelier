# LUMINA 2048

[简体中文](README.zh-CN.md) · [English](README.en.md) · [日本語](README.ja.md)

Slide tiles, merge equal numbers and work your way from 2 to 2048—and beyond. Choose Classic for an open-ended game, solve a short puzzle, build abilities across an Expedition, or rescue a position from a lost game.

**Web edition: [Open LUMINA 2048](https://lumina-2048.vercel.app/)**

The website is public. Open the link to play; no account or sign-in is required. Before switching addresses, export progress with 「导出进度」 in the old site’s settings, then import it with 「导入进度」 on the new site. Saves do not move automatically between addresses.

**Downloads: [App packages and offline manuals](https://github.com/srwang0506/2048-Atelier/releases/latest)** · [Source code](https://github.com/srwang0506/2048-Atelier)

For Windows, choose the Windows x64 package in Releases. GitHub’s “Download ZIP” contains source code only. The iPhone/iPad edition currently provides buildable native source, without a signed installer.

## Choose your device

| Device | Get started | Instructions |
|---|---|---|
| **Mac** | Double-click **启动游戏.command** in the game folder. First-time setup requires the environment described in the installation guide. | [Mac installation and help](docs/en/07-macos.md) |
| **Windows 10/11 · x64** | Fully extract the Windows portable package and open **2048.exe**. No separate Python installation. | [Windows installation and help](docs/en/08-windows.md) |
| **iPhone / iPad** | The native edition currently ships as source. Build and sign it with Xcode on a Mac before installation. No installable IPA or store download is available. | [iPhone / iPad setup and controls](docs/en/09-mobile.md) |
| **Browser** | Use the separate touch web edition with swipes or direction buttons. | [Web instructions](docs/en/09-mobile.md) |

Editions: Mac/Windows Desktop v12, Native iPhone/iPad 1.0.1 and Touch Web v1. The native deployment target is iOS/iPadOS 16.4+. Game labels are currently primarily Chinese; the handbook is available in Chinese, English and Japanese.

Keep the whole extracted Windows folder, not only the exe. A documentation-only ZIP contains instructions and demonstrations, not a playable game.

## Your first game

1. Select 「经典」 (Classic). Desktop starts at a mode lobby; the native mobile app opens Classic by default.
2. Use arrows/WASD, or drag/swipe inside the board, to move all tiles in one direction.
3. Equal numbers merge: 2 + 2 = 4, then 4 + 4 = 8. A tile created by a merge cannot merge again in that move.
4. A valid move normally adds a new tile. A direction that changes nothing costs no move and spawns nothing.
5. Keep playing after 2048. Even a full board can survive if a merge is still possible.

![Classic: moving, undo and redo](docs/media/11-desktop-classic.gif)

Actual play from the Mac desktop edition. See more in the [animated tutorials](docs/en/10-gallery.md).

## Six ways to play

| Mode | What to expect |
|---|---|
| **Classic** | Unlimited moves to organize your board and reach larger tiles. |
| **Expedition** | Six stages with move limits, ability choices, energy, Swap and Freeze. |
| **Rescue** | Recover at least three empty cells in six moves from a lost-game position; three practices included. |
| **Puzzle Theatre** | Twelve fixed puzzles with target tiles, move limits and three-star challenges. |
| **Daily** | A date-based challenge: the same date and action sequence reproduce spawns. |
| **60-Move Sprint** | Score as much as possible in sixty valid moves. |

Modes retain separate progress. Read the [rules](docs/en/03-rules.md) for scores, stars and winning conditions, or the [Expedition guide](docs/en/04-expedition.md) for every ability.

## Play yourself or ask AI for a hand

Hint recommends a move. Autoplay keeps playing until you pause or take over manually. Hints and AI count as assistance and affect the record category; Undo cannot clear that flag. AI runs locally and does not guarantee a particular tile in every game.

Common desktop shortcuts:

| Action | Key |
|---|---|
| Move | Arrows / WASD |
| Undo / redo | Z / Shift+Z or Y |
| Hint / one AI move | H / Enter |
| Autoplay / pause | Space |
| Mode lobby / Replay | B / R |

See [desktop controls](docs/en/02-controls.md) for the full list. Phones and tablets use on-screen buttons; desktop shortcuts do not all apply to the native App.

## Save and change devices

Progress saves automatically. Close the game normally before disconnecting a drive. Mac saves are in the game folder's `data/`; Windows saves are in `%LOCALAPPDATA%\2048-Atelier\data`. Native and Web editions can export JSON backups in settings.

There is no automatic cross-device sync. Matching Desktop v12 saves can move between Mac and Windows; Native, Web and Desktop formats are different. Read [backup, transfer and updates](docs/en/06-saves.md) before changing devices or importing.

## Need help?

- [Open the complete English handbook](docs/en/index.html) · [Choose a language](docs/index.html)
- [Frequently asked questions](docs/en/12-support.md) · [Detailed native iPhone/iPad manual](docs/native/docs/en/index.html)
- [All Puzzle and Rescue solutions](docs/en/11-solutions.md)—spoilers; try the challenges first.

If Windows does not launch, use `启动游戏.bat` to see the error or `check-windows.bat` for diagnostics. [Release notes](docs/en/12-support.md) describe verification limits: Windows hardware acceptance and iPhone/iPad device acceptance remain incomplete.
