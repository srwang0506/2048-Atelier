# iPhone、iPad 与网页版

## iPhone 与 iPad：同一原生工程，不同布局

**Native 1.0.1（build 2）** 是真正的 Swift / SwiftUI Universal App 源码，不是 WebView。iPhone 和 iPad 使用同一套规则与源码，按屏幕宽度排布；工程最低部署目标 iOS / iPadOS 16.4，构建工具要求 Swift 6.0+，并使用 Swift 5 语言模式。部署目标不是 Xcode 版本要求，两者不要混淆。

当前交付位于游戏根目录 `iOS/`，包含 `Lumina.xcodeproj`、核心、界面、资源、测试和原生手册。**没有已经签名的 IPA、TestFlight 邀请或 App Store 上架版本**。需在 Mac 安装完整 Xcode 与兼容的 iOS SDK，打开项目、设置自己的 Team 与 Bundle Identifier，选择设备后 Run。只安装 Command Line Tools 不足以完成 iPhone 安装。详见[逐步安装、签名、构建和验收](../native/docs/zh-CN/06-build.md)。

## 原生版怎么操作

启动默认进入经典；上方模式名称展开其他玩法。棋盘内四向滑动，撤销按钮回一步，灯泡请求提示，自动玩按钮开始 / 暂停。三点菜单含重做、重开、选择谜题或残局等操作。设置里有外观、声音、触感、减少动态效果、AI 强度与 JSON 备份。

外接键盘实现方向键和 WASD，不要把桌面 Z、R、C、P 等快捷键套过来。动画期最多排队两次滑动；菜单、后台或手动接管会处理队列并暂停 AI。iPhone 的窄屏纵向排列；iPad 宽屏把棋盘与信息分栏，小窗口按可用空间调整，说明较长时可以滚动。

导出前暂停 AI，在设置中导出 JSON 到「文件」等位置；导入先备份目标进度，导入会替换当前原生进度。原生备份不等于电脑版文件，也不等于 Touch JSON。请求提示立即标记辅助，即使没有实际按推荐走。

## 原有九章手册全部保留

- [入门、按钮、手势、iPhone / iPad 布局](../native/docs/zh-CN/01-start.md)
- [六种玩法](../native/docs/zh-CN/02-rules.md)与[能力和计分](../native/docs/zh-CN/03-expedition.md)
- [AI、纪录和备份](../native/docs/zh-CN/04-ai-data.md)
- [原生故障排查](../native/docs/zh-CN/05-faq.md)与[构建安装](../native/docs/zh-CN/06-build.md)
- [九段原生演示](../native/docs/zh-CN/07-gallery.md)、[解答](../native/docs/zh-CN/08-solutions.md)、[版本验证](../native/docs/zh-CN/09-release.md)

如果设备已安装 App，直接看操作章；如果拿到源码，先走构建章。Mac 主机上的原生测试和布局图不代替 iPhone / iPad 实机触摸、旋转、分屏、后台、VoiceOver 或帧率验收。

## Touch v1：单独的网页版

网页版与原生 App 分开使用，支持 Safari 触屏操作和添加到主屏幕。原生 App 的安装与操作请看本章前半部分。

1. 在 Safari 打开 [LUMINA 网页版](https://lumina-2048.vercel.app/)。无需注册或登录，也不需要 Vercel 账号。
2. 等首次完整加载，使用分享 → 添加到主屏幕。
3. 等离线准备完成后，再测试断网从主屏幕进入。首次打开前或资源未缓存完整时不能承诺离线。
4. 以棋盘内滑动或方向按钮游玩，也可用方向键 / WASD。
5. 设置里导出 JSON 备份；在另一台设备的 **Touch 版**导入，导入前先导出其原进度。

从旧网址搬到新网址时，先在旧网页的设置中「导出进度」，再到新网页「导入进度」。浏览器不会自动把旧网址的进度搬到新网址。原来的主屏幕图标也需要从新网址重新添加。

Touch 有六种玩法、提示、AI Worker、撤销重做、最近 100 次操作复盘、重生路线比较、明暗、声音和减少动态效果。打开菜单、后台和手动接管会暂停自动玩。它没有 Python 桌面版的完整快捷键，也不要按桌面 AI 毫秒档位理解它。

存档在当前站点 IndexedDB，带备份与离开页面的应急快照；不同浏览器、设备、主屏幕环境不自动同步。清网站数据、隐私浏览和系统回收存储都可能影响进度，先导出重要数据。网页改动后遇到旧界面，先导出，再联网重新打开等待更新，不要首先清空网站数据。

源码在 `mobile/`，本地 `python3 serve.py` 用于开发，默认不启用 Service Worker；手机正式使用需要 HTTPS。原生规则对照、网页自动测试与浏览器布局检查各有范围，不等于实体 iPhone / iPad 的离线冷启动、触感或系统手势已经通过。
