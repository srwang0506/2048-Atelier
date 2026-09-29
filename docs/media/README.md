# 演示媒体 / Media provenance / 実演媒体

## 中文

八段新增桌面演示由桌面 v12 的 `Atelier`、正式规则引擎和 pygame 渲染器实际运行产生。Mac 主机使用 SDL dummy 显示驱动采样，不是 Windows 实机录屏，也不是屏幕刷新率测试。临时存档完全隔离；拍摄工具没有读取玩家正常对局来演示。声音关闭，按 12 fps 输出 1080×820 JPEG 序列，经软件 FFmpeg 编成 H.264 MP4，再完整解码交付 MP4 生成 GIF。静止时相同帧可在 GIF 合并，但总时长保持。

`manifest.json` 记录每段操作时刻、最终模式 / 步数 / 分数、视频帧数、GIF 时长以及三种文件的 SHA-256。seed 42 用于经典与冲刺，seed 13 用于远征；每日由正式 `daily_game` 生成日期 2026-09-29 的挑战。谜题和练习用正式资源。AI 分析由实际后台进程计算，没有填入假分析结果。示例只展示片段，不宣传为完整高分纪录。

原生九段媒体及其独立出处保留于 [原生媒体说明](../native/docs/media/README.md)，是 Mac 上实际 SwiftUI / GameModel 的采样预览，不是 iPhone / iPad 录屏。没有新建 Windows、iOS 真机或 Web 录屏。

生成工具在 `tools/capture-desktop.py` 与 `tools/build-media.py`。录制需完整桌面源码及其依赖；可以用 `DESKTOP_SOURCE` 指定源码目录，`CAPTURE_OUT` 指定输出。转换需 Pillow 与 FFmpeg，使用 `FFMPEG` 指定可执行文件。文档工具依赖不属于新增的游戏运行依赖。原始帧在制作工作区保留，不装入发布 ZIP。

## English

Eight new clips run Desktop v12's actual Atelier UI, rules and pygame renderer on Mac with SDL dummy. They are not Windows hardware recordings or display-FPS measurements. A separate temporary profile is used; no normal player game is used for demonstrations. Silent 1080×820 JPEG frames are sampled at 12 fps, encoded to software H.264 MP4, then the delivered MP4 is fully decoded to create GIF. Identical frames may be coalesced in GIF without changing duration.

`manifest.json` contains action timings, final mode/moves/score, video frame counts, GIF duration and SHA-256 hashes. Classic/Sprint use seed 42, Expedition seed 13, and Daily uses the production `daily_game` for 2026-09-29. Puzzle/Rescue use production resources. AI output is computed by the actual background worker. Clips are instructional excerpts, not complete high-score records.

Nine retained native clips have [separate provenance](../native/docs/media/README.md). They sample real SwiftUI/GameModel execution on Mac, not iPhone/iPad screens. No Windows/iOS device or Web recordings were added.

Use `tools/capture-desktop.py` with the full desktop source and dependencies; set `DESKTOP_SOURCE` and optionally `CAPTURE_OUT`. `tools/build-media.py` requires Pillow and FFmpeg (`FFMPEG` sets the binary). Documentation tools do not add game runtime dependencies. Raw frames remain in the authoring workspace, outside release ZIPs.

## 日本語

追加八本は Mac 上でデスクトップ v12 の実際の Atelier・規則・pygame 描画を SDL dummy で動かした記録です。Windows 実機や画面 FPS の測定ではありません。専用の一時プロファイルを使い、通常のプレイヤーの局は使いません。無音・1080×820・12 fps の JPEG をソフトウェア H.264 MP4 にし、その配布動画を完全に復号して GIF を作ります。同一フレームは GIF 内で統合できますが、時間は保持します。

`manifest.json` に操作時刻、最終モード・手数・点数、動画フレーム数、GIF 時間、SHA-256 を記録します。通常／スプリントは seed 42、遠征は seed 13、デイリーは正式な `daily_game` による 2026-09-29 です。パズル・練習は正式資源を使用し、AI 結果も実ワーカーの計算です。教材の抜粋で、全編の高得点記録ではありません。

既存九本の原生動画には[別の出典](../native/docs/media/README.md)があります。Mac の SwiftUI / GameModel 表示で、iPhone / iPad 録画ではありません。Windows・iOS 実機・Web の録画は追加していません。

`tools/capture-desktop.py` は完全なデスクトップソースと依存関係を必要とし、`DESKTOP_SOURCE`、`CAPTURE_OUT` で場所を指定できます。`tools/build-media.py` は Pillow と FFmpeg を使い、`FFMPEG` で実体を指定します。文書ツールはゲームの新しい実行依存ではありません。元のフレームは制作領域に残し、配布 ZIP には含めません。
