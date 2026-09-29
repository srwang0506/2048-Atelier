# 文档验证 / Documentation QA / 文書検証

2026-09-29 · Desktop v12 / Native 1.0.1 build 2 / Touch v1

## 中文

本次为文档更新。新增三种语言各十二章全平台手册和三语根 README，完整保留原生三语九章。新增八段实际桌面游戏演示；连同已有九段原生演示，共十七个 GIF、十七个 MP4 与十七张封面。

- 文档验证脚本检查全部本地 Markdown / HTML 链接、HTML 锚点、章节数量、语言、十七段播放控件、三语谜题路线及媒体 SHA-256。原始结果见 `evidence/document-validation.log`。
- 桌面十二道谜题与三道练习经正式引擎重放；原生与桌面资源路线及初始盘面对照。结果见 `evidence/desktop-solutions.json`。
- 桌面捕获与转换见 `evidence/desktop-capture.log`、`evidence/desktop-media-build.log`。完整 MP4 解码帧数与源帧数一致，GIF 时长偏差小于 0.1 秒；关键帧汇总在 `evidence/desktop-contact.png`，人工检查可读性。
- Windows 附文档包仅增加 / 更新说明，不替换原游戏代码、exe、DLL、Python 运行环境、字体和资源。逐文件比对和 ZIP CRC 结果见根目录 `package-validation.json`。
- 外部游戏目录的个人存档在制作前后按 SHA-256 对比；文档录制只写临时独立存档。制作完成后的交付前核对在 `evidence/delivery-verification.json`。

离线 HTML 浏览器视觉与交互验收未完成：本机安全策略拒绝打开本地文档 URL，未尝试绕过。结构检查不等于浏览器点击验证；搜索、打印、跨语言导航、动图按钮仍应由读者实际试用。媒体关键帧独立检查，不把它记作 HTML 页面渲染验收。

桌面 v12 已有 90 项测试、原生 38 项检查等历史证据分别引用，未因文档更新重新声称验证所有设备。Windows 实机，以及 iPhone / iPad 的 iOS 构建、签名、触摸和性能仍未完成。线上 Touch 可用性未在此轮重新验证。

## English

Documentation-only update: twelve platform chapters per language, trilingual root READMEs and all nine original native chapters per language retained. Eight actual desktop clips plus nine native clips give seventeen GIFs, seventeen MP4s and seventeen posters.

The validator checks local Markdown/HTML links, HTML anchors, counts, languages, playable media, translated routes and media SHA-256 (`evidence/document-validation.log`). Twelve desktop puzzles and three practices are replayed with the real engine; resource comparisons are recorded in `evidence/desktop-solutions.json`. Capture/encoding logs and the reviewed contact sheet are in `evidence/`. Delivered MP4s are fully decoded; source/decoded frame counts match and GIF duration drift is under 0.1 seconds.

The Windows documentation package retains original executable, code, runtime, fonts and resources. File comparisons and CRC checks are in root `package-validation.json`. Original player-file hashes are checked before and after authoring, prior to delivery, while captures use a temporary profile (`evidence/delivery-verification.json`).

Offline HTML browser visual/interaction acceptance is incomplete: local-file URL access was rejected by security policy, with no bypass attempted. Structural checks do not prove search, print, language navigation or media buttons in a browser. Independently reviewed media frames are not HTML-render acceptance.

Earlier Desktop v12 and native test results remain edition-specific historical evidence. This update does not establish Windows hardware execution, an iOS SDK build/signing, physical iPhone/iPad input/performance, or current live Touch availability.

## 日本語

文書のみの更新です。三言語各十二章と三言語のルート README を追加し、既存の原生九章ずつを保持しています。実際のデスクトップ八本と原生九本で、GIF・MP4・表紙はそれぞれ十七点です。

検査はローカルリンク、HTML アンカー、章数、言語、媒体操作、翻訳解答、媒体ハッシュを対象にします。結果は `evidence/document-validation.log`。十二問と三練習を正式エンジンで再実行し、資源比較を `evidence/desktop-solutions.json` に記録します。採取・変換ログと目視したコンタクトシートも `evidence/` にあります。配布 MP4 を完全復号し、元フレーム数と一致、GIF の時間差は 0.1 秒未満です。

Windows 追加説明書パッケージは元の実行ファイル、ソース、環境、字体、資源を保持します。比較と CRC はルートの `package-validation.json`。個人ファイルは制作前後・交付前のハッシュで確認し、録画は一時プロファイルを使います（`evidence/delivery-verification.json`）。

オフライン HTML のブラウザー外観・操作確認は未完了です。安全ポリシーがローカル URL を拒否したため、回避は試していません。構造検査だけでは検索・印刷・言語移動・動画ボタンの動作確認にはなりません。媒体のフレーム確認も HTML の表示確認とは別です。

以前の v12・原生テストは版ごとの履歴です。今回の文書更新で Windows 実機、iOS SDK ビルド・署名、実 iPhone/iPad の入力・性能、公開 Touch の現在の可用性を検証したとはしていません。
