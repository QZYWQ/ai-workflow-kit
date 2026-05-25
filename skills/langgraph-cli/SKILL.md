---
name: langgraph-cli
description: "多智能体开发助手 CLI。新项目用 /langgraph init 初始化。提供代码分析（review/context/impact）、长期记忆（remember/recall）、YAML 工作流（run）。审查层+上下文层的核心工具。"
allowed-tools:
  - Bash(langgraph-cli *)
  - Bash(git *)
  - Bash(cat *)
  - Read
---

# LangGraph CLI - 执行层 + 上下文层

全局 CLI（`~/.local/bin/langgraph-cli`），在审查层和上下文层提供能力。

## 在整体工具栈中的位置

```
【理解】grill-with-docs / zoom-out         ← Matt Pocock
【计划】to-prd / langgraph-cli analyze     ← Matt Pocock + CLI
【编码】tdd / prototype / caveman          ← Matt Pocock
【审查】langgraph-cli review / context/impact  ← CLI（本工具）
        oh-my-claude code-reviewer / validator ← oh-my-claude
【上下文】langgraph-cli remember/recall    ← CLI 长期记忆
         handoff                           ← Matt Pocock 短期传递
         GitNexus                          ← 代码图谱
【执行】langgraph-cli run（YAML 并行）      ← CLI
        Agent() 并行（临时任务）            ← oh-my-claude
```

### langgraph-cli 负责
- **多维代码分析**：review 并行安全+质量，context/impact 代码图谱查询
- **长期记忆**：remember 存决策（"为什么"），recall 搜。handoff 负责短期（"继续上次的"）
- **YAML 工作流**：run 执行可复用的多 agent 并行编排，Agent() 管临时任务
- **项目初始化**：init 生成 .langgraph/ 目录和规则文件

### langgraph-cli 不负责（由其他工具处理）
- 需求追问 → grill-with-docs
- PRD 生成 → to-prd
- TDD 方法论 → Matt Pocock tdd
- PR diff 审查 → oh-my-claude code-reviewer
- 会话传递 → handoff

## 新项目初始化

```bash
cd 新项目
langgraph-cli init [--deep]    # 生成 .langgraph/ 完整规则体系
gitnexus analyze .              # 建代码图谱
```

## 命令速查

| 层级 | 命令 | 用途 |
|------|------|------|
| 审查 | `review <代码>` | 并行安全+质量审查 |
| 审查 | `context <符号>` | GitNexus 符号上下文 |
| 审查 | `impact <符号>` | 修改影响范围 |
| 计划 | `analyze .` | 项目结构分析 |
| 上下文 | `remember "内容" -t "标签"` | 长期记忆保存 |
| 上下文 | `recall "关键词"` | 长期记忆搜索 |
| 上下文 | `config key value` | 项目配置 |
| 执行 | `run workflow.yaml -i k=v` | YAML 工作流 |
| 执行 | `pr` | PR 描述生成 |
| 辅助 | `ask / test / doc / refactor` | 常规辅助 |
| 初始化 | `init [--deep]` | 项目初始化 |
