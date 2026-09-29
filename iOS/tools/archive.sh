#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."
if ! xcrun --sdk iphoneos --show-sdk-path >/dev/null 2>&1; then
    echo "需要完整 Xcode 和 iOS SDK。仅安装 Command Line Tools 无法生成 iPhone / iPad App。" >&2
    exit 2
fi
if [[ -z "${LUMINA_TEAM_ID:-}" ]]; then
    echo "请先在 Xcode 的 Signing & Capabilities 中选择 Team，或设置 LUMINA_TEAM_ID。" >&2
    echo "真机个人安装可直接在 Xcode 选择设备并运行；不要把未签名文件当成可安装 IPA。" >&2
    exit 2
fi
xcodebuild -project Lumina.xcodeproj -scheme Lumina -configuration Release \
    -destination 'generic/platform=iOS' -archivePath build/Lumina.xcarchive \
    DEVELOPMENT_TEAM="$LUMINA_TEAM_ID" -allowProvisioningUpdates archive
echo "Archive 已生成：build/Lumina.xcarchive。请在 Xcode Organizer 按账号类型选择分发；本脚本不会上传。"
