# LUMINA · Native iPhone / iPad edition

[简体中文](README.zh-CN.md) · [English](README.en.md) · [日本語](README.ja.md)

Six ways to play a quiet, considered number game. Classic always comes first.

This is the **1.0.1 Native source project**, not an installable IPA. Device installation still requires full Xcode, an iOS SDK and signing. An iOS build and device acceptance have not been completed here. App labels are currently Chinese; the documentation is available in Chinese, English and Japanese.

## Offline handbook

Open the [English reader](docs/en/index.html), or choose a language from the [documentation home](docs/index.html). Keep the entire docs folder after extraction so animations and videos remain available offline.

## Chapter guide

- [Getting started and controls](docs/en/01-start.md)
- [Rules for all six modes](docs/en/02-rules.md)
- [Expedition stages and abilities](docs/en/03-expedition.md)
- [AI, records and saves](docs/en/04-ai-data.md)
- [Troubleshooting and support](docs/en/05-faq.md)
- [Installation and development](docs/en/06-build.md)
- [Nine animated tutorials](docs/en/07-gallery.md)
- [Puzzle and Rescue solutions (spoilers)](docs/en/08-solutions.md)
- [Release and validation](docs/en/09-release.md)

## What you can play

Classic 2048, ability-based Expedition, Rescue, Daily, twelve puzzles and 60-Move Sprint. Includes undo/redo, local hints and autoplay, separate manual/assisted records, JSON backups, light/dark appearance and reduced motion. No login, ads or server dependency.

## Controls in one minute

Swipe within the board; use the top mode title to switch games. The lightbulb requests a hint; 自动玩 starts AI. The ellipsis contains redo and restart; top-right settings include backup export. A hint request immediately marks the game assisted.

## Demonstration

A Classic excerpt from nine actual native-preview demonstrations. Captured on macOS, not an iPhone / iPad screen recording or device frame-rate test.

![LUMINA Classic](docs/media/01-classic.gif)

## Project and validation

Open Lumina.xcodeproj and select your own Team in Signing & Capabilities. Chapter 6 covers installation, tests and Archive. Evidence includes 38 core/interaction checks and 5,760 mixed operations; see chapter 9 for limitations.

## Documentation and source

Each language has nine chapters. Shared media includes nine GIFs, nine MP4 source videos and static posters. Native saves are incompatible with older Python / Windows / PWA formats; those editions remain separate.
