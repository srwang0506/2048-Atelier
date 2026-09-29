import Foundation
import AVFoundation
import LuminaCore
#if os(iOS)
import UIKit
#endif

@MainActor final class GameFeedback {
    private var tick: AVAudioPlayer?, chime: AVAudioPlayer?
    #if os(iOS)
    private let impact = UIImpactFeedbackGenerator(style: .soft)
    #endif
    func play(merge: Bool, settings: Settings) {
        #if os(iOS)
        if settings.haptics { impact.impactOccurred(intensity: merge ? 0.55 : 0.25); impact.prepare() }
        #endif
        guard settings.sound else { return }
        if tick == nil {
            #if os(iOS)
            try? AVAudioSession.sharedInstance().setCategory(.ambient, options: .mixWithOthers)
            #endif
            tick = try? AVAudioPlayer(data: Self.tone(frequency: 640, duration: 0.04))
            chime = try? AVAudioPlayer(data: Self.tone(frequency: 880, duration: 0.10))
            tick?.prepareToPlay(); chime?.prepareToPlay()
        }
        let player = merge ? chime : tick; player?.currentTime = 0; player?.volume = 0.18; player?.play()
    }
    private static func tone(frequency: Double, duration: Double) -> Data {
        let rate = 22050, count = Int(Double(rate) * duration), bytes = count * 2
        var data = Data()
        func string(_ s: String) { data.append(contentsOf: s.utf8) }
        func word<T: FixedWidthInteger>(_ n: T) { var value = n.littleEndian; withUnsafeBytes(of: &value) { data.append(contentsOf: $0) } }
        string("RIFF"); word(UInt32(36 + bytes)); string("WAVEfmt "); word(UInt32(16)); word(UInt16(1)); word(UInt16(1)); word(UInt32(rate)); word(UInt32(rate * 2)); word(UInt16(2)); word(UInt16(16)); string("data"); word(UInt32(bytes))
        for i in 0..<count { let t = Double(i) / Double(rate), envelope = sin(.pi * Double(i) / Double(count)) * exp(-t * 24); word(Int16(sin(2 * .pi * frequency * t) * envelope * 12000)) }
        return data
    }
}
