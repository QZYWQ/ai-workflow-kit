# AI Workflow Kit v2.6

面向 Claude Code 的通用 AI 辅助开发工作流套件。基于 **spec 状态机 + Skill 运行时**。
多方法学支持：**TDD**（测试驱动）、**BDD**（行为驱动）、**DDD**（领域驱动）。

> v2.6 变化：+BDD（acceptance/evaluate/reconcile）+DDD（tenets/model）— 多方法学协同
> v2 核心变化：Skill("langgraph-cli") 现在是执行协议运行时，不是权限声明。加载后锁定主会话到状态机中。
> **共存**：协议激活时覆盖 oh-my-claude 的 "just start working"。任务完成后 oh-my-claude 恢复默认。
> 路由规则见 `.langgraph/CLAUDE.md`（紧凑决策树）和 `.langgraph/specs/`（可复用规范）。

## 安装

1. `bash install.sh` — 安装全部组件 + 执行验证
2. `langgraph-cli health` — 确认全部组件就绪
3. 如果 oh-my-claude 未安装：`/plugin marketplace add oh-my-claude`
4. 完成后："工作流就绪。新项目: `langgraph-cli init --deep`"

## 架构

```
收到任务
  → Skill("langgraph-cli") 被调用（路径 B–F）
    → 读取 .langgraph/specs/task-router.yaml
    → 锁定当前状态: classify
    → classify → plan → execute → verify → done
    → 每个状态有 {允许, 禁止, 工具, 产出}
    → Skill 注入的自检清单强制执行
```

## 路径速查

| 关键词 | 路径 | spec |
|--------|------|------|
| 提交\|API\|batch\|挖掘 | C | platform-operation.yaml |
| 实现\|开发\|重构\|写代码 | D | code-implementation.yaml |
| bug\|报错\|修复\|诊断 | E | diagnose.yaml |
| 设计\|架构\|方案\|规划 | F | design-planning.yaml |
| 审计\|安全\|冗余\|质量 | B | ops-analysis.yaml |
| 读\|解释\|简单问答 | A | 无（自由执行）|

## 组件

| 组件 | 作用 |
|------|------|
| langgraph-cli | CLI（14 命令） + 执行协议运行时 |
| OMEGA | 自动长期记忆 |
| GitNexus | 代码知识图谱 |
| oh-my-claude | 编排纪律、agents、hooks |
| Matt Pocock skills | 方法论（grill/tdd/diagnose 等）|
| BDD 工具链 | bdd-acceptance（spec 生成）、bdd-evaluate（行为验证）、bdd-reconcile（需求变更级联）|
| DDD 工具链 | ddd-tenets（架构约束）、ddd-model（领域模型持久化）|

详见 `docs/TOOL-LAYERING.md` 和 `docs/COEXISTENCE.md`

## 开发历史

所有架构决策和踩坑记录——新会话启动时建议浏览：
- `docs/LESSONS-LEARNED.md` — 14 个已验证的陷阱（trigger 门槛、deconflict 虚设、prompt 级无牙等）
- `docs/adr/001-multi-methodology-progressive-disclosure.md` — 核心架构决策
- `git log --oneline` — 开发时间线

<!-- gitnexus:start -->
# GitNexus — Code Intelligence

This project is indexed by GitNexus as **ai-workflow-kit** (377 symbols, 441 relationships, 0 execution flows). Use the GitNexus MCP tools to understand code, assess impact, and navigate safely.

> If any GitNexus tool warns the index is stale, run `npx gitnexus analyze` in terminal first.

## Always Do

- **MUST run impact analysis before editing any symbol.** Before modifying a function, class, or method, run `gitnexus_impact({target: "symbolName", direction: "upstream"})` and report the blast radius (direct callers, affected processes, risk level) to the user.
- **MUST run `gitnexus_detect_changes()` before committing** to verify your changes only affect expected symbols and execution flows.
- **MUST warn the user** if impact analysis returns HIGH or CRITICAL risk before proceeding with edits.
- When exploring unfamiliar code, use `gitnexus_query({query: "concept"})` to find execution flows instead of grepping. It returns process-grouped results ranked by relevance.
- When you need full context on a specific symbol — callers, callees, which execution flows it participates in — use `gitnexus_context({name: "symbolName"})`.

## Never Do

- NEVER edit a function, class, or method without first running `gitnexus_impact` on it.
- NEVER ignore HIGH or CRITICAL risk warnings from impact analysis.
- NEVER rename symbols with find-and-replace — use `gitnexus_rename` which understands the call graph.
- NEVER commit changes without running `gitnexus_detect_changes()` to check affected scope.

## Resources

| Resource | Use for |
|----------|---------|
| `gitnexus://repo/ai-workflow-kit/context` | Codebase overview, check index freshness |
| `gitnexus://repo/ai-workflow-kit/clusters` | All functional areas |
| `gitnexus://repo/ai-workflow-kit/processes` | All execution flows |
| `gitnexus://repo/ai-workflow-kit/process/{name}` | Step-by-step execution trace |

## CLI

| Task | Read this skill file |
|------|---------------------|
| Understand architecture / "How does X work?" | `.claude/skills/gitnexus/gitnexus-exploring/SKILL.md` |
| Blast radius / "What breaks if I change X?" | `.claude/skills/gitnexus/gitnexus-impact-analysis/SKILL.md` |
| Trace bugs / "Why is X failing?" | `.claude/skills/gitnexus/gitnexus-debugging/SKILL.md` |
| Rename / extract / split / refactor | `.claude/skills/gitnexus/gitnexus-refactoring/SKILL.md` |
| Tools, resources, schema reference | `.claude/skills/gitnexus/gitnexus-guide/SKILL.md` |
| Index, status, clean, wiki CLI commands | `.claude/skills/gitnexus/gitnexus-cli/SKILL.md` |

<!-- gitnexus:end -->
