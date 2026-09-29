import SwiftUI
import LuminaCore

@main
struct LuminaApp: App {
    @StateObject private var model = GameModel()
    @Environment(\.scenePhase) private var scenePhase

    var body: some Scene {
        WindowGroup {
            NativeGameView(model: model)
                .preferredColorScheme(model.settings.appearance == .system ? nil : model.settings.appearance == .dark ? .dark : .light)
                .task { await model.load() }
                .onChange(of: scenePhase) { phase in
                    if phase == .active { model.resume() } else { model.suspend() }
                }
        }
    }
}
