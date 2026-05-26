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
2. 设置当前状态为 `assess`（**v2.3: 每任务 assess + task-switch 检测 + mode refresh**）
3. 注入以下状态约束（**最高优先级**）

---

## 当前状态: assess

**允许**: 读文件、检查目录、查询 OMEGA、搜索 handoff
**禁止**: Bash / Write / Edit / Python / API / Agent
**产出**: `项目模式: [greenfield | brownfield_docs | brownfield_nodocs | midstream]`

### 项目模式判定
| 条件 | 模式 |
|------|------|
| !CONTEXT.md && 文件<10 && !docs/adr/ | greenfield（从零）|
| CONTEXT.md 或 docs/adr/ 存在 | brownfield_docs（有文档）|
| 文件≥10 && !CONTEXT.md && !docs/adr/ | brownfield_nodocs（有代码无文档）|
| handoff 文件/OMEGA 活跃会话 | midstream（续接）|

### 模式行为差异
| | greenfield | brownfield_docs | brownfield_nodocs | midstream |
|---|---|---|---|---|
| grill-with-docs | **强制**(建术语) | 检查对齐 | 可选(无文档对齐) | 恢复上下文 |
| 路径 D plan 前 | MUST 建 CONTEXT.md | MUST 读 CONTEXT.md | MUST analyze+gitnexus | 恢复任务列表 |
| 代码是真理? | N/A | ❌ 文档=真理 | ✅ 代码=真理 | 依恢复状态 |

### v2.3: midstream override
用户说 "不管上次"|"新任务"|"先不管"|"另起"|"从头" → 降级为项目文件状态检测的模式（忽略 handoff/OMEGA）

### v2.3: mode refresh
每个新任务前 re-check: 上次 assess 后项目状态变了？(新建了 CONTEXT.md? 新写了 ADR?) → 更新模式，≤1秒

### v2.3: task-switch detection
当前在 execute/verify，用户请求不匹配当前步骤 → "检测到任务切换。新任务重新 assess?" → 用户确认 → 返回 assess

---

## 状态: classify

**允许**: 分析关键词、匹配路径
**禁止**: Bash / Write / Edit / Python / API / Agent
**产出**: `路径 [A/B/C/D/E/F] | 匹配: <关键词> | 理由: ≤1行`
**midstream 模式**: 优先从恢复的上下文分类，不是用户当前请求字面

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

## 工具库

完整工具库见 `.langgraph/specs/task-router.yaml` → `tool_library` 章节。
每个工具定义了: trigger(必须/跳过), protocol(步骤), exit(完成条件), deconflict(重叠工具区分)。

### 状态⇄工具映射

| 状态 | 主要工具 |
|------|---------|
| classify | 无（仅分析+输出分类） |
| plan | grill-with-docs, gitnexus-context, langgraph-cli-analyze, oh-my-claude-advisor |
| execute | tdd, diagnose, gitnexus-impact, langgraph-cli-review, oh-my-claude-risk-assessor |
| verify | verify, gitnexus-detect-changes, oh-my-claude-validator, oh-my-claude-code-reviewer |
| done | omega-store |

### MUST NOT SKIP 工具

以下工具在对应状态下 **禁止跳过**：
- **gitnexus-context**: 修改任何函数/类前
- **gitnexus-impact**: 编辑任何符号前。HIGH/CRITICAL → 暂停+汇报
- **gitnexus-detect-changes**: 路径 D 提交前

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
