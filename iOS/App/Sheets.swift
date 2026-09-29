import SwiftUI
import UniformTypeIdentifiers
import LuminaCore

struct SheetHost: View {
    @ObservedObject var model: GameModel
    let sheet: AppSheet
    @Environment(\.dismiss) private var dismiss
    @Environment(\.colorScheme) private var scheme
    var body: some View {
        NavigationStack {
            Group {
                switch sheet {
                case .modes: modes
                case .settings: SettingsView(model: model)
                case .puzzles: puzzles
                case .rescues: rescues
                case .replay: if let challenge = model.currentChallenge { ReplayView(challenge: challenge) } else { Text("请先选择一个残局。") }
                }
            }.navigationTitle(title).inlineNavigationTitle()
                .toolbar { ToolbarItem(placement: .confirmationAction) { Button("完成") { dismiss() } } }
                .tint(Atelier.accent).foregroundStyle(scheme == .dark ? Color(hex: 0xEEF3F0) : Color(hex: 0x28352F))
        }
    }
    private var title: String { switch sheet { case .modes: return "选择玩法"; case .settings: return "设置"; case .puzzles: return "谜题剧场"; case .rescues: return "残局档案"; case .replay: return "对照复盘" } }
    private var modes: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 14) {
                Text("今天，想怎么玩？").font(.system(size: 29, weight: .semibold, design: .rounded)).tracking(-0.7).padding(.top, 12)
                Text("每种玩法分别保存进度，随时回来。 ").font(.subheadline).foregroundStyle(.secondary).padding(.bottom, 10)
                ForEach(GameMode.allCases) { mode in
                    Button { model.switchMode(mode) } label: {
                        HStack(spacing: 18) {
                            Image(systemName: mode.symbol).font(.system(size: mode == .classic ? 28 : 23, weight: .light)).foregroundStyle(Atelier.accent).frame(width: 42)
                            VStack(alignment: .leading, spacing: 7) { Text(mode.title).font(.system(size: mode == .classic ? 23 : 18, weight: .semibold)); Text(mode.subtitle).font(.system(size: 12)).foregroundStyle(.secondary).fixedSize(horizontal: false, vertical: true) }
                            Spacer(minLength: 0)
                            Image(systemName: model.game.mode == mode ? "checkmark.circle.fill" : "arrow.up.right").foregroundStyle(Atelier.accent.opacity(0.7)).font(.system(size: 16))
                        }.padding(.horizontal, 20).padding(.vertical, mode == .classic ? 30 : 23).frame(maxWidth: .infinity, alignment: .leading)
                            .background(mode == .classic ? Atelier.accent.opacity(0.095) : Color.primary.opacity(0.03), in: RoundedRectangle(cornerRadius: 25, style: .continuous))
                    }.buttonStyle(.plain)
                }
            }.padding(24).frame(maxWidth: 600).frame(maxWidth: .infinity)
        }
    }
    private var puzzles: some View {
        ScrollView {
            LazyVGrid(columns: [GridItem(.adaptive(minimum: 148), spacing: 14)], spacing: 14) {
                ForEach(model.levels) { level in
                    Button { model.start(level) } label: {
                        VStack(alignment: .leading, spacing: 12) {
                            HStack { Text(String(format: "%02d", level.id + 1)).font(.system(size: 30, weight: .light, design: .rounded)).foregroundStyle(Atelier.accent); Spacer(); Text(String(repeating: "★", count: model.book.stars[String(level.id)] ?? 0)).font(.caption).foregroundStyle(Color(hex: 0xAE9256)) }
                            Text(level.title).font(.headline)
                            Text("合成 \(level.target) · \(level.limit) 步").font(.caption).foregroundStyle(.secondary)
                            Text(level.note).font(.caption).foregroundStyle(.secondary).frame(minHeight: 34, alignment: .top)
                        }.frame(maxWidth: .infinity, alignment: .leading).padding(18).background(.primary.opacity(0.035), in: RoundedRectangle(cornerRadius: 23))
                    }.buttonStyle(.plain)
                }
            }.padding(24).frame(maxWidth: 800).frame(maxWidth: .infinity)
            Text("不使用提示、在标准步数内完成，且没有撤销，可获得三星。辅助完成记一星。").font(.caption).foregroundStyle(.secondary).padding(.horizontal, 28).padding(.bottom, 30)
        }
    }
    private var rescues: some View {
        List {
            if !model.book.rescues.isEmpty {
                Section("从你的对局中找到") { ForEach(model.book.rescues) { challenge in rescueRow(challenge) } }
            }
            Section { ForEach(model.practices) { challenge in rescueRow(challenge) } } header: { Text("精选残局") } footer: { Text("经典、每日或冲刺在棋盘无路可走时，可以寻找最后十步里的转机。原局完整保留；这里的挑战独立进行。") }
        }
    }
    private func rescueRow(_ challenge: RescueChallenge) -> some View {
        Button { model.start(challenge) } label: {
            HStack(spacing: 16) {
                Image(systemName: challenge.practice ? "square.stack.3d.up" : "arrow.uturn.backward").font(.title2).foregroundStyle(Atelier.accent).frame(width: 32)
                VStack(alignment: .leading, spacing: 5) { Text(challenge.title).font(.headline).foregroundStyle(.primary); Text("\(challenge.limit) 步内 · 腾出 \(challenge.goal) 个空位").font(.caption).foregroundStyle(.secondary) }
                Spacer(); Image(systemName: "chevron.right").font(.caption).foregroundStyle(.tertiary)
            }.padding(.vertical, 12)
        }
    }
}

struct ProgressDocument: FileDocument {
    static var readableContentTypes: [UTType] { [.json] }
    var data: Data
    init(data: Data) { self.data = data }
    init(configuration: ReadConfiguration) throws { guard let data = configuration.file.regularFileContents else { throw SaveError.invalid }; _ = try SaveBook.decode(data); self.data = data }
    func fileWrapper(configuration: WriteConfiguration) throws -> FileWrapper { FileWrapper(regularFileWithContents: data) }
}
struct SettingsView: View {
    @ObservedObject var model: GameModel
    @State private var importing = false
    @State private var exporting = false
    @State private var confirmImport = false
    @State private var pendingData: Data?
    @State private var error: String?
    @State private var document: ProgressDocument?
    var body: some View {
        Form {
            Section("感官") {
                Picker("外观", selection: $model.settings.appearance) { Text("跟随系统").tag(Appearance.system); Text("浅色").tag(Appearance.light); Text("深色").tag(Appearance.dark) }
                Toggle("声音", isOn: $model.settings.sound)
                Toggle("轻触反馈", isOn: $model.settings.haptics)
                Toggle("减少动态效果", isOn: $model.settings.reduceMotion)
            }
            Section { Picker("思考强度", selection: $model.settings.intelligence) { ForEach(Intelligence.allCases, id: \.self) { Text($0.title).tag($0) } }
                VStack(alignment: .leading, spacing: 8) { HStack { Text("自动游玩节奏"); Spacer(); Text(model.settings.autoplayInterval < 0.4 ? "轻快" : model.settings.autoplayInterval < 0.8 ? "从容" : "慢慢看").foregroundStyle(.secondary) }; Slider(value: $model.settings.autoplayInterval, in: 0.2...1.5, step: 0.05).accessibilityLabel("自动游玩间隔") }
            } header: { Text("智能助手") } footer: { Text("经典玩法会比较随机落子的后续局面；谜题和残局使用确定性搜索。开启提示、自动游玩，或提前查看解法，会记为辅助局。深度思考会消耗更多电量。") }
            Section("个人记录") {
                ForEach(GameMode.allCases) { mode in
                    HStack { Text(mode.title); Spacer(); VStack(alignment: .trailing, spacing: 3) { Text((model.book.records[mode.rawValue]?.manual ?? 0).formatted()).monospacedDigit(); Text("辅助 \((model.book.records[mode.rawValue]?.assisted ?? 0).formatted())").font(.caption).foregroundStyle(.secondary) } }
                }
            }
            Section {
                Button("导出进度备份", systemImage: "square.and.arrow.up") { do { document = ProgressDocument(data: try model.exportData()); exporting = true } catch { self.error = error.localizedDescription } }
                Button("导入进度备份", systemImage: "square.and.arrow.down") { importing = true }
            } header: { Text("进度") } footer: { Text("进度保存在本机。可通过“文件”或 AirDrop 把原生版 JSON 备份带到另一台设备；目前不自动进行 iCloud 同步。") }
            Section {
                LabeledContent("版本", value: "1.0.1 · Native")
                Text("离线游玩。无需登录，没有广告。\n为 iPhone 与 iPad 设计。").font(.subheadline).foregroundStyle(.secondary)
            }
        }.onChange(of: model.settings) { _ in model.settingsChanged() }
            .fileExporter(isPresented: $exporting, document: document, contentType: .json, defaultFilename: "LUMINA-\(Rules.dateToken()).json") { result in if case .failure(let e) = result { error = e.localizedDescription } }
            .fileImporter(isPresented: $importing, allowedContentTypes: [.json]) { result in
                do { let url = try result.get(); let granted = url.startAccessingSecurityScopedResource(); defer { if granted { url.stopAccessingSecurityScopedResource() } }; let data = try Data(contentsOf: url, options: .mappedIfSafe); _ = try SaveBook.decode(data); pendingData = data; confirmImport = true }
                catch { self.error = error.localizedDescription }
            }
            .confirmationDialog("用备份替换本机进度？", isPresented: $confirmImport, titleVisibility: .visible) {
                Button("导入备份", role: .destructive) { guard let data = pendingData else { return }; do { try model.importData(data); model.sheet = nil } catch { self.error = error.localizedDescription }; pendingData = nil }
                Button("取消", role: .cancel) { pendingData = nil }
            } message: { Text("会替换各模式的进度、记录和设置。建议先导出当前进度。") }
            .alert("无法完成", isPresented: Binding(get: { error != nil }, set: { if !$0 { error = nil } })) { Button("知道了") { error = nil } } message: { Text(error ?? "") }
    }
}

struct ReplayView: View {
    let challenge: RescueChallenge
    @State private var alternative = true
    @State private var step = 0
    var body: some View {
        let timeline = ReplayTimeline(challenge: challenge, alternative: alternative)
        let position = timeline.clampedIndex(step)
        ScrollView {
            VStack(alignment: .leading, spacing: 22) {
                Text("同一个起点，另一种可能。").font(.system(size: 25, weight: .semibold, design: .rounded)).padding(.top, 8)
                Picker("路线", selection: Binding(get: { alternative }, set: { alternative = $0; step = 0 })) { Text("原来的路线").tag(false); Text("转机路线").tag(true) }.pickerStyle(.segmented)
                StaticBoard(board: timeline.board(at: position))
                HStack { Text(timeline.caption(at: position)).font(.headline); Spacer(); Text("\(position) / \(timeline.lastIndex)").font(.subheadline.monospacedDigit()).foregroundStyle(.secondary) }
                HStack { Button("上一步", systemImage: "arrow.left") { step = max(0, position - 1) }.disabled(position == 0); Spacer(); Button("下一步", systemImage: "arrow.right") { step = min(timeline.lastIndex, position + 1) }.disabled(position == timeline.lastIndex) }.buttonStyle(GameButtonStyle())
                Text(alternative ? "逐步重放已验证的解法，落子位置与挑战完全一致。" : "这是原局从该位置走到结束的真实记录。").font(.subheadline).foregroundStyle(.secondary)
                Text("过关前查看转机路线，会将本次挑战记为辅助局。").font(.caption).foregroundStyle(.tertiary)
            }.padding(24).frame(maxWidth: 520).frame(maxWidth: .infinity)
        }
    }
}

struct ReplayTimeline {
    private let frames: [[Int]], directions: [Direction?]
    init(challenge: RescueChallenge, alternative: Bool) {
        if alternative {
            var board = challenge.origin.board, rng = challenge.origin.rng, result = [challenge.origin.board]
            for direction in challenge.solution { board = Rules.slide(board, direction).board; Rules.spawn(&board, rng: &rng); result.append(board) }
            frames = result; directions = [nil] + challenge.solution.map { Optional($0) }
        } else {
            frames = [challenge.origin.board] + challenge.original.map(\.board)
            directions = [nil] + challenge.original.map(\.direction)
        }
    }
    var lastIndex: Int { frames.count - 1 }
    func clampedIndex(_ proposed: Int) -> Int { min(max(0, proposed), lastIndex) }
    func board(at step: Int) -> [Int] { frames[clampedIndex(step)] }
    func caption(at step: Int) -> String {
        let index = clampedIndex(step)
        return index == 0 ? "起始局面" : "第 \(index) 步 · \(directions[index]?.title ?? "落子")"
    }
}

extension View {
    @ViewBuilder func inlineNavigationTitle() -> some View {
        #if os(iOS)
        self.navigationBarTitleDisplayMode(.inline)
        #else
        self
        #endif
    }
}
