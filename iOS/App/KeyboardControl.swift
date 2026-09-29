import SwiftUI
import LuminaCore
#if os(iOS)
import UIKit

struct KeyboardControl: UIViewRepresentable {
    let enabled: Bool
    let move: (Direction) -> Void
    func makeUIView(context: Context) -> KeyCapture { let view = KeyCapture(); view.move = move; view.enabled = enabled; return view }
    func updateUIView(_ uiView: KeyCapture, context: Context) { uiView.move = move; uiView.enabled = enabled; uiView.updateFocus() }
    final class KeyCapture: UIView {
        var move: ((Direction) -> Void)?
        var enabled = true
        override var canBecomeFirstResponder: Bool { enabled }
        func updateFocus() {
            if !enabled { if isFirstResponder { resignFirstResponder() } }
            else if window != nil && !isFirstResponder { becomeFirstResponder() }
        }
        override func didMoveToWindow() { super.didMoveToWindow(); DispatchQueue.main.async { [weak self] in self?.updateFocus() } }
        override var keyCommands: [UIKeyCommand]? {
            guard enabled else { return [] }
            return [UIKeyCommand.inputLeftArrow, UIKeyCommand.inputUpArrow, UIKeyCommand.inputRightArrow, UIKeyCommand.inputDownArrow, "a", "w", "d", "s"].map { input in
                let command = UIKeyCommand(input: input, modifierFlags: [], action: #selector(pressed(_:))); command.wantsPriorityOverSystemBehavior = true; return command
            }
        }
        @objc private func pressed(_ command: UIKeyCommand) {
            guard enabled else { return }
            switch command.input { case UIKeyCommand.inputLeftArrow, "a": move?(.left); case UIKeyCommand.inputRightArrow, "d": move?(.right); case UIKeyCommand.inputUpArrow, "w": move?(.up); case UIKeyCommand.inputDownArrow, "s": move?(.down); default: break }
        }
    }
}
#else
struct KeyboardControl: View {
    let enabled: Bool
    let move: (Direction) -> Void
    var body: some View { Color.clear.focusable(enabled).onMoveCommand { direction in guard enabled else { return }; switch direction { case .left: move(.left); case .right: move(.right); case .up: move(.up); case .down: move(.down); @unknown default: break } } }
}
#endif
