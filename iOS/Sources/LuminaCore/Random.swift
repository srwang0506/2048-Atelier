import Foundation

/// Integer-seeded MT19937, including Python's getrandbits rejection sampling.
public struct GameRandom: Codable, Equatable, Sendable {
    public var mt: [UInt32]
    public var index: Int

    public init(seed: UInt64) {
        mt = Array(repeating: 0, count: 624)
        index = 624
        mt[0] = 19_650_218
        for i in 1..<624 { mt[i] = 1_812_433_253 &* (mt[i - 1] ^ (mt[i - 1] >> 30)) &+ UInt32(i) }
        var words = [UInt32(truncatingIfNeeded: seed)]
        if seed >> 32 != 0 { words.append(UInt32(seed >> 32)) }
        var i = 1, j = 0
        for _ in 0..<max(624, words.count) {
            mt[i] = (mt[i] ^ ((mt[i - 1] ^ (mt[i - 1] >> 30)) &* 1_664_525)) &+ words[j] &+ UInt32(j)
            i += 1; j += 1
            if i >= 624 { mt[0] = mt[623]; i = 1 }
            if j >= words.count { j = 0 }
        }
        for _ in 0..<623 {
            mt[i] = (mt[i] ^ ((mt[i - 1] ^ (mt[i - 1] >> 30)) &* 1_566_083_941)) &- UInt32(i)
            i += 1
            if i >= 624 { mt[0] = mt[623]; i = 1 }
        }
        mt[0] = 0x80000000
    }

    public var isValid: Bool { mt.count == 624 && mt.contains(where: { $0 != 0 }) && (0...624).contains(index) }

    public mutating func next() -> UInt32 {
        if index >= 624 {
            for i in 0..<624 {
                let y = (mt[i] & 0x80000000) | (mt[(i + 1) % 624] & 0x7fffffff)
                mt[i] = mt[(i + 397) % 624] ^ (y >> 1) ^ (y & 1 == 1 ? 0x9908b0df : 0)
            }
            index = 0
        }
        var y = mt[index]; index += 1
        y ^= y >> 11; y ^= (y << 7) & 0x9d2c5680; y ^= (y << 15) & 0xefc60000; y ^= y >> 18
        return y
    }

    public mutating func random() -> Double {
        (Double(next() >> 5) * 67_108_864 + Double(next() >> 6)) / 9_007_199_254_740_992
    }

    public mutating func choice(_ count: Int) -> Int {
        precondition(count > 0)
        let bits = Int.bitWidth - count.leadingZeroBitCount
        var value: UInt32
        repeat { value = next() >> (32 - bits) } while value >= count
        return Int(value)
    }
}
