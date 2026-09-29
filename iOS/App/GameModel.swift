import SwiftUI
import LuminaCore
#if os(iOS)
import UIKit
#endif

enum AppSheet: String, Identifiable { case modes, settings, puzzles, rescues, replay; var id: String { rawValue } }
struct TileSprite: Identifiable { var id = UUID(); var cell: Int, value: Int; var scale = 1.0 }

@MainActor final class GameModel: ObservableObject {
    @Published private(set) var game = Game()
    @Published var settings = Settings()
    @Published private(set) var book = SaveBook()
    @Published private(set) var tiles: [TileSprite] = []
    @Published private(set) var ready = false
    @Published private(set) var busy = false
    @Published private(set) var thinking = false
    @Published private(set) var autoPlay = false
    @Published private(set) var extracting = false
    @Published var sheet: AppSheet? { didSet { if sheet != nil { pauseGameplay() } } }
    @Published var notice: String? { didSet { if notice != nil { pauseGameplay() } } }
    @Published var hint: SearchResult?
    @Published var swapping = false
    @Published var swapCell: Int?
    @Published var confirmRestart = false { didSet { if confirmRestart { pauseGameplay() } } }
    @Published private(set) var recovered: RescueChallenge?
    private(set) var levels: [PuzzleLevel] = [], practices: [RescueChallenge] = []
    private let repository: SaveRepository
    private let feedback = GameFeedback()
    private var loaded = false, revision = 0, generation = 0
    private var queued: [Direction] = []
    private var aiTask: Task<Void, Never>?, animationTask: Task<Void, Never>?, saveTask: Task<Void, Never>?
    private var worker: Task<SearchResult, Never>?, rescueWorker: Task<RescueExtraction, Never>?
    var motionReduced = false
    @Published private var isActive = true
    var acceptsGameplayInput: Bool { ready && isActive && sheet == nil && notice == nil && !confirmRestart }
    init(repository: SaveRepository = SaveRepository()) { self.repository = repository }
    var currentChallenge: RescueChallenge? { (book.rescues + practices).first { $0.id == game.rescue?.challenge } }
    var record: Record { book.records[game.mode.rawValue] ?? Record() }
    var best: Int { game.assisted ? record.assisted : record.manual }
    var objective: String {
        switch game.mode {
        case .classic: return game.maxTile >= 2048 ? "继续探索更大的数字" : "滑动，让相同数字相遇"
        case .daily: return "\(game.date ?? "") · 相同起点"
        case .sprint: return "六十步内，积累尽可能高的分数"
        case .puzzle: return "\(game.puzzle?.title ?? "谜题") · 合成 \(game.puzzle?.target ?? 0)"
        case .rescue: return "在 \(game.rescue?.limit ?? 6) 步内，腾出 \(game.rescue?.goal ?? 3) 个空位"
        case .expedition: guard let e = game.expedition else { return "" }; return "第 \(e.stage + 1) / 6 关 · \(ExpeditionState.stages[e.stage].title)"
        }
    }
    func load() async {
        guard !loaded else { return }; loaded = true
        do { levels = try GameContent.levels(); practices = try GameContent.practice() }
        catch { loaded = false; notice = "内置关卡读取失败：\(error.localizedDescription)"; return }
        let saved = await repository.load(); book = saved.book; settings = book.settings
        game = book.sessions["classic"] ?? Game(); notice = saved.message
        syncTiles(); ready = true
    }
    private func syncTiles() { tiles = game.board.indices.filter { game.board[$0] > 0 }.map { TileSprite(cell: $0, value: game.board[$0]) } }
    func stopAI() {
        generation += 1; autoPlay = false; thinking = false
        aiTask?.cancel(); worker?.cancel(); aiTask = nil; worker = nil
        rescueWorker?.cancel(); rescueWorker = nil; extracting = false
    }
    private func settle() {
        animationTask?.cancel(); animationTask = nil; busy = false; queued.removeAll(); syncTiles(); swapping = false; swapCell = nil
    }
    private func pauseGameplay() { stopAI(); settle() }
    func resume() { isActive = true }
    func suspend() {
        isActive = false; pauseGameplay(); persist(immediate: true)
    }
    func open(_ destination: AppSheet) { sheet = destination }
    func switchMode(_ mode: GameMode) {
        stopAI(); settle(); book.remember(game)
        let key = mode == .daily ? "daily:\(Rules.dateToken())" : mode.rawValue
        if let saved = book.sessions[key] { game = saved }
        else {
            switch mode {
            case .daily: game = .daily()
            case .puzzle: guard let first = levels.first else { return }; game = .puzzle(first)
            case .rescue: guard let first = (book.rescues + practices).first else { return }; game = .rescue(first)
            default: game = Game(mode: mode)
            }
        }
        hint = nil; recovered = nil; sheet = nil; syncTiles(); persist()
    }
    func start(_ level: PuzzleLevel) { guard level.isValid else { return }; pauseGameplay(); book.remember(game); game = .puzzle(level); hint = nil; recovered = nil; sheet = nil; syncTiles(); persist() }
    func start(_ challenge: RescueChallenge) {
        guard challenge.isValid else { return }; pauseGameplay(); book.remember(game)
        if !practices.contains(where: { $0.id == challenge.id }) { book.archive(challenge, keeping: challenge.id) }
        game = .rescue(challenge); hint = nil; recovered = nil; sheet = nil; syncTiles(); persist()
    }
    func restart() {
        stopAI(); settle(); let old = game; book.remember(old)
        switch old.mode {
        case .daily: game = .daily(old.date ?? Rules.dateToken())
        case .puzzle: if let level = old.puzzle { game = .puzzle(level) }
        case .rescue: if let challenge = currentChallenge { game = .rescue(challenge) }
        default: game = Game(mode: old.mode)
        }
        hint = nil; recovered = nil; syncTiles(); persist()
    }
    func choose(_ ability: Ability) {
        guard acceptsGameplayInput, game.expedition?.offers.contains(ability) == true else { return }
        pauseGameplay(); guard game.choose(ability) else { return }
        syncTiles(); persist(); feedback.play(merge: true, settings: settings)
    }
    func move(_ direction: Direction) {
        guard acceptsGameplayInput else { return }; stopAI(); swapping = false; swapCell = nil
        if busy { if queued.count < 2 { queued.append(direction) }; return }
        perform(.move(direction))
    }
    func usePower(_ action: GameAction) { guard acceptsGameplayInput, !busy else { return }; stopAI(); perform(action) }
    func tapTile(_ cell: Int) {
        guard acceptsGameplayInput, swapping, !busy, game.board.indices.contains(cell), game.board[cell] > 0 else { return }
        guard let first = swapCell else { swapCell = cell; return }
        if first == cell { swapCell = nil; return }
        let action = GameAction.swap(min(first, cell), max(first, cell))
        guard game.availablePowers.contains(action) else { notice = "请选择两枚不同数字的方块。"; return }
        swapping = false; swapCell = nil; usePower(action)
    }
    private func perform(_ action: GameAction, byAI: Bool = false) {
        guard !busy else { return }
        guard let result = game.perform(action, assisted: byAI) else { finishMove(); return }
        hint = nil; recovered = nil; feedback.play(merge: result.gain > 0, settings: settings); persist()
        guard !motionReduced && !settings.reduceMotion else { syncTiles(); finishMove(); return }
        busy = true
        let before = Dictionary(uniqueKeysWithValues: tiles.map { ($0.cell, $0) })
        withAnimation(.spring(response: 0.18, dampingFraction: 0.9)) {
            tiles = result.tracks.compactMap { track in guard var tile = before[track.source] else { return nil }; tile.cell = track.target; return tile }
        }
        animationTask = Task { [weak self] in
            do { try await Task.sleep(nanoseconds: 150_000_000) } catch { return }
            guard let self, !Task.isCancelled else { return }
            let moved = self.tiles
            var settled: [TileSprite] = []
            for cell in self.game.board.indices where self.game.board[cell] > 0 {
                var tile = moved.first { $0.cell == cell } ?? TileSprite(cell: cell, value: self.game.board[cell], scale: 0.35)
                tile.value = self.game.board[cell]
                if result.merges.contains(cell) { tile.scale = 1.10 }
                settled.append(tile)
            }
            self.tiles = settled
            // A separate transaction preserves spawn/merge interpolation on stable tile identities.
            await Task.yield()
            guard !Task.isCancelled else { return }
            withAnimation(.spring(response: 0.23, dampingFraction: 0.66)) { for i in self.tiles.indices { self.tiles[i].scale = 1 } }
            self.busy = false; self.finishMove()
        }
    }
    private func finishMove() {
        guard acceptsGameplayInput else { queued.removeAll(); stopAI(); return }
        if game.phase != .play { autoPlay = false; queued.removeAll(); return }
        if !queued.isEmpty { let next = queued.removeFirst(); perform(.move(next)) }
        else if autoPlay { scheduleAI() }
    }
    func undo() { guard acceptsGameplayInput else { return }; pauseGameplay(); guard game.undo() else { return }; hint = nil; recovered = nil; syncTiles(); persist() }
    func redo() { guard acceptsGameplayInput else { return }; pauseGameplay(); guard game.redo() else { return }; hint = nil; syncTiles(); persist() }
    func askHint() {
        guard acceptsGameplayInput, !busy, game.phase == .play else { return }; stopAI(); game.assisted = true; persist(); runSearch(automatically: false)
    }
    func followHint() { guard acceptsGameplayInput, let action = hint?.action, !busy else { return }; stopAI(); perform(action, byAI: true) }
    func toggleAuto() {
        if autoPlay { stopAI(); return }
        guard acceptsGameplayInput, !busy, game.phase == .play else { return }; stopAI(); game.assisted = true; autoPlay = true; persist(); runSearch(automatically: true)
    }
    private func scheduleAI() {
        let stamp = generation
        aiTask = Task { [weak self] in
            guard let self else { return }
            do { try await Task.sleep(nanoseconds: UInt64(max(0.04, self.settings.autoplayInterval - 0.15) * 1e9)) } catch { return }
            guard self.autoPlay, self.generation == stamp else { return }; self.runSearch(automatically: true)
        }
    }
    private func runSearch(automatically: Bool) {
        guard game.phase == .play else { stopAI(); return }
        let state = game, stamp = generation, budget = settings.intelligence.budget
        thinking = true
        let task = Task.detached(priority: .userInitiated) { Solver.solve(state, budget: budget) }; worker = task
        aiTask = Task { [weak self] in
            let result = await task.value
            guard let self, !Task.isCancelled, self.generation == stamp, self.game == state else { return }
            self.thinking = false; self.worker = nil
            if automatically, let action = result.action, self.autoPlay { self.perform(action, byAI: true) }
            else {
                self.autoPlay = false; self.hint = result
                if result.action == nil { self.notice = result.exact ? (result.complete ? "在剩余步数内没有找到解法，可以撤回一步再试。" : "这次搜索未完成，可以重试或先撤回。") : "当前没有可执行的动作。" }
            }
        }
    }
    func extractRescue() {
        guard acceptsGameplayInput, !extracting else { return }; stopAI(); extracting = true
        let state = game, stamp = generation
        let task = Task.detached(priority: .userInitiated) { Solver.extract(state) }; rescueWorker = task
        Task { [weak self] in
            let result = await task.value
            guard let self, self.generation == stamp, self.game.id == state.id, !task.isCancelled else { return }
            self.extracting = false; self.rescueWorker = nil
            if let challenge = result.challenge {
                self.book.archive(challenge, keeping: self.book.sessions["rescue"]?.rescue?.challenge)
                self.recovered = challenge; self.persist()
            } else { self.notice = result.timedOut ? "搜索时间已到，暂未确认转机。可以重试，也可以玩精选残局。" : "这局最后十步没有找到符合条件的转机。精选残局里还有其他挑战。" }
        }
    }
    func showReplay() {
        guard currentChallenge != nil else { return }
        if game.phase != .won { game.assisted = true; persist() }; open(.replay)
    }
    func settingsChanged() { stopAI(); persist() }
    func exportData() throws -> Data { book.settings = settings; book.remember(game); return try book.encoded() }
    func importData(_ data: Data) throws {
        let imported = try SaveBook.decode(data)
        stopAI(); settle(); book = imported; settings = imported.settings; game = imported.sessions["classic"] ?? Game()
        hint = nil; recovered = nil; syncTiles(); persist(immediate: true); notice = "进度已导入。各模式可以继续游玩。"
    }
    private func persist(immediate: Bool = false) {
        guard ready else { return }; book.settings = settings; book.remember(game)
        revision += 1
        if immediate { saveTask?.cancel(); saveTask = nil }
        guard saveTask == nil else { return }
        #if os(iOS)
        let backgroundSave = immediate ? BackgroundSaveLease() : nil
        #endif
        saveTask = Task { [weak self] in
            #if os(iOS)
            defer { backgroundSave?.finish() }
            #endif
            guard let self else { return }
            if !immediate { do { try await Task.sleep(nanoseconds: 280_000_000) } catch { return } }
            guard !Task.isCancelled else { return }
            // Coalesce to the newest state without postponing the scheduled write.
            let snapshot = self.book, number = self.revision
            self.saveTask = nil
            do { try await self.repository.save(snapshot, revision: number) }
            catch { self.notice = "保存失败：\(error.localizedDescription)" }
        }
    }
}

#if os(iOS)
@MainActor private final class BackgroundSaveLease {
    private var identifier = UIBackgroundTaskIdentifier.invalid
    init() {
        identifier = UIApplication.shared.beginBackgroundTask(withName: "Save LUMINA progress") { [weak self] in self?.finish() }
    }
    func finish() {
        guard identifier != .invalid else { return }
        let task = identifier; identifier = .invalid
        UIApplication.shared.endBackgroundTask(task)
    }
}
#endif
