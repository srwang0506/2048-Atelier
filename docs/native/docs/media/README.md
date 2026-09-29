# Media provenance / 媒体说明 / メディアの出典

## 中文

九段演示来自 `Tests/LuminaAppTests/DocumentationCapture.swift`：在 macOS 15.3 的真实 NSHostingView 中运行同一个 GameModel、SwiftUI 视图、规则和搜索。动作由收录脚本调用实际操作入口，不是假造棋盘动画。采用独立临时存档，不接触玩家正常数据。

采样画面先组装为中间视频，再用软件 H.264 编码生成交付的 **1000 × 700、12 帧/秒 MP4**。`tools/build-media.py` 完整解码每个交付 MP4，再将视频帧转换成 GIF；共核对 726 帧。GIF 用 80/80/90 毫秒循环近似 12 帧/秒，重复帧可能合并，时长保持一致。PNG 为每段开头，可供暂停和打印。HTML 阅读器同时提供可暂停 GIF 和可拖动进度的 MP4 播放器。

这是主机原生预览的**采样教学录像**，不是 iOS 屏幕录制、触摸测试或实时性能评测。采样和写入本身耗时，不能用播放时长反推实际运行速度。底部英文条只属于录制工具，三语步骤说明在各自手册中。声音关闭。

经典从 seed 42 经 30 次真实引擎动作后的中盘开始；撤销 / AI 延续同局。远征 seed 42，能力检查点由实际游玩获得能量。谜题第 01 题，残局为“一线生机”，每日固定 2026-09-29，冲刺 seed 42 经 57 次移动后录制最后三步。录制核对谜题 / 残局胜利、每日重开相同、冲刺结束与能力可用。

脚本会为部分展示选择求解器建议，再通过手动操作入口演示。因此片中的手动区分只表示所调用的 App 入口，不代表宣称取得了真人竞技成绩。没有下载外部游戏录像或使用 AI 生成游戏图像。动作时间线、尺寸、时长、帧数、文件大小和 SHA-256 见 `manifest.json`。

## English

The nine clips use the real GameModel, SwiftUI views, rules and search in a live macOS 15.3 NSHostingView. The opt-in recorder calls actual action entry points and uses isolated temporary saves, leaving player data untouched.

Sampled frames are assembled into an intermediate video and software-encoded into delivered **1000 × 700, 12 fps H.264 MP4s**. The converter fully decodes each delivered MP4 before making its GIF; 726 video frames are checked. GIF timing uses an 80/80/90 ms cycle, with duplicate frames optionally combined while preserving duration. PNG posters show the opening frame. The HTML reader offers both pausable GIFs and seekable MP4 players.

These are instructional native-host captures, not iOS screen recordings, touch tests or real-time performance measurements. Capture overhead means playback duration does not measure wall-clock game speed. The bottom English strip belongs to the recorder; each language's gallery explains the steps. Sound is disabled.

Classic uses seed 42 after 30 engine actions; undo and AI continue that run. Expedition uses seed 42 and legitimately earned energy. Puzzle 01, the first Rescue practice, Daily 2026-09-29 and Sprint seed 42 after 57 moves are shown. The recorder checks wins, the identical Daily reset, powers and the 60-move finish.

Some scripted demonstration moves are chosen with solver suggestions and executed through manual action entry points. A manual label in this footage is not a claim of human competitive achievement. No external footage or AI-generated gameplay imagery is used. Event times, sizes, durations, frame counts and SHA-256 values are in `manifest.json`.

## 日本語

九本とも macOS 15.3 の実際の NSHostingView で、本体と同じ GameModel、SwiftUI、ルール、探索を実行します。本来の操作関数を呼び、独立した一時保存先を使うため、通常のプレイヤーデータは変更しません。

採取フレームを中間動画にまとめ、ソフトウェアで **1000 × 700、12 fps の H.264 MP4** に変換します。同梱する MP4 を全フレーム復号してから GIF を作り、合計 726 フレームを確認します。GIF は 80/80/90 ミリ秒を繰り返し、重複フレームをまとめても総時間を保持します。PNG は開始フレーム。HTML は停止可能な GIF と、シークできる MP4 の両方に対応します。

iOS 画面録画、タッチ試験、実時間の性能測定ではなく、ホスト環境の動作を採取した教材です。収録処理に時間がかかるため、再生時間から実際のゲーム速度は判断できません。下の英語帯は収録ツールの注釈で、各言語の手順はギャラリーにあります。音声は無効です。

クラシックは seed 42 の 30 操作後から、戻すと AI はその続きを使います。遠征も seed 42、実操作で獲得したエネルギーを使用。パズル 01、最初のレスキュー、2026-09-29 のデイリー、seed 42 の 57 手目以降のスプリントを収録し、クリア、同じ初期盤面、能力条件、60 手終了を確認します。

一部の教材操作はソルバーの候補を使い、手動操作用の入口で実行します。映像の手動区分は人間の競技記録を主張するものではありません。外部映像や生成 AI によるゲーム画像は不使用。時間軸、寸法、長さ、容量、フレーム数、SHA-256 は `manifest.json` にあります。

## Reproduce / 重新生成 / 再生成

From the project root on a working macOS Swift toolchain:

```sh
LUMINA_CAPTURE_DIRECTORY=/tmp/lumina-documentation-media swift test -c release --disable-xctest --filter recordDocumentation
python3 tools/build-media.py /tmp/lumina-documentation-media
python3 tools/write-doc-extras.py
node tools/build-docs.mjs
python3 tools/validate-docs.py
```

`build-media.py` requires Pillow and software FFmpeg. Set `FFMPEG` to the executable, or install [imageio-ffmpeg](https://pypi.org/project/imageio-ffmpeg/), version 0.6.0 used here. It is a documentation tool dependency, not included in or required by the app.

`build-docs.mjs` requires Node and `marked`, or `MARKED_MODULE` pointing to its ESM file. Generated HTML uses no external scripts, fonts or network requests. This development machine used the temporary compiler overlay documented in `QA.md`; normal Xcode installations do not need that workaround.
