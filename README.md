# AI Workflow Kit

可复用的 AI 辅助开发工作流模板。一次安装，所有项目通用。

## 快速开始

```bash
git clone https://github.com/QZYWQ/ai-workflow-kit
cd ai-workflow-kit
```

在 Claude Code 中打开本目录，AI 会自动读取 CLAUDE.md 并执行 `bash install.sh`。

## 使用

```bash
cd 你的项目
langgraph-cli init [--deep]
gitnexus analyze .
langgraph-cli remember "项目定位" -t "概况"
```

日常开发对 AI 说需求即可，或手动：`langgraph-cli review file.py` / `langgraph-cli pr` / `langgraph-cli recall "关键词"`

## 包含

- **langgraph-cli** — 14 命令的 CLI（审查/测试/记忆/工作流）
- **GitNexus** — 代码知识图谱
- **Matt Pocock skills** — 14 个方法论 skill（grill-with-docs/tdd/diagnose 等）
- **两阶段执行协议** — 理解→执行

详见 CLAUDE.md（AI 入口）和 docs/TOOL-LAYERING.md
