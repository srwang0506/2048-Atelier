import SwiftUI

extension Color {
    init(hex: UInt32) { self.init(.sRGB, red: Double((hex >> 16) & 255) / 255, green: Double((hex >> 8) & 255) / 255, blue: Double(hex & 255) / 255, opacity: 1) }
}
enum Atelier {
    static let accent = Color(hex: 0x637C72)
    static func tile(_ value: Int, dark: Bool) -> Color {
        let colors: [UInt32] = dark ? [0x343F44, 0x3D4C50, 0x4B5C5C, 0x54685E, 0x64766A, 0x8A7A58, 0xAC9261, 0xB78C69, 0xA77065, 0x856477, 0x6C6282, 0x647C87] : [0xFDFCF9, 0xF1F3ED, 0xDEEAE1, 0xCBDFD5, 0xB6D3C5, 0xEFE4C4, 0xE7D09B, 0xE5B99B, 0xDCA999, 0xCCB6CC, 0xB6B9D7, 0xA6C4D4]
        let exponent = value > 0 ? Int.bitWidth - value.leadingZeroBitCount - 1 : 1
        return Color(hex: colors[min(max(0, exponent - 1), colors.count - 1)])
    }
}
struct GlassPanel: ViewModifier {
    @Environment(\.colorScheme) private var scheme
    var radius: CGFloat = 24
    func body(content: Content) -> some View {
        content.background(scheme == .dark ? Color.white.opacity(0.055) : Color.white.opacity(0.64), in: RoundedRectangle(cornerRadius: radius, style: .continuous))
            .overlay(RoundedRectangle(cornerRadius: radius, style: .continuous).strokeBorder(Color.white.opacity(scheme == .dark ? 0.10 : 0.86), lineWidth: 1))
    }
}
extension View { func glass(_ radius: CGFloat = 24) -> some View { modifier(GlassPanel(radius: radius)) } }
struct GameButtonStyle: ButtonStyle {
    var prominent = false
    @Environment(\.isEnabled) private var enabled
    @Environment(\.accessibilityReduceMotion) private var reduceMotion
    func makeBody(configuration: Configuration) -> some View {
        configuration.label.font(.system(size: 15, weight: .semibold)).lineLimit(1).minimumScaleFactor(0.8)
            .frame(minHeight: 46).padding(.horizontal, 16)
            .foregroundStyle(prominent ? Color.white : Color.primary.opacity(0.8))
            .background(prominent ? Atelier.accent : Color.primary.opacity(configuration.isPressed ? 0.10 : 0.045), in: RoundedRectangle(cornerRadius: 16, style: .continuous))
            .opacity(enabled ? 1 : 0.35)
            .scaleEffect(configuration.isPressed && !reduceMotion ? 0.97 : 1)
            .animation(reduceMotion ? nil : .easeOut(duration: 0.15), value: configuration.isPressed)
    }
}
struct RoundButton: View {
    let label: String, symbol: String
    var action: () -> Void
    var body: some View { Button(action: action) { Image(systemName: symbol).font(.system(size: 18, weight: .medium)).frame(width: 46, height: 46).contentShape(Circle()) }.buttonStyle(.plain).background(.primary.opacity(0.045), in: Circle()).accessibilityLabel(label) }
}

struct NumberTile: View {
    let value: Int, size: CGFloat
    @Environment(\.colorScheme) private var scheme
    var body: some View {
        let dark = scheme == .dark
        ZStack {
            RoundedRectangle(cornerRadius: size * 0.21, style: .continuous)
                .fill(LinearGradient(colors: [Atelier.tile(value, dark: dark), Atelier.tile(value, dark: dark).opacity(0.87)], startPoint: .topLeading, endPoint: .bottomTrailing))
            RoundedRectangle(cornerRadius: size * 0.21, style: .continuous).strokeBorder(.white.opacity(dark ? 0.15 : 0.80), lineWidth: 1)
            Text(value.formatted(.number.grouping(.never))).font(.system(size: size * (value < 100 ? 0.43 : value < 1000 ? 0.37 : 0.31), weight: .semibold, design: .rounded)).tracking(-size * 0.013)
                .foregroundStyle(dark ? Color.white.opacity(0.92) : Color(hex: 0x35453F)).minimumScaleFactor(0.3).lineLimit(1).padding(5)
        }.frame(width: size, height: size).compositingGroup()
            .shadow(color: .black.opacity(dark ? 0.12 : 0.065), radius: 3, x: 0, y: 3)
    }
}

// ImageRenderer cannot capture AppKit-backed scrolling layers. Snapshot tests
// render the same content without that platform container; live apps always scroll.
private struct LayoutSnapshotKey: EnvironmentKey { static let defaultValue = false }
extension EnvironmentValues {
    var layoutSnapshot: Bool {
        get { self[LayoutSnapshotKey.self] }
        set { self[LayoutSnapshotKey.self] = newValue }
    }
}
struct GameScroll<Content: View>: View {
    @Environment(\.layoutSnapshot) private var snapshot
    @ViewBuilder var content: () -> Content
    var body: some View {
        if snapshot { VStack(spacing: 0) { content(); Spacer(minLength: 0) }.frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .top).clipped() }
        else { ScrollView { content() } }
    }
}
