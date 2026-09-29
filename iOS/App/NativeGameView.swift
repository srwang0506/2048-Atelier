import SwiftUI
import LuminaCore

struct NativeGameView: View {
    @ObservedObject var model: GameModel
    @Environment(\.colorScheme) private var scheme
    @Environment(\.accessibilityReduceMotion) private var reduceMotion
    @Environment(\.layoutSnapshot) private var snapshot
    var body: some View {
        GeometryReader { geo in
            let wide = geo.size.width >= 700 || geo.size.width > geo.size.height * 1.35
            let boardSize = max(200, min(520, wide ? min((geo.size.width - 72) * 0.57, geo.size.height - 40) : geo.size.width - 40))
            ZStack {
                LinearGradient(colors: scheme == .dark ? [Color(hex: 0x131C20), Color(hex: 0x19232A)] : [Color(hex: 0xFAFAF7), Color(hex: 0xEFF3F1)], startPoint: .topLeading, endPoint: .bottomTrailing).ignoresSafeArea()
                if model.ready {
                    if wide {
                        HStack(spacing: 36) {
                            playfield(size: boardSize)
                            GameScroll { VStack(alignment: .leading, spacing: 22) { header; scores; controls; context; footer }.padding(.vertical, 10) }.frame(maxWidth: 390, maxHeight: boardSize)
                        }.padding(.horizontal, 28).frame(maxWidth: 1040).frame(maxWidth: .infinity, maxHeight: .infinity)
                    } else {
                        GameScroll {
                            VStack(spacing: 24) { header; scores; playfield(size: boardSize); controls; context; footer }
                                .frame(maxWidth: 520).padding(.horizontal, 20).padding(.top, 18).padding(.bottom, 24).frame(maxWidth: .infinity)
                        }.scrollIndicators(.hidden)
                    }
                } else { ProgressView("准备棋盘…").tint(Atelier.accent) }
            }
        }.tint(Atelier.accent).foregroundStyle(scheme == .dark ? Color(hex: 0xEEF3F0) : Color(hex: 0x28352F))
            .onAppear { model.motionReduced = reduceMotion }
            .onChange(of: reduceMotion) { model.motionReduced = $0 }
            .sheet(item: $model.sheet) { sheet in
                SheetHost(model: model, sheet: sheet).presentationDetents([.large]).presentationDragIndicator(.visible)
            }
            .alert("LUMINA", isPresented: Binding(get: { model.notice != nil }, set: { if !$0 { model.notice = nil } })) { Button("知道了", role: .cancel) { model.notice = nil } } message: { Text(model.notice ?? "") }
            .confirmationDialog("重新开始这一局？", isPresented: $model.confirmRestart, titleVisibility: .visible) {
                Button("重新开始", role: .destructive) { model.restart() }; Button("继续这一局", role: .cancel) {}
            } message: { Text(model.game.mode == .daily ? "今天的初始棋盘相同；当前进度会被替换。" : "当前模式的进度会被替换，其他模式会保留。") }
            .background(KeyboardControl(enabled: model.acceptsGameplayInput) { model.move($0) }.frame(width: 0, height: 0))
    }
    private var header: some View {
        HStack(alignment: .center) {
            VStack(alignment: .leading, spacing: 7) {
                Text("L U M I N A").font(.system(size: 11, weight: .semibold)).foregroundStyle(.secondary).fixedSize()
                Button { model.open(.modes) } label: {
                    HStack(spacing: 9) { Text(model.game.mode.title).font(.system(size: 28, weight: .semibold, design: .rounded)).tracking(-0.8).fixedSize(); Image(systemName: "chevron.down").font(.system(size: 12, weight: .semibold)).foregroundStyle(.secondary) }
                        .foregroundStyle(.primary).padding(.vertical, 4).contentShape(Rectangle())
                }.buttonStyle(.plain).accessibilityLabel("\(model.game.mode.title)，选择玩法")
            }
            Spacer(minLength: 8)
            RoundButton(label: "设置", symbol: "slider.horizontal.3") { model.open(.settings) }
        }
    }
    private var scores: some View {
        HStack(alignment: .firstTextBaseline, spacing: 14) {
            metric(label: "本局得分", value: model.game.score, main: true).frame(maxWidth: .infinity, alignment: .leading)
            metric(label: model.game.assisted ? "辅助最高" : "手动最高", value: model.best).frame(maxWidth: .infinity, alignment: .trailing)
            Rectangle().fill(.primary.opacity(0.07)).frame(width: 1, height: 35)
            metric(label: model.game.remaining == nil ? "步数" : "剩余步数", value: model.game.remaining ?? model.game.moves).frame(width: 60, alignment: .leading)
        }
    }
    private func metric(label: String, value: Int, main: Bool = false) -> some View {
        VStack(alignment: .leading, spacing: 6) {
            Text(label).font(.system(size: 11, weight: .medium)).foregroundStyle(.secondary)
            Text(value.formatted()).font(.system(size: main ? 30 : 23, weight: main ? .semibold : .medium, design: .rounded)).tracking(-0.7).monospacedDigit().lineLimit(1).minimumScaleFactor(0.5)
        }.accessibilityElement(children: .combine)
    }
    private func playfield(size: CGFloat) -> some View {
        ZStack {
            BoardView(model: model, size: size)
            if let e = model.game.expedition, [.draft, .clear].contains(e.phase) {
                DraftPanel(model: model, state: e).padding(14).frame(width: size, height: size)
                    .background(.ultraThinMaterial, in: RoundedRectangle(cornerRadius: size * 0.074))
            }
        }
    }
    private var controls: some View {
        ViewThatFits(in: .horizontal) { controlRow(compact: false); controlRow(compact: true) }
    }
    private func controlRow(compact: Bool) -> some View {
        HStack(spacing: 10) {
            RoundButton(label: "撤销一步", symbol: "arrow.uturn.backward") { model.undo() }.disabled(model.game.history.isEmpty)
            if compact {
                RoundButton(label: "提示", symbol: "lightbulb") { model.askHint() }.disabled(model.busy || model.thinking || model.game.phase != .play)
            } else {
                Button { model.askHint() } label: { Label("提示", systemImage: "lightbulb").fixedSize() }.buttonStyle(GameButtonStyle()).disabled(model.busy || model.thinking || model.game.phase != .play)
            }
            Button { model.toggleAuto() } label: {
                HStack(spacing: 7) { Image(systemName: model.autoPlay ? "pause.fill" : "sparkles"); Text(model.autoPlay ? "暂停" : "自动玩").fixedSize() }.frame(maxWidth: .infinity)
            }.buttonStyle(GameButtonStyle(prominent: true)).disabled(!model.autoPlay && (model.busy || model.game.phase != .play))
            if snapshot { moreLabel } else { Menu {
                Button("重做一步", systemImage: "arrow.uturn.forward") { model.redo() }.disabled(model.game.future.isEmpty)
                Button("重新开始", systemImage: "arrow.clockwise") { model.stopAI(); model.confirmRestart = true }
                Button("选择玩法", systemImage: "square.grid.2x2") { model.open(.modes) }
                if model.game.mode == .puzzle { Button("选择谜题", systemImage: "square.on.square") { model.open(.puzzles) } }
                if model.game.mode == .rescue { Button("残局档案", systemImage: "tray") { model.open(.rescues) }; Button("对照复盘", systemImage: "play.rectangle") { model.showReplay() } }
            } label: { moreLabel }.menuStyle(.borderlessButton).frame(width: 44).accessibilityLabel("更多操作") }
        }
    }
    private var moreLabel: some View { Image(systemName: "ellipsis").font(.system(size: 19, weight: .semibold)).frame(width: 44, height: 46).foregroundStyle(.primary) }
    @ViewBuilder private var context: some View {
        VStack(alignment: .leading, spacing: 14) {
            HStack(spacing: 8) {
                if model.thinking { ProgressView().controlSize(.small) } else { Image(systemName: model.game.mode.symbol).foregroundStyle(Atelier.accent) }
                Text(model.thinking ? "正在寻找更好的下一步…" : model.swapping ? "点选两枚不同数字，交换位置" : model.objective).font(.system(size: 13)).foregroundStyle(.secondary)
                Spacer(minLength: 0)
            }
            if let e = model.game.expedition, e.phase == .play {
                expedition(e)
            }
            if let hint = model.hint, let action = hint.action {
                VStack(alignment: .leading, spacing: 11) {
                    HStack {
                        Image(systemName: action.symbol).font(.title3).foregroundStyle(Atelier.accent)
                        VStack(alignment: .leading, spacing: 3) {
                            Text(action.title).font(.subheadline.weight(.semibold))
                            Text(hint.exact ? "找到 \(hint.solution.count) 步解法" : "比较随机落子后的后续局面").font(.caption).foregroundStyle(.secondary)
                        }
                        Spacer()
                        Button("走这一步") { model.followHint() }.buttonStyle(GameButtonStyle())
                    }
                    if !hint.exact {
                        HStack(spacing: 8) { ForEach(Array(hint.values.prefix(4).enumerated()), id: \.offset) { rank, candidate in
                            HStack(spacing: 4) { Image(systemName: candidate.action.symbol); Text(rank == 0 ? "优先" : "备选") }.font(.caption2).foregroundStyle(rank == 0 ? Atelier.accent : .secondary).padding(8).background(.primary.opacity(0.035), in: Capsule())
                        } }
                    }
                }.padding(16).glass(20)
            }
            if [.won, .lost].contains(model.game.phase) { resultCard }
            if let challenge = model.recovered {
                VStack(alignment: .leading, spacing: 10) {
                    Text("这里还有一条路").font(.headline)
                    Text("回到结束前 \(challenge.rewind) 步，\(challenge.limit) 步内腾出三个空位。已确认存在解法。").font(.subheadline).foregroundStyle(.secondary)
                    Button("试着改写这局") { model.start(challenge) }.buttonStyle(GameButtonStyle(prominent: true))
                }.padding(18).glass()
            }
        }.frame(maxWidth: .infinity, alignment: .leading)
    }
    private func expedition(_ e: ExpeditionState) -> some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack { Text("关卡得分"); Spacer(); Text("\(model.game.score - e.stageScore) / \(ExpeditionState.stages[e.stage].target)").monospacedDigit() }.font(.caption).foregroundStyle(.secondary)
            ProgressView(value: min(Double(ExpeditionState.stages[e.stage].target), Double(model.game.score - e.stageScore)), total: Double(ExpeditionState.stages[e.stage].target)).tint(Atelier.accent)
            HStack(spacing: 8) {
                Label("\(e.energy)", systemImage: "bolt.fill").font(.system(size: 14, weight: .semibold, design: .rounded)).foregroundStyle(Atelier.accent)
                Spacer()
                Button { model.usePower(.freeze) } label: { Label(e.freeze > 0 ? "凝时 \(e.freeze)" : e.cooldown > 0 ? "冷却 \(e.cooldown)" : "凝时 · 5", systemImage: "snowflake") }.buttonStyle(GameButtonStyle()).disabled(model.busy || !model.game.availablePowers.contains(.freeze))
                Button { model.stopAI(); model.swapping.toggle(); model.swapCell = nil } label: { Label(model.swapping ? "取消" : "交换 · \(e.swapCost)", systemImage: "arrow.left.arrow.right") }.buttonStyle(GameButtonStyle()).disabled(model.busy || !model.game.availablePowers.contains { if case .swap = $0 { return true }; return false })
            }
            if !e.perks.isEmpty {
                DisclosureGroup("能力收藏 · \(e.perks.values.reduce(0, +))") {
                    VStack(alignment: .leading, spacing: 12) { ForEach(Ability.allCases.filter { e.rank($0) > 0 }) { ability in
                        VStack(alignment: .leading, spacing: 4) { Label("\(ability.title) \(e.rank(ability) == 2 ? "II" : "I")", systemImage: ability.symbol).font(.caption.weight(.semibold)); Text(ability.detail(rank: e.rank(ability))).font(.caption).foregroundStyle(.secondary) }
                    } }.padding(.top, 10).frame(maxWidth: .infinity, alignment: .leading)
                }.font(.caption).tint(.secondary)
            }
        }.padding(16).glass(20)
    }
    private var resultCard: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack { Image(systemName: model.game.phase == .won ? "checkmark.circle" : "flag.checkered").foregroundStyle(Atelier.accent); Text(model.game.phase == .won ? "这一关，漂亮。" : model.game.mode == .sprint && model.game.moves == 60 ? "六十步，落定。" : "这一局，暂告一段落。").font(.headline) }
            if model.game.mode == .puzzle, let level = model.game.puzzle, model.game.phase == .won {
                Text(String(repeating: "★", count: model.book.stars[String(level.id)] ?? 1)).foregroundStyle(Color(hex: 0xAE9256)).font(.title3)
                Button(level.id < model.levels.count - 1 ? "下一道谜题" : "浏览全部谜题") { if level.id + 1 < model.levels.count { model.start(model.levels[level.id + 1]) } else { model.open(.puzzles) } }.buttonStyle(GameButtonStyle(prominent: true))
            } else if model.game.mode == .rescue {
                HStack { Button("对照复盘") { model.showReplay() }; Button("更多残局") { model.open(.rescues) } }.buttonStyle(GameButtonStyle())
            } else if [.classic, .daily, .sprint].contains(model.game.mode), !Rules.canMove(model.game.board) {
                Button { model.extractRescue() } label: { HStack { if model.extracting { ProgressView().controlSize(.small) }; Text(model.extracting ? "正在寻找转机…" : "寻找这局的另一种结局") } }.buttonStyle(GameButtonStyle(prominent: true)).disabled(model.extracting)
            }
            HStack { Button("再来一局") { model.confirmRestart = true }; if !model.game.history.isEmpty { Button("撤回一步") { model.undo() } } }.buttonStyle(GameButtonStyle())
        }.padding(18).glass()
    }
    private var footer: some View {
        HStack(spacing: 7) { Circle().fill(model.game.assisted ? Color(hex: 0xB29B73) : Atelier.accent.opacity(0.5)).frame(width: 4, height: 4); Text(model.game.assisted ? "辅助局 · 进度自动保存" : "手动局 · 进度自动保存") }.font(.system(size: 10, weight: .medium)).foregroundStyle(.tertiary).frame(maxWidth: .infinity)
    }
}

struct DraftPanel: View {
    @ObservedObject var model: GameModel
    let state: ExpeditionState
    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 10) {
                Text(state.phase == .clear ? "抵达下一段旅程" : "选择你的第一种能力").font(.system(size: 20, weight: .semibold)).padding(.top, 8)
                Text(state.phase == .clear ? "升级能力，释放一个格子，继续前进。" : "能力会伴随你走完六个关卡。").font(.caption).foregroundStyle(.secondary).padding(.bottom, 4)
                ForEach(state.offers) { ability in
                    Button { model.choose(ability) } label: {
                        HStack(alignment: .top, spacing: 12) {
                            Image(systemName: ability.symbol).font(.system(size: 20)).foregroundStyle(Atelier.accent).frame(width: 26).padding(.top, 2)
                            VStack(alignment: .leading, spacing: 4) { Text(ability.title + (state.rank(ability) == 1 ? " II" : "")).font(.system(size: 15, weight: .semibold)); Text(ability.detail(rank: state.rank(ability) + 1)).font(.system(size: 11)).foregroundStyle(.secondary).fixedSize(horizontal: false, vertical: true) }
                            Spacer(minLength: 0)
                        }.padding(13).frame(maxWidth: .infinity, alignment: .leading).glass(17).contentShape(RoundedRectangle(cornerRadius: 17))
                    }.buttonStyle(.plain)
                }
            }.padding(3)
        }.scrollIndicators(.hidden)
    }
}
