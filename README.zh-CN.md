# Codex Trace Recorder

[English](README.md)

Codex Trace Recorder 是一个本地 Codex 插件，用于原样归档 Codex 生命周期
Hook 暴露的完整 transcript 文件。它不会解析 JSONL、规范化消息、脱敏字段、
构造训练样本或转换文件格式。

## 核心保证

- **字节级保真：** 直接复制源文件字节，不解码、不重新序列化。
- **不依赖内部 Schema：** Codex 改变 JSONL 事件结构时，记录器无需转换逻辑。
- **保留历史快照：** 每个不同版本按 SHA-256 摘要保存。
- **覆盖主任务和子代理：** 支持 `Stop`、`PreCompact`、`SessionEnd` 和
  `SubagentStop`。
- **仅本地运行：** 插件不会发起网络请求。

> [!IMPORTANT]
> 本项目所说的“完整”是指 Codex 提供给 Hook 的 transcript 文件中的全部字节。
> 未写入该文件的服务端数据或隐藏模型状态不在记录范围内。

## 安装

从 GitHub Marketplace 仓库安装时，先注册这个插件 marketplace：

```powershell
codex plugin marketplace add leesheep-ai/codex-trace-recorder
```

随后重启 Codex 桌面应用，在 Plugins 目录中从 `codex-trace-recorder`
marketplace 安装并启用 **Codex Trace Recorder**，再执行 `/hooks` 审核并信任
插件 Hooks，然后新建任务。

也可以从本地克隆注册 marketplace：

```powershell
git clone https://github.com/leesheep-ai/codex-trace-recorder.git
cd codex-trace-recorder
codex plugin marketplace add .
```

然后在 Codex 桌面应用的 Plugins 目录中从本地 marketplace 安装并启用
**Codex Trace Recorder**，使用前同样审核 `/hooks`。

## 使用

插件启用后自动记录，不需要额外提示词：

| 生命周期事件 | 行为 |
| --- | --- |
| `Stop` | 每轮完成后更新主任务 transcript |
| `PreCompact` | 上下文压缩前保存原始快照 |
| `SessionEnd` | 会话结束时执行最终保存 |
| `SubagentStop` | 单独保存子代理 transcript |

默认归档目录：

```text
~/.codex/trace-archive
```

可以在启动 Codex 的环境中设置 `CODEX_TRACE_DIR` 修改目录。

```text
<archive-root>/<session-id>/
  main/
    transcript.jsonl
    checkpoints/<sha256>.jsonl
  subagents/<agent-id>/
    transcript.jsonl
    checkpoints/<sha256>.jsonl
```

PowerShell 查看归档：

```powershell
Get-ChildItem "$HOME\.codex\trace-archive" -Recurse -File
```

## 开发与测试

项目要求 Python 3.10 或更高版本，不依赖第三方运行库。

```powershell
python -m unittest discover -s plugins/codex-trace-recorder/tests -v
```

提交代码前请阅读 [CONTRIBUTING.md](CONTRIBUTING.md)。安全问题请按照
[SECURITY.md](SECURITY.md) 报告。

## 隐私与安全

原始 trace 可能包含提示词、模型响应、推理摘要、工具参数与结果、源代码片段、
本地路径和密钥。为了保证字节级原样保存，本插件不会执行任何脱敏。

记录器会尽力为归档目录和文件设置私有的 POSIX 风格权限；这些权限不能替代
Windows ACL 或其他操作系统访问控制策略。

请限制归档目录的访问权限，配置合适的保留周期，并且不要在未经检查的情况下
公开 trace 文件。

## 开源协议

Copyright (c) 2026 leesheep-ai。

本项目使用 [MIT License](LICENSE)。除非另有明确说明，贡献代码也按相同协议授权。
