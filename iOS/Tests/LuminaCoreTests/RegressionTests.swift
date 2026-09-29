import Foundation
import Testing
@testable import LuminaCore

@Suite("Native bug regressions") struct RegressionTests {
    @Test func missingPrimaryStillRecoversBackup() async throws {
        let directory = FileManager.default.temporaryDirectory.appendingPathComponent(UUID().uuidString)
        defer { try? FileManager.default.removeItem(at: directory) }
        let store = SaveRepository(directory: directory)
        var book = SaveBook(); book.remember(Game(seed: 111))
        try await store.save(book, revision: 1); try await store.save(book, revision: 2)
        try FileManager.default.removeItem(at: directory.appendingPathComponent("progress.json"))
        let restored = await store.load()
        #expect(restored.book == book); #expect(restored.message != nil)
    }
    @Test func unreadablePrimaryIsPreservedBeforeNextSave() async throws {
        let directory = FileManager.default.temporaryDirectory.appendingPathComponent(UUID().uuidString)
        defer { try? FileManager.default.removeItem(at: directory) }
        let store = SaveRepository(directory: directory)
        var book = SaveBook(); book.remember(Game(seed: 3))
        try await store.save(book, revision: 1)
        let damaged = Data("damaged original progress".utf8)
        try damaged.write(to: directory.appendingPathComponent("progress.json"))
        _ = await store.load(); try await store.save(book, revision: 2)
        let remaining = try FileManager.default.contentsOfDirectory(at: directory, includingPropertiesForKeys: nil)
        #expect(remaining.contains { (try? Data(contentsOf: $0)) == damaged })
    }
    @Test func classicRejectsForeignModeStateIncludingUndoFrames() {
        var game = Game(seed: 2), state = ExpeditionState(seed: 2)
        state.phase = .play; state.offers = []; state.perks = ["gambit": 2]
        game.expedition = state; #expect(!game.isValid)
        game.expedition = nil; var frame = game.snapshot; frame.expedition = state
        game.history = [frame]; #expect(!game.isValid)
    }
    @Test func invalidCalendarDateCannotEnterDailyArchive() {
        #expect(!Game.daily("2026-02-30").isValid)
        #expect(!Game.daily("2026-99-01").isValid)
        #expect(Game.daily("2024-02-29").isValid)
    }
    @Test func rescueMustMatchArchivedObjectiveAndOriginalRoute() throws {
        var challenge = try GameContent.practice()[0]
        var book = SaveBook(), game = Game.rescue(challenge)
        game.rescue?.goal = challenge.goal + 1; book.remember(game)
        #expect(!book.isValid)
        challenge.original[0].board.swapAt(0, 1); #expect(!challenge.isValid)
        challenge = try GameContent.practice()[0]; challenge.original = []; #expect(!challenge.isValid)
    }
    @Test func sprintLastMoveMaximizesImmediateScore() {
        var random = GameRandom(seed: 1989)
        for _ in 0..<16 {
            var game = Game(mode: .sprint, seed: 2)
            game.moves = 59; game.board = (0..<16).map { _ in random.choice(5) == 0 ? 0 : 1 << (random.choice(6) + 1) }
            let legal = Direction.allCases.map { Rules.slide(game.board, $0) }.filter(\.changed)
            guard !legal.isEmpty else { continue }
            if case .move(let direction) = Solver.solve(game, budget: 0.03).action {
                #expect(Rules.slide(game.board, direction).gain == legal.map(\.gain).max())
            } else { Issue.record("Sprint still has a legal last move") }
        }
    }
    @Test func sprintTwoMovePlanMatchesEnumeratedExpectedScore() {
        var random = GameRandom(seed: 54)
        for _ in 0..<8 {
            var game = Game(mode: .sprint, seed: 1); game.moves = 58
            game.board = (0..<16).map { _ in random.choice(5) == 0 ? 0 : 1 << (random.choice(6) + 1) }
            var values: [Direction: Double] = [:]
            for direction in Direction.allCases {
                let first = Rules.slide(game.board, direction); guard first.changed else { continue }
                let spaces = first.board.indices.filter { first.board[$0] == 0 }; var continuation = 0.0
                for position in spaces { for (tile, probability) in [(2, 0.9), (4, 0.1)] {
                    var child = first.board; child[position] = tile
                    let best = Direction.allCases.map { Rules.slide(child, $0).gain }.max() ?? 0
                    continuation += Double(best) * probability / Double(spaces.count)
                } }
                values[direction] = Double(first.gain) + continuation
            }
            guard !values.isEmpty else { continue }
            let result = Solver.solve(game, budget: 0.2)
            #expect(result.depth == 2)
            if case .move(let direction) = result.action {
                #expect(abs(values[direction]! - values.values.max()!) < 0.000001)
            } else { Issue.record("Missing two-step sprint decision") }
        }
    }
    @Test func savedStatesRemainValidAcrossMixedOperationsInAllModes() throws {
        let levels = try GameContent.levels(), rescues = try GameContent.practice()
        for mode in GameMode.allCases { for seed in 0..<6 {
            var random = GameRandom(seed: UInt64(seed)), book = SaveBook()
            func fresh() -> Game {
                switch mode {
                case .daily: return .daily("2026-09-29")
                case .puzzle: return .puzzle(levels[seed])
                case .rescue: return .rescue(rescues[seed % rescues.count])
                default: return Game(mode: mode, seed: UInt64(seed))
                }
            }
            var game = fresh()
            for index in 0..<160 {
                if random.choice(7) == 0 { _ = game.undo() }
                else if random.choice(11) == 0 { _ = game.redo() }
                else if let expedition = game.expedition, [.draft,.clear].contains(expedition.phase) { _ = game.choose(expedition.offers[random.choice(expedition.offers.count)]) }
                else if game.phase != .play { game = fresh() }
                else if mode == .expedition, random.choice(3) == 0, let action = game.availablePowers.first { _ = game.perform(action) }
                else { _ = game.perform(.move(Direction.allCases[random.choice(4)]), assisted: index % 13 == 0) }
                #expect(game.isValid, "\(mode.rawValue), seed \(seed), operation \(index)")
                book.remember(game)
                if index % 40 == 0 { #expect(try SaveBook.decode(book.encoded()) == book) }
            }
        } }
    }
}
