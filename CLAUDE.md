# AI Workflow Kit v2.5

面向 Claude Code 的通用 AI 辅助开发工作流套件。基于 **spec 状态机 + Skill 运行时**。

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

详见 `docs/TOOL-LAYERING.md` 和 `docs/COEXISTENCE.md`
