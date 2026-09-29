#if os(macOS)
import AppKit
import SwiftUI
import Testing
import LuminaCore
@testable import LuminaPreview

/// Opt-in capture only. Runs real GameModel actions in a live macOS NSHostingView.
/// It never reads or writes the player's normal Application Support directory.
@Suite("Documentation media", .serialized)
@MainActor struct DocumentationCapture {
    @Test(.enabled(if: ProcessInfo.processInfo.environment["LUMINA_CAPTURE_DIRECTORY"] != nil))
    func recordDocumentation() async throws {
        let directory = URL(fileURLWithPath: ProcessInfo.processInfo.environment["LUMINA_CAPTURE_DIRECTORY"]!)
        try FileManager.default.createDirectory(at: directory, withIntermediateDirectories: true)
        _ = NSApplication.shared
        let model = GameModel(repository: SaveRepository(directory: directory.appendingPathComponent("scratch-save")))
        await model.load()
        let recorder = try MovieRecorder(model: model, directory: directory)
        func load(_ game: Game) throws {
            var book = SaveBook(); book.remember(game); book.settings.sound = false; book.settings.haptics = false
            try model.importData(book.encoded()); model.notice = nil; model.switchMode(game.mode)
            model.settings.sound = false; model.settings.haptics = false
        }
        func move(_ d: Direction, _ label: String? = nil) async throws {
            recorder.label.text = label ?? [Direction.left: "SWIPE LEFT  ←", .up: "SWIPE UP  ↑", .right: "SWIPE RIGHT  →", .down: "SWIPE DOWN  ↓"][d]!
            model.move(d); try await recorder.hold(1.05)
        }
        var classic = Game(seed: 42)
        for _ in 0..<30 { if let a = Solver.solve(classic, budget: 0.025).action { classic.perform(a) } }
        try load(classic); try await recorder.begin("01-classic", caption: "CLASSIC · A REAL SEEDED GAME")
        for _ in 0..<5 { if case .move(let d) = Solver.solve(model.game, budget: 0.025).action { try await move(d) } }
        try await recorder.end()

        try await recorder.begin("02-undo-redo", caption: "UNDO & REDO · THE RANDOM STATE IS RESTORED")
        if case .move(let d) = Solver.solve(model.game, budget: 0.025).action { try await move(d) }
        recorder.label.text = "UNDO · SCORE, BOARD & MOVE COUNT RETURN"; model.undo(); try await recorder.hold(1.8)
        recorder.label.text = "REDO · THE SAME TILE RETURNS"; model.redo(); try await recorder.hold(1.8)
        try await recorder.end()

        try await recorder.begin("03-ai", caption: "HINT · THIS GAME IS NOW ASSISTED")
        model.askHint(); try await recorder.hold(1.4)
        recorder.label.text = "FOLLOW HINT"; model.followHint(); try await recorder.hold(1.1)
        recorder.label.text = "AUTOPLAY · LOCAL EXPECTIMAX SEARCH"; model.toggleAuto(); try await recorder.hold(7)
        model.stopAI(); recorder.label.text = "PAUSED · MANUAL CONTROL RESUMES"; try await recorder.hold(1)
        try await recorder.end()

        try load(Game(mode: .expedition, seed: 42)); try await recorder.begin("04-expedition-draft", caption: "EXPEDITION · CHOOSE ONE OF THREE ABILITIES")
        try await recorder.hold(1.2); model.choose(.battery); recorder.label.text = "BATTERY CORE · EXTRA ENERGY PER MERGE"; try await recorder.hold(1)
        for _ in 0..<4 { if case .move(let d) = Solver.solve(model.game, budget: 0.025).action { try await move(d) } }
        try await recorder.end()

        var powered = Game(mode: .expedition, seed: 42); powered.choose(.battery)
        for _ in 0..<100 {
            if powered.expedition?.phase == .clear { powered.choose(powered.expedition!.offers[0]) }
            if (powered.expedition?.energy ?? 0) >= 11 && powered.phase == .play { break }
            if let a = Solver.solve(powered, budget: 0.025).action { powered.perform(a) }
        }
        #expect(powered.availablePowers.contains(.freeze))
        try load(powered); try await recorder.begin("05-expedition-powers", caption: "EXPEDITION · CONTINUATION WITH EARNED ENERGY")
        recorder.label.text = "FREEZE · COST 5 · NO MOVE USED"; model.usePower(.freeze); try await recorder.hold(1.5)
        if case .swap(let a, let b) = model.game.availablePowers.first(where: { if case .swap = $0 { true } else { false } }) {
            model.swapping = true; model.tapTile(a); recorder.label.text = "SWAP · SELECT TWO DIFFERENT VALUES"; try await recorder.hold(0.8); model.tapTile(b); try await recorder.hold(1.1)
        }
        for _ in 0..<2 { if case .move(let d) = Solver.solve(model.game, budget: 0.025).action { try await move(d, "FREEZE ACTIVE · MOVE WITHOUT A NEW TILE") } }
        try await recorder.end()

        model.start(model.levels[0]); try await recorder.begin("06-puzzle", caption: "PUZZLE 01 · TARGET 64 · TWO-MOVE SOLUTION")
        for d in model.levels[0].solution { try await move(d) }
        #expect(model.game.phase == .won)
        recorder.label.text = "COMPLETE · NO HINTS, NO UNDO · THREE STARS"; try await recorder.hold(1.6)
        try await recorder.end()

        let challenge = model.practices[0]; model.start(challenge)
        try await recorder.begin("07-rescue", caption: "RESCUE · ONE START, TWO DIFFERENT OUTCOMES")
        try await move(challenge.original[0].direction!, "ORIGINAL ROUTE · NO LEGAL MOVE REMAINS")
        model.restart(); recorder.label.text = "RETRY THE SAME START · AIM FOR THREE EMPTY CELLS"; try await recorder.hold(1)
        for d in challenge.solution { try await move(d) }
        #expect(model.game.phase == .won)
        recorder.label.text = "RESCUED · THE SOURCE GAME STAYS SEPARATE"; try await recorder.hold(1.5)
        try await recorder.end()

        try load(.daily("2026-09-29")); let dailyStart = model.game.board
        try await recorder.begin("08-daily", caption: "DAILY · FIXED LOCAL DATE 2026-09-29")
        for _ in 0..<3 { if case .move(let d) = Solver.solve(model.game, budget: 0.025).action { try await move(d) } }
        model.restart(); #expect(model.game.board == dailyStart)
        recorder.label.text = "RESTART · THE SAME INITIAL BOARD RETURNS"; try await recorder.hold(1.8)
        try await recorder.end()

        var sprint = Game(mode: .sprint, seed: 42)
        for _ in 0..<57 { if let a = Solver.solve(sprint, budget: 0.025).action { sprint.perform(a) } }
        #expect(sprint.moves == 57)
        try load(sprint); try await recorder.begin("09-sprint", caption: "SPRINT · A REAL GAME AT MOVE 57")
        for _ in 0..<3 { if case .move(let d) = Solver.solve(model.game, budget: 0.04).action { try await move(d) } }
        #expect(model.game.moves == 60); #expect(model.game.phase == .lost)
        recorder.label.text = "60 VALID MOVES · FINAL SCORE"; try await recorder.hold(1.5)
        try await recorder.end()
        model.suspend(); recorder.window.orderOut(nil)
    }
}

@MainActor private final class CaptureLabel: ObservableObject { @Published var text = "LUMINA DOCUMENTATION" }
private struct CaptureRoot: View {
    @ObservedObject var model: GameModel
    @ObservedObject var label: CaptureLabel
    var body: some View {
        VStack(spacing: 0) {
            NativeGameView(model: model).frame(width: 1000, height: 660)
            HStack { Text(label.text).font(.system(size: 11, weight: .semibold, design: .monospaced)); Spacer(); Text("macOS native preview").font(.system(size: 10)) }.foregroundStyle(Color(hex: 0x52685E)).padding(.horizontal, 28).frame(height: 40).background(Color(hex: 0xE7EDE8))
        }.environment(\.colorScheme, .light)
    }
}
@MainActor private final class MovieRecorder {
    let window: NSWindow, hosting: NSHostingView<CaptureRoot>, label = CaptureLabel(), directory: URL
    private var frame = 0, name = "", events: [[String: Any]] = []
    init(model: GameModel, directory: URL) throws {
        self.directory = directory
        hosting = NSHostingView(rootView: CaptureRoot(model: model, label: label))
        window = NSWindow(contentRect: NSRect(x: 0, y: 0, width: 1000, height: 700), styleMask: [.borderless], backing: .buffered, defer: false)
        window.contentView = hosting; window.orderFront(nil)
    }
    func begin(_ name: String, caption: String) async throws {
        self.name = name; label.text = caption; frame = 0; events = []
        try FileManager.default.createDirectory(at: directory.appendingPathComponent(name), withIntermediateDirectories: true)
        try await hold(1.1)
    }
    func hold(_ seconds: Double) async throws {
        events.append(["time": Double(frame)/12, "caption": label.text])
        for _ in 0..<Int(seconds * 12) {
            try await Task.sleep(nanoseconds: 83_333_333)
            hosting.layoutSubtreeIfNeeded(); hosting.displayIfNeeded()
            let rep = try #require(hosting.bitmapImageRepForCachingDisplay(in: hosting.bounds))
            hosting.cacheDisplay(in: hosting.bounds, to: rep)
            if frame == 0, let png = rep.representation(using: .png, properties: [:]) { try png.write(to: directory.appendingPathComponent(name + "-poster.png")) }
            let jpeg = try #require(rep.representation(using: .jpeg, properties: [.compressionFactor: 0.88]))
            try jpeg.write(to: directory.appendingPathComponent(name).appendingPathComponent(String(format: "%05d.jpg", frame)))
            frame += 1
        }
    }
    func end() async throws {
        let manifest: [String: Any] = ["name": name, "frames": frame, "fps": 12, "duration": Double(frame)/12, "capture": "Live macOS NSHostingView running GameModel; frame sampling, not an iOS screen recording or FPS benchmark", "events": events]
        try JSONSerialization.data(withJSONObject: manifest, options: [.prettyPrinted, .sortedKeys]).write(to: directory.appendingPathComponent(name + ".json"))
        print("DOCUMENTATION_MOVIE \(name): \(frame) frames")
    }
}
#endif
