# Choose a platform and edition

This handbook covers **Mac, Windows, iPhone, iPad and Web**. They belong to one game family but use separate builds, version numbers, interfaces and save formats. This edition describes the source and delivery files available on 2026-09-29.

## Start with your device

| Device / edition | Delivery and launch | Read next |
|---|---|---|
| Mac · Python Desktop v12 | Double-click `启动游戏.command` in the game folder; first-time setup needs compatible Python | [Mac installation](07-macos.md), then [controls](02-controls.md) |
| Windows · Python Desktop v12 | Fully extract the Windows x64 portable ZIP; open `2048.exe` | [Windows installation](08-windows.md), then [controls](02-controls.md) |
| iPhone / iPad · Native 1.0.1, build 2 | SwiftUI source project; install after building and signing with Xcode and an iOS SDK | [App overview](09-mobile.md), then [nine-chapter native manual](../native/docs/en/index.html) |
| Browser · Touch v1 | Separate Web / PWA edition; Safari can add it to the Home Screen | [Web instructions](09-mobile.md) |

The Windows package targets Intel/AMD x64 computers running Windows 10/11. Mac execution has been checked on an Apple Silicon host; other Macs require dependency and runtime checks. The native project targets iOS/iPadOS 16.4 or later. An iOS build, signing and device acceptance remain outstanding in this environment. **Native source is not an installable IPA; a Home Screen web app is a different edition.**

## Feature differences

| Feature | Mac / Windows v12 | Native 1.0.1 | Touch v1 |
|---|---|---|---|
| Six modes, Classic first | Yes | Yes | Yes |
| Hints, autoplay, undo/redo | Yes | Yes | Yes |
| Automatic Coach analysis | Yes, C | No equivalent desktop control | No equivalent desktop control |
| General last-100-action Replay | Yes, R | No; Rescue has route comparison | Yes |
| In-game JSON import/export | No; copy save files | Yes | Yes |
| P screenshot / F fullscreen | Yes | Use system controls | Use browser/system controls |
| Storage | Local files | App sandbox | Browser site storage |

The **documentation** is trilingual; current game labels are primarily Chinese. English and Japanese instructions retain Chinese button labels to help you find them. There is no automatic cross-device cloud sync or shared online leaderboard. Do not import saves across editions. **Matching desktop v12** saves can be moved between Mac and Windows using the [file-transfer procedure](06-saves.md).

## How to use this handbook

Install the correct edition, read controls and rules, then explore AI assistance. Chapter 4 contains Expedition numbers; chapter 6 covers backups before updates or computer changes. Chapter 11 contains full solutions and spoilers.

Keep the whole folder for offline reading. Open `docs/index.html` and choose a language. Search covers the twelve chapters in that language; the separate native manual has its own search. Language switching preserves the chapter. GIFs start paused; press Play or expand the MP4 player. Reading the manual does not upload or modify game progress.
