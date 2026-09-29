import Foundation

public enum Appearance: String, Codable, CaseIterable, Sendable { case system, light, dark }
public enum Intelligence: String, Codable, CaseIterable, Sendable {
    case balanced, deep
    public var budget: Double { self == .deep ? 0.55 : 0.14 }
    public var title: String { self == .deep ? "深度思考" : "灵敏" }
}
public struct Settings: Codable, Equatable, Sendable {
    public var appearance = Appearance.system
    public var intelligence = Intelligence.balanced
    public var sound = true, haptics = true, reduceMotion = false
    public var autoplayInterval = 0.42
    public init() {}
    public var isValid: Bool { autoplayInterval.isFinite && (0.2...1.5).contains(autoplayInterval) }
}
public struct Record: Codable, Equatable, Sendable {
    public var manual = 0, assisted = 0
    public init() {}
}
public struct SaveBook: Codable, Equatable, Sendable {
    public var version = 1, settings = Settings()
    public var sessions: [String: Game] = [:], records: [String: Record] = [:]
    public var stars: [String: Int] = [:], rescues: [RescueChallenge] = []
    public init() {}
    public var isValid: Bool {
        guard version == 1 && settings.isValid && sessions.count <= 16 && records.count <= 100 && stars.count <= 32 &&
        sessions.allSatisfy { $0.key == $0.value.key && $0.value.isValid } &&
        records.allSatisfy { $0.key.count <= 120 && (0...(1 << 60)).contains($0.value.manual) && (0...(1 << 60)).contains($0.value.assisted) } &&
        stars.allSatisfy { $0.key.count <= 120 && (0...3).contains($0.value) } &&
        rescues.count <= 6 && Set(rescues.map(\.id)).count == rescues.count && rescues.allSatisfy(\.isValid) else { return false }
        if let objective = sessions["rescue"]?.rescue {
            guard let challenge = (rescues + ((try? GameContent.practice()) ?? [])).first(where: { $0.id == objective.challenge }) else { return false }
            return objective.goal == challenge.goal && objective.limit == challenge.limit && objective.par == challenge.par
        }
        return true
    }
    public mutating func remember(_ game: Game) {
        sessions[game.key] = game
        let daily = sessions.keys.filter { $0.hasPrefix("daily:") }.sorted()
        for key in daily.dropLast(7) { sessions.removeValue(forKey: key) }
        var record = records[game.mode.rawValue] ?? Record()
        if game.assisted { record.assisted = max(record.assisted, game.score) } else { record.manual = max(record.manual, game.score) }
        records[game.mode.rawValue] = record
        if game.mode == .puzzle, game.phase == .won, let level = game.puzzle {
            let value = game.assisted ? 1 : game.moves <= level.par && game.undos == 0 ? 3 : 2
            stars[String(level.id)] = max(stars[String(level.id)] ?? 0, value)
        }
    }
    public mutating func archive(_ challenge: RescueChallenge, keeping active: String?) {
        guard challenge.isValid, !rescues.contains(where: { $0.id == challenge.id }) else { return }
        rescues.insert(challenge, at: 0)
        while rescues.count > 6 {
            if let i = rescues.indices.reversed().first(where: { rescues[$0].id != active && rescues[$0].id != challenge.id }) { rescues.remove(at: i) }
            else { break }
        }
    }
    public static func decode(_ data: Data) throws -> SaveBook {
        guard data.count <= 24_000_000 else { throw SaveError.tooLarge }
        let book = try JSONDecoder().decode(Self.self, from: data)
        guard book.isValid else { throw SaveError.invalid }
        return book
    }
    public func encoded() throws -> Data {
        guard isValid else { throw SaveError.invalid }
        let encoder = JSONEncoder(); encoder.outputFormatting = [.sortedKeys]
        let data = try encoder.encode(self)
        guard data.count <= 24_000_000 else { throw SaveError.tooLarge }
        return data
    }
}
public enum SaveError: LocalizedError {
    case invalid, tooLarge
    public var errorDescription: String? { self == .invalid ? "存档格式不正确，当前进度已保留。" : "存档文件超过 24 MB，无法导入。" }
}
public struct LoadResult: Sendable { public var book: SaveBook, message: String? }
public actor SaveRepository {
    private let directory: URL
    private var lastRevision = -1
    public init(directory: URL? = nil) {
        self.directory = directory ?? FileManager.default.urls(for: .applicationSupportDirectory, in: .userDomainMask)[0].appendingPathComponent("Lumina", isDirectory: true)
    }
    private var primary: URL { directory.appendingPathComponent("progress.json") }
    private var backup: URL { directory.appendingPathComponent("progress-backup.json") }
    public func load() -> LoadResult {
        do { return .init(book: try SaveBook.decode(Data(contentsOf: primary, options: .mappedIfSafe)), message: nil) }
        catch {
            if let data = try? Data(contentsOf: backup, options: .mappedIfSafe), let book = try? SaveBook.decode(data) {
                return .init(book: book, message: "已从备用存档恢复进度。")
            }
            let existed = FileManager.default.fileExists(atPath: primary.path) || FileManager.default.fileExists(atPath: backup.path)
            return .init(book: SaveBook(), message: existed ? "旧存档无法读取，已保留原文件。可以在设置中导入备份。" : nil)
        }
    }
    public func save(_ book: SaveBook, revision: Int) throws {
        guard revision > lastRevision else { return }
        let data = try book.encoded()
        try FileManager.default.createDirectory(at: directory, withIntermediateDirectories: true)
        if let old = try? Data(contentsOf: primary) {
            if (try? SaveBook.decode(old)) != nil { try old.write(to: backup, options: .atomic) }
            else {
                let recovery = directory.appendingPathComponent("progress-unreadable-\(UUID().uuidString).json")
                try old.write(to: recovery, options: .atomic)
            }
        }
        try data.write(to: primary, options: .atomic); lastRevision = revision
    }
}
