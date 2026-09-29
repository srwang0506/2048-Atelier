import Foundation
import Testing
@testable import LuminaCore

@Suite("Optional native AI endurance") struct Benchmark {
    @Test(.enabled(if: ProcessInfo.processInfo.environment["LUMINA_BENCHMARK"] == "1"))
    func classicEndurance() throws {
        var classic = Game(seed: 42), decisions = 0
        let start = Date()
        while classic.phase == .play && decisions < 3200 {
            let result = Solver.solve(classic, budget: 0.035)
            guard let action = result.action else { Issue.record("AI returned no action on a playable board"); break }
            #expect(classic.perform(action, assisted: true) != nil); decisions += 1
        }
        print("NATIVE_BENCH classic: moves=\(classic.moves) score=\(classic.score) max=\(classic.maxTile) phase=\(classic.phase.rawValue) elapsed=\(Date().timeIntervalSince(start))s")
        #expect(classic.isValid); #expect(classic.maxTile >= 2048)
    }
    @Test(.enabled(if: ProcessInfo.processInfo.environment["LUMINA_BENCHMARK"] == "1"))
    func expeditionEndurance() throws {
        var game = Game(mode: .expedition, seed: 42), actions = 0
        let preference: [Ability] = [.gambit,.combo,.echo,.corner,.reserve,.flow,.battery,.warp,.ice]
        while ![Phase.lost,.won].contains(game.phase) && actions < 600 {
            if [.draft,.clear].contains(game.phase), let e = game.expedition {
                let choice = preference.first { e.offers.contains($0) }!; #expect(game.choose(choice) == true)
            } else {
                guard let action = Solver.solve(game, budget: 0.06).action else { Issue.record("Expedition has no AI action"); break }
                #expect(game.perform(action, assisted: true) != nil); actions += 1
            }
        }
        print("NATIVE_BENCH expedition: actions=\(actions) score=\(game.score) cleared=\(game.expedition?.cleared ?? 0) phase=\(game.phase.rawValue)")
        #expect(game.isValid); #expect(game.phase == .won)
    }
}
