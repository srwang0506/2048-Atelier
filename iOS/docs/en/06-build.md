# Installation, builds and developer guide

## Delivery status

LUMINA 1.0.1 is a native Swift / SwiftUI Universal App project for iPhone and iPad, with a minimum deployment target of iOS / iPadOS 16.4. It contains no WebView. The source includes the core, resources, Xcode project, tests, documentation and tutorial media. It currently includes **no signed IPA, simulator build, TestFlight release or App Store release**.

A deployment target is not a compiler requirement: the package requires a Swift 6.0+ toolchain and uses Swift 5 language mode. Xcode must also support your device OS. This development machine has only Command Line Tools; macOS checks have run, but an iOS SDK build and device acceptance have not.

## Run on your own device

1. Install full Xcode on a Mac. Choose a release compatible with the Mac and device using Apple's [Xcode requirements](https://developer.apple.com/xcode/system-requirements). Command Line Tools installed by `xcode-select --install` are insufficient.
2. Launch Xcode and finish installing required components. In Settings → Locations → Command Line Tools, select that Xcode.
3. Extract the project to a writable local directory. Open `Lumina.xcodeproj` and choose the shared **Lumina** scheme.
4. Add your Apple Account under Xcode → Settings → Accounts. In the target's Signing & Capabilities, select your Team. Change the Bundle Identifier if necessary to one unique to you.
5. Connect and unlock your device, complete trust pairing, and follow Xcode / system prompts for Developer Mode. Choose the iPhone or iPad as the run destination.
6. Press ▶ Run. Allow the initial build and signing to finish. If it fails, inspect the actual first error; changing a filename extension cannot fix signing.
7. Test Classic movement, orientation changes, all modes, saves, feedback and file import/export.

Apple references: [Running on simulated or physical devices](https://developer.apple.com/documentation/xcode/running-your-app-on-simulated-or-physical-devices), [accounts and teams](https://help.apple.com/xcode/mac/current/en.lproj/dev60b6fbbc7.html). Eligibility and distribution rules are governed by Apple at the time of use. Running on a personal device is distinct from distributing through TestFlight.

## Source map

| Path | Purpose |
| --- | --- |
| `App/` | SwiftUI, GameModel, input, feedback, app assets and privacy manifest |
| `Sources/LuminaCore/` | Rules, RNG, modes, search and persistence |
| `Sources/LuminaCore/Resources/` | 12 puzzles and 3 Rescue practices |
| `Tests/LuminaCoreTests/` | Rule fixtures, save regressions and AI endurance |
| `Tests/LuminaAppTests/` | Lifecycle, layouts and opt-in documentation capture |
| `Lumina.xcodeproj/` | Shared scheme and local package reference |
| `tools/` | Project generation, validation, archive and documentation tools |
| `docs/` | Three languages, offline HTML, shared GIFs and source demo videos |
| `QA/` | Retained test logs and layout images |

The runtime has no third-party SDK and requires no remote Swift package. Documentation-generation dependencies are separate from app runtime dependencies.

## Build and test commands

Run from the project root:

```sh
swift test -c release --disable-xctest
python3 tools/validate-project.py
./tools/check.sh
```

The first runs Swift Testing on the host Mac; the second checks configuration and resources. The third also attempts an iOS Simulator build and fails explicitly if the SDK is missing. Host tests do not substitute for an iOS build.

```sh
LUMINA_BENCHMARK=1 swift test -c release --disable-xctest --filter Benchmark
LUMINA_RENDER_DIRECTORY=/tmp/lumina-layouts swift test -c release --disable-xctest --filter renderNativeLayouts
```

These opt into endurance tests and static SwiftUI layout images. Layout images use a test container and are not device screenshots. Capture and conversion commands are in the [media notes](../media/README.md).

## Archive and distribution

Use Product → Archive in Xcode, or:

```sh
LUMINA_TEAM_ID=YOUR_TEAM_ID ./tools/archive.sh
```

The script creates `build/Lumina.xcarchive` only. It does not upload or export an IPA. Export must match your certificates, account eligibility, devices and distribution intent. Do not publish account credentials, certificates or device identifiers in source. These commands do not enroll you in a developer program.

## Maintaining the project

After adding `App/*.swift`, run `python3 tools/generate-project.py` to update references. The generator restores default Team / Bundle Identifier values, so preserve your local signing changes first. The optional capture test uses its own temporary save directory and does not touch a player's normal data.

Desktop-compatible random behavior is verified with fixtures, while native JSON remains a distinct format. When rules, abilities, levels or labels change, update all three manuals and relevant media. Documentation revisions are separate from gameplay versions; this documentation pass does not change game rules.

## Physical-device acceptance plan

| Scenario | Expected outcome |
| --- | --- |
| iPhone portrait / landscape | Complete board, reachable controls, scrollable objectives and results |
| iPad full screen / Split View | Resizing and rotation do not reset play or obscure controls |
| Fast swipes followed by a menu | Board stops; no stale queued move after dismissal |
| AI search while switching mode / backgrounding | Old search does not move or overwrite the new game |
| Relaunch after background / system termination | Latest persisted state restores; errors are reported |
| Export / import / cancel | Export can be read back; cancel and invalid files preserve progress |
| Keyboard / VoiceOver | Board is operable and focus behaves correctly around sheets |
| Six modes and powers | Limits, rewards, assistance and results match the rules |
| Sound / silent mode / haptics | Matches settings and hardware capabilities |

This is a pending acceptance plan, not a report that every device check has passed.
