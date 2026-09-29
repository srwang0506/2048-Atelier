# 十七段游戏动图与视频

八段桌面实演 + 九段原生实演。全部来自实际游戏代码运行，先生成 MP4，再从交付 MP4 解码转换 GIF。以 12 fps 采样作为操作教学，不是显示器帧率测量。HTML 内动图默认暂停，可点播放或展开 MP4；Markdown 查看器通常自动循环。

## Mac / Windows 桌面 v12 的操作

录制环境为 Mac 上的 Python / pygame 实际渲染器，使用 SDL dummy 与隔离临时存档。Windows 共用此代码，但不是 Windows 实机录屏。静音；没有使用玩家个人存档。

### 大厅：经典优先与精选玩法

从「经典与挑战」切到「精选玩法」，再返回经典。进入游戏后按 B 可以回大厅。

![大厅：经典优先与精选玩法](../media/10-desktop-lobby.gif)

[GIF](../media/10-desktop-lobby.gif) · [MP4 · 6.00 s](../media/10-desktop-lobby.mp4) · [PNG](../media/10-desktop-lobby-poster.png)

### 经典：移动、撤销与重做

seed 42 的真实新局。向左、下、左、上、右移动，然后撤销、重做；观察棋盘、得分与步数同步恢复。

![经典：移动、撤销与重做](../media/11-desktop-classic.gif)

[GIF](../media/11-desktop-classic.gif) · [MP4 · 7.00 s](../media/11-desktop-classic.mp4) · [PNG](../media/11-desktop-classic-poster.png)

### AI 分析、单步与复盘

真正启动后台搜索，展示四方向分析和左方向预览，执行 AI 一步，再查看历史。复盘不会改变当前棋盘。

![AI 分析、单步与复盘](../media/12-desktop-ai-replay.gif)

[GIF](../media/12-desktop-ai-replay.gif) · [MP4 · 8.50 s](../media/12-desktop-ai-replay.mp4) · [PNG](../media/12-desktop-ai-replay-poster.png)

### 解局：两步合成 64

第一章从初始状态连续向上两次，实际达标并获得三星。本段包含解答。

![解局：两步合成 64](../media/13-desktop-puzzle.gif)

[GIF](../media/13-desktop-puzzle.gif) · [MP4 · 5.33 s](../media/13-desktop-puzzle.mp4) · [PNG](../media/13-desktop-puzzle-poster.png)

### 远征：选能力与充能

seed 13 开局三选一，选择蓄能核心后移动，查看能量与规则面板。这里展示第一关开局，不是六关通关录像。

![远征：选能力与充能](../media/14-desktop-expedition.gif)

[GIF](../media/14-desktop-expedition.gif) · [MP4 · 8.00 s](../media/14-desktop-expedition.mp4) · [PNG](../media/14-desktop-expedition-poster.png)

### 重生：三步救局与路线对照

第一道练习从起点向右、上、上，达到三空格后查看对照，逐步比较。本段包含解答。

![重生：三步救局与路线对照](../media/15-desktop-rescue.gif)

[GIF](../media/15-desktop-rescue.gif) · [MP4 · 6.83 s](../media/15-desktop-rescue.mp4) · [PNG](../media/15-desktop-rescue-poster.png)

### 每日：固定日期与撤销重做

使用正式 daily_game 创建 2026-09-29 挑战；演示方向操作、撤销和重做。无效方向不增加步数。

![每日：固定日期与撤销重做](../media/16-desktop-daily.gif)

[GIF](../media/16-desktop-daily.gif) · [MP4 · 6.67 s](../media/16-desktop-daily.mp4) · [PNG](../media/16-desktop-daily-poster.png)

### 冲刺：观察剩余步数

seed 42 的真实冲刺新局，走五步后撤销、重做。这里示范计步，不是第 60 步结算录像。

![冲刺：观察剩余步数](../media/17-desktop-sprint.gif)

[GIF](../media/17-desktop-sprint.gif) · [MP4 · 7.50 s](../media/17-desktop-sprint.mp4) · [PNG](../media/17-desktop-sprint-poster.png)

## iPhone / iPad 原生版的操作（Mac 主机预览）

以下九段 GIF 均由原生代码实际运行的采样视频转换，另附 MP4 原视频。录制平台为 macOS 原生预览，**不是 iPhone / iPad 录屏，也不代表设备帧率**。底部英文条是教学标注。页面中可以暂停动图；Markdown 阅读器通常会自动循环。MP4 使用 H.264 编码，可在阅读版展开视频播放器，或下载后单独播放。所有素材本地保存，无需联网。

### 经典：移动、合并与落子

从 seed 42 实际游玩的中盘继续，依次观察整盘滑动、相同数字合并、得分上涨及新方块出现。方向标在画面底部。

![经典：移动、合并与落子](../native/docs/media/01-classic.gif)

先尝试保持大数字在角落；注意没有合并的位移也会产生新方块。

[GIF](../native/docs/media/01-classic.gif) · [MP4 · 6.08 s](../native/docs/media/01-classic.mp4) · [PNG](../native/docs/media/01-classic-poster.png)

### 撤销与重做：同一落子被恢复

执行一步，撤销，再重做。观察棋盘、得分和移动次数一起变化。

![撤销与重做：同一落子被恢复](../native/docs/media/02-undo-redo.gif)

重做藏在三点菜单；随机状态也一起恢复，所以不是重新抽签。

[GIF](../native/docs/media/02-undo-redo.gif) · [MP4 · 5.58 s](../native/docs/media/02-undo-redo.mp4) · [PNG](../native/docs/media/02-undo-redo-poster.png)

### 智能助手：提示、执行、自动玩、暂停

先请求提示，再执行建议，随后打开自动游玩并暂停。

![智能助手：提示、执行、自动玩、暂停](../native/docs/media/03-ai.gif)

查看底部从手动局变成辅助局；暂停之后辅助标记仍在。

[GIF](../native/docs/media/03-ai.gif) · [MP4 · 11.5 s](../native/docs/media/03-ai.mp4) · [PNG](../native/docs/media/03-ai-poster.png)

### 远征：三选一与首关

开始新的 seed 42 远征，选择蓄能核心，再完成数次有效移动。

![远征：三选一与首关](../native/docs/media/04-expedition-draft.gif)

同一步多组合并会获得更多能量，先理解目标分与总分的区别。

[GIF](../native/docs/media/04-expedition-draft.gif) · [MP4 · 7.25 s](../native/docs/media/04-expedition-draft.mp4) · [PNG](../native/docs/media/04-expedition-draft-poster.png)

### 远征：凝时与交换

从实际获得 12 能量的局面继续，先凝时，再选两枚不同数字交换，最后移动两次。

![远征：凝时与交换](../native/docs/media/05-expedition-powers.gif)

观察使用主动能力时剩余步数不变；凝时后的移动不会生成新方块。

[GIF](../native/docs/media/05-expedition-powers.gif) · [MP4 · 6.42 s](../native/docs/media/05-expedition-powers.mp4) · [PNG](../native/docs/media/05-expedition-powers-poster.png)

### 谜题：两步合成 64

完整演示第 01 题，从重置后的棋盘向上、再向上，合成 64。

![谜题：两步合成 64](../native/docs/media/06-puzzle.gif)

本段含解答；未请求提示且没有撤销，因此得到三星。

[GIF](../native/docs/media/06-puzzle.gif) · [MP4 · 4.67 s](../native/docs/media/06-puzzle.mp4) · [PNG](../native/docs/media/06-puzzle-poster.png)

### 残局：从错误走法到可解路线

精选“一线生机”：先复现原来的向左走法导致无路可走，再从同一起点执行右、上、上。

![残局：从错误走法到可解路线](../native/docs/media/07-rescue.gif)

比较两种结局；成功目标是落子后至少三个空位。它展示实际操作过程，不是完整经典局录像。

[GIF](../native/docs/media/07-rescue.gif) · [MP4 · 7.58 s](../native/docs/media/07-rescue.mp4) · [PNG](../native/docs/media/07-rescue-poster.png)

### 每日：相同日期与重开

固定演示 2026-09-29 的每日局，移动三次后重开。

![每日：相同日期与重开](../native/docs/media/08-daily.gif)

观察重开后的两枚初始方块与开始时一致；不是联网同步。

[GIF](../native/docs/media/08-daily.gif) · [MP4 · 5.83 s](../native/docs/media/08-daily.mp4) · [PNG](../native/docs/media/08-daily-poster.png)

### 冲刺：最后三步与结束

seed 42 的真实冲刺先推进到第 57 步，再记录最后三步及结算。

![冲刺：最后三步与结束](../native/docs/media/09-sprint.gif)

看剩余次数从 3 到 0；不是秒表，也没有第 61 步。

[GIF](../native/docs/media/09-sprint.gif) · [MP4 · 5.58 s](../native/docs/media/09-sprint.mp4) · [PNG](../native/docs/media/09-sprint-poster.png)

[Media / 媒体 / メディア](../native/docs/media/README.md)
