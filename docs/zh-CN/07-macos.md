# macOS 安装与排错

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
