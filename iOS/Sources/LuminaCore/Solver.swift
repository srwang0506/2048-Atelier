import Foundation

public struct MoveValue: Sendable, Identifiable {
    public var action: GameAction, value: Double
    public var id: String { action.title }
}
public struct SearchResult: Sendable {
    public var action: GameAction?, solution: [Direction] = [], values: [MoveValue] = []
    public var exact = false, complete = true, solvable = false
    public var depth = 0, nodes = 0, milliseconds = 0
}
public struct RescueExtraction: Sendable {
    public var challenge: RescueChallenge?
    public var timedOut: Bool
    public init(challenge: RescueChallenge? = nil, timedOut: Bool) { self.challenge = challenge; self.timedOut = timedOut }
}

public enum Solver {
    public static func solve(_ game: Game, budget: Double = 0.18) -> SearchResult {
        guard game.phase == .play else { return SearchResult(exact: game.mode == .puzzle || game.mode == .rescue, solvable: game.phase == .won) }
        if game.mode == .puzzle || game.mode == .rescue { return exact(game, budget: max(1.0, budget)) }
        var searcher = Expectimax(game: game, budget: budget)
        return searcher.run()
    }
    public static func exact(_ game: Game, budget: Double = 2.0) -> SearchResult {
        let start = Date.timeIntervalSinceReferenceDate, deadline = start + budget, limit = min(7, game.remaining ?? 0)
        let goal: ([Int]) -> Bool = { b in game.mode == .puzzle ? (b.max() ?? 0) >= (game.puzzle?.target ?? Int.max) : Rules.empty(b) >= (game.rescue?.goal ?? 16) && Rules.canMove(b) }
        if goal(game.board) { return SearchResult(exact: true, solvable: true) }
        struct Node { var board: [Int], rng: GameRandom, path: [Direction] }
        var queue = [Node(board: game.board, rng: game.rng, path: [])], head = 0, nodes = 0, complete = true
        while head < queue.count {
            let node = queue[head]; head += 1; nodes += 1
            if nodes & 31 == 0 && (Date.timeIntervalSinceReferenceDate >= deadline || Task.isCancelled) { complete = false; break }
            if node.path.count >= limit { continue }
            for d in Direction.allCases {
                let result = Rules.slide(node.board, d); if !result.changed { continue }
                var board = result.board, rng = node.rng
                Rules.spawn(&board, rng: &rng, puzzle: game.mode == .puzzle)
                let path = node.path + [d]
                if goal(board) { return SearchResult(action: .move(path[0]), solution: path, exact: true, solvable: true, depth: path.count, nodes: nodes, milliseconds: Int((Date.timeIntervalSinceReferenceDate - start) * 1000)) }
                if path.count < limit && Rules.canMove(board) { queue.append(Node(board: board, rng: rng, path: path)) }
            }
        }
        return SearchResult(exact: true, complete: complete, depth: limit, nodes: nodes, milliseconds: Int((Date.timeIntervalSinceReferenceDate - start) * 1000))
    }
    public static func extract(_ failed: Game, budget: Double = 3) -> RescueExtraction {
        guard [.classic, .daily, .sprint].contains(failed.mode), !Rules.canMove(failed.board), !failed.history.isEmpty else { return .init(challenge: nil, timedOut: false) }
        let deadline = Date.timeIntervalSinceReferenceDate + budget
        for distance in 1...min(10, failed.history.count) {
            if Date.timeIntervalSinceReferenceDate >= deadline || Task.isCancelled { return .init(challenge: nil, timedOut: true) }
            let f = failed.history[failed.history.count - distance]
            if Rules.empty(f.board) > 1 { continue }
            var candidate = Game(mode: .rescue, seed: 0); candidate.board = f.board; candidate.rng = f.rng
            candidate.rescue = .init(challenge: "temporary", goal: 3, limit: 6, par: 1)
            let result = exact(candidate, budget: max(0.01, deadline - Date.timeIntervalSinceReferenceDate))
            if !result.complete { return .init(challenge: nil, timedOut: true) }
            guard result.solvable else { continue }
            let frames = Array(failed.history.suffix(distance)) + [failed.snapshot]
            var original: [RescueFrame] = []
            for index in 0..<(frames.count - 1) {
                var chosen: Direction?
                for direction in Direction.allCases {
                    let shifted = Rules.slide(frames[index].board, direction); if !shifted.changed { continue }
                    var board = shifted.board, rng = frames[index].rng; Rules.spawn(&board, rng: &rng)
                    if board == frames[index + 1].board && rng == frames[index + 1].rng { chosen = direction; break }
                }
                original.append(.init(board: frames[index + 1].board, direction: chosen))
            }
            let challenge = RescueChallenge(id: "rescue-\(failed.id)-\(f.moves)", title: "我的转机", origin: .init(board: f.board, rng: f.rng), goal: 3, limit: 6, par: result.solution.count, solution: result.solution, original: original, sourceScore: failed.score, sourceMoves: f.moves, rewind: distance, practice: false)
            if challenge.isValid { return .init(challenge: challenge, timedOut: false) }
        }
        return .init(challenge: nil, timedOut: false)
    }
}

private struct RowResult { var cells: [UInt8], gain: Int }
private func compact(_ row: [UInt8]) -> RowResult {
    let values = row.filter { $0 > 0 }; var out: [UInt8] = [], gain = 0, i = 0
    while i < values.count { var v = values[i]; if i + 1 < values.count && values[i + 1] == v { v += 1; gain += 1 << v; i += 1 }; out.append(v); i += 1 }
    while out.count < 4 { out.append(0) }; return .init(cells: out, gain: gain)
}
private func scoreRow(_ row: [UInt8]) -> Double {
    var inc = 0.0, dec = 0.0, smooth = 0.0, pairs = 0
    for i in 0..<3 {
        let delta = pow(Double(row[i]), 3.5) - pow(Double(row[i + 1]), 3.5)
        inc += max(0, delta); dec += max(0, -delta)
        if row[i] > 0 && row[i + 1] > 0 { smooth += abs(Double(row[i]) - Double(row[i + 1])) }
    }
    let occupied = row.filter { $0 > 0 }; var i = 0
    while i + 1 < occupied.count { if occupied[i] == occupied[i + 1] { pairs += 1; i += 1 }; i += 1 }
    return Double(row.filter { $0 == 0 }.count * 270 + pairs * 200) - min(inc, dec) * 11 - smooth * 8
}
private func packed(_ row: [UInt8]) -> Int { Int(row[0]) | Int(row[1]) << 4 | Int(row[2]) << 8 | Int(row[3]) << 12 }
private final class RowTables: @unchecked Sendable {
    static let shared = RowTables()
    let scores: [Double], left: [Int], right: [Int], gains: [Int]
    private init() {
        var scores = Array(repeating: 0.0, count: 65536), left = Array(repeating: 0, count: 65536), right = left, gains = left
        for code in 0..<65536 {
            let row: [UInt8] = [UInt8(code & 15), UInt8((code >> 4) & 15), UInt8((code >> 8) & 15), UInt8(code >> 12)]
            scores[code] = scoreRow(row); let a = compact(row), b = compact(row.reversed())
            left[code] = a.cells.contains(16) ? 65536 : packed(a.cells)
            right[code] = b.cells.contains(16) ? 65536 : packed(b.cells.reversed()); gains[code] = a.gain
        }
        self.scores = scores; self.left = left; self.right = right; self.gains = gains
    }
}
private struct PositionKey: Hashable {
    var a: UInt64 = 0, b: UInt64 = 0, depth: Int, streak: Int, energy: Int, freeze: Int, cooldown: Int
    init(_ board: [UInt8], _ depth: Int, _ state: ExpeditionState?) {
        self.depth = depth; streak = state?.streak ?? 0; energy = state?.energy ?? 0; freeze = state?.freeze ?? 0; cooldown = state?.cooldown ?? 0
        for i in 0..<8 { a |= UInt64(board[i]) << (i * 8); b |= UInt64(board[i + 8]) << (i * 8) }
    }
}
private enum Deadline: Error { case reached }
private struct Shifted { var board: [UInt8], gain: Int, changed: Bool }
private struct SearchChoice { var direction: Direction, board: [UInt8], points: Int, skip: Bool, state: ExpeditionState? }
private struct Expectimax {
    let game: Game, table: RowTables, start: Double, deadline: Double
    var nodes = 0, completedDepth = 0, iterationDepth = 0, cache: [PositionKey: Double] = [:]
    init(game: Game, budget: Double) {
        self.game = game; table = RowTables.shared; start = Date.timeIntervalSinceReferenceDate; deadline = start + min(1.2, max(0.025, budget))
    }
    mutating func check() throws { nodes += 1; if nodes & 127 == 0 && (Date.timeIntervalSinceReferenceDate > deadline || Task.isCancelled) { throw Deadline.reached } }
    func shift(_ board: [UInt8], _ d: Direction) -> Shifted {
        var out = Array(repeating: UInt8(0), count: 16), gain = 0
        for line in 0..<4 {
            let ids = (0..<4).map { d == .left || d == .right ? line * 4 + $0 : $0 * 4 + line }
            let row = ids.map { board[$0] }, reverse = d == .right || d == .down
            var result = 65536, code = 0
            if row.allSatisfy({ $0 < 16 }) { code = packed(row); result = reverse ? table.right[code] : table.left[code] }
            if result == 65536 {
                let r = compact(reverse ? row.reversed() : row); gain += r.gain
                let cells = reverse ? Array(r.cells.reversed()) : r.cells
                for i in 0..<4 { out[ids[i]] = cells[i] }
            } else { gain += table.gains[code]; for i in 0..<4 { out[ids[i]] = UInt8((result >> (4 * i)) & 15) } }
        }
        return .init(board: out, gain: gain, changed: out != board)
    }
    func evaluate(_ board: [UInt8]) -> Double {
        var score = 0.0
        for r in 0..<4 { for row in [Array(board[(r * 4)..<(r * 4 + 4)]), [board[r], board[r + 4], board[r + 8], board[r + 12]]] { score += row.allSatisfy { $0 < 16 } ? table.scores[packed(row)] : scoreRow(row) } }
        let maximum = board.max() ?? 0, corner = [0, 3, 12, 15].map { board[$0] }.max() == maximum
        return score + Double(Int(maximum) * Int(maximum) * (corner ? 14 : -20))
    }
    func effect(_ board: [UInt8], _ d: Direction, _ shifted: Shifted, _ e: ExpeditionState?) -> SearchChoice {
        guard let e else { return .init(direction: d, board: shifted.board, points: shifted.gain, skip: false, state: nil) }
        let r = Rules.slide(board.map { $0 == 0 ? 0 : 1 << $0 }, d), reward = e.reward(board: r.board, gain: r.gain, merges: r.merges)
        return .init(direction: d, board: shifted.board, points: reward.points, skip: reward.skip, state: reward.state)
    }
    mutating func player(_ board: [UInt8], depth: Int, probability: Double, state: ExpeditionState?) throws -> Double {
        try check()
        if game.mode == .sprint, iterationDepth - depth >= (game.remaining ?? 0) { return 0 }
        if depth <= 0 || probability < 0.00012 { return evaluate(board) + Double((state?.energy ?? 0) * 24) }
        let key = PositionKey(board, depth, state); if let value = cache[key] { return value }
        var best = -1e8
        for d in Direction.allCases {
            let r = shift(board, d); if !r.changed { continue }
            let c = effect(board, d, r, state)
            let continuation = try c.skip ? player(c.board, depth: depth - 1, probability: probability, state: c.state) : chance(c.board, depth: depth - 1, probability: probability, state: c.state)
            best = max(best, Double(c.points) * 0.18 + continuation)
        }
        if best == -1e8 {
            if game.mode == .sprint { best = 0 }
            else if let state, state.energy >= state.swapCost { best = -20000 }
        }
        if cache.count < 60_000 { cache[key] = best }; return best
    }
    mutating func chance(_ board: [UInt8], depth: Int, probability: Double, state: ExpeditionState?) throws -> Double {
        try check(); let cells = board.indices.filter { board[$0] == 0 }
        if cells.isEmpty { return try player(board, depth: depth, probability: probability, state: state) }
        let four = state?.fourProbability ?? 0.1, count = Double(cells.count); var total = 0.0
        for index in cells {
            var child = board; child[index] = 1
            total += (1 - four) * (try player(child, depth: depth, probability: probability * (1 - four) / count, state: state))
            child[index] = 2
            total += four * (try player(child, depth: depth, probability: probability * four / count, state: state))
        }
        return total / count
    }
    mutating func run() -> SearchResult {
        let root = game.board.map { $0 == 0 ? UInt8(0) : UInt8(Int.bitWidth - $0.leadingZeroBitCount - 1) }
        var choices: [SearchChoice] = [], best: [MoveValue] = []
        for d in Direction.allCases {
            let r = shift(root, d); if !r.changed { continue }
            let c = effect(root, d, r, game.expedition); choices.append(c)
            let positionValue = game.mode == .sprint && game.remaining == 1 ? 0 : evaluate(r.board)
            best.append(.init(action: .move(d), value: positionValue + Double(c.points) * 0.18))
        }
        do {
            if !choices.isEmpty { for depth in 1...max(1, min(7, game.remaining ?? 7)) {
                iterationDepth = depth
                var iteration: [MoveValue] = []; cache.removeAll(keepingCapacity: true)
                for c in choices {
                    let continuation = try c.skip ? player(c.board, depth: depth - 1, probability: 1, state: c.state) : chance(c.board, depth: depth - 1, probability: 1, state: c.state)
                    iteration.append(.init(action: .move(c.direction), value: Double(c.points) * 0.18 + continuation))
                }
                best = iteration; completedDepth = depth
                if Date.timeIntervalSinceReferenceDate > deadline { break }
            } }
        } catch { /* The last fully completed iteration remains authoritative. */ }
        if let e = game.expedition {
            let needed = ExpeditionState.stages[e.stage].target - (game.score - e.stageScore)
            for i in best.indices {
                guard let c = choices.first(where: { best[i].action == .move($0.direction) }) else { continue }
                if c.points >= needed { best[i].value += 1e7 } else if game.remaining == 1 { best[i].value -= 1e7 }
            }
            if !choices.contains(where: { $0.points >= needed }) {
                var swaps: [(Double, GameAction)] = []; let baseline = evaluate(root), available = game.availablePowers
                for action in available { if case .swap(let a, let b) = action { var board = root; board.swapAt(a, b); let delta = evaluate(board) - baseline; if !Rules.canMove(game.board) || delta > 600 { swaps.append((delta, action)) } } }
                if let swap = swaps.max(by: { $0.0 < $1.0 }) { best.append(.init(action: swap.1, value: (best.map(\.value).max() ?? -1e8) + max(1, swap.0 - 500))) }
                else if available.contains(.freeze) && Rules.empty(game.board) <= 3 { best.append(.init(action: .freeze, value: (best.map(\.value).max() ?? -1e8) + 1)) }
            }
        }
        best.sort { $0.value > $1.value }
        return SearchResult(action: best.first?.action, values: best, depth: completedDepth, nodes: nodes, milliseconds: Int((Date.timeIntervalSinceReferenceDate - start) * 1000))
    }
}
