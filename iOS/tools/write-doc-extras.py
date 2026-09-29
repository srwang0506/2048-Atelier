from pathlib import Path
import json
root=Path(__file__).resolve().parents[1]
chapters=['01-start','02-rules','03-expedition','04-ai-data','05-faq','06-build','07-gallery','08-solutions','09-release']
titles={
'zh-CN':['开始游玩与完整操作','六种玩法的完整规则','能力远征：关卡与能力','智能助手、记录与存档','常见问题与问题反馈','安装、构建与开发','九段动图教程','谜题与残局解答（含剧透）','版本与验证范围'],
'en':['Getting started and controls','Rules for all six modes','Expedition stages and abilities','AI, records and saves','Troubleshooting and support','Installation and development','Nine animated tutorials','Puzzle and Rescue solutions (spoilers)','Release and validation'],
'ja':['はじめに・操作ガイド','六つのモードのルール','能力遠征・ステージと能力','AI・記録・セーブ','よくある質問と報告','インストールと開発','九本の動くチュートリアル','パズルとレスキューの解答（ネタバレ）','更新履歴と検証範囲']}
media=json.loads((root/'docs/media/manifest.json').read_text())
cliptext={
'zh-CN':[
('经典：移动、合并与落子','从 seed 42 实际游玩的中盘继续，依次观察整盘滑动、相同数字合并、得分上涨及新方块出现。方向标在画面底部。','先尝试保持大数字在角落；注意没有合并的位移也会产生新方块。'),
('撤销与重做：同一落子被恢复','执行一步，撤销，再重做。观察棋盘、得分和移动次数一起变化。','重做藏在三点菜单；随机状态也一起恢复，所以不是重新抽签。'),
('智能助手：提示、执行、自动玩、暂停','先请求提示，再执行建议，随后打开自动游玩并暂停。','查看底部从手动局变成辅助局；暂停之后辅助标记仍在。'),
('远征：三选一与首关','开始新的 seed 42 远征，选择蓄能核心，再完成数次有效移动。','同一步多组合并会获得更多能量，先理解目标分与总分的区别。'),
('远征：凝时与交换','从实际获得 12 能量的局面继续，先凝时，再选两枚不同数字交换，最后移动两次。','观察使用主动能力时剩余步数不变；凝时后的移动不会生成新方块。'),
('谜题：两步合成 64','完整演示第 01 题，从重置后的棋盘向上、再向上，合成 64。','本段含解答；未请求提示且没有撤销，因此得到三星。'),
('残局：从错误走法到可解路线','精选“一线生机”：先复现原来的向左走法导致无路可走，再从同一起点执行右、上、上。','比较两种结局；成功目标是落子后至少三个空位。它展示实际操作过程，不是完整经典局录像。'),
('每日：相同日期与重开','固定演示 2026-09-29 的每日局，移动三次后重开。','观察重开后的两枚初始方块与开始时一致；不是联网同步。'),
('冲刺：最后三步与结束','seed 42 的真实冲刺先推进到第 57 步，再记录最后三步及结算。','看剩余次数从 3 到 0；不是秒表，也没有第 61 步。')],
'en':[
('Classic: slide, merge and spawn','Continue a real seed-42 game from midgame. Watch the entire board slide, equal values merge, the score rise and a new tile appear. The bottom strip identifies directions.','Try keeping your largest tile near a corner. A slide without a merge still spawns a tile.'),
('Undo and redo: restore the same spawn','Make one move, undo it, then redo. The board, score and counter change together.','Redo is in the ellipsis menu. The random state is restored too; this is not a reroll.'),
('AI: hint, follow, autoplay and pause','Request a hint, follow it, run autoplay, then pause.','The footer changes from manual to assisted. Pausing does not clear the assisted flag.'),
('Expedition: draft and opening moves','Begin a seed-42 expedition, choose Battery Core and make several valid moves.','Multiple merged pairs earn more energy. Distinguish the stage target from cumulative score.'),
('Expedition: freeze and swap','Continue from an actually played position with 12 energy. Freeze, select two different values to swap, then make two moves.','Active powers leave the move counter unchanged. Frozen moves do not spawn a new tile.'),
('Puzzle: make 64 in two moves','Puzzle 01 from its reset state: up, then up, reaching 64.','Contains the solution. No hint or undo is used, so the result earns three stars.'),
('Rescue: a failed move and a recovery route','Practice A Glimmer of Hope: left reproduces the original blocked outcome. Restart, then right, up, up.','Compare the outcomes. Success requires at least three empty cells after spawning. This shows actual challenge actions, not a full Classic recording.'),
('Daily: same date, same restart','Use the fixed demonstration date 2026-09-29, make three moves, then restart.','The two initial tiles match the opening. No network synchronization is involved.'),
('Sprint: final three moves','A real seed-42 Sprint is advanced to move 57, then the last three moves and result are captured.','Remaining moves fall from 3 to 0. This is not a timer, and there is no move 61.')],
'ja':[
('クラシック：移動・合体・出現','seed 42 で実際に進めた中盤から再開。盤面全体の移動、同じ数字の合体、得点、新タイルを確認します。方向は下の帯に表示します。','最大タイルを角付近に保つ練習に。合体しない移動でも新タイルは出ます。'),
('戻す・やり直す：同じ出現を復元','一手動かし、戻して、やり直します。盤面、点数、手数が一緒に変わります。','やり直しは三点メニュー内です。乱数状態も復元するので引き直しではありません。'),
('AI：ヒント・実行・自動・停止','ヒントを要求して実行し、自動プレイを開始してから止めます。','下部表示が手動からアシストへ変化。止めてもアシスト区分は残ります。'),
('遠征：三択と序盤','seed 42 の新しい遠征で蓄電コアを選び、数手動かします。','複数組の合体でエネルギーが増えます。ステージ点と累計点の違いを確認します。'),
('遠征：凝時と交換','実際の操作で 12 エネルギーを得た状態から、凝時、異なる二枚の交換、二回の移動を実演します。','能力を使っても残り手数は変わらず、凝時中の移動では新タイルが出ません。'),
('パズル：二手で 64','第 01 問を最初から、上、上と動かして 64 にします。','解答を含みます。ヒントと戻すを使わず、星三つを取得します。'),
('レスキュー：失敗する手と救済ルート','練習「一线生机」で元の左移動による詰みを再現。最初からやり直して、右、上、上と進めます。','二つの結末を比較します。成功には出現後の空き三マスが必要。クラシック全局の録画ではなく、問題の実操作です。'),
('デイリー：同じ日付で再開始','例の日付 2026-09-29 で三手動かし、最初から始め直します。','最初の二枚が元に戻ることを確認します。通信による同期ではありません。'),
('スプリント：最後の三手','seed 42 の本物の局を 57 手目まで進め、残り三手と終了を収録します。','残りが 3 から 0 へ減ります。秒数制限ではなく、第 61 手はありません。')]}
intros={
'zh-CN':'以下九段 GIF 均由原生代码实际运行的采样视频转换，另附 MP4 原视频。录制平台为 macOS 原生预览，**不是 iPhone / iPad 录屏，也不代表设备帧率**。底部英文条是教学标注。页面中可以暂停动图；Markdown 阅读器通常会自动循环。MP4 使用 H.264 编码，可在阅读版展开视频播放器，或下载后单独播放。所有素材本地保存，无需联网。',
'en':'These nine GIFs are converted from sampled videos of the actual native code running. The MP4 source videos are included. Capture platform: macOS native preview, **not iPhone / iPad screen recording or a device FPS test**. The English bottom strip is a tutorial annotation. The HTML reader can pause animations; Markdown viewers usually loop them. MP4 uses H.264. Expand the video player in the HTML reader or download it for separate playback. All media is local and works offline.',
'ja':'九本の GIF は原生コードを実行して採取した動画から変換し、元の MP4 も同梱しています。環境は macOS ネイティブプレビューで、**iPhone / iPad の録画や実機 FPS 検査ではありません**。下の英語帯は教材の注釈です。HTML では停止可能、Markdown では通常ループします。MP4 は H.264 形式です。HTML の動画プレイヤーを開くか、ダウンロードして再生できます。すべてローカルで、通信は不要です。'}
for lang in titles:
    folder=root/'docs'/lang
    lines=['# '+titles[lang][6],intros[lang]]
    for meta, (title,desc,note) in zip(media,cliptext[lang]):
        n=meta['name']; duration=round(meta['duration'],2)
        lines += ['## '+title,desc,f'![{title}](../media/{n}.gif)',note,f'[GIF](../media/{n}.gif) · [MP4 · {duration} s](../media/{n}.mp4) · [PNG](../media/{n}-poster.png)']
    lines += ['[Media / 媒体 / メディア](../media/README.md)']
    (folder/'07-gallery.md').write_text('\n\n'.join(lines)+'\n')

levels=json.loads((root/'Sources/LuminaCore/Resources/puzzle-levels.json').read_text())
rescues=json.loads((root/'Sources/LuminaCore/Resources/rescue-practice.json').read_text())
arrows={'left':'←','up':'↑','right':'→','down':'↓'}
for lang in titles:
    text={'zh-CN':['# 谜题与残局解答（含剧透）','请先自行尝试，再打开本章。所有路线都从对应问题的初始盘面开始；请先重新开始该题。箭头表示移动方向，0 表示空格。路线直接从随 App 的资源读取，避免翻译时改错方向。','本章的阅读发生在 App 之外，游戏无法自动标记你读过外部攻略。若要保持个人“纯手动”挑战的意义，请自行避免使用攻略；不要把已经知道解法的练习成绩当作盲解。','谜题','目标 / 标准 / 上限','路线','精选残局','六步内腾出三个空格；目标在新方块生成后检查。以下“原路线”会走向无路可走，用于比较，不是建议。','原路线（失败）','转机路线（成功）','个人残局的起点各不相同，没有通用箭头答案。请使用该挑战自己的提示或对照复盘。'],
    'en':['# Puzzle and Rescue solutions (spoilers)','Try each challenge yourself before reading. Every route starts at its original board: restart the matching challenge first. Arrows are move directions; 0 is empty. Routes are generated directly from bundled game resources so translation cannot alter a direction.','Reading an external manual is outside the app, so it cannot automatically mark that you consulted these solutions. For your own unassisted challenge, avoid external answers; a practiced known route is different from solving a puzzle blind.','Puzzle','Target / par / limit','Route','Built-in Rescue','Create three empty cells within six moves, checked after spawning. The original route below ends in a blocked board and is included for comparison, not as advice.','Original route (loss)','Recovery route (success)','Personal Rescue starting positions vary. There is no universal arrow sequence; use the individual challenge hint or comparison replay.'],
    'ja':['# パズルとレスキューの解答（ネタバレ）','まず自分で試してから読んでください。すべて初期盤面からのルートなので、対応する問題を最初から始めます。矢印は移動方向、0 は空白です。方向は翻訳で変わらないよう、同梱リソースから直接生成しています。','外部説明書の閲覧はアプリの外なので、解答を読んだことを自動判定してアシスト扱いにはできません。自力挑戦を大切にする場合は外部解答を避け、既知ルートの練習と初見の解法発見を区別してください。','パズル','目標 / 標準 / 上限','ルート','内蔵レスキュー','六手以内に空きを三マス作ります。新タイル出現後に判定します。「元のルート」は移動不能になる比較例であり、推奨手ではありません。','元のルート（失敗）','救済ルート（成功）','個人レスキューは開始盤面が異なり、共通の矢印解答はありません。その問題のヒントや比較リプレイを使ってください。']}[lang]
    out=text[:3]
    for level in levels:
        board='\n'.join(' '.join(f'{x:4}' for x in level['board'][r:r+4]) for r in range(0,16,4))
        out += [f'## {text[3]} {level["id"]+1:02d} · {level["title"]}',f'{text[4]}: **{level["target"]} / {level["par"]} / {level["limit"]}**',f'```text\n{board}\n```',f'{text[5]}: **'+ '  '.join(arrows[d] for d in level['solution'])+'**']
    out += ['## '+text[6],text[7]]
    for ch in rescues:
        out += ['### '+ch['title'],text[8]+': '+' '.join(arrows[f['direction']] for f in ch['original']),text[9]+': **'+' '.join(arrows[d] for d in ch['solution'])+'**']
    out+=[text[10]]
    # Use spaces between directional arrows, never an extra right-arrow separator.
    joined='\n\n'.join(out)
    (root/'docs'/lang/'08-solutions.md').write_text(joined+'\n')

readmes={
'zh-CN':('LUMINA · iPhone / iPad 原生版','六种玩法，一个安静、清晰的数字游戏。经典始终放在第一位。','当前是 **1.0.1 Native 源码工程**，不是可直接安装的 IPA。仍需完整 Xcode、iOS SDK 和签名完成设备安装；本机尚未完成 iOS 构建与真机验收。App 按钮目前为中文，本套文档提供中、英、日文。','离线说明书','推荐先打开 [中文阅读版](docs/zh-CN/index.html)，或从 [三语入口](docs/index.html)选择语言。解压后保留整个 docs 文件夹，动图和视频都可以离线使用。','章节导航','有什么可以玩','经典 2048、能力远征、败局重生、每日同局、十二道谜题、六十步冲刺。支持撤销与重做、本地 AI 提示与自动游玩、手动 / 辅助记录、JSON 备份、浅深色和减少动态效果。无账号、广告或服务器依赖。','一分钟认识操作','盘面内上下左右滑动；顶部模式名切换玩法；灯泡请求提示；“自动玩”开始 AI；三点菜单包含重做和重开；右上角设置可导出备份。提示请求即计为辅助局。','演示','九段实际原生预览演示中的经典片段。录制于 macOS，非 iPhone / iPad 录屏；不用于判断设备帧率。','项目与验证','打开 Lumina.xcodeproj，在 Signing & Capabilities 选择自己的 Team。完整安装、测试、Archive 命令见第 6 章。已有 38 项核心 / 交互测试、5,760 次混合操作检查；具体边界见第 9 章。','文档与代码','docs 下每种语言有九章，另有九段 GIF、九个 MP4 原视频和静态封面。原生存档不兼容旧 Python / Windows / PWA 格式。原有其他版本独立保留。'),
'en':('LUMINA · Native iPhone / iPad edition','Six ways to play a quiet, considered number game. Classic always comes first.','This is the **1.0.1 Native source project**, not an installable IPA. Device installation still requires full Xcode, an iOS SDK and signing. An iOS build and device acceptance have not been completed here. App labels are currently Chinese; the documentation is available in Chinese, English and Japanese.','Offline handbook','Open the [English reader](docs/en/index.html), or choose a language from the [documentation home](docs/index.html). Keep the entire docs folder after extraction so animations and videos remain available offline.','Chapter guide','What you can play','Classic 2048, ability-based Expedition, Rescue, Daily, twelve puzzles and 60-Move Sprint. Includes undo/redo, local hints and autoplay, separate manual/assisted records, JSON backups, light/dark appearance and reduced motion. No login, ads or server dependency.','Controls in one minute','Swipe within the board; use the top mode title to switch games. The lightbulb requests a hint; 自动玩 starts AI. The ellipsis contains redo and restart; top-right settings include backup export. A hint request immediately marks the game assisted.','Demonstration','A Classic excerpt from nine actual native-preview demonstrations. Captured on macOS, not an iPhone / iPad screen recording or device frame-rate test.','Project and validation','Open Lumina.xcodeproj and select your own Team in Signing & Capabilities. Chapter 6 covers installation, tests and Archive. Evidence includes 38 core/interaction checks and 5,760 mixed operations; see chapter 9 for limitations.','Documentation and source','Each language has nine chapters. Shared media includes nine GIFs, nine MP4 source videos and static posters. Native saves are incompatible with older Python / Windows / PWA formats; those editions remain separate.'),
'ja':('LUMINA · iPhone / iPad ネイティブ版','落ち着いて数字に向き合う、六つの遊び方。クラシックをいつも先頭に。','これは **1.0.1 Native のソースプロジェクト**で、インストール可能な IPA ではありません。端末導入には完全な Xcode、iOS SDK、署名が必要です。ここでは iOS ビルドと実機受け入れ確認は未完了です。現在の画面は中国語、説明書は中国語・英語・日本語です。','オフライン説明書','[日本語の読みやすい版](docs/ja/index.html)、または[三言語の入口](docs/index.html)を開いてください。展開後も docs フォルダー全体を残せば、動図と動画をオフラインで利用できます。','章の一覧','遊べるもの','クラシック 2048、能力遠征、レスキュー、デイリー、十二問のパズル、60 手スプリント。戻す・やり直す、端末内 AI のヒントと自動プレイ、手動 / アシスト別記録、JSON バックアップ、明暗表示、動きを減らす設定を用意。ログイン、広告、サーバー依存はありません。','一分でわかる操作','盤面内を上下左右にスワイプ。上のモード名で切り替え、電球でヒント、「自动玩」で AI を開始。三点メニューにやり直しと最初から、右上設定にバックアップがあります。ヒントは要求した時点でアシスト扱いです。','操作例','九本のネイティブプレビュー教材からクラシックの例。macOS 収録で、iPhone / iPad の録画や実機フレームレート検査ではありません。','プロジェクトと検証','Lumina.xcodeproj を開き、Signing & Capabilities で自分の Team を選択します。導入、検査、Archive は第 6 章へ。コア・操作 38 項目と混合操作 5,760 回を確認済み。範囲は第 9 章に記載しています。','文書とソース','各言語に九章、共有素材に九本の GIF、九本の元 MP4、静止画を同梱。原生保存は旧 Python / Windows / PWA の形式と非互換で、それらの版は独立して残っています。')}
for lang, data in readmes.items():
    h,tag,status,*parts=data
    nav=parts.pop(2)
    out=['# '+h,'[简体中文](README.zh-CN.md) · [English](README.en.md) · [日本語](README.ja.md)',tag,status]
    for i in range(0,len(parts),2):
        out+=['## '+parts[i],parts[i+1]]
        if i==0:
            out+=['## '+nav]
            out+=['\n'.join(f'- [{title}](docs/{lang}/{chapter}.md)' for chapter,title in zip(chapters,titles[lang]))]
        if parts[i] in ['演示','Demonstration','操作例']:
            out+=['![LUMINA Classic](docs/media/01-classic.gif)']
    (root/f'README.{lang}.md').write_text('\n\n'.join(out)+'\n')
(root/'README.md').write_text((root/'README.zh-CN.md').read_text())
(root/'docs/catalog.json').write_text(json.dumps({'chapters':chapters,'titles':titles},ensure_ascii=False,indent=2)+'\n')
# Prefer natural Japanese terminology throughout the generated and authored guide.
for p in [*(root/'docs/ja').glob('*.md'),root/'README.ja.md']:
    text=p.read_text()
    for a,b in [('原生','ネイティブ'),('主機','ホスト環境'),('動図','GIF アニメーション'),('交付する','同梱する'),('端末導入','端末へのインストール')]:
        text=text.replace(a,b)
    p.write_text(text)
