from pathlib import Path
import json,shutil
root=Path(__file__).resolve().parents[1];docs=root/'docs'
chapters=['01-platforms','02-controls','03-rules','04-expedition','05-ai-replay','06-saves','07-macos','08-windows','09-mobile','10-gallery','11-solutions','12-support']
titles={
'zh-CN':['先选平台与版本','桌面版入门与完整操作','桌面版六种玩法与计分','桌面版能力远征详解','桌面版 AI、教练与复盘','存档、备份、迁移与升级','macOS 安装与排错','Windows 安装与排错','iPhone、iPad 与网页版','十七段游戏动图与视频','十二章谜题与三道残局解答','常见问题、开发与验证'],
'en':['Choose a platform and edition','Desktop quick start and controls','Desktop modes and scoring','Desktop Expedition in depth','Desktop AI, Coach and Replay','Saves, backup, transfer and updates','macOS installation and troubleshooting','Windows installation and troubleshooting','iPhone, iPad and the web edition','Seventeen animated demonstrations','Twelve puzzles and three Rescue solutions','FAQ, development and validation'],
'ja':['プラットフォームと版を選ぶ','デスクトップ版の始め方と操作','デスクトップ版のモードと得点','デスクトップ版・能力遠征の詳細','デスクトップ版の AI・コーチ・リプレイ','セーブ・バックアップ・移行・更新','macOS の導入とトラブル対処','Windows の導入とトラブル対処','iPhone・iPad・Web 版','十七本のゲーム実演','十二問のパズルと三問のレスキュー解答','よくある質問・開発・検証']}
for lang in titles:(docs/lang).mkdir(parents=True,exist_ok=True)
(docs/'catalog.json').write_text(json.dumps(dict(chapters=chapters,titles=titles),ensure_ascii=False,indent=2))
def w(lang,index,text):
 (docs/lang/(chapters[index-1]+'.md')).write_text('# '+titles[lang][index-1]+'\n\n'+text.strip()+'\n',encoding='utf-8')

w('zh-CN',1,r'''
本手册覆盖 **Mac、Windows、iPhone、iPad 和 Web**。它们属于同一个游戏系列，但并非同一个安装包；版本号、界面和存档格式分别管理。文档基于 2026-09-29 的现有代码与交付文件。

## 按你的设备开始

| 设备 / 版本 | 交付形态与启动入口 | 阅读入口 |
|---|---|---|
| Mac · Python 桌面版 v12 | 游戏目录内双击 `启动游戏.command`；首次准备需要兼容 Python | [Mac 安装](07-macos.md) → [桌面操作](02-controls.md) |
| Windows · Python 桌面版 v12 | 完整解压 Windows x64 便携 ZIP，双击 `2048.exe` | [Windows 安装](08-windows.md) → [桌面操作](02-controls.md) |
| iPhone / iPad · Native 1.0.1，build 2 | SwiftUI 原生源码工程；需 Xcode、iOS SDK 与签名后安装 | [原生 App 说明](09-mobile.md) → [九章原生手册](../native/docs/zh-CN/index.html) |
| 浏览器 · Touch v1 | 独立 Web / PWA，Safari 可添加到主屏幕 | [网页版说明](09-mobile.md) |

Windows 包面向 Windows 10 / 11 的 Intel、AMD x64 电脑。Mac 当前已在 Apple Silicon 主机运行；其他 Mac 需按依赖安装结果核验。原生工程目标是 iOS / iPadOS 16.4 及以上；尚未在本环境完成 iOS 构建、签名和设备验收。**原生源码不是可直接安装的 IPA；Web 添加主屏幕也不等于原生 App。**

## 同样的游戏，有各自的功能

| 功能 | Mac / Windows v12 | iPhone / iPad Native 1.0.1 | Touch v1 |
|---|---|---|---|
| 六种玩法、经典在前 | 有 | 有 | 有 |
| 提示 / AI 自动玩 / 撤销重做 | 有 | 有 | 有 |
| 自动分析教练 | 有，C 键 | 无桌面版同等入口 | 无桌面版同等入口 |
| 通用最近 100 步复盘 | 有，R 键 | 无；有重生路线对照 | 有 |
| 游戏内 JSON 导入导出 | 无，备份存档文件 | 有 | 有 |
| P 键截图 / F 全屏 | 有 | 使用系统功能 | 使用浏览器 / 系统功能 |
| 存档位置 | 本地文件 | App 沙盒 | 浏览器站点存储 |

三语的是**文档**，当前游戏主界面的标签主要是中文。英语和日语说明会保留按钮的中文名称，方便你对照寻找。没有自动跨设备云同步，也没有统一线上排行榜。版本之间不要互相导入存档；Mac 与 Windows **同版 v12** 可按[文件迁移步骤](06-saves.md)操作。

## 阅读顺序

第一次玩：先安装对应版本，再读操作与规则；需要高分辅助时看 AI 章节。能力远征的数值单独列在第四章。需要搬电脑或升级先看存档章节。第十一章包含完整解答，请在自己尝试后再打开。

离线阅读时保留整个文件夹。打开 `docs/index.html` 选择语言；侧栏可搜索当前语言的十二章内容，原生九章手册有独立搜索。切换语言会保留所在章节；动图默认静止，点播放后开始，也可展开 MP4 逐段观看。不会因为阅读文档而上传或改动游戏进度。
''')
w('en',1,r'''
This handbook covers **Mac, Windows, iPhone, iPad and Web**. They belong to one game family but use separate builds, version numbers, interfaces and save formats. This edition describes the source and delivery files available on 2026-09-29.

## Start with your device

| Device / edition | Delivery and launch | Read next |
|---|---|---|
| Mac · Python Desktop v12 | Double-click `启动游戏.command` in the game folder; first-time setup needs compatible Python | [Mac installation](07-macos.md), then [controls](02-controls.md) |
| Windows · Python Desktop v12 | Fully extract the Windows x64 portable ZIP; open `2048.exe` | [Windows installation](08-windows.md), then [controls](02-controls.md) |
| iPhone / iPad · Native 1.0.1, build 2 | SwiftUI source project; install after building and signing with Xcode and an iOS SDK | [App overview](09-mobile.md), then [nine-chapter native manual](../native/docs/en/index.html) |
| Browser · Touch v1 | Separate Web / PWA edition; Safari can add it to the Home Screen | [Web instructions](09-mobile.md) |

The Windows package targets Intel/AMD x64 computers running Windows 10/11. Mac execution has been checked on an Apple Silicon host; other Macs require dependency and runtime checks. The native project targets iOS/iPadOS 16.4 or later. An iOS build, signing and device acceptance remain outstanding in this environment. **Native source is not an installable IPA; a Home Screen web app is a different edition.**

## Feature differences

| Feature | Mac / Windows v12 | Native 1.0.1 | Touch v1 |
|---|---|---|---|
| Six modes, Classic first | Yes | Yes | Yes |
| Hints, autoplay, undo/redo | Yes | Yes | Yes |
| Automatic Coach analysis | Yes, C | No equivalent desktop control | No equivalent desktop control |
| General last-100-action Replay | Yes, R | No; Rescue has route comparison | Yes |
| In-game JSON import/export | No; copy save files | Yes | Yes |
| P screenshot / F fullscreen | Yes | Use system controls | Use browser/system controls |
| Storage | Local files | App sandbox | Browser site storage |

The **documentation** is trilingual; current game labels are primarily Chinese. English and Japanese instructions retain Chinese button labels to help you find them. There is no automatic cross-device cloud sync or shared online leaderboard. Do not import saves across editions. **Matching desktop v12** saves can be moved between Mac and Windows using the [file-transfer procedure](06-saves.md).

## How to use this handbook

Install the correct edition, read controls and rules, then explore AI assistance. Chapter 4 contains Expedition numbers; chapter 6 covers backups before updates or computer changes. Chapter 11 contains full solutions and spoilers.

Keep the whole folder for offline reading. Open `docs/index.html` and choose a language. Search covers the twelve chapters in that language; the separate native manual has its own search. Language switching preserves the chapter. GIFs start paused; press Play or expand the MP4 player. Reading the manual does not upload or modify game progress.
''')
w('ja',1,r'''
この説明書は **Mac・Windows・iPhone・iPad・Web** を対象にしています。同じゲームシリーズですが、配布物、バージョン番号、画面、セーブ形式はそれぞれ異なります。2026-09-29 時点のソースコードと配布ファイルに基づく説明です。

## 使う端末から選ぶ

| 端末・版 | 配布形式と起動方法 | 読むページ |
|---|---|---|
| Mac・Python デスクトップ版 v12 | ゲームフォルダーの `启动游戏.command` をダブルクリック。初回準備には対応する Python が必要 | [Mac の導入](07-macos.md) → [操作](02-controls.md) |
| Windows・Python デスクトップ版 v12 | Windows x64 用 ZIP を完全に展開し、`2048.exe` を開く | [Windows の導入](08-windows.md) → [操作](02-controls.md) |
| iPhone / iPad・Native 1.0.1、build 2 | SwiftUI のソースプロジェクト。Xcode と iOS SDK でビルド・署名して導入 | [App の概要](09-mobile.md) → [全九章の原生版説明書](../native/docs/ja/index.html) |
| ブラウザー・Touch v1 | 独立した Web / PWA 版。Safari からホーム画面に追加可能 | [Web 版の説明](09-mobile.md) |

Windows パッケージの対象は Windows 10 / 11 の Intel・AMD x64 PC です。Mac は Apple Silicon の開発機で動作確認しています。他の Mac は依存関係と実行環境の確認が必要です。原生版の設定は iOS / iPadOS 16.4 以上を対象としていますが、この環境では iOS ビルド・署名・端末検証が未完了です。**ソース一式はそのままインストールできる IPA ではありません。ホーム画面に追加した Web 版も別の版です。**

## 版ごとの機能

| 機能 | Mac / Windows v12 | Native 1.0.1 | Touch v1 |
|---|---|---|---|
| 六つのモード・クラシックを先頭に配置 | あり | あり | あり |
| ヒント・自動プレイ・取り消し／やり直し | あり | あり | あり |
| 自動分析コーチ | C キー | 同等のデスクトップ操作なし | 同等のデスクトップ操作なし |
| 通常の直近 100 操作リプレイ | R キー | なし。レスキューのルート比較はあり | あり |
| ゲーム内 JSON 読み込み／書き出し | なし。ファイルをコピー | あり | あり |
| P で撮影・F で全画面 | あり | OS の機能を使用 | ブラウザー・OS の機能を使用 |
| 保存場所 | ローカルファイル | App のサンドボックス | サイトのブラウザーストレージ |

三言語に対応するのは**説明書**です。現在のゲーム表示は主に中国語で、英語・日本語の説明にも操作ボタンの中国語名を併記しています。端末間の自動クラウド同期や共通オンラインランキングはありません。異なる版のセーブは互換ではありません。Mac と Windows の**同じ v12** は[ファイル移行手順](06-saves.md)で移せます。

## 読み方

対応する版を導入し、操作とルールから始めてください。遠征の数値は第 4 章、更新・引っ越し前のバックアップは第 6 章です。第 11 章には解答があるので、自分で挑戦してから開くことをおすすめします。

オフラインで読むにはフォルダー全体を保持し、`docs/index.html` で言語を選びます。検索対象はその言語の十二章です。原生版の九章には別の検索があります。言語を切り替えても同じ章を開きます。GIF は最初は静止画で、再生ボタンか MP4 プレイヤーで動きを確認できます。説明書を読むだけでゲームの進行が変更・送信されることはありません。
''')

w('zh-CN',2,r'''
本章只适用于 **Mac / Windows 桌面 v12**，两个系统的游戏操作相同。

## 第一次开局

1. 打开游戏，进入「选择玩法」。默认是「经典与挑战」，经典占左侧主卡。
2. 点击「经典」开始。上方显示得分与最佳，中央是 4×4 棋盘。
3. 按方向键或 WASD，或在棋盘上用鼠标按住拖动。整盘方块一起移动，不能拖动单个方块。
4. 合并相同数字，留出空格。新手先用手动方式玩几步，再尝试提示。
5. 点左上角模式名称或 B 返回大厅；「精选玩法」里有能力远征与绝境重生。「继续当前局」返回当前棋盘。切换玩法分别保留进度。

## 全部快捷键

| 按键 | 对局中的作用 |
|---|---|
| ↑ ↓ ← → / W S A D | 滑动；手动输入可接管 AI |
| 空格 | 开启 / 暂停自动玩 |
| Z | 撤销 |
| Shift+Z / Y | 重做 |
| H | 请求提示 |
| Enter | AI 走一步 |
| C | 开关教练；实际分析会计入辅助 |
| R | 打开复盘 |
| B | 模式大厅 |
| N | 新开当前玩法；有确认时按提示完成 |
| T / M | 切换明暗 / 音效 |
| F / P | 全屏 / 保存截图 |
| F1 | 玩法与操作帮助 |
| Esc | 关闭面板、退出全屏或暂停，取决于当前状态 |

复盘面板中，← / → 是前后帧，Home 是起点，End 是当前末帧，空格播放 / 暂停。输入快捷键前让游戏窗口获得焦点。按钮也可用鼠标点击；触控滑动取决于系统和 SDL 设备支持，未把桌面触控作为所有电脑的保证。

## 关键操作的区别

**撤销**会回退棋盘、得分、步数及随机状态；**重做**恢复被撤销的一步。撤销后走另一方向会开始新分支，旧分支不能再重做。保留最近 100 步历史，已保存的历史重启后可以继续用；辅助标记不随撤销清除。

**复盘**只是查看过去，不会改当前棋盘；**原局重试**重开固定谜题 / 重生挑战；**新开一局**会替换该模式当前进度，其他模式进度保留。每日新开是重试当前挑战日期，进入今天请经过大厅。

## 设置与显示

右上圆形设置按钮包含 AI 档位、游玩速度、明暗、音效、动画、全屏、战绩和玩法等入口。AI 的思考档位与自动玩的播放速度是两项不同设置。冲分速度会跳过逐步动画；想观看动效请选择正常或慢速并开启动画。

P 截图保存在[本机 exports 目录](06-saves.md)，不是剪贴板。截图失败只会提示，不应退出游戏。屏幕截图文件名避免同秒覆盖。关闭窗口后等保存完成再拔出移动硬盘；不要直接终止进程代替正常退出。
''')
w('en',2,r'''
This chapter applies to **Mac / Windows Desktop v12**. Both platforms use the same game controls.

## Your first game

1. Launch the game to open 「选择玩法」 (mode selection). 「经典与挑战」 is the default page; the large Classic card is on the left.
2. Select 「经典」. Scores are at the top, with a 4×4 board in the center.
3. Use arrows, WASD or a mouse drag on the board. A move slides the whole board; you cannot drag individual tiles.
4. Merge equal numbers and keep space available. Try a few manual moves before requesting a hint.
5. Click the mode title or press B to return. 「精选玩法」 contains Expedition and Rescue. 「继续当前局」 resumes the current board. Each mode retains its own progress.

## Keyboard reference

| Key | During play |
|---|---|
| Arrows / WASD | Slide; manual input can take over from AI |
| Space | Start / pause autoplay |
| Z | Undo |
| Shift+Z / Y | Redo |
| H | Request a hint |
| Enter | One AI move |
| C | Toggle Coach; an actual analysis counts as assistance |
| R | Open Replay |
| B | Mode lobby |
| N | Restart the current mode; complete a confirmation if shown |
| T / M | Toggle appearance / sound |
| F / P | Fullscreen / save screenshot |
| F1 | Rules and control help |
| Esc | Close a panel, leave fullscreen or pause, depending on state |

Inside Replay, Left/Right step between frames, Home selects the beginning, End selects the current final frame and Space plays/pauses. Focus the game window before using shortcuts. Buttons also work with a mouse. Desktop touch depends on the OS and SDL input device support; it has not been validated on every touchscreen computer.

## Undo, Replay and restart are different

**Undo** restores board, score, move count and random state. **Redo** restores the undone action. Making a different move after Undo creates a new branch and discards the previous redo branch. Up to 100 actions are retained; saved history survives restart. Assistance flags remain after Undo.

**Replay** only views history. **原局重试** restarts the fixed Puzzle/Rescue challenge. **新开一局** replaces the current game of that mode, keeping other modes. Restarting Daily retries its current challenge date; use the lobby to enter today's challenge.

## Settings and display

The round settings button at the upper right contains AI quality, playback speed, light/dark appearance, sound, animation, fullscreen, records and help. AI thinking quality and autoplay speed are separate settings. 「冲分」 skips step-by-step animations; choose normal/slow speed with animation enabled to watch transitions.

P saves a file in [the local exports folder](06-saves.md), rather than the clipboard. Screenshot failures show a message without intentionally exiting; filenames avoid same-second overwrites. Close normally and let saving finish before disconnecting an external drive.
''')
w('ja',2,r'''
この章は **Mac / Windows のデスクトップ版 v12** 用です。両 OS でゲーム内の操作は共通です。

## 最初の一局

1. 起動すると「选择玩法」（モード選択）が開きます。最初の「经典与挑战」ページでは左の大きなカードがクラシックです。
2. 「经典」を選びます。上部に得点、中央に 4×4 の盤面があります。
3. 矢印キー、WASD、または盤面上のマウスドラッグで動かします。盤面全体が動き、個別のタイルをつかむ操作ではありません。
4. 同じ数字を合体させ、空きマスを残します。まず手動で数手遊んでからヒントを試してください。
5. 左上のモード名か B でロビーへ。「精选玩法」に遠征とレスキューがあり、「继续当前局」で現在の盤面に戻ります。モードごとに進行を保持します。

## キーボード一覧

| キー | 対局中の動作 |
|---|---|
| 矢印 / WASD | スライド。AI から手動操作に戻れる |
| Space | 自動プレイ開始／停止 |
| Z | 取り消し |
| Shift+Z / Y | やり直し |
| H | ヒントを依頼 |
| Enter | AI が一手進める |
| C | コーチの切り替え。実際の分析は補助使用扱い |
| R | リプレイ |
| B | モード選択 |
| N | 現在のモードをやり直す。確認が出た場合は内容に従う |
| T / M | 明暗／音の切り替え |
| F / P | 全画面／画像保存 |
| F1 | ルールと操作のヘルプ |
| Esc | 状況に応じてパネルを閉じる、全画面解除、停止 |

リプレイ内では ← / → が前後のフレーム、Home が先頭、End が現在の最終フレーム、Space が再生／停止です。キー操作の前にゲームウィンドウを選択してください。マウスでも各ボタンを押せます。デスクトップのタッチ操作は OS と SDL の入力機器対応に依存し、すべてのタッチ PC で検証したものではありません。

## 取り消し・リプレイ・再挑戦

**取り消し**は盤面、得点、手数、乱数状態を戻します。**やり直し**は取り消した操作を復元します。取り消した後に別の手を選ぶと分岐し、元の分岐はやり直せません。直近 100 操作まで保持し、保存済み履歴は再起動後も利用できます。補助使用の印は取り消しでは消えません。

**リプレイ**は履歴の閲覧だけです。**原局重试**は固定パズル・レスキューの再挑戦、**新开一局**はそのモードの進行を置き換える操作です。他のモードは保持します。デイリーの再開局は現在の日付の課題をやり直します。今日の課題へはロビーから入ってください。

## 設定と表示

右上の丸い設定ボタンには AI の品質、速度、明暗、効果音、アニメーション、全画面、記録、遊び方などがあります。AI の思考時間と自動プレイの速度は別の設定です。「冲分」は一手ずつのアニメーションを省きます。動きを見る場合は通常または低速とアニメーション有効を選びます。

P の画像は[端末の exports フォルダー](06-saves.md)へ保存され、クリップボードではありません。保存に失敗した場合はメッセージを表示します。同じ秒の連続撮影でも別名を使います。外付けディスクを外す前に、正常終了してセーブの完了を待ってください。
''')

w('zh-CN',3,r'''
## 合并的基本规则

4×4 棋盘，每次向一个方向滑到底；相邻同数合并成双倍。一次滑动中新生成的合并方块不会再合并。向左例子（均为落新方块之前）：

| 原行 | 结果 | 加分 |
|---|---|---:|
| 2, 2, 2, 2 | 4, 4, 0, 0 | 8 |
| 2, 2, 4, 0 | 4, 4, 0, 0 | 4 |
| 4, 0, 4, 4 | 8, 4, 0, 0 | 8 |

一次有效移动后，通常在空位生成 2（90%）或 4（10%）。无效方向不产生新方块、不消耗步数，也不推进随机序列。远征的能力可改变落子与分数。满盘不一定结束：只要有相邻同数仍能继续。

## 经典与每日同局

经典没有步数上限，达到 2048 后继续追求更大数字，无合法移动才结束。合并得到的数字计为本次基础分，例如 8+8 合成 16 得 16 分。

每日同局以日期固定种子。同日期、相同操作序列可复现落子；仅日期相同而操作不同不保证相同盘面。从大厅进入今天；重开当前局沿用该局日期。本机保留最近七个已保存日期的进度，没有旧日期选择器和联网排名。

## 六十步冲刺

60 次有效移动内争取高分，无法移动会提前结束。撤销回退已用步数；按不能移动的方向不扣步。手动与含辅助成绩分别记录，得分不计入经典最高分。单纯用完 60 步不会生成重生挑战，实际堵死才会进入败局提取条件。

## 解局剧场：十二章

固定开局与随机状态，目标从 64 到 2048。最短解 2–5 步，每章允许比最短解多一步，因此上限 3–6 步。右侧显示剩余步数与下一枚方块；重试同一路线重现落子，改变方向会影响可用落点。

| 通关条件 | 星级 |
|---|---|
| 无辅助、无撤销，在最短步数内达标 | 三星 |
| 其他无辅助通关 | 二星 |
| 使用辅助后通关 | 一星 |

每章保留历史最高星级。再次选择同一未完成章会续玩；「原局重试」才重置该章。选择别章会替换当前谜题进度，已获星级保留。设置内 AI 分析可以看确定下一步、余下步数内的可解性与完整路线。阅读解答属于剧透。

## 绝境重生：六步救回空间

经典、每日或冲刺因无路可走而结束时，后台检查最近最多十步。候选局面须只有零或一个空格，并能在六次有效移动内达到至少三个空格、继续可移动。搜索按完整随机状态求最短路，再用正式引擎验证后才入库。

进入重生是独立挑战，零分零步开始；原败局保存，切回相应模式仍在。可重试、撤销、提示、自动玩。手动与辅助最佳步数分开保存。进行中打开「路线对照」会标记辅助；它显示本次 / 原败局与验证路线，可逐步比较。撤销不清除辅助标记。

最近六个个人残局保存在本机，当前挑战保留。没有个人样本时可选三道明确标为练习的残局，最短解分别 3、5、5 步。不是每盘败局都能提取；搜索有时限，未找到不等于证明无解。

## 能力远征与公平记录

远征是六关、限步得分、能力构筑与主动技能，详见[下一章](04-expedition.md)。它的分数不进入经典纪录。

提示、实际教练分析、AI 单步与自动玩属于辅助，影响本局的辅助标记；撤销不能洗掉。玩法中各自使用星级、最佳分或最佳步数，不能把远征倍率分与经典得分直接比较。外部手册提供的解答不能被游戏自动检测，请自行区分独立解题与参考解答练习。
''')
w('en',3,r'''
## The merge rule

On a 4×4 board, slide all tiles as far as possible in one direction. Adjacent equal values merge into double their value. A newly merged tile cannot merge again in the same move. Left-move examples, before the new tile spawns:

| Before | After | Score gained |
|---|---|---:|
| 2, 2, 2, 2 | 4, 4, 0, 0 | 8 |
| 2, 2, 4, 0 | 4, 4, 0, 0 | 4 |
| 4, 0, 4, 4 | 8, 4, 0, 0 | 8 |

A valid move normally spawns a 2 (90%) or 4 (10%) in an empty cell. Invalid moves do not spawn a tile, consume a move or advance randomness. Expedition abilities can change scoring and spawning. A full board is not necessarily lost: adjacent equal values can still merge.

## Classic and Daily

Classic has unlimited moves. Reaching 2048 does not end play; keep going until no legal move remains. A merge awards the resulting value: 8+8 makes 16 and awards 16 base points.

Daily uses a date-based seed. The same date **and action sequence** reproduce spawns; the same date with different moves does not imply the same board. Enter today's challenge through the lobby. Restart keeps the current challenge date. Up to seven saved dates are retained locally, without an older-date picker or online leaderboard.

## 60-Move Sprint

Score as much as possible in 60 valid moves, or until the board becomes immobile. Undo restores the move allowance; invalid directions cost nothing. Manual and assisted best scores are separate and do not contribute to the Classic best. Merely reaching move 60 does not trigger Rescue extraction; a blocked board can.

## Puzzle Theatre: twelve chapters

Each chapter has a fixed board and random state, with targets from 64 to 2048. Shortest solutions take 2–5 moves. The limit is one move above par: 3–6 moves. The side panel shows remaining moves and the next tile value. Retrying the same route reproduces spawns; a different direction changes available spawn locations.

| Completion | Stars |
|---|---|
| No assistance, no undo, finish within par | Three |
| Any other unassisted completion | Two |
| Completion with assistance | One |

Each chapter retains its highest star result. Re-selecting the same unfinished chapter resumes it; 「原局重试」 resets it. Selecting another chapter replaces the current puzzle board but keeps earned stars. AI analysis can show the deterministic next board, solvability within remaining moves and the full route. Solutions are spoilers.

## Rescue: recover space in six moves

When Classic, Daily or Sprint ends because no slide is possible, a background search examines up to ten recent positions. A candidate must have zero or one empty cell and permit recovery to at least three empty cells with continued legal movement within six valid moves. Search preserves full random state, finds a shortest route and verifies it through the real engine before offering a challenge.

Rescue starts as a separate zero-score, zero-move game. The original loss remains intact in its own mode. Retry, undo, hints and autoplay are available. Manual and assisted best move counts are stored separately. Opening 「路线对照」 while the challenge is in progress marks assistance; it compares your route or the original loss with the verified route, step by step. Undo does not clear assistance.

Up to six personal challenges are retained, preserving the current one. Three clearly labelled practice challenges are available, with shortest routes of 3, 5 and 5 moves. Not every loss yields a challenge. Search has a time limit; no result does not prove impossibility.

## Expedition and record categories

Expedition combines six score-target stages, move limits, ability choices and active powers. See [chapter 4](04-expedition.md). Its score is separate from Classic.

Hints, actual Coach analysis, AI single moves and autoplay count as assistance. Undo cannot remove that flag. Modes use different records—stars, score or moves—so multiplied Expedition scores are not directly comparable to Classic. The game cannot detect that you read an external solution; distinguish independent solving from practice with a known route.
''')
w('ja',3,r'''
## 合体の基本

4×4 の盤面全体を一方向へ動かし、隣り合う同じ数字を倍の数字に合体させます。その手で合体したタイルは、同じ手の中では再合体しません。左へ動かした例です。新しいタイルが出る前の状態を示します。

| 移動前 | 移動後 | 加点 |
|---|---|---:|
| 2, 2, 2, 2 | 4, 4, 0, 0 | 8 |
| 2, 2, 4, 0 | 4, 4, 0, 0 | 4 |
| 4, 0, 4, 4 | 8, 4, 0, 0 | 8 |

有効な移動後は通常、空きマスに 2（90%）または 4（10%）が出ます。動かない方向は手数を消費せず、出現も乱数の進行もありません。遠征では能力によって得点・出現規則が変わります。満杯でも隣り合う同数があれば続けられます。

## クラシックとデイリー

クラシックは手数無制限です。2048 に達しても続けられ、合法手がなくなると終了します。合体した数字が基本点になり、8+8→16 なら 16 点です。

デイリーは日付に基づくシードを使います。同じ日付と操作順なら出現を再現できますが、操作が異なれば同じ盤面にはなりません。今日の課題はロビーから開きます。再開局は現在の課題の日付を維持します。保存済みの直近七日分を保持し、古い日付を選ぶ画面やオンライン順位表はありません。

## 60 手スプリント

有効な 60 手で高得点を目指します。途中で動けなくなると早期終了します。取り消しは残り手数も戻し、無効な方向は手数を消費しません。手動と補助使用の最高得点は別で、クラシックの最高点には入りません。60 手を使い切っただけではレスキューを抽出せず、盤面が詰まった場合が対象です。

## パズルシアター：十二章

初期盤面と乱数状態が固定され、目標は 64～2048 です。最短解は 2～5 手、上限は最短より一手多い 3～6 手です。横の欄に残り手数と次の数字を表示します。同じ手順の再挑戦では同じ出現になり、方向を変えると空きマスも変わります。

| 達成条件 | 星 |
|---|---|
| 補助なし・取り消しなし・最短手数以内 | 三つ |
| その他の補助なしクリア | 二つ |
| 補助使用後にクリア | 一つ |

各章の最高評価を保持します。同じ未完了の章を選ぶと続きから始まり、「原局重试」でリセットします。別の章を選ぶと現在のパズル盤面は置き換わりますが、星は残ります。AI 分析では確定した次の盤面、残り手数で解けるか、全手順を確認できます。解答を見る操作はネタバレになります。

## レスキュー：六手で空間を取り戻す

クラシック・デイリー・スプリントが移動不能で終わると、バックグラウンドで直近最大十手を調べます。空きが 0 または 1 マスで、六手以内に三マス以上の空きを作り、移動可能な盤面に戻せる局面が候補です。乱数状態を保持して最短経路を探索し、正式なエンジンで再実行してから出題します。

独立した課題として 0 点・0 手から始め、元の敗局は元のモードに残します。再挑戦、取り消し、ヒント、自動プレイを使えます。手動・補助使用の最少手数は別々に記録します。進行中に「路线对照」を開くと補助使用となります。自分の手順または元の敗局と、検証済み解答を一手ずつ比較できます。取り消しでも補助の印は消えません。

個人の残局は直近六件まで保持し、現在の課題を残します。練習と明記した三問もあり、最短解は 3・5・5 手です。すべての敗局から出題されるわけではありません。探索には時間制限があり、未発見は「解なし」の証明ではありません。

## 遠征と記録の区別

遠征は六ステージの得点目標、手数制限、能力選択、能動スキルを組み合わせます。[第 4 章](04-expedition.md)に詳細があります。得点はクラシックの記録とは別です。

ヒント、実際のコーチ分析、AI の一手、自動プレイは補助使用です。取り消しでは解除できません。星・得点・手数など記録形式が違うため、倍率のある遠征の得点をクラシックと直接比較できません。外部説明書の解答閲覧はゲームから検出できません。独力の挑戦と解答を知った練習を区別してください。
''')
# Shared numerical rules are checked against desktop expedition.py. Adapt the UI instructions.
for lang in titles:
 text=(root/'docs/native/docs'/lang/'03-expedition.md').read_text().split('\n',1)[1]
 text=text.replace('(07-gallery.md)','(10-gallery.md)')
 text=text.replace('点交换，依次点两枚不同数值的非空方块','点交换，选两枚不同数值的非空方块，再点「确认交换」')
 text=text.replace('Tap 交换, then two occupied tiles with different values','Click 交换, select two occupied tiles with different values, then 确认交换 (Confirm swap)')
 text=text.replace('交換を押し、値の異なる二枚を選ぶ','交換を押し、値の異なる二枚を選んで「确认交换」で確定する')
 note={'zh-CN':'本章适用于桌面 v12。三选一奖励一旦生成就固定，关闭面板或重启不能刷新。远征单独保留至多 12 场较高成绩及能力组合，按通关数与分数排序。','en':'This chapter covers Desktop v12. Reward offers are fixed when generated; closing a panel or restarting does not reroll them. Up to twelve higher-ranked Expedition results and their builds are retained separately, ordered by cleared stages and score.','ja':'この章はデスクトップ版 v12 用です。三択の候補は生成時に固定され、画面を閉じる・再起動する操作では引き直せません。遠征の記録は突破ステージ数と得点で順位付けし、能力構成とともに上位十二件まで別に保持します。'}[lang]
 w(lang,4,note+'\n'+text)

w('zh-CN',5,r'''
## 怎么选择辅助

| 功能 | 玩家怎么用 | 是否会走棋 |
|---|---|---|
| 提示 H | 计算推荐方向，查看本步合并数与直接得分 | 不会 |
| AI 单步 Enter | 让 AI 完成一个操作 | 会 |
| 自动玩 空格 | 连续让 AI 决策；再次空格暂停 | 会 |
| 教练 C | 停止手动操作约 450 ms 后后台分析 | 不会 |
| 设置 → 查看 AI 分析 | 比较方向、棋盘预览、深度、节点、耗时 | 预览不会；分析属于辅助 |
| 复盘 R | 浏览已经发生的操作 | 不会，不改变随机状态 |

人工滑动可以接管自动玩。切换模式、撤销、暂停会使过期 AI 结果作废。首次启动后台搜索核心会准备数秒，期间可手动玩。远征每次过关会暂停自动玩，由玩家选能力。

## 思考质量与播放速度

| 搜索档位 | 每步预算 |
|---|---:|
| 快速 | 约 25 ms |
| 标准 | 约 100 ms |
| 深入 | 约 450 ms |
| 自适应（默认） | 以 120 ms 为基础，按空格数约 90–300 ms；方向稳定可提前结束 |

慢速、正常、快速、冲分是另一组**游玩节奏**。冲分省略逐步动画，不意味着更深入搜索。机器负载会影响实际耗时，预算不是帧率承诺。要观察走势，用标准或自适应配正常速度；要比较算法，请固定种子、档位、版本、设备和统计样本，不凭一盘最高分断言胜率。

## 四方向分析应当怎么读

经典 / 每日 / 冲刺的方向预览是合并后的盘面，**不包含随机新方块**。空格与风险说明会考虑下一次随机落子；终局风险只指那一次落子后立即无路可走的概率，不是整局失败率。相对评分条不是胜率。

解局 / 重生的落子状态固定，分析可以显示包含新方块的确定盘面与已验证路线。AI 在经典、每日、冲刺里不会读取未来随机状态来作弊。最近 32 个相同棋盘、相同预算的分析可复用；「重新分析」会强制重新算。

## 算法实际做了什么

桌面经典算法是独立进程内的 Numba 本机编译 Expectimax：对玩家走法取优，对随机落子按概率加权，逐层加深，并保留完整完成的深度结果。它使用行查表、局面缓存、低概率分支裁剪、空格 / 排列 / 合并潜力等启发式。双字 80 位棋盘每格 5 位，32768 以后继续完整搜索，编码支持到 2³⁰。不是训练出来的神经网络，也不保证全局最优。

远征是独立的规则感知限时搜索，考虑能力、能量、凝时、交换与改变后的落子概率；空位多时采样落点。解局与重生采用携带完整随机状态的广度优先搜索，求最短解并重放验证。超时或未发现解不能写成「证明无解」。三个算法各有适用场景，不应把一种预算或分数套给所有玩法。

## 复盘

按 R 查看最近 100 步，可逐步、自动播放或点得分曲线定位。复盘不回滚当前游戏，也不改变撤销记录或随机数。关卡奖励后远征会重新开始记录当前关历史，因此不能假设能跨关回放所有动作。重生的「路线对照」另有原败局 / 本次与参考路线，用于比较选择。
''')
w('en',5,r'''
## Choose the assistance you need

| Feature | Use | Executes a move? |
|---|---|---|
| Hint, H | Recommended direction, merge count and immediate gain | No |
| AI step, Enter | Ask AI for one action | Yes |
| Autoplay, Space | Continuous decisions; press again to pause | Yes |
| Coach, C | Background analysis after roughly 450 ms without manual action | No |
| Settings → 查看 AI 分析 | Compare directions, previews, depth, nodes and time | Preview does not move; analysis counts as assistance |
| Replay, R | Review actions already taken | No; randomness is unchanged |

Manual input takes over from autoplay. Mode changes, undo and pauses invalidate stale AI results. The compiled search core may need a few seconds to prepare at startup; manual play remains available. Expedition pauses after each cleared stage for your ability choice.

## Thinking quality versus playback speed

| Search quality | Per-move budget |
|---|---:|
| 快速 / Fast | About 25 ms |
| 标准 / Standard | About 100 ms |
| 深入 / Deep | About 450 ms |
| 自适应 / Adaptive, default | Based on 120 ms, roughly 90–300 ms depending on empty cells; may stop early when direction stabilizes |

Slow, Normal, Fast and 「冲分」 are separate **playback speeds**. Score-push skips animations; it does not imply deeper search. Load affects actual time, and budgets are not frame-rate promises. Standard/Adaptive at normal speed is convenient for watching. Algorithm comparisons require matched seeds, quality, versions, hardware and enough trials; one high-scoring game is not a win-rate estimate.

## Read direction analysis correctly

Classic/Daily/Sprint previews show the board **after merging but before a random tile spawns**. Empty-space and risk descriptions account for the next random spawn. Terminal risk means immediate loss after that one spawn, not the probability of losing the entire future game. Relative score bars are not win probabilities.

Puzzle/Rescue randomness is fixed, so analysis can include the new tile and verified routes. Classic, Daily and Sprint do not peek at future RNG state. Up to 32 same-board/same-budget analyses can be reused; 「重新分析」 forces a fresh search.

## What the algorithms do

Desktop Classic uses Numba-compiled Expectimax in a separate process: maximize player choices, weight tile spawns by probability and deepen iteratively while retaining fully completed depth results. It uses row tables, state caching, low-probability pruning and heuristics for empty space, ordering and merge potential. Its two-word 80-bit board allocates five bits per cell, retains full search beyond 32768 and encodes tiles through 2³⁰. It is not a trained neural network and does not guarantee a global optimum.

Expedition uses a separate bounded search aware of abilities, energy, Freeze, Swap and altered spawn probabilities, sampling spawn locations on open boards. Puzzle/Rescue use breadth-first search with complete random state and replay verification of shortest solutions. Timeout or no discovered route is not proof of impossibility. Budgets and scores from one algorithm should not be applied to every mode.

## Replay

R opens up to 100 recent actions. Step through, play automatically or seek via the score graph. Viewing does not roll back the current game, modify undo history or alter randomness. Expedition starts a new history after stage rewards, so cross-stage playback is not implied. Rescue's separate route comparison contrasts your/original moves with the verified reference.
''')
w('ja',5,r'''
## 補助機能の選び方

| 機能 | 使い方 | 盤面を進めるか |
|---|---|---|
| H・ヒント | 推奨方向、合体数、直接の加点を表示 | 進めない |
| Enter・AI の一手 | 一操作を AI に任せる | 進める |
| Space・自動プレイ | 連続して判断。もう一度押すと停止 | 進める |
| C・コーチ | 手動操作が約 450 ms 止まると背景で分析 | 進めない |
| 設定 → 查看 AI 分析 | 方向、予測盤面、深さ、局面数、時間を比較 | 予測表示では進まない。分析は補助使用 |
| R・リプレイ | 過去の操作を見る | 進めない。乱数も不変 |

手動入力で自動プレイから操作を取り戻せます。モード変更、取り消し、停止後には古い分析結果を適用しません。起動直後はコンパイル済み探索コアの準備に数秒かかることがありますが、手動では遊べます。遠征はステージ突破で止まり、プレイヤーが能力を選びます。

## 思考品質と再生速度

| 品質 | 一手の時間予算 |
|---|---:|
| 快速 | 約 25 ms |
| 标准 | 約 100 ms |
| 深入 | 約 450 ms |
| 自适应・初期値 | 基準 120 ms。空きに応じて約 90～300 ms、方向が安定すれば早期終了 |

低速・通常・高速・「冲分」は別の**プレイ速度**です。「冲分」はアニメーションを省略する設定で、探索が深くなる設定ではありません。負荷によって実時間は変わり、フレームレートの保証ではありません。観察には標準または自適応と通常速度が便利です。性能比較にはシード、品質、版、端末、試行数を揃えてください。一局の高得点だけで勝率は判断できません。

## 四方向分析の見方

クラシック・デイリー・スプリントの予測盤面は**合体後、新タイル出現前**です。空きマスや危険度は次の一回の出現を考慮します。終了リスクはその出現直後に動けなくなる確率で、将来の一局全体の敗北率ではありません。相対評価の棒も勝率ではありません。

パズル・レスキューは乱数状態が固定されるため、新タイル込みの確定盤面と検証済み経路を表示できます。通常三モードでは未来の乱数状態を先読みしません。同盤面・同予算の分析は直近 32 件を再利用でき、「重新分析」で再計算します。

## アルゴリズム

通常モードは独立プロセスで Numba によるネイティブコンパイル済み Expectimax を実行します。プレイヤーの選択は最大化し、出現は確率で重み付けし、反復深化で完了した深さの結果を保持します。行テーブル、局面キャッシュ、低確率分岐の削減、空き・並び・合体可能性などの評価を使います。二ワードの 80 ビット盤面は各セル 5 ビットで、32768 を超えても通常探索を続け、符号化は 2³⁰ のタイルまで対応します。学習済みニューラルネットではなく、最適解の保証もありません。

遠征は能力、エネルギー、凝時、交換、出現率を考慮する別の時間制限探索です。空きが多い場合は出現位置を抽出して調べます。パズル・レスキューは完全な乱数状態を含む幅優先探索で最短解を求め、エンジンで検証します。時間切れ・未発見は解なしの証明ではありません。別モードの予算や得点を同一視しないでください。

## リプレイ

R で直近最大 100 操作を表示し、一手ずつ、再生、得点グラフによる位置選択ができます。現在の盤面、取り消し履歴、乱数は変更しません。遠征は報酬選択後に履歴をリセットするため、全ステージを跨ぐ再生ではありません。レスキューには元の敗局／今回と検証済み経路を比べる専用画面があります。
''')

w('zh-CN',6,r'''
## 先找对存档

| 版本 | 主存档 / 备份 | 截图、日志 |
|---|---|---|
| Mac 桌面 v12 | 游戏目录 `data/save.json`、`data/save.bak` | 游戏目录 `exports/`；启动脚本的终端输出 |
| Windows 桌面 v12 | `%LOCALAPPDATA%\2048-Atelier\data\save.json`、同目录 `save.bak` | `%LOCALAPPDATA%\2048-Atelier\exports` 与 `logs` |
| Native 1.0.1 | App 沙盒；用游戏设置的 JSON 导出 / 导入 | 原生手册的备份说明 |
| Touch v1 | 当前站点的 IndexedDB；用设置导出 / 导入 | 与浏览器、设备和站点身份有关 |

桌面版约每 5 秒及关键操作后在后台保存，正常退出会等待最后写入。主档缺失或损坏会尝试读取上次可用的 `save.bak`。这是一份滚动备份，不是无限版本历史，重要进度还应复制到别处。存档包含 RNG、撤销历史、各模式进度及记录，手改数字可能破坏一致性。

## 桌面版手动备份

1. 在所有打开的游戏窗口中停止自动玩，正常退出。
2. Mac 在 Finder 打开游戏目录的 `data`；Windows 在资源管理器地址栏粘贴 `%LOCALAPPDATA%\2048-Atelier\data`。
3. 将 `save.json` 和 `save.bak`（存在时）一起复制到带日期的独立文件夹。
4. 如需保存截图，另复制 `exports`。不要把截图当作可恢复的游戏存档。

复制期间不要运行游戏。若存在更旧版本仍打开，先关闭它；新版锁不能阻止不遵守锁的旧版写入。仅复制 `2048.exe` 或 `game.py` 不会备份用户目录进度。

## Mac 与 Windows v12 互相迁移

1. 确认两端均为桌面 v12，并分别做好原存档备份。
2. 目标端先正常运行一次并退出，以建立目录。
3. 两端游戏均关闭后，把源端主档与备份作为一组复制到目标端 `data`。
4. 如果源端没有 `save.bak`，先把目标端旧备份移到单独备份目录，避免源端主档损坏时误回到另一盘旧局。
5. 重开目标端，核对模式、分数、棋盘、撤销历史；确认无误后再继续。此操作**替换**目标进度，不会合并两台电脑的成绩。

Windows 的旧版自动迁移仅发生在用户目录内 **save.json 与 save.bak 都不存在** 时，才复制旧游戏目录的两份文件。已有任意一份就不自动覆盖；旧文件不删除。不要通过反复删除存档来尝试迁移，按上面的显式备份步骤处理。

## 更新与恢复

Windows 更新时保留用户目录，完整解压新游戏包到新的文件夹即可；先关闭旧窗口。Mac 更新游戏源码和资源时保留 `data`、`exports` 与本机环境。移动 Mac 虚拟环境到另一台机器不可靠，按安装章重建依赖。

若提示从备份恢复，先核对恢复的棋盘，再备份现有文件。若主档和备份都不可用，保存错误原件以便排查，使用自己另存的有效备份；没有有效副本就不能承诺找回进度。磁盘满、只读目录或拔盘可能导致保存失败，应处理提示后正常退出重试。

## 跨版本范围

Native JSON、Touch JSON、Python 桌面存档不是互换格式。不要因扩展名都为 `.json` 就互导。原生与 Web 导入会替换各自版的当前进度，操作前先导出目标端。没有自动 iCloud 或跨平台云同步；删除 App、清网站数据、换浏览器前先备份对应版本。
''')
w('en',6,r'''
## Find the right data

| Edition | Main save / backup | Images and logs |
|---|---|---|
| Mac Desktop v12 | Game folder: `data/save.json`, `data/save.bak` | Game folder `exports/`; launcher Terminal output |
| Windows Desktop v12 | `%LOCALAPPDATA%\2048-Atelier\data\save.json`, adjacent `save.bak` | `%LOCALAPPDATA%\2048-Atelier\exports` and `logs` |
| Native 1.0.1 | App sandbox; use settings JSON export/import | See the native backup guide |
| Touch v1 | Site IndexedDB; use settings export/import | Bound to browser, device and site identity |

Desktop saves in the background about every five seconds and after key actions. Normal exit waits for the final write. Missing or damaged main saves trigger an attempt to restore the last readable `save.bak`. This is one rolling backup, not unlimited history. Copy important progress elsewhere. Saves include RNG, undo history, mode progress and records; editing numbers by hand can break consistency.

## Manual desktop backup

1. Stop autoplay and close every game window normally.
2. On Mac, open the game folder's `data` directory in Finder. On Windows, paste `%LOCALAPPDATA%\2048-Atelier\data` into Explorer's address bar.
3. Copy `save.json` and `save.bak`, when present, together into a separate dated folder.
4. Copy `exports` separately if you want screenshots. An image cannot restore a game.

Do not run the game during copying. Close older versions too: the new lock cannot protect against an old process that does not use it. Copying `2048.exe` or `game.py` alone does not back up progress in the user-data folder.

## Transfer between Mac and Windows v12

1. Confirm both are Desktop v12 and back up both original profiles.
2. Launch and close the destination game once to establish its folders.
3. With both games closed, copy the source main save and backup as a pair into the destination `data` folder.
4. If the source has no `save.bak`, move the destination's old backup into your separate backup folder first. Otherwise a damaged new main save might restore an unrelated old game.
5. Relaunch and verify mode, score, board and undo history before continuing. This **replaces** destination progress; it does not merge two profiles.

Windows automatically imports old game-folder saves only when **neither save.json nor save.bak exists** in user data. If either exists, it does not overwrite automatically. Old files are left in place. Use the explicit backup procedure instead of repeatedly deleting files to provoke migration.

## Updates and recovery

For Windows updates, keep the user-data folder and fully extract the new game into a new folder after closing the old window. For Mac source updates, retain `data`, `exports` and the local environment. A copied virtual environment is not portable to another computer; recreate dependencies as described in the installation chapter.

After a backup-recovery message, verify the board and back up the current files. If both files are unusable, preserve the damaged originals for diagnosis and restore your separate valid copy. Without a valid copy, recovery cannot be promised. Disk-full, read-only folders or disconnecting a drive can prevent saving; resolve the reported issue and exit normally.

## Edition boundaries

Native JSON, Touch JSON and Python desktop saves are different formats. The `.json` extension does not make them interchangeable. Native/Web import replaces that edition's current progress; export the destination first. There is no automatic iCloud or cross-platform cloud sync. Back up before deleting the App, clearing site data or changing browsers.
''')
w('ja',6,r'''
## 保存場所

| 版 | 主セーブ・予備 | 画像・ログ |
|---|---|---|
| Mac v12 | ゲーム内 `data/save.json`、`data/save.bak` | ゲーム内 `exports/`、起動したターミナルの出力 |
| Windows v12 | `%LOCALAPPDATA%\2048-Atelier\data\save.json` と同じ場所の `save.bak` | `%LOCALAPPDATA%\2048-Atelier\exports` と `logs` |
| Native 1.0.1 | App サンドボックス。設定で JSON を書き出し／読み込み | 原生版の保存ガイドを参照 |
| Touch v1 | サイトの IndexedDB。設定で書き出し／読み込み | ブラウザー・端末・サイトごと |

デスクトップ版は約五秒ごとと主要操作後に背景で保存し、通常終了時には最後の書き込みを待ちます。主セーブがない・壊れている場合は、直前の読み取り可能な `save.bak` を試します。予備は一世代で、無制限の履歴ではありません。重要な進行は別の場所にもコピーしてください。乱数、取り消し履歴、各モード、記録を含むため、数値の手動編集は整合性を壊すことがあります。

## デスクトップ版のバックアップ

1. 自動プレイを止め、開いているすべてのゲームを正常終了します。
2. Mac は Finder でゲーム内の `data` を開きます。Windows は Explorer のアドレス欄に `%LOCALAPPDATA%\2048-Atelier\data` を入力します。
3. 存在する `save.json` と `save.bak` を一組として日付付きの別フォルダーへコピーします。
4. 画像も必要なら `exports` を別にコピーします。画像から対局を復元することはできません。

コピー中はゲームを起動しないでください。旧版も終了します。新しい排他ロックに従わない旧プロセスの書き込みは防げません。`2048.exe` や `game.py` だけのコピーでは、ユーザーデータを保存したことになりません。

## Mac と Windows の v12 間で移行

1. 両方がデスクトップ v12 であることを確認し、両端の現在のデータをバックアップします。
2. 移行先を一度起動・終了して保存フォルダーを作ります。
3. 両端を終了した状態で、移行元の主セーブと予備を一組で移行先の `data` にコピーします。
4. 移行元に `save.bak` がない場合は、移行先の古い予備を先に別のバックアップ先へ移します。壊れた主セーブから無関係な古い局へ戻ることを避けます。
5. 起動し、モード、点数、盤面、取り消し履歴を確認します。これは移行先を**置き換える**操作で、二台の成績を統合しません。

Windows の旧フォルダーからの自動移行は、ユーザーデータに **save.json と save.bak の両方が存在しない場合だけ**です。片方でもあれば自動上書きせず、元ファイルも削除しません。移行させるために削除を繰り返すのではなく、上記の手順で明示的に移してください。

## 更新と復旧

Windows 更新では旧ウィンドウを閉じ、新しいゲームを別フォルダーへ完全に展開します。ユーザーデータは残します。Mac のソース更新では `data`、`exports`、その Mac の環境を保持します。仮想環境は別の PC へそのまま移す用途に向かないので、導入章に従って再作成してください。

予備から復元したと表示された場合は盤面を確認し、現在のファイルも保存します。両方壊れている場合は原本を診断用に残し、自分で保管した正常なコピーを使います。有効なコピーなしでの復旧は保証できません。容量不足、読み取り専用、ディスクの切断は保存失敗の原因になります。表示された問題を解決して正常終了してください。

## 別の版との互換性

Native、Touch、Python のセーブは異なる形式です。拡張子が `.json` でも相互に読み込めません。原生・Web の読み込みは、その版の現在の進行を置き換えます。移行先を先に書き出してください。自動 iCloud・プラットフォーム間同期はありません。App 削除、サイトデータ消去、ブラウザー変更の前に対応する版でバックアップします。
''')

w('zh-CN',7,r'''
## Mac 应该用哪个版本

Mac 游玩使用 **Python 桌面 v12**。现有交付是源码目录与启动脚本，不是单独打包的 `.app`。同目录下的 `iOS/Lumina.xcodeproj` 是 iPhone / iPad 工程；文档里的 SwiftUI 主机预览也不是替代桌面版的 Mac 安装包。

下面以 `~/2048-Atelier` 为例；请将路径换成实际游戏文件夹。首次使用需要建立自己的 Python 环境，不要从其他电脑复制虚拟环境。

## 已准备好的本机

1. 挂载移动硬盘，打开游戏目录。
2. 双击 `启动游戏.command`，等待窗口与后台 AI 准备。
3. 在大厅选经典或继续当前局。终端窗口用于显示启动问题。
4. 正常关闭游戏，等保存完成后再弹出硬盘。

也可在终端运行：

```sh
cd ~/2048-Atelier
.venv/bin/python game.py
```

## 新 Mac 的首次准备

需要可用的 **64 位 Python 3.12–3.14**，以项目固定依赖可正常安装为准。打开终端进入自己实际的游戏目录，逐条运行：

```sh
python3 --version
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python game.py
```

先检查第一条输出；如果 `python3` 不是兼容版本，改用已安装的兼容解释器创建环境。首次下载依赖需要联网，完成后正常游玩与 AI 不依赖服务器。依赖版本记录在 [requirements 参考](../../reference/desktop-requirements.txt)。安装在游戏自己的 `.venv`，不需要用 `sudo pip` 改系统 Python。

若源目录已有从别处复制的失效 `.venv`，退出游戏后将其改名保留，再用本机 Python 新建。不要删 `data`。CPU 架构变化时同样重建环境。已验证的开发主机是 Apple Silicon Mac；这里没有给所有 Intel Mac 或 macOS 版本作实机兼容承诺。

## 常见启动问题

| 现象 | 检查与处理 |
|---|---|
| 文件找不到 / 路径失效 | 硬盘是否已挂载，目录名是否改变；含空格的路径在命令中用引号 |
| 双击脚本没有启动 | 在终端运行 `/bin/zsh "启动游戏.command"` 看第一条错误 |
| 提示缺少 Python / 包 | 检查 Python 版本，用当前 `.venv/bin/python -m pip install -r requirements.txt` |
| `.venv/bin/python` 无法执行 | 虚拟环境是否来自另一台机器；保留旧环境后重建 |
| 提示已有实例 | 找回原游戏窗口并正常退出；不要在仍运行时删除锁文件 |
| 游戏能动但 AI 未就绪 | 等待后台编译准备；长时间无结果时保留启动错误输出 |
| 字体或图标异常 | 保留整个 `fonts/` 与资源目录；系统苹方仅在本机读取，不随包分发 |
| 无法保存 / 截图 | 检查游戏目录写权限、磁盘容量与连接；存档在游戏内 `data/` |

如 macOS 对下载来源提出拦截，先核实来源和文件完整性，按照系统显示的逐项打开流程处理；不要全局关闭系统保护。旧窗口不会自动加载新代码，更新后需要完整退出再启动。
''')
w('en',7,r'''
## Which edition runs on Mac?

Use **Python Desktop v12**. The current delivery is a source folder with a launcher, not a separately packaged `.app`. `iOS/Lumina.xcodeproj` is the iPhone/iPad project; SwiftUI host previews in this manual are not a replacement Mac desktop distribution.

The examples use `~/2048-Atelier`; replace it with your game folder. Create a fresh Python environment on your Mac rather than copying one from another computer.

## This prepared Mac

1. Mount the external drive and open the game folder.
2. Double-click `启动游戏.command` and wait for the window and AI preparation.
3. Choose Classic or resume in the lobby. Terminal output helps diagnose startup failures.
4. Exit normally and let saving finish before ejecting the drive.

Alternatively:

```sh
cd ~/2048-Atelier
.venv/bin/python game.py
```

## First setup on another Mac

Use **64-bit Python 3.12–3.14**, subject to successful installation of the pinned dependencies. In Terminal, enter the actual game directory and run each command:

```sh
python3 --version
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python game.py
```

Check the first output. If `python3` is incompatible, create the environment with an installed compatible interpreter. Initial dependency downloads need a network connection; prepared gameplay and AI do not require a server. Pinned versions are in the [requirements reference](../../reference/desktop-requirements.txt). Use the game's `.venv`, without modifying system Python via `sudo pip`.

If an existing copied `.venv` is unusable, close the game, rename that environment to retain it, then create a new one locally. Keep `data`. Recreate environments across CPU architectures too. The tested development host is an Apple Silicon Mac; this is not a claim of physical testing across every Intel Mac or macOS release.

## Startup troubleshooting

| Symptom | Check and action |
|---|---|
| Path or file missing | Confirm drive mount and folder name; quote paths containing spaces |
| Double-click does not start | Run `/bin/zsh "启动游戏.command"` in Terminal and read the first error |
| Python/package missing | Check version; install requirements with `.venv/bin/python -m pip` |
| `.venv/bin/python` fails | Was it copied from another computer? Preserve it, then recreate locally |
| Another instance is reported | Find and close the existing window normally; do not delete a lock while it runs |
| Manual play works, AI not ready | Allow compilation preparation; retain output if it remains stuck |
| Missing glyphs | Keep `fonts/` and all resources; system PingFang is read locally, not redistributed |
| Save/screenshot failure | Check game-folder write access, disk space and drive connection; saves are in `data/` |

If macOS flags the download, verify its source and integrity and follow the system's per-item opening flow. Do not disable system protection globally. Existing windows do not load new source automatically; exit and relaunch after updates.
''')
w('ja',7,r'''
## Mac で遊ぶ版

**Python デスクトップ版 v12** を使います。現在の配布はソースフォルダーと起動スクリプトで、独立した `.app` パッケージではありません。`iOS/Lumina.xcodeproj` は iPhone / iPad 用です。説明書内の SwiftUI ホスト表示も、デスクトップ版の代わりとなる Mac 配布アプリではありません。

以下は `~/2048-Atelier` を例にしています。実際のゲームフォルダーに読み替えてください。初回は Mac 上で Python 環境を作成し、他の端末の仮想環境はコピーしないでください。

## 準備済みの Mac

1. 外付けディスクを接続し、ゲームフォルダーを開きます。
2. `启动游戏.command` をダブルクリックし、ウィンドウと AI の準備を待ちます。
3. ロビーでクラシックまたは続きから開始します。起動時の問題はターミナルに表示されます。
4. 通常終了し、保存完了後にディスクを取り出します。

ターミナルからは次でも起動できます。

```sh
cd ~/2048-Atelier
.venv/bin/python game.py
```

## 別の Mac で初回準備

**64 ビット Python 3.12～3.14** と、固定された依存関係の導入成功が必要です。ターミナルで実際のゲームフォルダーへ移動し、一行ずつ実行します。

```sh
python3 --version
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python game.py
```

最初の出力を確認します。`python3` が対応版でなければ、インストール済みの対応 Python を環境作成に使います。初回ダウンロードには通信が必要ですが、準備後のゲームと AI はサーバーに依存しません。[依存版の一覧](../../reference/desktop-requirements.txt)を参照してください。ゲーム専用の `.venv` を使い、`sudo pip` でシステム Python を変更する必要はありません。

コピーしてきた `.venv` が動かない場合は、ゲーム終了後に旧環境を改名して保持し、この Mac で新しく作ります。`data` は残します。CPU アーキテクチャが変わる場合も再作成します。実行確認した開発機は Apple Silicon Mac で、すべての Intel Mac・macOS 版を実機確認したわけではありません。

## 起動時の対処

| 症状 | 確認・対処 |
|---|---|
| ファイルがない | ディスクの接続とフォルダー名を確認。空白を含むパスは引用符で囲む |
| ダブルクリックで動かない | ターミナルで `/bin/zsh "启动游戏.command"` を実行し、最初のエラーを見る |
| Python やパッケージがない | バージョン確認後、`.venv/bin/python -m pip` で requirements を導入 |
| `.venv/bin/python` が動かない | 他の PC 由来か確認。旧環境を保持して作り直す |
| 別の起動があると出る | 元のウィンドウを探し正常終了。動作中のロックは削除しない |
| 手動は動くが AI が準備中 | 初期化を待つ。止まったままならターミナル出力を保存 |
| 文字が欠ける | `fonts/` と全リソースを保持。システムの苹方は再配布せずローカルで読む |
| 保存・撮影に失敗 | フォルダーの書込権限、空き容量、接続を確認。セーブは `data/` |

ダウンロードに対する macOS の警告が出たら、配布元と整合性を確認し、OS が示す個別の開く手順に従います。システム保護を全体で無効化しないでください。起動中の旧画面には新ソースが自動反映されないため、更新後は終了して起動し直します。
''')

w('zh-CN',8,r'''
## Windows 便携版：推荐入口

适用范围：**Windows 10 / 11，Intel / AMD x64**。现有包不是 32 位程序，也不是原生 Windows ARM64 包；没有验证 ARM 模拟执行。原包是 `2048-v12-Windows-x64.zip`，本次另提供附全平台三语手册的 `2048-v12-Windows-x64-with-docs.zip`，游戏与运行环境不变。

1. 把 ZIP 复制到 Windows 电脑；右键「全部解压」，选择可用的本地文件夹。
2. 打开展开后的 `2048-Windows` 文件夹，双击 **2048.exe**。
3. 首次等待 AI 初始化数秒，期间可以手动玩。无需另装 Python，也不需要联网玩。
4. 选择经典，按方向键试走；退出并重新打开，确认棋盘能恢复。
5. 包内 `README.zh-CN.md / README.en.md / README.ja.md` 与 `docs/index.html` 都可离线阅读。

必须保留 `runtime/`、`fonts/`、JSON 关卡和 Python 文件等完整结构。**不要在 ZIP 内直接运行，也不要只复制 exe。** 包内自带 Python 3.13.15 与固定依赖，不会因为电脑装了另一版本 Python 就要求你更换系统版本。

## 存档并不在 exe 旁边

在资源管理器地址栏输入 `%LOCALAPPDATA%\2048-Atelier`：

| 子目录 | 内容 |
|---|---|
| `data` | `save.json` 主档、`save.bak` 备份、进程锁 |
| `exports` | P 键截图 |
| `logs` | `latest.log` 启动日志、`diagnostics.json` 自检结果 |
| `cache/numba` | AI 编译缓存，可重新生成，不是玩家存档 |

完整备份 / 升级 / 旧目录迁移见[第六章](06-saves.md)。换一个解压文件夹不会自动重置用户目录的游戏。

## 打不开时的诊断顺序

1. 确认已经完全解压，且是 x64 Windows 10 / 11。
2. 双击 **启动游戏.bat**，保留控制台上的第一条错误；不要只描述「闪退」。
3. 双击 **check-windows.bat**。它检查依赖版本、中文字体、12 道谜题、3 道练习、临时存档与后台 AI。使用临时数据，不改个人对局；运行后窗口会暂停以便阅读。
4. 检查 `%LOCALAPPDATA%\2048-Atelier\logs`。只有程序成功写出报告才会有 `diagnostics.json`；若依赖导入就失败，请保留控制台错误。
5. 按下表处理，再附版本、系统、错误输出和复现步骤反馈。

| 现象 | 处理 |
|---|---|
| 找不到 runtime / Python / DLL | 核对是否少解压；重新完整解压原始包，不从不明站点单独下载 DLL |
| 提示已有实例 | 回到原窗口；真正退出后系统会释放锁，磁盘留有锁文件不代表仍锁住 |
| 中文方框 | 核对 `fonts/NotoSansSC-*.ttf` 与 `fonts/OFL.txt` 均在；不要删除字体 |
| 只在 exe 下失败 | 用 bat 入口看错误，提供 latest.log；缺日志时用控制台内容 |
| 手动可玩但 AI 一直不动 | 等首次初始化；运行自检查看后台进程 / Numba 错误 |
| 放大缩小或全屏显示异常 | 先回到窗口模式，记录 Windows 缩放比例与屏幕分辨率 |
| 截图或保存失败 | 检查用户目录权限和可用容量；不必把游戏放进系统目录 |
| 更新后没有新功能 | 旧窗口是否已关闭；确认启动的是新的完整解压目录 |

入口在创建窗口前设置 DPI awareness，但这不意味着已经验证了所有多屏缩放。若系统对来源提出警告，请核验包与来源，使用系统提供的具体文件处理方式；不需要全局关闭保护或以管理员身份强行启动。

## Windows 源码版（需要自己准备环境）

便携版用户可跳过本节。源码版需要 **64 位 Python 3.12–3.14**。双击 `启动游戏.bat`：它优先用随附 runtime，其次已建 `.venv`，否则寻找兼容 Python 创建环境并安装固定依赖。初次安装需要网络；失败时保留错误信息。已就绪时不会每次重新下载。

手动方式（在游戏目录的命令提示符执行，以已安装 Python 3.13 为例）：

```bat
py -3.13 -m venv .venv
.venv\Scripts\python.exe -m pip install --only-binary=:all: -r requirements.txt
.venv\Scripts\python.exe game.py
```

## 验证范围

包经过 ZIP CRC、下载依赖 SHA-256、135 个 x64 PE 文件及必需 DLL 导入检查；保留 [v12 测试报告](../../reference/desktop-v12-validation.md)。**尚未在 Windows 实机执行**。这些检查不能代替窗口、声音、显卡、缩放和真实屏幕帧率测试。本文桌面动图来自 Mac 上相同的 Python 游戏代码，不伪称 Windows 录屏。
''')
w('en',8,r'''
## Windows portable edition

Target: **Windows 10/11 on Intel/AMD x64**. This is neither a 32-bit build nor a native ARM64 package; ARM emulation has not been validated. The original is `2048-v12-Windows-x64.zip`. The new `2048-v12-Windows-x64-with-docs.zip` adds the complete trilingual handbook while retaining the same game and runtime.

1. Copy the ZIP to the Windows computer. Right-click → Extract All into a local folder.
2. Open the extracted `2048-Windows` folder and double-click **2048.exe**.
3. Allow a few seconds for initial AI preparation. Manual play is available. No separate Python installation or gameplay network connection is required.
4. Select Classic, try arrow-key moves, then close and reopen to check restoration.
5. Read `README.zh-CN.md / README.en.md / README.ja.md` or `docs/index.html` offline.

Keep the complete structure, including `runtime/`, `fonts/`, level JSON and Python files. **Do not run inside the ZIP or copy only the exe.** Python 3.13.15 and pinned dependencies are included; a different system Python does not need replacement.

## Data is not next to the exe

Paste `%LOCALAPPDATA%\2048-Atelier` into Explorer:

| Folder | Contents |
|---|---|
| `data` | Main `save.json`, backup `save.bak`, process lock |
| `exports` | Screenshots saved with P |
| `logs` | Startup `latest.log`; self-check `diagnostics.json` |
| `cache/numba` | Regenerable AI cache, not player progress |

See [chapter 6](06-saves.md) for backups, updates and migration. Extracting a different game folder does not reset progress in user data.

## Diagnose startup failures

1. Confirm full extraction and Windows 10/11 x64.
2. Open **启动游戏.bat** and retain the first console error.
3. Run **check-windows.bat**. It checks dependency versions, Chinese fonts, twelve puzzles, three practices, temporary storage and background AI. Temporary checks do not modify your personal game. The console pauses for reading.
4. Inspect `%LOCALAPPDATA%\2048-Atelier\logs`. `diagnostics.json` only exists if the report was successfully written; if importing a dependency fails earlier, keep the console output.
5. Use the table, then report version, OS, exact error and reproduction steps.

| Symptom | Action |
|---|---|
| Missing runtime/Python/DLL | Check extraction and extract the original package again; do not obtain individual DLLs from unknown sites |
| Another instance reported | Return to that window; normal exit releases the OS lock. A leftover lock file alone does not mean an active lock |
| Chinese square glyphs | Check bundled `fonts/NotoSansSC-*.ttf` and `fonts/OFL.txt`; keep the fonts |
| Only exe startup fails | Use the bat console and latest.log; provide console output when no log exists |
| AI never moves, manual play works | Wait for initial preparation, then use diagnostics for worker/Numba failures |
| Scaling/fullscreen trouble | Return to windowed mode and record display scale and resolution |
| Save or screenshot failure | Check user-folder permissions and disk capacity; no system-folder installation is necessary |
| Update appears unchanged | Close the old window and launch from the new fully extracted folder |

The launcher configures DPI awareness before creating a window; this is not proof of all multi-monitor scaling behavior. If Windows flags the source, verify the package and origin and use the system's per-file handling. Do not globally disable protection or force administrator execution.

## Windows source setup

Portable users can skip this. Source setup needs **64-bit Python 3.12–3.14**. `启动游戏.bat` prefers a bundled runtime, then an existing `.venv`, otherwise finds compatible Python and prepares an environment with pinned dependencies. Initial setup needs networking; prepared launches do not reinstall everything.

Manual Command Prompt example with Python 3.13 installed, from the game directory:

```bat
py -3.13 -m venv .venv
.venv\Scripts\python.exe -m pip install --only-binary=:all: -r requirements.txt
.venv\Scripts\python.exe game.py
```

## Validation status

The original package passed ZIP CRC checks, dependency SHA-256 checks and inspection of 135 x64 PE files and required DLL imports. See the [v12 report](../../reference/desktop-v12-validation.md). **No Windows hardware run has been completed.** Static checks do not validate windows, audio, GPU, scaling or real display frame rate. Desktop clips show the same Python game running on Mac; they are not Windows recordings.
''')
w('ja',8,r'''
## Windows ポータブル版

対象は **Windows 10 / 11、Intel・AMD x64** です。32 ビット版やネイティブ ARM64 版ではなく、ARM 上のエミュレーションも未検証です。元の配布物は `2048-v12-Windows-x64.zip` です。今回の `2048-v12-Windows-x64-with-docs.zip` は、同じゲーム・実行環境に全版の三言語説明書を追加しています。

1. Windows PC に ZIP をコピーし、右クリックの「すべて展開」でローカルフォルダーへ展開します。
2. 展開後の `2048-Windows` を開き、**2048.exe** をダブルクリックします。
3. 最初の AI 準備に数秒待ちます。手動では遊べます。別途 Python を入れたり、プレイ中に通信したりする必要はありません。
4. クラシックで矢印操作を試し、終了・再起動して盤面が戻ることを確認します。
5. `README.zh-CN.md / README.en.md / README.ja.md`、または `docs/index.html` をオフラインで読めます。

`runtime/`、`fonts/`、JSON、Python ファイルを含めた全構成を保持してください。**ZIP の中から起動したり exe だけコピーしたりしないでください。** Python 3.13.15 と固定依存関係を同梱しており、PC に別の Python があっても入れ替える必要はありません。

## セーブは exe の横ではない

Explorer のアドレス欄に `%LOCALAPPDATA%\2048-Atelier` を入力します。

| フォルダー | 内容 |
|---|---|
| `data` | 主セーブ `save.json`、予備 `save.bak`、プロセスロック |
| `exports` | P で保存した画像 |
| `logs` | 起動ログ `latest.log`、自己診断 `diagnostics.json` |
| `cache/numba` | 再生成可能な AI キャッシュ。進行データではない |

バックアップ・更新・移行は[第 6 章](06-saves.md)にあります。別の場所へ展開しても、ユーザーフォルダーの進行はリセットされません。

## 起動できないとき

1. 完全に展開済みで Windows 10 / 11 x64 か確認します。
2. **启动游戏.bat** を開き、コンソールの最初のエラーを保存します。
3. **check-windows.bat** を実行します。依存版、中文字形、十二問のパズル、三問の練習、一時セーブ、背景 AI を確認します。個人の対局は変更せず、結果を読むために画面が停止します。
4. `%LOCALAPPDATA%\2048-Atelier\logs` を確認します。`diagnostics.json` は報告を書き出せた場合のみ作られます。依存関係の読み込みで先に失敗した場合はコンソール出力を保存します。
5. 下表で確認し、版・OS・エラー全文・再現手順を添えて報告します。

| 症状 | 対処 |
|---|---|
| runtime / Python / DLL がない | 元のパッケージを完全展開し直す。不明なサイトで単独 DLL を探さない |
| 別の起動がある | 元の画面へ戻る。終了で OS ロックが解除される。ファイルが残るだけではロック中とは限らない |
| 中国語が四角になる | `fonts/NotoSansSC-*.ttf` と `fonts/OFL.txt` を確認し、字体を削除しない |
| exe だけ失敗する | bat のコンソールと latest.log を確認。ログなしならコンソール内容を報告 |
| AI だけ止まる | 初回準備を待ち、自己診断でワーカー・Numba の問題を見る |
| 拡大率・全画面の不具合 | ウィンドウへ戻し、OS 拡大率と解像度を記録 |
| 保存・撮影失敗 | ユーザーフォルダーの権限・容量を確認。システム領域への導入は不要 |
| 更新が反映されない | 旧画面を閉じ、新しく完全展開した場所から起動 |

起動前に DPI awareness を設定しますが、全マルチモニター構成の検証を意味しません。Windows が配布元を警告した場合は元ファイルと出所を確認し、OS の個別ファイル用の処理に従ってください。保護機能の全体無効化や、管理者権限での強制起動は不要です。

## Windows ソース版

ポータブル版ならこの節は不要です。**64 ビット Python 3.12～3.14** が必要です。`启动游戏.bat` は同梱 runtime、既存 `.venv` の順に使い、なければ対応 Python を探して環境と依存関係を準備します。初回は通信が必要ですが、準備済みなら毎回再導入しません。

Python 3.13 を導入済みの場合、ゲームフォルダーのコマンドプロンプトでの例です。

```bat
py -3.13 -m venv .venv
.venv\Scripts\python.exe -m pip install --only-binary=:all: -r requirements.txt
.venv\Scripts\python.exe game.py
```

## 検証範囲

元のパッケージでは ZIP CRC、依存ファイルの SHA-256、135 個の x64 PE と必須 DLL の参照を確認しています。[v12 検証記録](../../reference/desktop-v12-validation.md)を参照してください。**Windows 実機では未実行です。** 静的確認は画面、音、GPU、拡大率、実画面のフレームレート検証ではありません。デスクトップ動画は同じ Python ゲームを Mac で動かしたもので、Windows 録画ではありません。
''')

w('zh-CN',9,r'''
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

1. 在 Safari 打开 [LUMINA 网页版](https://lumina-2048.vercel.app/)。当前入口为受限访问，需要有权限的 Vercel 账号登录。
2. 等首次完整加载，使用分享 → 添加到主屏幕。
3. 等离线准备完成后，再测试断网从主屏幕进入。首次打开前或资源未缓存完整时不能承诺离线。
4. 以棋盘内滑动或方向按钮游玩，也可用方向键 / WASD。
5. 设置里导出 JSON 备份；在另一台设备的 **Touch 版**导入，导入前先导出其原进度。

从旧网址搬到新网址时，先在旧网页的设置中「导出进度」，再到新网页「导入进度」。浏览器不会自动把旧网址的进度搬到新网址。原来的主屏幕图标也需要从新网址重新添加。

Touch 有六种玩法、提示、AI Worker、撤销重做、最近 100 次操作复盘、重生路线比较、明暗、声音和减少动态效果。打开菜单、后台和手动接管会暂停自动玩。它没有 Python 桌面版的完整快捷键，也不要按桌面 AI 毫秒档位理解它。

存档在当前站点 IndexedDB，带备份与离开页面的应急快照；不同浏览器、设备、主屏幕环境不自动同步。清网站数据、隐私浏览和系统回收存储都可能影响进度，先导出重要数据。网页改动后遇到旧界面，先导出，再联网重新打开等待更新，不要首先清空网站数据。

源码在 `mobile/`，本地 `python3 serve.py` 用于开发，默认不启用 Service Worker；手机正式使用需要 HTTPS。原生规则对照、网页自动测试与浏览器布局检查各有范围，不等于实体 iPhone / iPad 的离线冷启动、触感或系统手势已经通过。
''')
w('en',9,r'''
## iPhone and iPad: one native project, adaptive layouts

**Native 1.0.1 (build 2)** is a real Swift/SwiftUI Universal App source project, with no WebView. iPhone and iPad share rules and source while adapting layout to width. The deployment target is iOS/iPadOS 16.4; the toolchain requires Swift 6.0+ with Swift 5 language mode. A deployment target and a compiler requirement are different.

The game root's `iOS/` folder contains `Lumina.xcodeproj`, core, UI, resources, tests and the native handbook. **There is no signed IPA, TestFlight invitation or App Store release.** Install full Xcode and a compatible iOS SDK on Mac, open the project, configure your Team/Bundle Identifier, select a device and Run. Command Line Tools alone cannot install the app on an iPhone. Follow the [installation, signing, build and acceptance guide](../native/docs/en/06-build.md).

## Native controls

Launch defaults to Classic. The top mode title opens other modes. Swipe inside the board, use the curved arrow for Undo, the lightbulb for Hint and autoplay to start/pause. The ellipsis contains Redo, restart and mode-specific puzzle/Rescue choices. Settings include appearance, sound, haptics, reduced motion, AI strength and JSON backups.

External keyboards support arrows/WASD; desktop Z/R/C/P shortcuts do not apply. Up to two swipes can queue during animation; menus, backgrounding and manual takeover handle pending input and pause AI. Narrow iPhone layouts stack vertically; wider iPad layouts place board and information side by side. Smaller windows adapt, and long information can scroll.

Pause AI, then export JSON through settings to Files or another location. Back up the destination before importing, which replaces native progress. This format differs from both Python desktop saves and Touch JSON. Requesting a native hint immediately marks assistance even if you never use the suggested move.

## All nine native chapters remain available

- [Getting started, gestures and iPhone/iPad layouts](../native/docs/en/01-start.md)
- [Six modes](../native/docs/en/02-rules.md) and [abilities/scoring](../native/docs/en/03-expedition.md)
- [AI, records and backups](../native/docs/en/04-ai-data.md)
- [Troubleshooting](../native/docs/en/05-faq.md) and [build/install](../native/docs/en/06-build.md)
- [Nine native demonstrations](../native/docs/en/07-gallery.md), [solutions](../native/docs/en/08-solutions.md), [release validation](../native/docs/en/09-release.md)

If the App is already installed, begin with controls. If you received source, begin with builds. Mac host tests and layout images do not replace device testing of touch, rotation, Split View, backgrounding, VoiceOver or display performance.

## Touch v1: the separate web edition

The web edition is separate from the native App. It supports Safari touch controls and adding the game to the Home Screen. For the native App, use the installation and control instructions above.

1. Open [LUMINA for the web](https://lumina-2048.vercel.app/) in Safari. Access is currently restricted; sign in with an authorized Vercel account.
2. Wait for full initial loading, then Share → Add to Home Screen.
3. Wait for offline preparation before testing a disconnected Home Screen launch. Offline availability is not promised before caching completes.
4. Swipe inside the board, use direction buttons or arrows/WASD.
5. Export JSON in settings. Import only into another **Touch** edition, after backing up that destination.

Touch has all six modes, hints, Worker-based AI, undo/redo, last-100-action Replay, Rescue route comparison, appearance, sound and reduced motion. Menus, backgrounding and manual takeover pause autoplay. It does not implement the full Python desktop keyboard map, and desktop AI time presets do not describe its settings.

Progress lives in site IndexedDB with backup and a page-leaving emergency snapshot. Browser/device/Home Screen contexts do not synchronize automatically. Clearing site data, private browsing or storage eviction can affect progress. Export important data first. If an old web interface persists after an update, export before reconnecting/reopening for the update; do not begin by deleting site data.

When moving from the old address, first choose 「导出进度」 in the old site’s settings, then 「导入进度」 on the new site. Browser saves do not move automatically between addresses. Add a new Home Screen icon from the new address as well.

Source lives in `mobile/`. Local `python3 serve.py` is for development and skips Service Worker registration by default; phone deployment needs HTTPS. Native rule comparisons, web tests and browser layout checks do not prove physical-device offline cold start, haptics or system-gesture behavior.
''')
w('ja',9,r'''
## iPhone と iPad：共通の原生プロジェクト

**Native 1.0.1（build 2）** は Swift / SwiftUI の Universal App ソースで、WebView ではありません。iPhone と iPad は同じ規則とコードを使い、幅に応じて配置を変えます。最低配布対象は iOS / iPadOS 16.4、ツールチェーンは Swift 6.0 以上、言語モードは Swift 5 です。最低 OS とコンパイラー要件は別のものです。

ゲーム内 `iOS/` に `Lumina.xcodeproj`、コア、画面、リソース、テスト、説明書があります。**署名済み IPA、TestFlight 招待、App Store 公開版は含みません。** Mac に完全な Xcode と対応 iOS SDK を入れ、プロジェクトで自分の Team と Bundle Identifier を設定し、端末を選んで Run します。Command Line Tools だけでは iPhone へ導入できません。[導入・署名・ビルド・端末確認](../native/docs/ja/06-build.md)に手順があります。

## 原生版の操作

起動時はクラシックです。上のモード名から切り替えます。盤面内をスワイプし、戻る矢印で取り消し、電球でヒント、自動プレイで開始／停止します。三点メニューにはやり直し、再開局、パズル・レスキューの選択があります。設定には明暗、音、触覚、動きを減らす、AI 品質、JSON バックアップがあります。

外部キーボードは矢印と WASD に対応します。デスクトップの Z/R/C/P は適用しないでください。動作中に最大二回のスワイプを待機でき、メニュー・背景移行・手動への切り替えで待機入力を処理して AI を止めます。狭い iPhone は縦配置、広い iPad は盤面と情報を左右に置き、小さいウィンドウにも合わせます。長い説明はスクロールできます。

AI を止め、設定から JSON を「ファイル」などへ書き出します。読み込みは原生版の進行を置き換えるので、移行先を先に保存してください。Python・Touch の JSON とは別形式です。原生版はヒントを依頼した時点で補助使用になり、推奨手を実行しなくても同じです。

## 既存の九章をすべて保持

- [操作・ジェスチャー・iPhone/iPad 配置](../native/docs/ja/01-start.md)
- [六モード](../native/docs/ja/02-rules.md)と[能力・得点](../native/docs/ja/03-expedition.md)
- [AI・記録・バックアップ](../native/docs/ja/04-ai-data.md)
- [問題への対処](../native/docs/ja/05-faq.md)と[ビルド・導入](../native/docs/ja/06-build.md)
- [九本の実演](../native/docs/ja/07-gallery.md)、[解答](../native/docs/ja/08-solutions.md)、[更新と検証](../native/docs/ja/09-release.md)

インストール済みなら操作章から、ソースを受け取った場合はビルド章から読みます。Mac 上のテストとレイアウト画像は、実機のタッチ、回転、Split View、背景復帰、VoiceOver、表示性能の代わりにはなりません。

## Touch v1：独立した Web 版

Web 版はネイティブ App とは別の版です。Safari のタッチ操作とホーム画面への追加に対応します。ネイティブ App はこの章の前半にある導入・操作手順を参照してください。

1. Safari で [LUMINA Web 版](https://lumina-2048.vercel.app/)を開きます。現在はアクセス制限があるため、利用権限のある Vercel アカウントでログインしてください。
2. 初回読込完了を待ち、共有 → ホーム画面に追加を選びます。
3. オフライン準備後に切断してホーム画面から起動を試します。キャッシュ前はオフライン利用を保証しません。
4. 盤面内スワイプ、方向ボタン、矢印／WASD で遊べます。
5. 設定で JSON を書き出し、別端末の **Touch 版**へ読み込みます。移行先も先に保存します。

六モード、ヒント、Worker AI、取り消し／やり直し、直近 100 操作リプレイ、レスキュー比較、明暗、音、動きを減らす設定があります。メニュー・背景・手動切り替えで自動プレイを止めます。Python 版の全キー操作はなく、AI の時間設定もデスクトップと同じではありません。

保存はサイトの IndexedDB で、予備とページ離脱時の緊急記録を持ちます。ブラウザー、端末、ホーム画面環境間で自動同期しません。サイトデータ削除、プライベート閲覧、OS の容量整理で失われる場合があるため、重要データは書き出してください。更新後も旧画面の場合は、先に保存し、接続して開き直して更新を待ちます。最初にサイトデータを消さないでください。

旧 URL から移行する場合は、先に旧サイトの設定で「导出进度」を選び、新サイトの「导入进度」で読み込んでください。ブラウザーのセーブは URL をまたいで自動移行されません。ホーム画面のアイコンも新しい URL から追加し直してください。

ソースは `mobile/` です。開発用 `python3 serve.py` は通常 Service Worker を登録しません。携帯端末向けの公開には HTTPS が必要です。原生との規則比較、Web 自動テスト、ブラウザー配置確認は、実機のオフライン起動・触覚・システムジェスチャーの検証を意味しません。
''')

w('zh-CN',12,r'''
## 常见问题

**为什么经典在 Mac 打开是大厅，手机却直接进棋盘？** 桌面 v12 先显示模式大厅，原生 1.0.1 默认进入经典，属于不同版本的入口设计。经典都排在第一位。

**为什么没有 Mac 的 exe，Windows 为什么不打开 command？** `.exe` 是 Windows 入口，`.command` 是 Mac 脚本。它们共享 Python 游戏代码，启动环境按系统准备。iPhone / iPad 则是独立 Swift 工程。

**文档有三种语言，游戏为什么仍是中文？** 本次交付新增的是三语说明与 README，没有把游戏界面改成三语。对应按钮原名保留在译文中。

**能保证自动玩合成 32768 吗？** 不能。AI 有预算、剪枝与启发式，随机局面不同。历史高分仅是具体试跑；这里没有把旧基准说成当前每台设备都能复现的保证。

**同一日为什么手机和电脑不同？** 先确认同版本、日期、操作序列、是否撤销和辅助。对照通过的规则不等于跨版本所有开局和存档相同，尤其远征选卡洗牌存在版本差异。

**文档动图比游戏慢？** 教学媒体按 12 fps 采样，便于阅读且控制文件体积。它不是游戏帧率录像，不用于证明屏幕刷新率。看操作细节可展开 MP4。

**星级或纪录不如预期？** 核对是否用了辅助、撤销、是否达到最短步数，以及是否看的是该玩法的纪录。最高成绩不会因为撤销当前局而下降。

## 源码与开发

| 目录 / 文件 | 用途 |
|---|---|
| `game.py`, `air_ui.py`, `interface_base.py` | 桌面入口与界面 |
| `engine.py`, `modes.py`, `persistence.py` | 规则、独立模式进度、后台保存 |
| `ai.py`, `search_native.py` | 桌面搜索与后台进程 |
| `expedition.py`, `rescue.py`, `puzzles.py` | 专用玩法规则与解法 |
| `desktop_start.py`, `platform_paths.py`, `check_runtime.py` | 平台启动、路径、锁和诊断 |
| `tests/`, `validation/v12/` | 桌面测试与保留证据 |
| `iOS/` | Swift 原生 App 工程 |
| `mobile/` | Touch Web 工程 |
| `docs/`, `README*.md` | 全平台手册与三语入口 |

文档单独 ZIP 只含说明、媒体、参考记录和生成工具，**不含可运行游戏或完整 App 源码**。Windows 附文档 ZIP 含 Windows 游戏和其运行环境，但也不含完整 iOS 工程。游戏根目录才是各版工程与发布物的集合。

桌面开发先准备对应平台虚拟环境，在游戏根目录执行：

```sh
python -m unittest discover -s tests
```

这里的 `python` 应替换为当前游戏环境解释器，Mac 为 `.venv/bin/python`，Windows 源码为 `.venv\Scripts\python.exe`。Windows 便携自检优先用 `check-windows.bat`。Web 在 `mobile/` 内运行 `node --test tests/*.test.js`，本地启动 `python3 serve.py`；Native 测试、Xcode 和设备检查见原生构建章。

字体与运行环境按现有许可证分发，桌面完整游戏中的 `THIRD_PARTY.md`、`fonts/OFL.txt` 和 Windows `licenses/` 应保留。系统苹方等只在本机读取，不从 Mac 复制给 Windows。不要因源码可见就假定所有代码有未声明的再分发授权。

## 验证记录如何区分

桌面 v12 的已有报告记录 **90 项测试通过**，另有六关远征 6,098 分 / 123 步、真实败局提取、字体回退与 Windows 静态包检查。这是保留的 v12 证据，非本次文档改动重新跑出的硬件报告。

原生 1.0.1 的已有记录包括 **38 项核心 / 交互检查、5,760 次混合操作**。网页有自己的规则与浏览器检查。三套证据不可互相代替。

本次新增文档的检查与媒体来源见 [文档 QA](../QA.md)：本地链接和页面锚点、三语章节、谜题路线、GIF / MP4 解码与帧数、包内资源、Windows 运行文件未改与个人存档未变。离线 HTML 的浏览器视觉和交互验收未完成，未将结构检查当作实际点击通过。

## 报告问题的模板

```text
平台与版本：Mac / Windows v12，Native 1.0.1，或 Touch v1
系统 / 设备 / 架构：
安装方式与文件名：
玩法、日期或章节：
精确操作步骤：
期望结果 / 实际结果：
是否可重复：
是否用了 AI、撤销或模式切换：
错误全文 / 截图 / 相关日志：
```

若涉及存档，先备份，再只分享愿意用于排查的副本；无需账户密码、签名证书等。请写明确平台和版本，这能避免把电脑快捷键问题当成手机手势问题。
''')
w('en',12,r'''
## Frequently asked questions

**Why does Mac open a lobby while native opens a board?** Desktop v12 opens mode selection; Native 1.0.1 starts in Classic. They have different entry designs, both keeping Classic first.

**Why is there no Mac exe?** `.exe` is the Windows entry and `.command` the Mac launcher. The two share Python game code but prepare platform-specific runtimes. iPhone/iPad use a separate Swift project.

**Why are game labels Chinese if documentation has three languages?** This delivery adds trilingual documentation and READMEs, not a game UI language selector. Translations preserve the actual button names.

**Does autoplay guarantee 32768?** No. Search is bounded and heuristic, with random outcomes. Historical high scores describe specific trials, not a promise for every version or device.

**Why do phone and computer Daily boards differ?** Check edition, date, action order, undo and assistance. Rule fixtures do not imply identical saves or every cross-edition start; Expedition offer shuffling in particular differs by edition.

**Why do tutorial GIFs look slower?** Media is sampled at 12 fps for readability and file size. It is not a display frame-rate recording or benchmark. Expand MP4 for playback controls.

**Why are stars or records different from expected?** Check assistance, undo, par and the mode whose record you are viewing. Undoing a current game does not lower an established best record.

## Source and development

| Path | Purpose |
|---|---|
| `game.py`, `air_ui.py`, `interface_base.py` | Desktop entry and UI |
| `engine.py`, `modes.py`, `persistence.py` | Rules, independent sessions, background saving |
| `ai.py`, `search_native.py` | Search and worker process |
| `expedition.py`, `rescue.py`, `puzzles.py` | Specialized rules and solvers |
| `desktop_start.py`, `platform_paths.py`, `check_runtime.py` | Platform launch, paths, locking, diagnostics |
| `tests/`, `validation/v12/` | Desktop tests and retained evidence |
| `iOS/` | Native Swift project |
| `mobile/` | Touch web project |
| `docs/`, `README*.md` | Unified handbooks and language entry points |

The standalone documentation ZIP contains manuals, media, reference reports and generation tools, **not a runnable game or full native source**. The Windows-with-docs ZIP includes the Windows game/runtime but not the full iOS project. The original game root is the collection of edition projects and releases.

Prepare a desktop environment, then run from the game root:

```sh
python -m unittest discover -s tests
```

Replace `python` with the game interpreter: `.venv/bin/python` on Mac or `.venv\Scripts\python.exe` for Windows source. Portable Windows users should use `check-windows.bat`. Within `mobile/`, use `node --test tests/*.test.js` and `python3 serve.py` for local web development. Native tests, Xcode builds and device checks are documented in its build chapter.

Retain `THIRD_PARTY.md`, `fonts/OFL.txt` and Windows `licenses/` in the complete game. System fonts such as PingFang are read locally, not copied from Mac for Windows distribution. Source visibility does not imply an unstated redistribution license.

## Separate evidence by edition

The retained Desktop v12 report records **90 passing tests**, a six-stage Expedition with 6,098 points/123 moves, real-loss Rescue extraction, font fallback and Windows static package checks. These are earlier v12 results, not new hardware tests performed for this documentation update.

Native 1.0.1 has **38 core/interaction checks and 5,760 mixed operations** in its retained evidence. Web has separate rule/browser checks. None substitutes for another edition.

See [documentation QA](../QA.md) for this pass: local links and anchors, translated chapters, solution routes, GIF/MP4 decoding and frame counts, packaged resources, unchanged Windows runtime files and unchanged player saves. Offline HTML browser visual/interaction acceptance remains incomplete; structural validation is not a claim of successful clicking through the reader.

## Useful bug report

```text
Edition: Mac/Windows v12, Native 1.0.1, or Touch v1
OS / device / CPU architecture:
Installation method and package filename:
Mode, date or chapter:
Exact reproduction steps:
Expected / actual result:
Repeatable?:
AI, undo or mode changes involved?:
Full error / screenshot / relevant log:
```

Back up before investigating save problems and share only a copy you are willing to use for diagnosis. Passwords and signing certificates are unnecessary. Always identify platform and edition so desktop keyboard issues are not confused with mobile gesture behavior.
''')
w('ja',12,r'''
## よくある質問

**Mac はロビー、原生版は盤面から始まるのはなぜ？** v12 はモード選択、Native 1.0.1 はクラシックから開始します。入口が異なりますが、どちらもクラシックを先頭にしています。

**Mac 用 exe は？** `.exe` は Windows 用、`.command` は Mac の起動スクリプトです。Python コードは共通で、実行環境は OS ごとに準備します。iPhone / iPad は別の Swift 工程です。

**説明書は三言語なのにゲームは中国語？** 今回は説明書と README の三言語化で、ゲーム内言語切り替えを追加する変更ではありません。訳文にも実際のボタン名を残しています。

**自動プレイなら必ず 32768？** 保証しません。時間制限・評価関数とランダムな結果があり、過去の高得点は特定の試行です。全端末・全版の保証ではありません。

**携帯と PC のデイリーが違う？** 版、日付、操作順、取り消し、補助を確認してください。規則比較の成功は、全開始状態やセーブの互換性を意味しません。特に遠征の選択肢の並べ方は版によって異なります。

**GIF が遅く見える？** 読みやすさと容量のため 12 fps で採取した教材です。実画面のフレームレート測定ではありません。MP4 を開くと再生操作ができます。

**星や記録が予想と違う？** 補助使用、取り消し、最短手数、表示中のモードを確認します。現在局を取り消しても過去の最高記録は下がりません。

## ソースと開発

| パス | 役割 |
|---|---|
| `game.py`, `air_ui.py`, `interface_base.py` | デスクトップ起動と画面 |
| `engine.py`, `modes.py`, `persistence.py` | 規則、モード保存、背景保存 |
| `ai.py`, `search_native.py` | 探索と別プロセス |
| `expedition.py`, `rescue.py`, `puzzles.py` | 専用モードと解法 |
| `desktop_start.py`, `platform_paths.py`, `check_runtime.py` | 起動、保存先、ロック、診断 |
| `tests/`, `validation/v12/` | デスクトップテストと証拠 |
| `iOS/` | Swift 原生工程 |
| `mobile/` | Touch Web 工程 |
| `docs/`, `README*.md` | 全版ガイドと三言語入口 |

説明書単独 ZIP は文章、媒体、参照報告、生成ツールを含み、**実行ゲームや完全な原生ソースは含みません**。Windows-with-docs ZIP は Windows ゲームと環境を含みますが、完全な iOS 工程は含みません。元のゲームルートが各版の工程と配布物をまとめた場所です。

デスクトップ環境を準備し、ゲームルートで実行します。

```sh
python -m unittest discover -s tests
```

`python` はゲーム用の実体に置き換えます。Mac は `.venv/bin/python`、Windows ソースは `.venv\Scripts\python.exe` です。ポータブル Windows では `check-windows.bat` を使います。Web は `mobile/` 内で `node --test tests/*.test.js`、開発起動は `python3 serve.py` です。原生版のテスト・Xcode・実機確認は専用ビルド章を参照してください。

ゲーム全体の `THIRD_PARTY.md`、`fonts/OFL.txt`、Windows `licenses/` を残します。苹方などシステム字体はローカルで読むもので、Windows 配布用にコピーしません。コードが読めることだけで、明示されていない再配布許諾を推定しないでください。

## 検証記録を区別する

保管された v12 報告は **90 テスト成功**、遠征六ステージ 6,098 点・123 手、実敗局からのレスキュー抽出、字体代替、Windows 静的確認を記録しています。以前の v12 の証拠であり、今回の説明書更新で新たに実施したハードウェア試験ではありません。

Native 1.0.1 の記録には **38 のコア／操作確認、5,760 回の混合操作**があります。Web にも独立した規則・ブラウザー確認があります。別の版の検証で代用はできません。

今回のリンク・アンカー、翻訳章、解答経路、GIF / MP4 の復号とフレーム数、配布資源、Windows 実行ファイル不変、個人セーブ不変の確認は[文書 QA](../QA.md)を参照してください。オフライン HTML のブラウザーによる外観・操作確認は未完了です。構造検査をクリック操作済みと表現していません。

## 問題報告の書式

```text
版：Mac/Windows v12、Native 1.0.1、Touch v1
OS・端末・CPU：
導入方法・配布ファイル名：
モード・日付・章：
正確な再現手順：
期待した結果・実際の結果：
再現するか：
AI・取り消し・モード変更の有無：
エラー全文・画像・関連ログ：
```

セーブ調査前にはバックアップし、診断に提供してよいコピーだけ共有します。パスワードや署名証明書は不要です。端末と版を明記し、PC のキー問題と携帯のジェスチャーを混同しないようにしてください。
''')

demo={
'zh-CN':[
('大厅：经典优先与精选玩法','从「经典与挑战」切到「精选玩法」，再返回经典。进入游戏后按 B 可以回大厅。'),
('经典：移动、撤销与重做','seed 42 的真实新局。向左、下、左、上、右移动，然后撤销、重做；观察棋盘、得分与步数同步恢复。'),
('AI 分析、单步与复盘','真正启动后台搜索，展示四方向分析和左方向预览，执行 AI 一步，再查看历史。复盘不会改变当前棋盘。'),
('解局：两步合成 64','第一章从初始状态连续向上两次，实际达标并获得三星。本段包含解答。'),
('远征：选能力与充能','seed 13 开局三选一，选择蓄能核心后移动，查看能量与规则面板。这里展示第一关开局，不是六关通关录像。'),
('重生：三步救局与路线对照','第一道练习从起点向右、上、上，达到三空格后查看对照，逐步比较。本段包含解答。'),
('每日：固定日期与撤销重做','使用正式 daily_game 创建 2026-09-29 挑战；演示方向操作、撤销和重做。无效方向不增加步数。'),
('冲刺：观察剩余步数','seed 42 的真实冲刺新局，走五步后撤销、重做。这里示范计步，不是第 60 步结算录像。')],
'en':[
('Lobby: Classic first and featured modes','Switch from Classic/Challenges to Featured, return and enter Classic. B returns to the lobby during play.'),
('Classic: move, undo and redo','A real seed-42 opening: left, down, left, up, right, then undo and redo. Board, score and move count restore together.'),
('AI analysis, one step and Replay','The actual worker computes direction analysis. Preview left, execute one AI move, then review history without changing the current board.'),
('Puzzle: reach 64 in two moves','Puzzle 01 from its original state: up, up, then the actual three-star result. Contains the solution.'),
('Expedition: choose an ability and gain energy','A seed-13 opening, Battery Core selection, moves, energy and the rules panel. This is stage-one instruction, not a full six-stage run.'),
('Rescue: three moves and route comparison','Practice 01: right, up, up creates three empty cells. Open comparison after success and step through. Contains the solution.'),
('Daily: fixed date, undo and redo','Created by the production daily_game function for 2026-09-29. Demonstrates moves, undo and redo; invalid directions do not add moves.'),
('Sprint: track the move allowance','A real seed-42 Sprint opening, five moves, undo and redo. This explains the counter, not the move-60 result.')],
'ja':[
('ロビー：クラシックを先頭に','クラシックのページから精选玩法へ移り、戻って開始します。対局中は B でロビーへ戻れます。'),
('クラシック：移動・取り消し・やり直し','seed 42 の実際の新局で左・下・左・上・右、その後に取り消しとやり直し。盤面・得点・手数が一緒に戻ります。'),
('AI 分析・一手・リプレイ','実際のワーカーで分析し、左の予測、一手実行、履歴表示を行います。リプレイでは現在の盤面を変えません。'),
('パズル：二手で 64','第一章を初期状態から上・上と動かし、実際に三つ星で達成します。解答を含みます。'),
('遠征：能力選択と充電','seed 13 の新局で蓄能核心を選び、移動とエネルギー、説明パネルを見ます。第一ステージの導入で、六ステージ全編ではありません。'),
('レスキュー：三手と経路比較','練習一問目を右・上・上で三空きに戻し、成功後に比較を開いて進めます。解答を含みます。'),
('デイリー：固定日付と履歴','正式な daily_game で 2026-09-29 を生成し、移動・取り消し・やり直しを示します。無効な方向は手数に入りません。'),
('スプリント：残り手数を見る','seed 42 の新局を五手進め、取り消しとやり直しを行います。手数の説明で、60 手目の終了映像ではありません。')]
}
files=['10-desktop-lobby','11-desktop-classic','12-desktop-ai-replay','13-desktop-puzzle','14-desktop-expedition','15-desktop-rescue','16-desktop-daily','17-desktop-sprint']
for lang in titles:
 lead={
 'zh-CN':'八段桌面实演 + 九段原生实演。全部来自实际游戏代码运行，先生成 MP4，再从交付 MP4 解码转换 GIF。以 12 fps 采样作为操作教学，不是显示器帧率测量。HTML 内动图默认暂停，可点播放或展开 MP4；Markdown 查看器通常自动循环。',
 'en':'Eight desktop clips plus nine native clips, all from the actual game code. Each GIF was made by decoding its delivered MP4. Sampling at 12 fps serves instruction, not display performance measurement. GIFs start paused in HTML; play them or expand MP4. Markdown viewers usually loop GIFs automatically.',
 'ja':'デスクトップ八本と原生九本を収録。実際のコードで動かした画像から MP4 を作り、その配布 MP4 を復号して GIF にしています。12 fps の教材で、実画面の性能測定ではありません。HTML は停止状態から再生でき、MP4 も開けます。Markdown は通常自動で繰り返します。'}[lang]
 h={'zh-CN':'## Mac / Windows 桌面 v12 的操作\n\n录制环境为 Mac 上的 Python / pygame 实际渲染器，使用 SDL dummy 与隔离临时存档。Windows 共用此代码，但不是 Windows 实机录屏。静音；没有使用玩家个人存档。',
 'en':'## Mac / Windows Desktop v12 controls\n\nCaptured from the real Python/pygame renderer on Mac using SDL dummy and an isolated temporary profile. Windows shares this code, but these are not Windows hardware recordings. Silent; no personal player save was used.',
 'ja':'## Mac / Windows デスクトップ v12 の操作\n\nMac の実際の Python / pygame 描画を SDL dummy と独立した一時セーブで記録しています。Windows と共通コードですが、Windows 実機の録画ではありません。無音で、個人セーブは使いません。'}[lang]
 parts=[lead,h]
 for (title,desc),name in zip(demo[lang],files):
  meta=next(m for m in json.loads((docs/'media/manifest.json').read_text()) if m['name']==name)
  parts.append(f'### {title}\n\n{desc}\n\n![{title}](../media/{name}.gif)\n\n[GIF](../media/{name}.gif) · [MP4 · {meta["duration"]:.2f} s](../media/{name}.mp4) · [PNG](../media/{name}-poster.png)')
 native=(root/'docs/native/docs'/lang/'07-gallery.md').read_text().split('\n',1)[1].replace('../media/','../native/docs/media/').replace('\n## ','\n### ')
 parts.append({'zh-CN':'## iPhone / iPad 原生版的操作（Mac 主机预览）','en':'## Native iPhone / iPad controls (Mac host preview)','ja':'## iPhone / iPad 原生版の操作（Mac ホスト表示）'}[lang]+'\n'+native)
 w(lang,10,'\n\n'.join(parts))
 solutions=(root/'docs/native/docs'/lang/'08-solutions.md').read_text().split('\n',1)[1]
 note={'zh-CN':'以下 12 章与 3 道练习的资源、起点和路线已与桌面 v12 核对；不同版本按钮位置请分别看对应操作章。','en':'The resources, starting boards and routes for these twelve puzzles and three practices have been checked against Desktop v12. Use each edition’s control chapter for its button locations.','ja':'以下の十二章・三問の練習は、資源・初期盤面・経路をデスクトップ v12 と照合しています。ボタン位置は各版の操作章を参照してください。'}[lang]
 w(lang,11,note+'\n'+solutions)

readmes={'zh-CN': '# LUMINA 2048\n'
          '\n'
          '[简体中文](README.zh-CN.md) · [English](README.en.md) · [日本語](README.ja.md)\n'
          '\n'
          '滑动方块，合并相同数字，从 2 一路挑战到 2048，甚至更高。想轻松玩一局，就选经典；想换个挑战，可以试试限步谜题、能力远征，或者把一盘败局救回来。\n'
          '\n'
          '## 选择你的设备\n'
          '\n'
          '| 设备 | 如何开始 | 使用说明 |\n'
          '|---|---|---|\n'
          '| **Mac** | 在游戏文件夹中双击 **启动游戏.command**。首次使用需要按安装说明准备环境。 | [Mac 安装与排错](docs/zh-CN/07-macos.md) |\n'
          '| **Windows 10 / 11 · x64** | 完整解压 Windows 便携包，双击 **2048.exe**。无需另外安装 Python。 | [Windows '
          '安装与排错](docs/zh-CN/08-windows.md) |\n'
          '| **iPhone / iPad** | 原生版目前提供源码工程，需要在 Mac 上用 Xcode 构建并签名安装。尚无可直接安装的 IPA 或商店下载。 | [iPhone / iPad '
          '安装与操作](docs/zh-CN/09-mobile.md) |\n'
          '| **浏览器** | 使用单独的触屏网页版，支持滑动与方向按钮。 | [网页版使用说明](docs/zh-CN/09-mobile.md) |\n'
          '\n'
          '对应版本：Mac / Windows 桌面 v12；iPhone / iPad 原生 1.0.1；触屏网页版 v1。原生版的最低系统目标为 iOS / iPadOS '
          '16.4。游戏界面目前主要使用中文，本说明书提供中文、英文和日文。\n'
          '\n'
          'Windows 请保留完整解压目录，不要只拷贝 exe。若拿到的是“文档压缩包”，里面只有说明和演示，不能直接启动游戏。\n'
          '\n'
          '## 第一次怎么玩\n'
          '\n'
          '1. 选择「经典」。电脑端从模式大厅进入，原生手机版打开后默认进入经典。\n'
          '2. 用方向键 / WASD，或在棋盘内拖动、滑动，让所有方块一起移动。\n'
          '3. 相同数字相遇会合并：2 + 2 = 4，4 + 4 = 8。一次移动中新合并的方块不会再次合并。\n'
          '4. 每次有效移动后通常会出现一枚新方块；完全不能移动的方向不扣步数、不落子。\n'
          '5. 合成 2048 后还可以继续。棋盘满了也不一定结束，只要还能合并就还有机会。\n'
          '\n'
          '![经典模式：移动、撤销与重做](docs/media/11-desktop-classic.gif)\n'
          '\n'
          '上图来自 Mac 桌面版的实际操作。更多玩法请看[动图与视频教程](docs/zh-CN/10-gallery.md)。\n'
          '\n'
          '## 六种玩法，随你选择\n'
          '\n'
          '| 玩法 | 适合怎样的一局 |\n'
          '|---|---|\n'
          '| **经典** | 不限步数，慢慢整理棋盘，挑战更高数字。 |\n'
          '| **能力远征** | 六关限步挑战，逐关选择能力，积攒能量后使用交换与凝时。 |\n'
          '| **绝境重生** | 从败局中找转机，六步内腾出至少三个空格；附三道练习。 |\n'
          '| **解局剧场** | 十二道固定谜题，在规定步数内合成目标数字，争取三星。 |\n'
          '| **每日同局** | 按日期生成挑战，同一天按相同顺序操作可复现落子。 |\n'
          '| **60 步冲刺** | 用六十次有效移动争取高分。 |\n'
          '\n'
          '各模式分别保存当前进度。详细的计分、星级和胜负条件见[游戏规则](docs/zh-CN/03-rules.md)，远征的全部能力见[能力说明](docs/zh-CN/04-expedition.md)。\n'
          '\n'
          '## 想自己想，或让 AI 帮一手\n'
          '\n'
          '「提示」推荐下一步；「自动玩」让 AI 接着走，暂停或手动移动即可接管。提示与 AI 属于辅助，会影响该局的记录类别；撤销不能去掉辅助标记。AI 在本机计算，不能保证每局都达到指定数字。\n'
          '\n'
          '电脑端常用快捷键：\n'
          '\n'
          '| 操作 | 按键 |\n'
          '|---|---|\n'
          '| 移动 | 方向键 / WASD |\n'
          '| 撤销 / 重做 | Z / Shift+Z 或 Y |\n'
          '| 提示 / AI 走一步 | H / Enter |\n'
          '| 自动玩 / 暂停 | 空格 |\n'
          '| 模式大厅 / 复盘 | B / R |\n'
          '\n'
          '完整按钮与快捷键见[电脑操作指南](docs/zh-CN/02-controls.md)。手机和平板使用屏幕按钮；不要把电脑快捷键直接套到原生 App 上。\n'
          '\n'
          '## 保存与换设备\n'
          '\n'
          '游戏自动保存，退出前请正常关闭窗口。Mac 存档在游戏目录的 `data/`；Windows 存档在 '
          '`%LOCALAPPDATA%\\2048-Atelier\\data`。原生版和网页版可在设置里导出 JSON 备份。\n'
          '\n'
          '没有自动跨设备同步。Mac 与 Windows 同版 v12 '
          '可按步骤迁移存档；原生版、网页版与桌面版的格式不同。换设备或导入前先看[备份、迁移与升级](docs/zh-CN/06-saves.md)。\n'
          '\n'
          '## 需要帮助时\n'
          '\n'
          '- [打开完整中文手册](docs/zh-CN/index.html) · [选择其他语言](docs/index.html)\n'
          '- [常见问题](docs/zh-CN/12-support.md) · [iPhone / iPad 详细手册](docs/native/docs/zh-CN/index.html)\n'
          '- [全部谜题与残局解答](docs/zh-CN/11-solutions.md)：含剧透，建议先自己试一试。\n'
          '\n'
          'Windows 打不开时，用 `启动游戏.bat` 查看错误，或运行 `check-windows.bat` '
          '自检。具体兼容和验证范围见[版本说明](docs/zh-CN/12-support.md)：Windows 实机验收和 iPhone / iPad 设备验收仍未完成。\n',
 'en': '# LUMINA 2048\n'
       '\n'
       '[简体中文](README.zh-CN.md) · [English](README.en.md) · [日本語](README.ja.md)\n'
       '\n'
       'Slide tiles, merge equal numbers and work your way from 2 to 2048—and beyond. Choose Classic for an '
       'open-ended game, solve a short puzzle, build abilities across an Expedition, or rescue a position '
       'from a lost game.\n'
       '\n'
       '## Choose your device\n'
       '\n'
       '| Device | Get started | Instructions |\n'
       '|---|---|---|\n'
       '| **Mac** | Double-click **启动游戏.command** in the game folder. First-time setup requires the '
       'environment described in the installation guide. | [Mac installation and help](docs/en/07-macos.md) '
       '|\n'
       '| **Windows 10/11 · x64** | Fully extract the Windows portable package and open **2048.exe**. No '
       'separate Python installation. | [Windows installation and help](docs/en/08-windows.md) |\n'
       '| **iPhone / iPad** | The native edition currently ships as source. Build and sign it with Xcode on '
       'a Mac before installation. No installable IPA or store download is available. | [iPhone / iPad setup '
       'and controls](docs/en/09-mobile.md) |\n'
       '| **Browser** | Use the separate touch web edition with swipes or direction buttons. | [Web '
       'instructions](docs/en/09-mobile.md) |\n'
       '\n'
       'Editions: Mac/Windows Desktop v12, Native iPhone/iPad 1.0.1 and Touch Web v1. The native deployment '
       'target is iOS/iPadOS 16.4+. Game labels are currently primarily Chinese; the handbook is available '
       'in Chinese, English and Japanese.\n'
       '\n'
       'Keep the whole extracted Windows folder, not only the exe. A documentation-only ZIP contains '
       'instructions and demonstrations, not a playable game.\n'
       '\n'
       '## Your first game\n'
       '\n'
       '1. Select 「经典」 (Classic). Desktop starts at a mode lobby; the native mobile app opens Classic by '
       'default.\n'
       '2. Use arrows/WASD, or drag/swipe inside the board, to move all tiles in one direction.\n'
       '3. Equal numbers merge: 2 + 2 = 4, then 4 + 4 = 8. A tile created by a merge cannot merge again in '
       'that move.\n'
       '4. A valid move normally adds a new tile. A direction that changes nothing costs no move and spawns '
       'nothing.\n'
       '5. Keep playing after 2048. Even a full board can survive if a merge is still possible.\n'
       '\n'
       '![Classic: moving, undo and redo](docs/media/11-desktop-classic.gif)\n'
       '\n'
       'Actual play from the Mac desktop edition. See more in the [animated '
       'tutorials](docs/en/10-gallery.md).\n'
       '\n'
       '## Six ways to play\n'
       '\n'
       '| Mode | What to expect |\n'
       '|---|---|\n'
       '| **Classic** | Unlimited moves to organize your board and reach larger tiles. |\n'
       '| **Expedition** | Six stages with move limits, ability choices, energy, Swap and Freeze. |\n'
       '| **Rescue** | Recover at least three empty cells in six moves from a lost-game position; three '
       'practices included. |\n'
       '| **Puzzle Theatre** | Twelve fixed puzzles with target tiles, move limits and three-star '
       'challenges. |\n'
       '| **Daily** | A date-based challenge: the same date and action sequence reproduce spawns. |\n'
       '| **60-Move Sprint** | Score as much as possible in sixty valid moves. |\n'
       '\n'
       'Modes retain separate progress. Read the [rules](docs/en/03-rules.md) for scores, stars and winning '
       'conditions, or the [Expedition guide](docs/en/04-expedition.md) for every ability.\n'
       '\n'
       '## Play yourself or ask AI for a hand\n'
       '\n'
       'Hint recommends a move. Autoplay keeps playing until you pause or take over manually. Hints and AI '
       'count as assistance and affect the record category; Undo cannot clear that flag. AI runs locally and '
       'does not guarantee a particular tile in every game.\n'
       '\n'
       'Common desktop shortcuts:\n'
       '\n'
       '| Action | Key |\n'
       '|---|---|\n'
       '| Move | Arrows / WASD |\n'
       '| Undo / redo | Z / Shift+Z or Y |\n'
       '| Hint / one AI move | H / Enter |\n'
       '| Autoplay / pause | Space |\n'
       '| Mode lobby / Replay | B / R |\n'
       '\n'
       'See [desktop controls](docs/en/02-controls.md) for the full list. Phones and tablets use on-screen '
       'buttons; desktop shortcuts do not all apply to the native App.\n'
       '\n'
       '## Save and change devices\n'
       '\n'
       'Progress saves automatically. Close the game normally before disconnecting a drive. Mac saves are in '
       "the game folder's `data/`; Windows saves are in `%LOCALAPPDATA%\\2048-Atelier\\data`. Native and Web "
       'editions can export JSON backups in settings.\n'
       '\n'
       'There is no automatic cross-device sync. Matching Desktop v12 saves can move between Mac and '
       'Windows; Native, Web and Desktop formats are different. Read [backup, transfer and '
       'updates](docs/en/06-saves.md) before changing devices or importing.\n'
       '\n'
       '## Need help?\n'
       '\n'
       '- [Open the complete English handbook](docs/en/index.html) · [Choose a language](docs/index.html)\n'
       '- [Frequently asked questions](docs/en/12-support.md) · [Detailed native iPhone/iPad '
       'manual](docs/native/docs/en/index.html)\n'
       '- [All Puzzle and Rescue solutions](docs/en/11-solutions.md)—spoilers; try the challenges first.\n'
       '\n'
       'If Windows does not launch, use `启动游戏.bat` to see the error or `check-windows.bat` for diagnostics. '
       '[Release notes](docs/en/12-support.md) describe verification limits: Windows hardware acceptance and '
       'iPhone/iPad device acceptance remain incomplete.\n',
 'ja': '# LUMINA 2048\n'
       '\n'
       '[简体中文](README.zh-CN.md) · [English](README.en.md) · [日本語](README.ja.md)\n'
       '\n'
       'タイルを動かし、同じ数字を合体させて、2 から 2048、その先へ。じっくり遊ぶならクラシック、短い問題ならパズル。能力を選ぶ遠征や、負けた局面を立て直すレスキューも楽しめます。\n'
       '\n'
       '## 使う端末を選ぶ\n'
       '\n'
       '| 端末 | 始め方 | 説明 |\n'
       '|---|---|---|\n'
       '| **Mac** | ゲームフォルダーの **启动游戏.command** をダブルクリック。初回は導入ガイドに従って環境を準備します。 | [Mac '
       'の導入と対処](docs/ja/07-macos.md) |\n'
       '| **Windows 10 / 11・x64** | ポータブル版を完全に展開して **2048.exe** を開きます。Python の別途導入は不要です。 | [Windows '
       'の導入と対処](docs/ja/08-windows.md) |\n'
       '| **iPhone / iPad** | ネイティブ版は現在ソースでの提供です。Mac の Xcode でビルド・署名して導入します。インストール用 IPA やストア配信はありません。 | '
       '[iPhone / iPad の導入と操作](docs/ja/09-mobile.md) |\n'
       '| **ブラウザー** | 独立したタッチ Web 版を、スワイプや方向ボタンで遊べます。 | [Web 版の説明](docs/ja/09-mobile.md) |\n'
       '\n'
       '対応する版は Mac / Windows デスクトップ v12、iPhone / iPad ネイティブ 1.0.1、タッチ Web v1 です。ネイティブ版の対象は iOS / iPadOS 16.4 '
       '以上。ゲーム表示は現在主に中国語で、説明書は中国語・英語・日本語に対応しています。\n'
       '\n'
       'Windows は exe だけでなく、展開したフォルダー全体を残してください。説明書専用 ZIP は文章と実演のみで、ゲームは起動できません。\n'
       '\n'
       '## 最初の一局\n'
       '\n'
       '1. 「经典」（クラシック）を選びます。PC はモード選択から、ネイティブの携帯版はクラシックから始まります。\n'
       '2. 矢印／WASD、または盤面内のドラッグ・スワイプで、全タイルを一方向に動かします。\n'
       '3. 同じ数字が合体します。2 + 2 = 4、4 + 4 = 8。その手でできたタイルは、同じ手では再合体しません。\n'
       '4. 有効な移動後には通常、新しいタイルが出ます。動かない方向は手数を使わず、出現もありません。\n'
       '5. 2048 の後も続けられます。満杯でも、合体できる組み合わせがあればまだ続行できます。\n'
       '\n'
       '![クラシックの移動・取り消し・やり直し](docs/media/11-desktop-classic.gif)\n'
       '\n'
       'Mac デスクトップ版の実際の操作です。[GIF と動画のチュートリアル](docs/ja/10-gallery.md)でほかの遊び方も確認できます。\n'
       '\n'
       '## 六つの遊び方\n'
       '\n'
       '| モード | 内容 |\n'
       '|---|---|\n'
       '| **クラシック** | 手数無制限で盤面を整え、より大きな数字を目指します。 |\n'
       '| **遠征** | 六ステージの手数制限。能力を選び、エネルギーで交換や凝時を使います。 |\n'
       '| **レスキュー** | 敗局からの局面を六手以内に三マス以上の空きへ戻します。練習三問付き。 |\n'
       '| **パズルシアター** | 十二問の固定パズル。指定手数で目標の数字を作り、三つ星を狙います。 |\n'
       '| **デイリー** | 日付ごとの課題。同じ日付と操作順なら出現を再現できます。 |\n'
       '| **60 手スプリント** | 有効な六十手で高得点を目指します。 |\n'
       '\n'
       '進行はモードごとに保持します。得点・星・勝敗は[ゲームのルール](docs/ja/03-rules.md)、遠征の全能力は[能力ガイド](docs/ja/04-expedition.md)を参照してください。\n'
       '\n'
       '## 自分で考える、AI に一手頼む\n'
       '\n'
       'ヒントは次の方向を提案します。自動プレイは停止するか手動で動かすまで続けます。ヒントや AI は補助使用として記録の分類に反映され、取り消しでは解除されません。AI '
       'は端末内で動き、毎回決まった数字に到達する保証はありません。\n'
       '\n'
       'PC の主なキー操作です。\n'
       '\n'
       '| 操作 | キー |\n'
       '|---|---|\n'
       '| 移動 | 矢印／WASD |\n'
       '| 取り消し／やり直し | Z／Shift+Z または Y |\n'
       '| ヒント／AI の一手 | H／Enter |\n'
       '| 自動プレイ／停止 | Space |\n'
       '| モード選択／リプレイ | B／R |\n'
       '\n'
       '全操作は[PC 操作ガイド](docs/ja/02-controls.md)へ。携帯・タブレットは画面のボタンを使います。PC のキー操作がそのままネイティブ App に使えるわけではありません。\n'
       '\n'
       '## 保存と端末の変更\n'
       '\n'
       '自動保存されます。ディスクを外す前に正常終了してください。Mac はゲーム内の `data/`、Windows は `%LOCALAPPDATA%\\2048-Atelier\\data` '
       'に保存します。ネイティブ版と Web 版は設定から JSON を書き出せます。\n'
       '\n'
       '端末間の自動同期はありません。同じ v12 の Mac と Windows '
       'は移行できますが、ネイティブ・Web・デスクトップは別形式です。端末の変更や読み込みの前に[バックアップと移行](docs/ja/06-saves.md)を確認してください。\n'
       '\n'
       '## 困ったときは\n'
       '\n'
       '- [日本語の全ガイド](docs/ja/index.html) · [言語を選ぶ](docs/index.html)\n'
       '- [よくある質問](docs/ja/12-support.md) · [iPhone / iPad の詳しい説明](docs/native/docs/ja/index.html)\n'
       '- [パズルとレスキューの全解答](docs/ja/11-solutions.md)：ネタバレを含むので、まず自分で挑戦してみてください。\n'
       '\n'
       'Windows が起動しない場合は `启动游戏.bat` でエラーを確認するか、`check-windows.bat` '
       'で診断します。[版と検証の説明](docs/ja/12-support.md)に対応範囲があります。Windows 実機、iPhone / iPad 端末での受け入れ確認は未完了です。\n'}
web_notices={
 'zh-CN':'**网页版入口：[打开 LUMINA 2048](https://lumina-2048.vercel.app/)**\n\n当前网页需要有权限的 Vercel 账号登录。换网址前，请在旧网页设置中「导出进度」，再到新网页「导入进度」；存档不会自动跟随网址迁移。',
 'en':'**Web edition: [Open LUMINA 2048](https://lumina-2048.vercel.app/)**\n\nThe website currently requires an authorized Vercel account. Before switching addresses, export progress with 「导出进度」 in the old site’s settings, then import it with 「导入进度」 on the new site. Saves do not move automatically between addresses.',
 'ja':'**Web 版：[LUMINA 2048 を開く](https://lumina-2048.vercel.app/)**\n\n現在は利用権限のある Vercel アカウントでのログインが必要です。URL を切り替える前に、旧サイトの設定で「导出进度」を選び、新サイトの「导入进度」で読み込んでください。セーブは新しい URL へ自動では移行されません。'
}
download_notices={'zh-CN': '**下载：[应用包和离线文档](https://github.com/srwang0506/2048-Atelier/releases/latest)** · [查看源码](https://github.com/srwang0506/2048-Atelier)\n\nWindows 请下载 Releases 中的 Windows x64 包；GitHub 的“Download ZIP”只下载源码。iPhone / iPad 当前提供可构建的原生源码，尚无已签名安装包。', 'en': '**Downloads: [App packages and offline manuals](https://github.com/srwang0506/2048-Atelier/releases/latest)** · [Source code](https://github.com/srwang0506/2048-Atelier)\n\nFor Windows, choose the Windows x64 package in Releases. GitHub’s “Download ZIP” contains source code only. The iPhone/iPad edition currently provides buildable native source, without a signed installer.', 'ja': '**ダウンロード：[アプリ配布物・オフライン説明書](https://github.com/srwang0506/2048-Atelier/releases/latest)** · [ソースコード](https://github.com/srwang0506/2048-Atelier)\n\nWindows は Releases の Windows x64 パッケージを選んでください。GitHub の「Download ZIP」はソースのみです。iPhone / iPad 版は現在、ビルド用の原生ソースを提供しており、署名済みインストーラーはありません。'}
for lang in web_notices:
 web_notices[lang]+="\n\n"+download_notices[lang]
for lang,text in readmes.items():
 text=text.replace('\n## ','\n'+web_notices[lang]+'\n\n## ',1)
 (root/f'README.{lang}.md').write_text(text)
shutil.copy2(root/'README.zh-CN.md',root/'README.md')
# Correct the distributed font extension; native text does not assume desktop resources.
for p in [*docs.glob('*/*.md'),*root.glob('README*.md')]:
 if p.name.startswith('._'):continue
 s=p.read_text().replace('NotoSansSC-*.ttf','NotoSansSC-*.otf').replace('## 实際操作','## 实际操作')
 p.write_text(s)
print('Wrote 36 platform chapters and four root READMEs; retained all native documentation.')
