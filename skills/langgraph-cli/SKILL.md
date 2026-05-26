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

1. **智能接管** — 读取 `.langgraph/specs/intelligent-takeover.yaml`，按四维感知协议探测项目状态（见下方接管协议）
2. 输出 **Takeover Card** — 一张结构化卡片，后续所有路径引用
3. 读取 `.langgraph/specs/task-router.yaml` — 通用路由 spec
4. 根据 Takeover Card 的 recovery 级别决定行为路径（热恢复/温恢复/冷启动）
5. 注入以下状态约束（**最高优先级**）

---

## 接管协议 (Intelligent Takeover)

### Layer 1 — State: 项目四维状态
- **lifecycle**: newborn / growing / mature
  - 判定依据: 文件数 + git log 深度 + 有无 docs/ 或产出目录
- **activity**: active(最近 < 2天) / idle(2-14天) / dormant(>14天)
  - 判定依据: git log -1 + 工作区状态
- **integrity**: clean / dirty / broken
  - 判定依据: git status + 关键文件存在性
- 产出: `lifecycle=..., activity=..., integrity=...`

### Layer 2 — Context: 上次做到哪了
- 检查 `.langgraph/state.json`（活跃任务栈 + 当前路径+状态）
- 检查 handoff 文件、OMEGA 简报
- 判定 recovery 级别:
  - **hot**: state.json 存在 + activity=active → 直接恢复任务栈
  - **warm**: 无 state.json 但有 OMEGA/handoff → 从记忆重建
  - **inferred**: 无 state.json 无 OMEGA, 但有 git log + 产出目录 → 推断活跃方向, 标注 [inferred]
  - **cold**: 无任何上下文 → 全新评估
- 产出: `recovery=hot|warm|cold, task_stack=[...], last_path=...`

### Layer 3 — Health: 工具链健康
- credential 存在性（不实际调用 API）
- git 可用性
- 依赖文件存在性（package.json / pyproject.toml / requirements.txt）
- 判定: full / degraded / broken
  - degraded → 标注不可用路径
- 产出: `health=full|degraded|broken, unavailable=[...]`

### Layer 4 — Rules: 约束规则加载
- 从 CLAUDE.md / AGENTS.md / CONTEXT.md 提取硬规则
- 提取领域术语表
- 产出: `hard_rules=N, domain_terms=[...], output_root=...`

### 接管后的行为路由
| recovery | 行为 |
|----------|------|
| hot + active_task 未完成 | **直接恢复任务栈**，回到上次路径+状态，不重新 classify |
| warm | 从 OMEGA/handoff 重建上下文，按用户当前请求 classify |
| inferred | 从 git log + 产出目录推断活跃方向，标注 [inferred]，用户确认后 classify |
| cold | 标准 assess → classify |
| health=degraded | 标注不可用路径，用户触发时提前告知 |
| integrity=broken | 进入诊断模式，先修基础设施 |

### Takeover Card
接管完成后输出一张卡，注入后续所有路径的上下文。格式：
```
## Takeover Card
lifecycle=growing | activity=active | integrity=dirty
recovery=hot | health=full | rules=8 hard rules
active_task: gross_profitability_24h_batch
current_path: C | current_state: execute | step: 4/5
recommendation: 恢复 batch 执行，从 Phase 3 继续
```

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
| plan | preflight | 路径 C 且需要探索性 API 验证（字段可用性/覆盖率检查） |
| preflight | plan | 收集到足够信息（preflight 的 exit_when） |
| plan | execute | 路径 A 或无 spec 时跳过；否则已对齐相应路径 spec |
| execute | analyze | 结果需诊断优化（v2.4: iterate 循环） |
| analyze | execute | ≤3 轮迭代 AND 有定向修复策略 |
| execute | verify | 所有步骤标有 [✓] 且不需迭代 |
| verify | done | 验证通过 |

**状态中的 forbid 列表优先于用户请求。违反时回复: "当前在状态 [X]，该操作禁止。先完成 [门]。"**

### v2.4: 错误分级

遇到错误时按级别处理，不全部暂停:
- **exp** (预期失败): 记录 → 跳过 → 继续 → `[EXP]`
- **rate** (临时限流): 等待 → 重试 ≤3 → 仍失败则记录+跳过 → `[RATE]`
- **sys** (系统意外): 暂停 → 汇报 → 等用户 → `[SYS]`

### v2.4: 技能叠加

路径 spec 控制流程（何时做），领域 skill 控制约束（什么是正确的），同时加载不互斥。冲突时领域 hard rule 优先。`[SKILL STOP]` marker 记下原因。

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
