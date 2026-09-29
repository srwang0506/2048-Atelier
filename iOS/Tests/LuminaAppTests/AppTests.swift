import Foundation
import SwiftUI
import Testing
import LuminaCore
@testable import LuminaPreview

@MainActor @Suite("Native interaction lifecycle", .serialized) struct AppTests {
    private func model() async -> GameModel {
        let directory = FileManager.default.temporaryDirectory.appendingPathComponent("lumina-app-test-\(UUID().uuidString)")
        let model = GameModel(repository: SaveRepository(directory: directory))
        await model.load(); model.settings.sound = false; model.settings.haptics = false
        return model
    }
    @Test func cancelAnimationWithUndoDoesNotLeaveGhostTiles() async throws {
        let model = await model(), initial = model.game
        let direction = try #require(Direction.allCases.first { Rules.slide(initial.board, $0).changed })
        model.move(direction); #expect(model.busy); model.undo()
        try await Task.sleep(nanoseconds: 260_000_000)
        #expect(model.game.board == initial.board); #expect(model.game.rng == initial.rng); #expect(!model.busy)
        #expect(Set(model.tiles.map(\.cell)).count == model.tiles.count)
        #expect(model.tiles.allSatisfy { $0.value == model.game.board[$0.cell] })
        model.suspend()
    }
    @Test func switchingModesCancelsAutoplayAndRetainsBothSessions() async throws {
        let model = await model(); model.motionReduced = true
        model.move(.left); model.toggleAuto(); model.switchMode(.sprint)
        let sprint = model.game
        try await Task.sleep(nanoseconds: 350_000_000)
        #expect(model.game == sprint); #expect(!model.autoPlay); #expect(!model.thinking)
        model.move(.down); let moved = model.game; model.switchMode(.classic); #expect(model.game.assisted)
        model.switchMode(.sprint); #expect(model.game == moved); model.suspend()
    }
    @Test func backgroundDuringAnimationSettlesAndSaves() async throws {
        let model = await model(); model.move(.down); let committed = model.game
        model.suspend(); try await Task.sleep(nanoseconds: 250_000_000)
        #expect(model.game == committed); #expect(!model.busy); #expect(model.tiles.count == committed.board.filter { $0 > 0 }.count)
        #expect(try SaveBook.decode(model.exportData()).sessions[model.game.key] == committed)
    }
    @Test func rapidSwipesDoNotCreateDuplicateTiles() async throws {
        let model = await model()
        for direction in [Direction.left, .down, .right, .up, .left] { model.move(direction) }
        for _ in 0..<100 { if !model.busy { break }; try await Task.sleep(nanoseconds: 20_000_000) }
        #expect(!model.busy); #expect(model.game.isValid)
        #expect(model.tiles.count == Set(model.tiles.map(\.cell)).count)
        #expect(model.tiles.allSatisfy { $0.value == model.game.board[$0.cell] }); model.suspend()
    }
    @Test func hintCannotMutateBoardAfterRestart() async throws {
        let model = await model(); model.askHint(); model.restart(); let fresh = model.game
        try await Task.sleep(nanoseconds: 350_000_000)
        #expect(model.game == fresh); #expect(model.hint == nil); #expect(!model.thinking); #expect(!model.game.assisted); model.suspend()
    }
    @Test func menusAndRestartConfirmationBlockBoardInput() async {
        let model = await model(); let original = model.game
        model.open(.modes); model.move(.left); #expect(model.game == original)
        model.sheet = nil; model.confirmRestart = true; model.move(.down); #expect(model.game == original); model.suspend()
    }
    @Test func invalidImportPreservesExistingSession() async throws {
        let model = await model(); let original = model.game
        #expect(throws: (any Error).self) { try model.importData(Data("{}".utf8)) }
        #expect(model.game == original); model.suspend()
    }
    @Test func modalPresentationCancelsQueuedSwipes() async throws {
        for useConfirmation in [false, true] {
            let model = await model()
            let first = try #require(Direction.allCases.first { Rules.slide(model.game.board, $0).changed })
            model.move(first)
            let queued = try #require(Direction.allCases.first { Rules.slide(model.game.board, $0).changed })
            model.move(queued); let committed = model.game
            if useConfirmation { model.confirmRestart = true } else { model.open(.modes) }
            try await Task.sleep(nanoseconds: 360_000_000)
            #expect(model.game == committed); #expect(!model.busy); model.suspend()
        }
    }
    @Test func uninterruptedMovesStillReachDisk() async throws {
        let directory = FileManager.default.temporaryDirectory.appendingPathComponent(UUID().uuidString)
        let store = SaveRepository(directory: directory), model = GameModel(repository: SaveRepository(directory: directory))
        await model.load(); model.settings.sound = false; model.settings.haptics = false; model.motionReduced = true
        for _ in 0..<8 {
            if let direction = Direction.allCases.first(where: { Rules.slide(model.game.board, $0).changed }) { model.move(direction) }
            try await Task.sleep(nanoseconds: 80_000_000)
        }
        let persisted = await store.load()
        #expect((persisted.book.sessions["classic"]?.moves ?? 0) > 0)
        model.suspend()
    }
    @Test func alertAndBackgroundBlockEveryGameplayEntryPoint() async throws {
        let model = await model(); model.motionReduced = true
        let direction = try #require(Direction.allCases.first { Rules.slide(model.game.board, $0).changed })
        model.move(direction); let original = model.game
        for blockedByAlert in [true, false] {
            if blockedByAlert { model.notice = "测试提示" } else { model.suspend() }
            #expect(!model.acceptsGameplayInput)
            model.move(.down); model.undo(); model.redo(); model.askHint(); model.toggleAuto()
            model.followHint(); model.usePower(.freeze); model.tapTile(-1); model.tapTile(16)
            #expect(model.game == original); #expect(!model.autoPlay && !model.thinking)
            model.notice = nil; model.resume(); #expect(model.acceptsGameplayInput)
        }
        model.undo(); #expect(model.game.moves == original.moves - 1); model.suspend()
    }
    @Test func shortReplayRouteClampsOldCursorIncludingEmptyRoute() throws {
        var challenge = try GameContent.practice()[1]
        let long = ReplayTimeline(challenge: challenge, alternative: true)
        let short = ReplayTimeline(challenge: challenge, alternative: false)
        #expect(short.clampedIndex(long.lastIndex) == short.lastIndex)
        #expect(short.board(at: 999) == challenge.original.last?.board)
        #expect(short.board(at: -1) == challenge.origin.board)
        challenge.original = []
        let empty = ReplayTimeline(challenge: challenge, alternative: false)
        #expect(empty.caption(at: long.lastIndex) == "起始局面")
        #expect(empty.board(at: long.lastIndex) == challenge.origin.board)
    }
    @Test func switchingDuringMergeThenResumingLeavesUniqueTiles() async throws {
        let model = await model(); model.start(model.levels[0]); let start = model.game
        model.move(start.puzzle!.solution[0]); model.move(start.puzzle!.solution[1])
        model.switchMode(.classic); let classic = model.game
        try await Task.sleep(nanoseconds: 250_000_000)
        #expect(model.game == classic); #expect(Set(model.tiles.map(\.cell)).count == model.tiles.count)
        model.switchMode(.puzzle); #expect(model.game.moves == 1)
        #expect(model.tiles.allSatisfy { $0.value == model.game.board[$0.cell] }); model.suspend()
    }
    @Test(.enabled(if: ProcessInfo.processInfo.environment["LUMINA_RENDER_DIRECTORY"] != nil))
    func renderNativeLayouts() async throws {
        #if os(macOS)
        let model = await model(); var book = SaveBook(), game = Game(seed: 7)
        game.board = [2,4,16,64,8,32,128,256,0,2,64,512,0,0,4,1024]; game.score = 12480; game.moves = 728; book.remember(game)
        try model.importData(book.encoded()); model.notice = nil
        let directory = URL(fileURLWithPath: ProcessInfo.processInfo.environment["LUMINA_RENDER_DIRECTORY"]!)
        try FileManager.default.createDirectory(at: directory, withIntermediateDirectories: true)
        for (name, width, height) in [("iphone",390.0,763.0),("iphone-small",335.0,620.0),("ipad",1194.0,790.0),("iphone-landscape",750.0,350.0)] {
            let view = NativeGameView(model: model).frame(width: width, height: height).environment(\.colorScheme, .light).environment(\.layoutSnapshot, true)
            let renderer = ImageRenderer(content: view); renderer.scale = 2
            if let image = renderer.nsImage, let tiff = image.tiffRepresentation, let bitmap = NSBitmapImageRep(data: tiff), let png = bitmap.representation(using: .png, properties: [:]) {
                var darkPixels = 0
                for x in stride(from: 0, to: bitmap.pixelsWide, by: 8) { for y in stride(from: 0, to: bitmap.pixelsHigh, by: 8) { if let color = bitmap.colorAt(x: x, y: y)?.usingColorSpace(.deviceRGB), color.redComponent < 0.6 { darkPixels += 1 } } }
                #expect(darkPixels > 30, "A background-only image must not count as a successful render")
                try png.write(to: directory.appendingPathComponent(name + ".png"))
            }
            else { Issue.record("SwiftUI could not render \(name) in this environment") }
        }
        model.suspend()
        #endif
    }
}

#if os(macOS)
import AppKit
#endif
