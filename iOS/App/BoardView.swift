import SwiftUI
import LuminaCore

struct BoardView: View {
    @ObservedObject var model: GameModel
    let size: CGFloat
    @Environment(\.colorScheme) private var scheme
    private var geometry: BoardGeometry { BoardGeometry(size: size) }
    var body: some View {
        ZStack(alignment: .topLeading) {
            RoundedRectangle(cornerRadius: size * 0.074, style: .continuous)
                .fill(scheme == .dark ? Color(hex: 0x1B252A) : Color(hex: 0xE4E9E5).opacity(0.82))
                .overlay(RoundedRectangle(cornerRadius: size * 0.074).strokeBorder(.white.opacity(scheme == .dark ? 0.12 : 0.95), lineWidth: 1))
            slots
            pieces
            if model.swapping { swapTargets }
        }.frame(width: size, height: size).contentShape(Rectangle())
            .shadow(color: .black.opacity(scheme == .dark ? 0.14 : 0.055), radius: 22, x: 0, y: 14)
            .highPriorityGesture(DragGesture(minimumDistance: 16).onEnded { gesture in
                let x = gesture.translation.width, y = gesture.translation.height
                guard max(abs(x), abs(y)) >= 20 else { return }
                let direction: Direction = abs(x) > abs(y) ? (x > 0 ? .right : .left) : (y > 0 ? .down : .up)
                model.move(direction)
            })
            .accessibilityElement(children: .contain).accessibilityLabel("2048 棋盘")
            .accessibilityAction(named: Text("向左移动")) { model.move(.left) }
            .accessibilityAction(named: Text("向上移动")) { model.move(.up) }
            .accessibilityAction(named: Text("向右移动")) { model.move(.right) }
            .accessibilityAction(named: Text("向下移动")) { model.move(.down) }
    }
    private var slots: some View {
        ForEach(0..<16) { index in
            RoundedRectangle(cornerRadius: geometry.cell * 0.21, style: .continuous)
                .fill(scheme == .dark ? Color.white.opacity(0.028) : Color.white.opacity(0.40))
                .frame(width: geometry.cell, height: geometry.cell).position(geometry.center(index))
                .accessibilityLabel(cellLabel(index))
        }
    }
    private var pieces: some View {
        ForEach(model.tiles) { tile in
            NumberTile(value: tile.value, size: geometry.cell).scaleEffect(tile.scale)
                .overlay(RoundedRectangle(cornerRadius: geometry.cell * 0.21).strokeBorder(Atelier.accent, lineWidth: model.swapCell == tile.cell ? 3 : 0))
                .position(geometry.center(tile.cell)).accessibilityHidden(true)
        }
    }
    private var swapTargets: some View {
        ForEach(0..<16) { index in
            Color.clear.frame(width: geometry.cell, height: geometry.cell).contentShape(Rectangle())
                .position(geometry.center(index)).onTapGesture { model.tapTile(index) }
                .accessibilityLabel("选择" + cellLabel(index)).accessibilityAddTraits(.isButton)
        }
    }
    private func cellLabel(_ index: Int) -> String {
        let value = model.game.board[index] == 0 ? "空" : String(model.game.board[index])
        return "第 \(index / 4 + 1) 行，第 \(index % 4 + 1) 列，\(value)"
    }
}
struct StaticBoard: View {
    let board: [Int]
    var body: some View {
        GeometryReader { geo in
            let gap = geo.size.width * 0.022, inset = geo.size.width * 0.03, cell = (geo.size.width - inset * 2 - gap * 3) / 4
            ZStack(alignment: .topLeading) {
                RoundedRectangle(cornerRadius: 22).fill(.primary.opacity(0.05))
                ForEach(0..<16) { i in
                    Group { if board[i] > 0 { NumberTile(value: board[i], size: cell) } else { RoundedRectangle(cornerRadius: cell * 0.2).fill(.primary.opacity(0.04)).frame(width: cell, height: cell) } }
                        .position(x: inset + cell / 2 + CGFloat(i % 4) * (cell + gap), y: inset + cell / 2 + CGFloat(i / 4) * (cell + gap))
                }
            }
        }.aspectRatio(1, contentMode: .fit).accessibilityLabel("棋盘：\(board.map(String.init).joined(separator: "，"))")
    }
}

private struct BoardGeometry {
    let size: CGFloat
    var gap: CGFloat { max(7, size * 0.024) }
    var inset: CGFloat { size * 0.032 }
    var cell: CGFloat { (size - inset * 2 - gap * 3) / 4 }
    func center(_ index: Int) -> CGPoint {
        let x = inset + cell / 2 + CGFloat(index % 4) * (cell + gap)
        let y = inset + cell / 2 + CGFloat(index / 4) * (cell + gap)
        return CGPoint(x: x, y: y)
    }
}
