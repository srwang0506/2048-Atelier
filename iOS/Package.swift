// swift-tools-version: 6.0
import PackageDescription

let package = Package(
    name: "Lumina",
    platforms: [.iOS(.v16), .macOS(.v14)],
    products: [.library(name: "LuminaCore", targets: ["LuminaCore"]),
               .executable(name: "LuminaPreview", targets: ["LuminaPreview"])],
    targets: [
        .target(name: "LuminaCore", resources: [.process("Resources")]),
        .executableTarget(name: "LuminaPreview", dependencies: ["LuminaCore"], path: "App",
                          exclude: ["Assets.xcassets", "Info.plist", "PrivacyInfo.xcprivacy"]),
        .testTarget(name: "LuminaCoreTests", dependencies: ["LuminaCore"], resources: [.process("Fixtures")]),
        .testTarget(name: "LuminaAppTests", dependencies: ["LuminaPreview", "LuminaCore"])
    ],
    swiftLanguageModes: [.v5]
)
