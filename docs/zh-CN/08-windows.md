# Windows 安装与排错

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
| 中文方框 | 核对 `fonts/NotoSansSC-*.otf` 与 `fonts/OFL.txt` 均在；不要删除字体 |
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
