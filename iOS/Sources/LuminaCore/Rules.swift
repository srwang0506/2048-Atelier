import Foundation
import CryptoKit

public enum Direction: String, CaseIterable, Codable, Sendable {
    case left, up, right, down
    public var symbol: String { switch self { case .left: return "arrow.left"; case .up: return "arrow.up"; case .right: return "arrow.right"; case .down: return "arrow.down" } }
    public var title: String { switch self { case .left: return "向左"; case .up: return "向上"; case .right: return "向右"; case .down: return "向下" } }
}
public enum GameMode: String, Codable, CaseIterable, Identifiable, Sendable {
    case classic, expedition, rescue, daily, puzzle, sprint
    public var id: String { rawValue }
    public var title: String { switch self { case .classic: return "经典 2048"; case .expedition: return "能力远征"; case .rescue: return "败局重生"; case .daily: return "每日同局"; case .puzzle: return "谜题剧场"; case .sprint: return "六十步冲刺" } }
    public var subtitle: String { switch self { case .classic: return "纯粹的合并，熟悉的乐趣。"; case .expedition: return "九种能力，六段旅程。"; case .rescue: return "回到那个岔路口，找到另一种可能。"; case .daily: return "同一天，相同的起点。"; case .puzzle: return "十二道题，把每步想好。"; case .sprint: return "六十步，让每一步都值得。" } }
    public var symbol: String { switch self { case .classic: return "square.grid.2x2"; case .expedition: return "sparkles"; case .rescue: return "arrow.uturn.backward"; case .daily: return "sun.max"; case .puzzle: return "square.on.square"; case .sprint: return "bolt" } }
}
public enum Phase: String, Codable, Sendable { case draft, play, clear, won, lost }
public enum GameAction: Equatable, Codable, Sendable {
    case move(Direction), freeze, swap(Int, Int)
    public var title: String { switch self { case .move(let d): return d.title; case .freeze: return "凝时"; case .swap: return "交换方块" } }
    public var symbol: String { switch self { case .move(let d): return d.symbol; case .freeze: return "snowflake"; case .swap: return "arrow.left.arrow.right" } }
}
public struct MotionTrack: Equatable, Codable, Sendable {
    public var source: Int, target: Int, value: Int
    public init(source: Int, target: Int, value: Int) { self.source = source; self.target = target; self.value = value }
}
public struct SlideResult: Sendable {
    public var board: [Int], gain: Int, tracks: [MotionTrack], merges: [Int], changed: Bool
    public var spawn: Int? = nil
}
public enum Rules {
    public static func validBoard(_ b: [Int]) -> Bool { b.count == 16 && b.allSatisfy { $0 == 0 || ($0 >= 2 && $0 <= (1 << 50) && $0 & ($0 - 1) == 0) } }
    public static func empty(_ b: [Int]) -> Int { b.filter { $0 == 0 }.count }
    public static func canMove(_ b: [Int]) -> Bool {
        guard b.count == 16, b.contains(where: { $0 > 0 }) else { return false }
        if b.contains(0) { return true }
        for i in 0..<16 {
            if i % 4 < 3 && b[i] == b[i + 1] { return true }
            if i < 12 && b[i] == b[i + 4] { return true }
        }
        return false
    }
    public static func slide(_ board: [Int], _ direction: Direction) -> SlideResult {
        precondition(board.count == 16)
        var out = Array(repeating: 0, count: 16), tracks: [MotionTrack] = [], merged: [Int] = [], gain = 0
        for line in 0..<4 {
            let ids = (0..<4).map { c in switch direction { case .left: return line * 4 + c; case .right: return line * 4 + 3 - c; case .up: return c * 4 + line; case .down: return (3 - c) * 4 + line } }
            let cells = ids.filter { board[$0] > 0 }; var n = 0, dest = 0
            while n < cells.count {
                let source = cells[n], target = ids[dest]; var value = board[source]
                tracks.append(.init(source: source, target: target, value: value))
                if n + 1 < cells.count && board[cells[n + 1]] == value {
                    n += 1; tracks.append(.init(source: cells[n], target: target, value: value)); value *= 2; gain += value; merged.append(target)
                }
                out[target] = value; dest += 1; n += 1
            }
        }
        return SlideResult(board: out, gain: gain, tracks: tracks, merges: merged, changed: out != board)
    }
    @discardableResult public static func spawn(_ board: inout [Int], rng: inout GameRandom, puzzle: Bool = false, fourProbability: Double = 0.1) -> Int? {
        let cells = board.indices.filter { board[$0] == 0 }; guard !cells.isEmpty else { return nil }
        let index = cells[puzzle ? Int(rng.random() * Double(cells.count)) : rng.choice(cells.count)]
        board[index] = rng.random() < 1 - fourProbability ? 2 : 4
        return index
    }
    public static func dateToken(_ date: Date = Date(), timeZone: TimeZone = .current) -> String {
        let f = DateFormatter(); f.calendar = Calendar(identifier: .gregorian); f.locale = Locale(identifier: "en_US_POSIX"); f.timeZone = timeZone; f.dateFormat = "yyyy-MM-dd"; return f.string(from: date)
    }
    public static func dailySeed(_ date: String) -> UInt64 {
        SHA256.hash(data: Data("2048-Atelier/daily/v1/\(date)".utf8)).prefix(8).reduce(0) { ($0 << 8) | UInt64($1) }
    }
    public static func validDateToken(_ token: String) -> Bool {
        let bytes = Array(token.utf8)
        guard bytes.count == 10, bytes[4] == 45, bytes[7] == 45,
              bytes.enumerated().allSatisfy({ $0.offset == 4 || $0.offset == 7 || (48...57).contains($0.element) }) else { return false }
        let parts = token.split(separator: "-")
        guard let year = Int(parts[0]), let month = Int(parts[1]), let day = Int(parts[2]), year > 0, (1...12).contains(month) else { return false }
        let leap = year % 400 == 0 || (year % 4 == 0 && year % 100 != 0)
        let days = [31, leap ? 29 : 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        return (1...days[month - 1]).contains(day)
    }
}

public struct PuzzleLevel: Codable, Equatable, Identifiable, Sendable {
    public var id: Int, title: String, note: String, target: Int, par: Int, limit: Int, seed: UInt64, board: [Int], solution: [Direction]
    public var isValid: Bool { (0..<12).contains(id) && Rules.validBoard(board) && (1...7).contains(limit) && (1...limit).contains(par) && target >= 2 && target <= 65536 && target & (target - 1) == 0 && title.count <= 30 && note.count <= 200 && solution.count <= 7 }
}
public struct RescueOrigin: Codable, Equatable, Sendable { public var board: [Int], rng: GameRandom }
public struct RescueFrame: Codable, Equatable, Sendable { public var board: [Int], direction: Direction? }
public struct RescueChallenge: Codable, Equatable, Identifiable, Sendable {
    public var id: String, title: String, origin: RescueOrigin, goal: Int, limit: Int, par: Int, solution: [Direction], original: [RescueFrame], sourceScore: Int, sourceMoves: Int, rewind: Int, practice: Bool
    public var isValid: Bool {
        guard id.count <= 120, title.count <= 40, Rules.validBoard(origin.board), origin.rng.isValid,
              (2...5).contains(goal), (1...7).contains(limit), (1...limit).contains(par), solution.count == par,
              (1...10).contains(rewind), original.count == rewind, original.allSatisfy({ Rules.validBoard($0.board) }), sourceScore >= 0, sourceMoves >= 0 else { return false }
        var board = origin.board, rng = origin.rng
        guard Rules.empty(board) < goal else { return false }
        for d in solution {
            guard Rules.empty(board) < goal else { return false }
            let result = Rules.slide(board, d); guard result.changed else { return false }
            board = result.board; Rules.spawn(&board, rng: &rng)
        }
        guard Rules.empty(board) >= goal && Rules.canMove(board) else { return false }
        board = origin.board; rng = origin.rng
        for frame in original {
            guard let direction = frame.direction else { return false }
            let result = Rules.slide(board, direction); guard result.changed else { return false }
            board = result.board; Rules.spawn(&board, rng: &rng)
            guard board == frame.board else { return false }
        }
        return !Rules.canMove(board)
    }
}
public enum GameContent {
    public static func levels() throws -> [PuzzleLevel] { try load("puzzle-levels") }
    public static func practice() throws -> [RescueChallenge] { try load("rescue-practice") }
    private static func load<T: Decodable>(_ name: String) throws -> T {
        guard let url = Bundle.module.url(forResource: name, withExtension: "json") else { throw CocoaError(.fileNoSuchFile) }
        let d = JSONDecoder(); d.keyDecodingStrategy = .convertFromSnakeCase
        return try d.decode(T.self, from: Data(contentsOf: url))
    }
}
