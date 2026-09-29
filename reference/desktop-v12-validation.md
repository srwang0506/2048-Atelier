# 第十二版：缺陷检查与 Windows 便携版

2026-09-29，验证主机为 Apple Silicon Mac，Python 3.12.9、pygame-ce 2.5.8。Windows 包使用 CPython 3.13.15 的官方 x64 嵌入式运行环境。

## 本轮修复

1. 章节及练习残局的 JSON 读取显式指定 UTF-8，避免 Windows 使用 ANSI 代码页时乱码、练习缺失或启动失败。
2. 主存档文件丢失时也检查上一份备份，恢复棋盘、随机状态与撤销历史。已有的主存档损坏恢复机制保留。
3. 截图遇到无权限、磁盘满或图像写入错误时只提示失败；连续截图使用不同文件名，避免同秒覆盖。
4. 桌面入口加操作系统文件锁，阻止两个新版游戏进程同时写同一套存档；进程退出或崩溃后由系统释放锁。
5. Windows 存档、截图、AI 缓存与日志放在用户目录。旧源码版存档按需复制迁移，不覆盖用户目录现有进度，也不删除旧文件。
6. Windows 中文字体随包附带真实的三种字重，系统字体路径不再固定 C 盘；系统数字字体缺失时也有可显示中文的回退。
7. Windows 源码启动器检查 Python 架构、版本、依赖及错误码；依赖已就绪时不再每次启动都运行 pip。便携包直接使用随附运行环境。
8. Windows PE 审核发现 Numba 必需的 `msvcp140.dll` 缺失：将 NumPy 官方 wheel 随附的 Microsoft 运行库保留原样，以标准 DLL 名放入运行环境，并核对 Numba 要求的导出函数。

经典仍是默认大厅页、左侧主卡和第一个顶部标签；六个模式的原规则与功能保留。

## 验证结果

- **90 项测试通过，16.686 秒**：原有 84 项回归，加 6 项资源编码、缺失存档恢复、迁移隔离、跨进程锁、截图错误和字体字重测试。`validation/v12/tests.log`。
- 完整应用流程复测：远征六关、123 步、6,098 分；关卡间升级能力、存盘恢复一致。真实经典败局生成三步重生挑战，完成、对照、切回原局及档案持久化均通过。`validation/v12/full-flow.json`。
- 新入口的 SDL dummy 启动和截图检查通过。诊断程序在 Mac 通过依赖、12 章节、3 练习局、字体、临时存档和 spawn 后台原生 AI 检查。`validation/v12/diagnostics.log`。
- Noto 字体回退检查 16 个实际界面、547 组文字 / 字号组合，无缺字和字形裁切；已人工查看大厅和能力选择布局。`validation/v12/windows-font-check.json`。
- 稳定绘制 CPU 耗时中位数 4.29 ms、P95 5.70 ms；完整流程中位数 6.33 ms、P95 9.49 ms、最大 60.69 ms。均为 SDL dummy 下的 CPU 耗时，不能当作原生显示帧率或“完全不卡顿”的证明。
- 修改模块编译检查通过。便携 ZIP 的 CRC 完整性检查、官方 Python 与 PyPI wheel 的 SHA-256 校验通过；135 个 PE 文件均为 x86-64，游戏必需的非系统 DLL 导入已满足。详情在 `validation/v12/windows-build.json` 和包内 `build-manifest.json`。

## Windows 包

`2048-v12-Windows-x64.zip` 中的 `2048.exe` 使用 distlib 可重定位启动器，调用随包的 `runtime/pythonw.exe`。必须完整解压；无需安装 Python，游玩不联网。依赖为 pygame-ce 2.5.8、NumPy 2.5.3、Numba 0.67.0、llvmlite 0.49.0、Pillow 12.3.0，另附 Noto Sans SC 字体与对应许可。

默认使用 Numba 自带的 workqueue 线程后端。游戏的 AI 搜索没有使用并行 JIT；wheel 中可选的 TBB / OpenMP 插件需要额外运行库，本包不启用它们，静态检查将这两项单独记录。没有把可选插件的缺项伪装成全部依赖均可运行。

`check-windows.bat` 提供目标机器自检，不修改个人进度。日志在 `%LOCALAPPDATA%\2048-Atelier\logs`。

**尚未在 Windows 实机执行。** 这轮不能验证 Windows 显卡驱动、窗口缩放、声音和屏幕帧率，也不等同于逐条执行 Windows 批处理脚本。PE 检查只涵盖静态导入及必需 Microsoft 运行库的函数，不能替代系统加载器和实际启动。没有宣称已消除所有可能的 bug。

## 安装与备份

macOS 只更新源码、说明、测试、字体回退资源和验证记录，不替换已有虚拟环境或个人存档。旧文件备份到 `backups/v11-source/`。Windows ZIP 另放入 `releases/`，方便复制到 Windows 电脑。安装后文件哈希及存档未变检查见 `validation/v12/deploy.json`。

关闭旧窗口后重新打开启动脚本才能加载修复。当前已经运行的旧版进程不会自动获得新版的启动锁。
