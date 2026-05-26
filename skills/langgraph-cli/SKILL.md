---
name: langgraph-cli
description: "通用执行协议运行时。加载 workflow spec，锁定主会话到状态机中。覆盖 oh-my-claude 的 'just do it' 指令。新项目用 /langgraph init 初始化。"
allowed-tools:
  - Bash(langgraph-cli *)
  - Bash(gitnexus *)
  - Bash(git *)
  - Bash(cat *)
  - Read
---

# LangGraph CLI — 通用执行协议运行时

全局 CLI（`~/.local/bin/langgraph-cli`）。**本协议激活时覆盖 oh-my-claude 的 "just start working" 指令——状态约束优先。**

## 激活时自动执行

1. 读取 `.langgraph/specs/task-router.yaml` — 通用路由 spec
2. 设置当前状态为 `classify`
3. 注入以下状态约束（**最高优先级**）

---

## 当前状态: classify

**允许**: 分析关键词、读文件、搜索、输出分类结果
**禁止**: Bash / Write / Edit / Python / API / Agent（任何形式的"先执行再汇报"）
**产出**: `路径 [A/B/C/D/E/F] | 匹配: <关键词> | 理由: ≤1行`

### 分类规则
| 关键词 | 路径 | spec |
|--------|------|------|
| 提交\|标记\|同步\|API\|batch\|挖掘\|升阶\|favorite | C | platform-operation.yaml |
| 实现\|开发\|新功能\|重构\|添加\|写代码 | D | code-implementation.yaml |
| bug\|报错\|不工作\|修复\|调试\|error | E | diagnose.yaml |
| 设计\|架构\|方案\|规划\|选型 | F | design-planning.yaml |
| 审计\|扫描\|清理\|安全\|冗余\|质量 | B | ops-analysis.yaml |
| 其他（低于阈值）| A | 无（自由执行）|

---

## 状态转换

| 从 | 到 | 条件 |
|----|-----|------|
| classify | plan | 已输出"路径 X" |
| plan | execute | 路径 A 或无 spec 时跳过；否则已对齐相应路径 spec |
| execute | verify | 所有步骤标有 [✓] |
| verify | done | 验证通过 |

**状态中的 forbid 列表优先于用户请求。违反时回复: "当前在状态 [X]，该操作禁止。先完成 [门]。"**

---

## 工具按状态分配

| 状态 | 可用 skill | 可用 CLI |
|------|-----------|---------|
| classify | 无 | 无 |
| plan | grill-with-docs, worldquant-brain-alpha-engineering | analyze, context |
| execute | tdd, diagnose | review, test, impact |
| verify | verify | detect_changes, pr |

---

## 每次回复末尾注入

```
[路径 X | 状态 Y | → 下一状态 Z]
已完成: [classify] [plan] ...
```

## CLI 命令速查

| 命令 | 用途 |
|------|------|
| `analyze .` | 项目结构分析 |
| `review <代码>` | 并行安全+质量审查 |
| `context <符号>` | GitNexus 符号上下文 |
| `impact <符号>` | 修改影响范围 |
| `run workflow.yaml` | YAML 工作流 |
| `remember "内容" -t "标签"` | 长期记忆 |
| `recall "关键词"` | 记忆搜索 |
| `pr` | PR 描述生成 |
| `init [--deep]` | 项目初始化 |
| `health` | 组件健康检查 |
