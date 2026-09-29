# Documentation QA / 文档验收 / 文書検証

Revision: 2026-09-29 · Game: 1.0.1 Native

## 中文

- 三种语言各九章，共 27 篇手册；另有独立中文、英文、日文 README，默认 README 为中文副本。
- 实际读取游戏规则、状态协调、界面按钮、存档、搜索及内置题目后编写；App / Sources 的生产代码未因本轮文档工作改变。
- 九段录制调用同一 GameModel，录制检查通过；开局、撤销重做、AI、能力、谜题胜利、残局胜利、每日重置及冲刺结算均有实际画面。
- 九段 H.264 MP4 共 726 帧完成软件解码检查，GIF 从交付 MP4 的解码帧生成。逐段比较 GIF / MP4 时长，差异小于 0.1 秒。文件有 SHA-256 清单。
- 549 处本地链接 / 锚点 / 媒体引用有效；36 条三语谜题解答路线与资源一致；README 和章节数量检查通过。
- 生成器和阅读器 JavaScript 语法检查通过；没有外部运行时脚本、字体或网络依赖。动图默认封面，需手动播放，可暂停。MP4 可展开控制播放。
- 已检查九段动图的开始、中间与末尾关键帧。静态拼图见 `evidence/media-contact.png`。
- 内置浏览器的本地文件 URL 安全策略阻止了 HTML 预览，未绕过该策略。因此**桌面 / 窄屏 HTML 视觉验收和浏览器按钮交互不能标记为已完成**；代码检查不替代实际浏览器验收。
- 仍无 iOS SDK / 真机录屏；媒体是 macOS 主机原生预览的采样教程，不是设备 FPS 证明。文档多语言不等于当前中文 UI 已本地化。

## English

Three complete nine-chapter handbooks, three localized READMEs and a Chinese default were checked against the current implementation. Production `App/` and `Sources/` were unchanged. The native recording check passed. Nine H.264 MP4s were software-decoded in full (726 frames); GIFs were made from those decoded videos, with duration differences under 0.1 s and per-file SHA-256 records.

Validation covers 549 local references, 36 translated puzzle routes, chapter counts and JavaScript syntax. Start, middle and end frames of all clips were visually inspected. The reader is self-contained and defaults animations to static posters.

The in-app browser blocked local-file HTML access under its URL security policy; no workaround was attempted. Desktop / narrow-screen HTML visual acceptance and actual browser button interaction remain unverified. Source checks do not replace browser testing. Media captures a macOS native preview, not an iOS device. The current app UI remains Chinese.

## 日本語

三言語各九章と三つの README を現行実装と照合しました。`App/` と `Sources/` の本体コードは未変更です。ネイティブ収録チェックは合格。九本の H.264 MP4 を全 726 フレーム復号して GIF に変換し、時間差は各 0.1 秒未満。各ファイルに SHA-256 を記録しています。

ローカル参照 549 件、三言語のパズル解答 36 件、章数、JavaScript 構文を確認し、各GIF アニメーションの開始・中間・最後を目視しました。説明書は外部通信なしで読め、GIF アニメーションの初期表示は静止画です。

内蔵ブラウザーの URL 安全ポリシーでローカル HTML が拒否され、回避はしていません。そのためデスクトップ・狭い画面の HTML 見た目や、実ブラウザーでのボタン操作は未検証です。ソース検査で代替済みとは扱いません。教材は macOS のネイティブプレビューで、iOS 実機映像ではありません。アプリ表示は引き続き中国語です。

## Evidence

- `evidence/native-capture.log`: optional native capture run and outcome.
- `evidence/media-build.log`: software video encoding and GIF generation.
- `evidence/document-validation.log`: document structure and reference checks.
- `evidence/media-contact.png`: first / middle / last GIF frames.
- `media/manifest.json`: individual media metadata and hashes.
