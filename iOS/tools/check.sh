#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."
plutil -lint App/Info.plist App/PrivacyInfo.xcprivacy Lumina.xcodeproj/project.pbxproj
python3 tools/validate-project.py
swift test -c release --disable-xctest
if ! xcrun --sdk iphoneos --show-sdk-path >/dev/null 2>&1; then
    echo "原生逻辑检查结束；此 Mac 缺少 iOS SDK，尚未进行 iOS 构建。请安装完整 Xcode 并选择其 Command Line Tools。" >&2
    exit 2
fi
xcodebuild -project Lumina.xcodeproj -scheme Lumina -configuration Debug \
    -destination 'generic/platform=iOS Simulator' -derivedDataPath build/DerivedData \
    CODE_SIGNING_ALLOWED=NO build
echo "iOS 模拟器构建通过。真机运行仍需选择 Signing Team。"
