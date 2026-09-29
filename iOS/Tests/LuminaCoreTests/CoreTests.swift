import Foundation
import Testing
@testable import LuminaCore

private struct Fixtures: Decodable {
    struct Random: Decodable { var seed: String, floats: [Double] }
    struct Slide: Decodable { var board: [Int], direction: Direction, after: [Int], gain: Int, merges: [Int], tracks: [MotionTrack] }
    struct Moves: Decodable {
        struct Initial: Decodable { var board: [Int], rng: GameRandom }
        struct Row: Decodable { var direction: Direction, changed: Bool, board: [Int], score: Int, moves: Int, rng: GameRandom }
        var mode: GameMode, initial: Initial, rows: [Row]
    }
    struct Reward: Decodable { var board: [Int], gain: Int, merges: [Int], extra: ExpeditionState, points: Int, skip: Bool, after: ExpeditionState }
    var random: [Random], slides: [Slide], moves: [Moves], reward: [Reward]
    static func load() throws -> Self {
        let decoder = JSONDecoder(); decoder.keyDecodingStrategy = .convertFromSnakeCase
        return try decoder.decode(Self.self, from: Data(contentsOf: Bundle.module.url(forResource: "desktop-fixtures", withExtension: "json")!))
    }
}

@Suite("Native rules and desktop parity") struct CoreTests {
    @Test func seededRandomMatchesPython() throws {
        for fixture in try Fixtures.load().random { var rng = GameRandom(seed: UInt64(fixture.seed)!); for expected in fixture.floats { #expect(rng.random() == expected) } }
    }
    @Test func fourHundredSlidesMatchDesktop() throws {
        for fixture in try Fixtures.load().slides {
            let result = Rules.slide(fixture.board, fixture.direction)
            #expect(result.board == fixture.after); #expect(result.gain == fixture.gain); #expect(result.merges == fixture.merges); #expect(result.tracks == fixture.tracks)
            #expect(result.board.reduce(0, +) == fixture.board.reduce(0, +))
        }
    }
    @Test func threeHundredMovesMatchDesktopIncludingRandomState() throws {
        for fixture in try Fixtures.load().moves {
            var game = Game(mode: fixture.mode, seed: 42)
            #expect(game.board == fixture.initial.board); #expect(game.rng == fixture.initial.rng)
            if game.mode == .puzzle { var level = try GameContent.levels()[0]; level.target = 1 << 40; level.limit = 1000; game.puzzle = level }
            for row in fixture.rows {
                let result = game.perform(.move(row.direction))
                #expect((result != nil) == row.changed); #expect(game.board == row.board); #expect(game.rng == row.rng)
                #expect(game.score == row.score); #expect(game.moves == row.moves)
            }
        }
    }
    @Test func oneHundredAbilityRewardsMatchDesktop() throws {
        for fixture in try Fixtures.load().reward {
            let result = fixture.extra.reward(board: fixture.board, gain: fixture.gain, merges: fixture.merges)
            #expect(result.points == fixture.points); #expect(result.skip == fixture.skip); #expect(result.state == fixture.after)
        }
    }
    @Test func allTwelvePuzzlesHaveVerifiedMinimalSolutions() throws {
        let levels = try GameContent.levels(); #expect(levels.count == 12)
        for level in levels {
            #expect(level.isValid); var game = Game.puzzle(level)
            let result = Solver.exact(game, budget: 10)
            #expect(result.complete); #expect(result.solvable); #expect(result.solution.count == level.par)
            for direction in result.solution { #expect(game.perform(.move(direction)) != nil) }; #expect(game.phase == .won)
            var supplied = Game.puzzle(level); for d in level.solution { _ = supplied.perform(.move(d)) }; #expect(supplied.phase == .won)
        }
    }
    @Test func allRescuesAreReplayableAndSolvable() throws {
        let rescues = try GameContent.practice(); #expect(rescues.count == 3)
        for challenge in rescues {
            #expect(challenge.isValid); var game = Game.rescue(challenge), untouched = game
            let result = Solver.exact(game, budget: 10)
            #expect(result.complete && result.solvable); #expect(result.solution.count == challenge.par); #expect(game == untouched)
            for direction in result.solution { #expect(game.perform(.move(direction)) != nil) }; #expect(game.phase == .won)
            for frame in challenge.original { if let d = frame.direction { _ = untouched.perform(.move(d)); #expect(untouched.board == frame.board) } }
        }
    }
    @Test func undoRedoAndBranchRestoreRandomness() throws {
        var game = Game(seed: 61); let initial = game.snapshot
        let direction = try #require(Direction.allCases.first { Rules.slide(game.board, $0).changed })
        _ = game.perform(.move(direction), assisted: true); let moved = game.snapshot
        #expect(game.undo() == true); #expect(game.snapshot == initial); #expect(game.assisted)
        #expect(game.redo() == true); #expect(game.snapshot == moved); #expect(game.assisted)
        #expect(game.undo() == true); _ = game.perform(.move(direction), assisted: true); #expect(game.snapshot == moved); #expect(game.future.isEmpty)
    }
    @Test func noOpDoesNotConsumeRandomOrHistory() {
        var game = Game(seed: 4); game.board = [2,4,8,16] + Array(repeating: 0, count: 12)
        let before = game; #expect(game.perform(.move(.left)) == nil); #expect(game == before)
    }
    @Test func sprintStopsAtSixtyAndUndoRestoresBudget() {
        var game = Game(mode: .sprint, seed: 8); game.moves = 59; game.board = [2,2] + Array(repeating: 0, count: 14)
        #expect(game.perform(.move(.left)) != nil); #expect(game.moves == 60); #expect(game.phase == .lost)
        #expect(game.perform(.move(.down)) == nil); #expect(game.undo() == true); #expect(game.remaining == 1)
    }
    @Test func puzzleWinHasPriorityOnLastMove() throws {
        var level = try GameContent.levels()[0]; level.limit = 1; level.target = 4; level.board = [2,2] + Array(repeating: 0, count: 14)
        var game = Game.puzzle(level); _ = game.perform(.move(.left)); #expect(game.remaining == 0); #expect(game.phase == .won)
    }
    @Test func powersPreserveTurnAndRandomAndAreUndoable() {
        var game = Game(mode: .expedition, seed: 43); #expect(game.choose(.battery) == true); game.expedition?.energy = 12
        game.board = [2,4,8,16] + Array(repeating: 0, count: 12); let initial = game.snapshot
        #expect(game.perform(.freeze) != nil); #expect(game.rng == initial.rng); #expect(game.moves == 0); #expect(game.expedition?.energy == 7)
        #expect(game.perform(.freeze) == nil); #expect(game.undo() == true); #expect(game.snapshot == initial)
        #expect(game.perform(.swap(0,1)) != nil); #expect(game.board[0] == 4); #expect(game.moves == 0); #expect(game.rng == initial.rng)
        #expect(game.undo() == true); #expect(game.snapshot == initial)
        _ = game.perform(.freeze); let rng = game.rng; _ = game.perform(.move(.down)); #expect(game.rng == rng); #expect(game.expedition?.freeze == 1); #expect(game.expedition?.cooldown == 5)
    }
    @Test func stageClearAndFinalWinHavePriorityOnLastMove() {
        var game = Game(mode: .expedition, seed: 42); _ = game.choose(.battery); game.moves = 25; game.score = 96; game.board = [2,2] + Array(repeating: 0, count: 14)
        _ = game.perform(.move(.left)); #expect(game.phase == .clear); #expect(game.expedition?.offers.count == 3)
        let offer = game.expedition!.offers[0]; #expect(game.choose(offer) == true); #expect(game.expedition?.stage == 1); #expect(game.history.isEmpty); #expect(game.phase == .play)
        game.expedition?.stage = 5; game.expedition?.stageStart = game.moves; game.expedition?.stageScore = game.score; game.score += 2196
        game.board = [2,2] + Array(repeating: 0, count: 14); _ = game.perform(.move(.left)); #expect(game.phase == .won); #expect(game.expedition?.cleared == 6)
    }
    @Test func solverChoosesLegalActionAndHandlesLargeTiles() {
        var game = Game(seed: 4); game.board = [65536,65536,32768,0,8192,4096,2048,0,512,256,128,0,32,16,8,0]
        let original = game; let result = Solver.solve(game, budget: 0.04)
        #expect(game == original); #expect(result.depth >= 1); #expect(result.nodes > 0)
        if let action = result.action { #expect(game.perform(action, assisted: true) != nil) } else { Issue.record("Missing legal AI action") }
    }
    @Test func realFailedGameCanBecomeAnIndependentChallenge() {
        var failed = Game(seed: 17), chooser = GameRandom(seed: 9)
        for _ in 0..<4000 {
            let legal = Direction.allCases.filter { Rules.slide(failed.board, $0).changed }; if legal.isEmpty { break }
            _ = failed.perform(.move(legal[chooser.choice(legal.count)]))
        }
        #expect(!Rules.canMove(failed.board)); let original = failed; let result = Solver.extract(failed, budget: 10)
        #expect(!result.timedOut); #expect(failed == original)
        if let challenge = result.challenge { #expect(challenge.isValid); var game = Game.rescue(challenge); for d in challenge.solution { _ = game.perform(.move(d)) }; #expect(game.phase == .won) }
        else { Issue.record("Expected a verified rescue in this deterministic failed game") }
    }
    @Test func nativeBackupRoundTripAndValidation() throws {
        var book = SaveBook(); var game = Game(seed: 5); _ = game.perform(.move(.left)); book.remember(game)
        #expect(try SaveBook.decode(book.encoded()) == book)
        var invalid = book; invalid.sessions["classic"]?.rng.index = -1
        #expect(throws: (any Error).self) { try SaveBook.decode(JSONEncoder().encode(invalid)) }
        invalid = book; invalid.sessions["classic"]?.board = [3]
        #expect(throws: (any Error).self) { try SaveBook.decode(JSONEncoder().encode(invalid)) }
        #expect(throws: (any Error).self) { try SaveBook.decode(Data(repeating: 0, count: 24_000_001)) }
    }
    @Test func automaticBackupRecoveryAndRevisionOrdering() async throws {
        let url = FileManager.default.temporaryDirectory.appendingPathComponent(UUID().uuidString)
        defer { try? FileManager.default.removeItem(at: url) }
        let store = SaveRepository(directory: url); var first = SaveBook(); first.remember(Game(seed: 2))
        var second = first; second.settings.sound = false
        try await store.save(first, revision: 1); try await store.save(second, revision: 3); try await store.save(first, revision: 2)
        let loaded = await store.load(); #expect(loaded.book == second)
        try Data("broken".utf8).write(to: url.appendingPathComponent("progress.json"))
        let recovered = await store.load(); #expect(recovered.book == first); #expect(recovered.message != nil)
    }
    @Test func invalidStageAndOrphanRescueAreRejectedBeforePlay() throws {
        var game = Game(mode: .expedition, seed: 12)
        game.expedition?.phase = .clear; game.expedition?.stage = 5
        #expect(!game.isValid)
        var book = SaveBook(); book.sessions["expedition"] = game
        #expect(throws: (any Error).self) { try SaveBook.decode(JSONEncoder().encode(book)) }
        book = SaveBook(); var rescue = Game.rescue(try GameContent.practice()[0]); rescue.rescue?.challenge = "missing-challenge"
        book.sessions["rescue"] = rescue; #expect(!book.isValid)
    }
    @Test func recordsStarsDailyRetentionAndArchivePinning() throws {
        var book = SaveBook(); var game = Game(seed: 1); game.score = 256; book.remember(game); game.assisted = true; game.score = 1024; book.remember(game)
        #expect(book.records["classic"]?.manual == 256); #expect(book.records["classic"]?.assisted == 1024)
        for day in 1...10 { book.remember(.daily(String(format: "2026-09-%02d", day))) }; #expect(book.sessions.keys.filter { $0.hasPrefix("daily:") }.count == 7)
        let level = try GameContent.levels()[0]; var puzzle = Game.puzzle(level); for d in level.solution { _ = puzzle.perform(.move(d)) }; book.remember(puzzle); #expect(book.stars["0"] == 3)
        let base = try GameContent.practice()[0]
        for i in 0..<8 { var challenge = base; challenge.id = "test-\(i)"; book.archive(challenge, keeping: "test-0") }
        #expect(book.rescues.count == 6); #expect(book.rescues.contains { $0.id == "test-0" }); #expect(book.isValid)
    }
}
