# 第三方组件

Windows 包将运行环境与应用一起分发，启动时不从网络下载或执行代码。原始许可证随对应组件保留。

| 组件 | 版本 | 来源与许可位置 |
|---|---|---|
| CPython Windows embeddable x64 | 3.13.15 | [Python 官方发布页](https://www.python.org/downloads/release/python-31315/)，`runtime/LICENSE.txt` 与 `licenses/Python-LICENSE.txt` |
| pygame-ce | 2.5.8 | [PyPI](https://pypi.org/project/pygame-ce/2.5.8/)，对应 `.dist-info` 及包内许可证；含 SDL 等随附库 |
| NumPy | 2.5.3 | [PyPI](https://pypi.org/project/numpy/2.5.3/)，对应 `.dist-info` 及随附库许可证 |
| Numba | 0.67.0 | [PyPI](https://pypi.org/project/numba/0.67.0/)，对应 `.dist-info` 许可证 |
| llvmlite | 0.49.0 | [PyPI](https://pypi.org/project/llvmlite/0.49.0/)，对应 `.dist-info` 及 LLVM 许可证 |
| Pillow | 12.3.0 | [PyPI](https://pypi.org/project/Pillow/12.3.0/)，对应 `.dist-info` 许可证 |
| distlib Windows GUI launcher | 0.4.0 | [PyPI](https://pypi.org/project/distlib/0.4.0/)，`licenses/distlib-LICENSE.txt` |
| Noto Sans SC，Regular / Medium / Bold | 源文件随包保留 | [官方字体仓库](https://github.com/notofonts/noto-cjk/tree/main/Sans/SubsetOTF/SC)，SIL Open Font License，`fonts/OFL.txt` |

`2048.exe` 使用 distlib 的可重定位启动器，调用同目录的 `runtime/pythonw.exe`。这是带完整 Python 运行环境的应用包。组装方法参考 [Python 嵌入式分发说明](https://docs.python.org/3.13/using/windows.html#the-embeddable-package)和 [distlib 可重定位启动器说明](https://distlib.readthedocs.io/en/latest/tutorial.html#specifying-the-executable)。Python ZIP 对照官方发布页的 SHA-256 校验，依赖 wheel 对照 PyPI 元数据的 SHA-256 校验，记录在 `build-manifest.json`。

macOS 仍读取本机安装的苹方及 Helvetica Neue；这些系统字体没有被复制或分发。Windows 中文与无系统字体时的回退使用随包分发的 Noto Sans SC。
