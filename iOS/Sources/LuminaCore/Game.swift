import Foundation

public enum Ability: String, CaseIterable, Codable, Identifiable, Sendable {
    case combo, battery, gambit, corner, echo, flow, reserve, warp, ice
    public var id: String { rawValue }
    public var title: String { switch self { case .combo: return "连击引擎"; case .battery: return "蓄能核心"; case .gambit: return "豪赌协议"; case .corner: return "角落增幅"; case .echo: return "共鸣回路"; case .flow: return "空间回流"; case .reserve: return "从容节拍"; case .warp: return "折跃透镜"; case .ice: return "凝时晶体" } }
    public var symbol: String { switch self { case .combo: return "arrow.up.forward"; case .battery: return "bolt.fill"; case .gambit: return "diamond"; case .corner: return "arrow.up.left.and.arrow.down.right"; case .echo: return "circle.circle"; case .flow: return "wind"; case .reserve: return "plus"; case .warp: return "arrow.left.arrow.right"; case .ice: return "snowflake" } }
    public func detail(rank: Int) -> String {
        switch self {
        case .combo: return "连续合并，从第二次起每次加成 \(rank == 1 ? 25 : 40)%，最多叠加四层。"
        case .battery: return "每组合并额外获得 \(rank) 点能量，驱动更多主动能力。"
        case .gambit: return "全部得分 ×\(rank == 1 ? "2" : "2.5")；新方块为 4 的概率升至 \(rank == 1 ? 30 : 40)%。"
        case .corner: return "在四角合并时，额外获得该方块 \(50 * rank)% 的分数。"
        case .echo: return "一步合并至少两组，基础分额外增加 \(50 * rank)%。"
        case .flow: return "一步合并至少 \(4 - rank) 组，本步不生成新方块。"
        case .reserve: return "每关增加 \(4 * rank) 步，当前关卡立刻生效。"
        case .warp: return "交换两枚不同数字只消耗 \(rank == 1 ? 4 : 3) 点能量。"
        case .ice: return "凝时阻止接下来 \(2 + rank) 次落子，冷却仍为六步。"
        }
    }
}
public struct ExpeditionStage: Sendable { public let title: String, target: Int, moves: Int }
public struct ExpeditionState: Codable, Equatable, Sendable {
    public static let stages: [ExpeditionStage] = [
        .init(title: "启程", target: 100, moves: 26), .init(title: "蓄势", target: 260, moves: 34),
        .init(title: "回响", target: 520, moves: 42), .init(title: "临界", target: 900, moves: 46),
        .init(title: "跃迁", target: 1400, moves: 52), .init(title: "终章", target: 2200, moves: 60)]
    public var seed: UInt64
    public var stage = 0, phase = Phase.draft, perks: [String: Int] = [:], offers: [Ability] = [.combo, .battery, .gambit]
    public var stageScore = 0, stageStart = 0, energy = 0, streak = 0, freeze = 0, cooldown = 0, cleared = 0
    public init(seed: UInt64) { self.seed = seed }
    public func rank(_ a: Ability) -> Int { perks[a.rawValue, default: 0] }
    public var limit: Int { Self.stages[stage].moves + 4 * rank(.reserve) }
    public var swapCost: Int { [6, 4, 3][rank(.warp)] }
    public var fourProbability: Double { rank(.gambit) > 0 ? 0.2 + 0.1 * Double(rank(.gambit)) : 0.1 }
    public var isValid: Bool {
        (0..<6).contains(stage) && (phase != .clear || stage < 5) && (phase != .draft || stage == 0) &&
        (phase != .won || (stage == 5 && cleared == 6)) &&
        seed <= (1 << 53) && perks.allSatisfy { Ability(rawValue: $0.key) != nil && (1...2).contains($0.value) } &&
        offers.count <= 3 && Set(offers).count == offers.count && offers.allSatisfy { rank($0) < 2 } &&
        (![Phase.draft, .clear].contains(phase) || offers.count == 3) &&
        (0...12).contains(energy) && (0...4).contains(freeze) && (0...6).contains(cooldown) && (0...6).contains(cleared) &&
        (0...1_000_000).contains(streak) && (0...(1 << 60)).contains(stageScore) && (0...10_000_000).contains(stageStart)
    }
    public func reward(board: [Int], gain: Int, merges: [Int]) -> (points: Int, skip: Bool, state: ExpeditionState) {
        var e = self; e.streak = gain > 0 ? streak + 1 : 0
        let multiplier = rank(.combo) > 0 ? 1 + Double(min(4, max(0, e.streak - 1))) * (rank(.combo) == 2 ? 0.4 : 0.25) : 1
        var bonus = Double(merges.filter { [0, 3, 12, 15].contains($0) }.reduce(0) { $0 + board[$1] }) * 0.5 * Double(rank(.corner))
        if merges.count >= 2 { bonus += Double(gain) * 0.5 * Double(rank(.echo)) }
        let gambit = rank(.gambit) == 0 ? 1 : rank(.gambit) == 1 ? 2.0 : 2.5
        let points = Int(((Double(gain) + bonus) * multiplier * gambit).rounded(.toNearestOrEven))
        e.energy = min(12, energy + merges.count * (1 + rank(.battery)))
        let skip = freeze > 0 || (rank(.flow) > 0 && merges.count >= 4 - rank(.flow))
        e.freeze = max(0, freeze - 1); e.cooldown = max(0, cooldown - 1)
        return (points, skip, e)
    }
}
public struct RescueObjective: Codable, Equatable, Sendable {
    public var challenge: String, goal: Int, limit: Int, par: Int
    public var isValid: Bool { challenge.count <= 120 && (2...5).contains(goal) && (1...7).contains(limit) && (1...limit).contains(par) }
}
public struct GameFrame: Codable, Equatable, Sendable {
    public var board: [Int], rng: GameRandom, score: Int, moves: Int, aiMoves: Int, expedition: ExpeditionState?
    public var isValid: Bool { Rules.validBoard(board) && rng.isValid && (0...(1 << 60)).contains(score) && (0...10_000_000).contains(moves) && (0...20_000_000).contains(aiMoves) && (expedition?.isValid ?? true) }
}
public struct Game: Codable, Equatable, Identifiable, Sendable {
    public var id = UUID().uuidString
    public var mode: GameMode, board: [Int], rng: GameRandom
    public var score = 0, moves = 0, aiMoves = 0, undos = 0, assisted = false
    public var history: [GameFrame] = [], future: [GameFrame] = []
    public var expedition: ExpeditionState?, puzzle: PuzzleLevel?, rescue: RescueObjective?, date: String?

    public init(mode: GameMode = .classic, seed: UInt64 = UInt64.random(in: 0..<(1 << 53))) {
        self.mode = mode; board = Array(repeating: 0, count: 16); rng = GameRandom(seed: seed)
        Rules.spawn(&board, rng: &rng, puzzle: mode == .puzzle); Rules.spawn(&board, rng: &rng, puzzle: mode == .puzzle)
        if mode == .expedition { expedition = ExpeditionState(seed: seed) }
    }
    public static func daily(_ date: String = Rules.dateToken()) -> Game { var g = Game(mode: .daily, seed: Rules.dailySeed(date)); g.date = date; return g }
    public static func puzzle(_ level: PuzzleLevel) -> Game { var g = Game(mode: .puzzle, seed: level.seed); g.board = level.board; g.rng = GameRandom(seed: level.seed); g.puzzle = level; return g }
    public static func rescue(_ challenge: RescueChallenge) -> Game {
        var g = Game(mode: .rescue, seed: 0); g.board = challenge.origin.board; g.rng = challenge.origin.rng
        g.rescue = RescueObjective(challenge: challenge.id, goal: challenge.goal, limit: challenge.limit, par: challenge.par); return g
    }
    public var key: String { mode == .daily ? "daily:\(date ?? Rules.dateToken())" : mode.rawValue }
    public var maxTile: Int { board.max() ?? 0 }
    public var remaining: Int? {
        switch mode {
        case .sprint: return max(0, 60 - moves)
        case .puzzle: return max(0, (puzzle?.limit ?? 0) - moves)
        case .rescue: return max(0, (rescue?.limit ?? 0) - moves)
        case .expedition: guard let e = expedition else { return 0 }; return max(0, e.limit - (moves - e.stageStart))
        default: return nil
        }
    }
    public var phase: Phase {
        if mode == .expedition { return expedition?.phase ?? .lost }
        if mode == .puzzle, let puzzle, maxTile >= puzzle.target { return .won }
        if mode == .rescue, let rescue, Rules.empty(board) >= rescue.goal { return .won }
        return remaining == 0 || !Rules.canMove(board) ? .lost : .play
    }
    public var snapshot: GameFrame { GameFrame(board: board, rng: rng, score: score, moves: moves, aiMoves: aiMoves, expedition: expedition) }
    public var isValid: Bool {
        guard !id.isEmpty, id.count <= 100, snapshot.isValid, (0...10_000_000).contains(undos), history.count + future.count <= 100,
              (history + future).allSatisfy({ $0.isValid && (mode == .expedition ? $0.expedition != nil : $0.expedition == nil) }),
              (mode == .expedition || expedition == nil), (mode == .puzzle || puzzle == nil),
              (mode == .rescue || rescue == nil), (mode == .daily || date == nil) else { return false }
        switch mode {
        case .expedition:
            guard let expedition, expedition.isValid else { return false }
            return expedition.stageStart <= moves && expedition.stageScore <= score &&
                (history + future).allSatisfy { frame in
                    guard let state = frame.expedition else { return false }
                    return state.stageStart <= frame.moves && state.stageScore <= frame.score
                }
        case .puzzle: return puzzle?.isValid == true
        case .rescue: return rescue?.isValid == true
        case .daily: return date.map(Rules.validDateToken) ?? false
        default: return true
        }
    }
    public var availablePowers: [GameAction] {
        guard mode == .expedition, let e = expedition, e.phase == .play else { return [] }
        var result: [GameAction] = []
        if e.energy >= 5 && e.cooldown == 0 && e.freeze == 0 && Rules.canMove(board) { result.append(.freeze) }
        if e.energy >= e.swapCost {
            for i in 0..<16 { for j in (i + 1)..<16 where board[i] > 0 && board[j] > 0 && board[i] != board[j] { result.append(.swap(i, j)) } }
        }
        return result
    }
    private mutating func remember() { history.append(snapshot); if history.count > 100 { history.removeFirst() }; future.removeAll() }
    private mutating func apply(_ f: GameFrame) { board = f.board; rng = f.rng; score = f.score; moves = f.moves; aiMoves = f.aiMoves; expedition = f.expedition }
    @discardableResult public mutating func undo() -> Bool { guard let frame = history.popLast() else { return false }; future.append(snapshot); apply(frame); undos += 1; return true }
    @discardableResult public mutating func redo() -> Bool { guard let frame = future.popLast() else { return false }; history.append(snapshot); apply(frame); return true }
    @discardableResult public mutating func choose(_ ability: Ability) -> Bool {
        guard var e = expedition, [.draft, .clear].contains(e.phase), e.offers.contains(ability) else { return false }
        if e.phase == .clear {
            e.stage += 1; e.stageScore = score; e.stageStart = moves
            let ids = board.indices.filter { board[$0] > 0 }
            if ids.count > 1, let smallest = ids.min(by: { board[$0] == board[$1] ? $0 < $1 : board[$0] < board[$1] }) { board[smallest] = 0 }
        }
        e.perks[ability.rawValue] = e.rank(ability) + 1; e.phase = .play; e.offers = []; e.freeze = 0; e.cooldown = 0; e.streak = 0
        expedition = e; history = []; future = []; refresh(); return true
    }
    @discardableResult public mutating func perform(_ action: GameAction, assisted isAssisted: Bool = false) -> SlideResult? {
        guard phase == .play else { return nil }
        switch action {
        case .move(let direction):
            var result = Rules.slide(board, direction); guard result.changed else { return nil }
            remember(); board = result.board; var skip = false
            if let e = expedition, mode == .expedition { let reward = e.reward(board: board, gain: result.gain, merges: result.merges); result.gain = reward.points; skip = reward.skip; expedition = reward.state }
            if !skip { result.spawn = Rules.spawn(&board, rng: &rng, puzzle: mode == .puzzle, fourProbability: expedition?.fourProbability ?? 0.1) }
            score += result.gain; moves += 1; if isAssisted { assisted = true; aiMoves += 1 }; refresh(); result.board = board; return result
        default:
            guard availablePowers.contains(action), var e = expedition else { return nil }
            remember(); var tracks = board.indices.filter { board[$0] > 0 }.map { MotionTrack(source: $0, target: $0, value: board[$0]) }
            switch action {
            case .freeze: e.energy -= 5; e.freeze = 2 + e.rank(.ice); e.cooldown = 6
            case .swap(let a, let b): board.swapAt(a, b); for i in tracks.indices { if tracks[i].source == a { tracks[i].target = b }; if tracks[i].source == b { tracks[i].target = a } }; e.energy -= e.swapCost
            default: break
            }
            expedition = e; if isAssisted { assisted = true; aiMoves += 1 }; refresh()
            return SlideResult(board: board, gain: 0, tracks: tracks, merges: [], changed: true)
        }
    }
    private mutating func refresh() {
        guard var e = expedition, e.phase == .play else { return }
        if score - e.stageScore >= ExpeditionState.stages[e.stage].target {
            e.cleared = e.stage + 1; e.phase = e.stage == 5 ? .won : .clear
            if e.phase == .clear {
                var pool = Ability.allCases.filter { e.rank($0) < 2 }
                var r = GameRandom(seed: e.seed &+ UInt64(e.stage + 1) &* 0x9e3779b9)
                for i in stride(from: pool.count - 1, through: 1, by: -1) { pool.swapAt(i, r.choice(i + 1)) }
                e.offers = Array(pool.prefix(3))
            }
        } else if remaining == 0 || (!Rules.canMove(board) && availablePowers.isEmpty) { e.phase = .lost }
        expedition = e
    }
}
