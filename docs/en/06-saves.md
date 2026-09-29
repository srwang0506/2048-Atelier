# Saves, backup, transfer and updates

## Find the right data

| Edition | Main save / backup | Images and logs |
|---|---|---|
| Mac Desktop v12 | Game folder: `data/save.json`, `data/save.bak` | Game folder `exports/`; launcher Terminal output |
| Windows Desktop v12 | `%LOCALAPPDATA%\2048-Atelier\data\save.json`, adjacent `save.bak` | `%LOCALAPPDATA%\2048-Atelier\exports` and `logs` |
| Native 1.0.1 | App sandbox; use settings JSON export/import | See the native backup guide |
| Touch v1 | Site IndexedDB; use settings export/import | Bound to browser, device and site identity |

Desktop saves in the background about every five seconds and after key actions. Normal exit waits for the final write. Missing or damaged main saves trigger an attempt to restore the last readable `save.bak`. This is one rolling backup, not unlimited history. Copy important progress elsewhere. Saves include RNG, undo history, mode progress and records; editing numbers by hand can break consistency.

## Manual desktop backup

1. Stop autoplay and close every game window normally.
2. On Mac, open the game folder's `data` directory in Finder. On Windows, paste `%LOCALAPPDATA%\2048-Atelier\data` into Explorer's address bar.
3. Copy `save.json` and `save.bak`, when present, together into a separate dated folder.
4. Copy `exports` separately if you want screenshots. An image cannot restore a game.

Do not run the game during copying. Close older versions too: the new lock cannot protect against an old process that does not use it. Copying `2048.exe` or `game.py` alone does not back up progress in the user-data folder.

## Transfer between Mac and Windows v12

1. Confirm both are Desktop v12 and back up both original profiles.
2. Launch and close the destination game once to establish its folders.
3. With both games closed, copy the source main save and backup as a pair into the destination `data` folder.
4. If the source has no `save.bak`, move the destination's old backup into your separate backup folder first. Otherwise a damaged new main save might restore an unrelated old game.
5. Relaunch and verify mode, score, board and undo history before continuing. This **replaces** destination progress; it does not merge two profiles.

Windows automatically imports old game-folder saves only when **neither save.json nor save.bak exists** in user data. If either exists, it does not overwrite automatically. Old files are left in place. Use the explicit backup procedure instead of repeatedly deleting files to provoke migration.

## Updates and recovery

For Windows updates, keep the user-data folder and fully extract the new game into a new folder after closing the old window. For Mac source updates, retain `data`, `exports` and the local environment. A copied virtual environment is not portable to another computer; recreate dependencies as described in the installation chapter.

After a backup-recovery message, verify the board and back up the current files. If both files are unusable, preserve the damaged originals for diagnosis and restore your separate valid copy. Without a valid copy, recovery cannot be promised. Disk-full, read-only folders or disconnecting a drive can prevent saving; resolve the reported issue and exit normally.

## Edition boundaries

Native JSON, Touch JSON and Python desktop saves are different formats. The `.json` extension does not make them interchangeable. Native/Web import replaces that edition's current progress; export the destination first. There is no automatic iCloud or cross-platform cloud sync. Back up before deleting the App, clearing site data or changing browsers.
