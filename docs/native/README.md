# LUMINA · iPhone / iPad 原生版

[简体中文](README.zh-CN.md) · [English](README.en.md) · [日本語](README.ja.md)

六种玩法，一个安静、清晰的数字游戏。经典始终放在第一位。

当前是 **1.0.1 Native 源码工程**，不是可直接安装的 IPA。仍需完整 Xcode、iOS SDK 和签名完成设备安装；本机尚未完成 iOS 构建与真机验收。App 按钮目前为中文，本套文档提供中、英、日文。

## 离线说明书

推荐先打开 [中文阅读版](docs/zh-CN/index.html)，或从 [三语入口](docs/index.html)选择语言。解压后保留整个 docs 文件夹，动图和视频都可以离线使用。

## 章节导航

- [开始游玩与完整操作](docs/zh-CN/01-start.md)
- [六种玩法的完整规则](docs/zh-CN/02-rules.md)
- [能力远征：关卡与能力](docs/zh-CN/03-expedition.md)
- [智能助手、记录与存档](docs/zh-CN/04-ai-data.md)
- [常见问题与问题反馈](docs/zh-CN/05-faq.md)
- [安装、构建与开发](docs/zh-CN/06-build.md)
- [九段动图教程](docs/zh-CN/07-gallery.md)
- [谜题与残局解答（含剧透）](docs/zh-CN/08-solutions.md)
- [版本与验证范围](docs/zh-CN/09-release.md)

## 有什么可以玩

经典 2048、能力远征、败局重生、每日同局、十二道谜题、六十步冲刺。支持撤销与重做、本地 AI 提示与自动游玩、手动 / 辅助记录、JSON 备份、浅深色和减少动态效果。无账号、广告或服务器依赖。

## 一分钟认识操作

盘面内上下左右滑动；顶部模式名切换玩法；灯泡请求提示；“自动玩”开始 AI；三点菜单包含重做和重开；右上角设置可导出备份。提示请求即计为辅助局。

## 演示

九段实际原生预览演示中的经典片段。录制于 macOS，非 iPhone / iPad 录屏；不用于判断设备帧率。

![LUMINA Classic](docs/media/01-classic.gif)

## 项目与验证

打开 Lumina.xcodeproj，在 Signing & Capabilities 选择自己的 Team。完整安装、测试、Archive 命令见第 6 章。已有 38 项核心 / 交互测试、5,760 次混合操作检查；具体边界见第 9 章。

## 文档与代码

docs 下每种语言有九章，另有九段 GIF、九个 MP4 原视频和静态封面。原生存档不兼容旧 Python / Windows / PWA 格式。原有其他版本独立保留。
