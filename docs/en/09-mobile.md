# iPhone, iPad and the web edition

## iPhone and iPad: one native project, adaptive layouts

**Native 1.0.1 (build 2)** is a real Swift/SwiftUI Universal App source project, with no WebView. iPhone and iPad share rules and source while adapting layout to width. The deployment target is iOS/iPadOS 16.4; the toolchain requires Swift 6.0+ with Swift 5 language mode. A deployment target and a compiler requirement are different.

The game root's `iOS/` folder contains `Lumina.xcodeproj`, core, UI, resources, tests and the native handbook. **There is no signed IPA, TestFlight invitation or App Store release.** Install full Xcode and a compatible iOS SDK on Mac, open the project, configure your Team/Bundle Identifier, select a device and Run. Command Line Tools alone cannot install the app on an iPhone. Follow the [installation, signing, build and acceptance guide](../native/docs/en/06-build.md).

## Native controls

Launch defaults to Classic. The top mode title opens other modes. Swipe inside the board, use the curved arrow for Undo, the lightbulb for Hint and autoplay to start/pause. The ellipsis contains Redo, restart and mode-specific puzzle/Rescue choices. Settings include appearance, sound, haptics, reduced motion, AI strength and JSON backups.

External keyboards support arrows/WASD; desktop Z/R/C/P shortcuts do not apply. Up to two swipes can queue during animation; menus, backgrounding and manual takeover handle pending input and pause AI. Narrow iPhone layouts stack vertically; wider iPad layouts place board and information side by side. Smaller windows adapt, and long information can scroll.

Pause AI, then export JSON through settings to Files or another location. Back up the destination before importing, which replaces native progress. This format differs from both Python desktop saves and Touch JSON. Requesting a native hint immediately marks assistance even if you never use the suggested move.

## All nine native chapters remain available

- [Getting started, gestures and iPhone/iPad layouts](../native/docs/en/01-start.md)
- [Six modes](../native/docs/en/02-rules.md) and [abilities/scoring](../native/docs/en/03-expedition.md)
- [AI, records and backups](../native/docs/en/04-ai-data.md)
- [Troubleshooting](../native/docs/en/05-faq.md) and [build/install](../native/docs/en/06-build.md)
- [Nine native demonstrations](../native/docs/en/07-gallery.md), [solutions](../native/docs/en/08-solutions.md), [release validation](../native/docs/en/09-release.md)

If the App is already installed, begin with controls. If you received source, begin with builds. Mac host tests and layout images do not replace device testing of touch, rotation, Split View, backgrounding, VoiceOver or display performance.

## Touch v1: the separate web edition

The web edition is separate from the native App. It supports Safari touch controls and adding the game to the Home Screen. For the native App, use the installation and control instructions above.

1. Open [LUMINA for the web](https://lumina-2048.vercel.app/) in Safari. Access is currently restricted; sign in with an authorized Vercel account.
2. Wait for full initial loading, then Share → Add to Home Screen.
3. Wait for offline preparation before testing a disconnected Home Screen launch. Offline availability is not promised before caching completes.
4. Swipe inside the board, use direction buttons or arrows/WASD.
5. Export JSON in settings. Import only into another **Touch** edition, after backing up that destination.

Touch has all six modes, hints, Worker-based AI, undo/redo, last-100-action Replay, Rescue route comparison, appearance, sound and reduced motion. Menus, backgrounding and manual takeover pause autoplay. It does not implement the full Python desktop keyboard map, and desktop AI time presets do not describe its settings.

Progress lives in site IndexedDB with backup and a page-leaving emergency snapshot. Browser/device/Home Screen contexts do not synchronize automatically. Clearing site data, private browsing or storage eviction can affect progress. Export important data first. If an old web interface persists after an update, export before reconnecting/reopening for the update; do not begin by deleting site data.

When moving from the old address, first choose 「导出进度」 in the old site’s settings, then 「导入进度」 on the new site. Browser saves do not move automatically between addresses. Add a new Home Screen icon from the new address as well.

Source lives in `mobile/`. Local `python3 serve.py` is for development and skips Service Worker registration by default; phone deployment needs HTTPS. Native rule comparisons, web tests and browser layout checks do not prove physical-device offline cold start, haptics or system-gesture behavior.
