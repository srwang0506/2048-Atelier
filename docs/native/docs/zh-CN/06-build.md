# 安装、构建与开发者说明

## 当前交付是什么

LUMINA 1.0.1 是 Swift / SwiftUI 原生 iPhone + iPad Universal App 工程，最低部署 iOS / iPadOS 16.4。没有 WebView。源码包包含独立核心、资源、Xcode 工程、测试、文档与演示媒体。当前没有已签名 IPA、模拟器构建产物或 TestFlight / 商店发布。

最低部署版本不等于任意旧 Xcode 都能构建：Swift 包声明 Swift 工具链 6.0+、Swift 5 语言模式。还需 Xcode 支持目标设备系统。本机只有 Command Line Tools，已完成 macOS 主机检查；未完成 iOS SDK 编译和真机验收。

## 安装到自己的 iPhone / iPad

1. 准备 Mac，安装完整 Xcode。按 Apple [Xcode 兼容表](https://developer.apple.com/xcode/system-requirements)选择兼容 Mac 与设备系统的版本。不要只安装 `xcode-select --install` 提供的命令行工具。
2. 启动 Xcode，完成首次组件安装；在 Settings → Locations → Command Line Tools 选择该 Xcode。
3. 解压源码到可写的本地目录。双击 `Lumina.xcodeproj`，选择共享 Scheme **Lumina**。
4. Xcode → Settings → Accounts 添加自己的 Apple Account。在 target → Signing & Capabilities 选择自己的 Team；必要时将 Bundle Identifier 改成自己唯一的标识。
5. 连接并解锁设备，处理系统的信任配对；按 Xcode / 系统提示启用 Developer Mode。在运行目标中选择这台 iPhone 或 iPad。
6. 点 ▶ Run。第一次构建与签名可能需要等待。失败时先阅读最上面的实际错误，不要把改文件扩展名当成解决办法。
7. 启动后依次验证经典滑动、横竖屏、所有模式、存档恢复、声音 / 触感和文件导入导出。

Apple 官方：[在模拟器或设备运行 App](https://developer.apple.com/documentation/xcode/running-your-app-on-simulated-or-physical-devices)、[开发者账户与团队](https://help.apple.com/xcode/mac/current/en.lproj/dev60b6fbbc7.html)。团队资格与分发要求以 Apple 当时规则为准；不要把个人设备 Run 安装等同于 TestFlight 分发。

## 项目布局

| 路径 | 作用 |
| --- | --- |
| `App/` | SwiftUI 界面、GameModel、输入、声音与触感、资源和隐私清单 |
| `Sources/LuminaCore/` | 规则、随机数、六种模式、搜索与存档 |
| `Sources/LuminaCore/Resources/` | 12 道谜题与 3 道精选残局 |
| `Tests/LuminaCoreTests/` | 规则对照、存档、回归、长局 AI |
| `Tests/LuminaAppTests/` | 生命周期交互、布局、可选文档媒体采集 |
| `Lumina.xcodeproj/` | 共享 Scheme、本地 Swift 包引用 |
| `tools/` | 工程生成、配置检查、Archive、文档生成工具 |
| `docs/` | 三语 Markdown、离线 HTML、共享 GIF 与原始演示视频 |
| `QA/` | 现有测试日志与布局检查图 |

运行时无第三方 SDK，也无需联网下载 Swift 包。文档制作工具的依赖与 App 运行依赖分开。

## 常用命令

在项目根目录执行：

```sh
swift test -c release --disable-xctest
python3 tools/validate-project.py
./tools/check.sh
```

第一条在 Mac 上运行 Swift Testing；第二条验证工程与资源引用；第三条还尝试 iOS Simulator 构建，没有 iOS SDK 时明确失败。macOS 测试通过不能替代 iOS 构建。

```sh
LUMINA_BENCHMARK=1 swift test -c release --disable-xctest --filter Benchmark
LUMINA_RENDER_DIRECTORY=/tmp/lumina-layouts swift test -c release --disable-xctest --filter renderNativeLayouts
```

第一条开启长局检查；第二条输出静态 SwiftUI 布局图。布局图使用测试容器，不是设备截图。文档录制命令与转换工具见[媒体说明](../media/README.md)。

## Archive 与交付

可在 Xcode 中用 Product → Archive，或：

```sh
LUMINA_TEAM_ID=你的团队ID ./tools/archive.sh
```

脚本只生成 `build/Lumina.xcarchive`，不自动上传或导出 IPA。导出方式必须与自己的证书、账户资格、设备和分发目标匹配。不要把团队 ID、证书或设备信息提交到公开源码。文档中的命令不会替你申请开发者资格。

## 工程再生成与开发注意事项

新增 `App/*.swift` 后可执行 `python3 tools/generate-project.py` 更新引用。生成器会恢复默认 Team / Bundle Identifier，先保留本机签名修改。文档录制测试只在环境变量开启时运行，使用独立临时存档目录，不接触玩家正常存档。

随机数与桌面版规则兼容通过夹具检查；原生 JSON 结构仍独立。改变规则、能力数值、关卡或按钮名称时，应同时更新三套手册和动图，不能只改中文 README。代码发布与文档修订分开记录；本轮文档没有改变游戏规则。

## 真机验收清单

| 场景 | 通过标准 |
| --- | --- |
| iPhone 竖屏 / 横屏 | 棋盘完整，按钮可点，目标和结果可滚动看到 |
| iPad 全屏 / 分屏 | 缩放和旋转后没有重置游戏或遮挡控件 |
| 连续滑动后打开菜单 | 棋盘停止，关闭后没有遗留输入 |
| AI 思考时切模式 / 后台 | 旧任务不再落子，不错误覆盖新局 |
| 后台与系统终止后重开 | 最近已保存状态恢复，异常有提示 |
| 文件导出 / 导入 / 取消 | 文件可再次读取，取消不改进度，无效文件不覆盖 |
| 键盘 / VoiceOver | 对局可操作，弹窗和设置期间焦点正确 |
| 六模式与远征能力 | 步数、奖励、辅助标记和胜负符合规则 |
| 声音 / 静音 / 触感 | 与设置及设备能力一致 |

该表是待执行验收计划，不是声称已经全部通过的报告。
