# 工具分层 v2

## 架构

```
收到任务 → classify（分类）→ plan（计划）→ execute（执行）→ verify（验证）
               │                │               │               │
          【理解层】       【计划层】        【编码层】       【审查层】
               │                │               │               │
          └───────────── 上下文层（全程）──────────────────────┘
```

## 按状态分配（由 spec 定义，Skill 注入）

| 状态 | 可用 skill | 可用 CLI | 可用 agent |
|------|-----------|---------|-----------|
| classify | 无 | 无 | 无 |
| plan | grill-with-docs, worldquant-brain-alpha-engineering | analyze, context | Explore, librarian, advisor |
| execute | tdd, diagnose | review, test, impact | general-purpose, oh-my-claude:code-reviewer |
| verify | verify | detect_changes, pr | oh-my-claude:validator, oh-my-claude:security-auditor |
| 全程 | langgraph-cli remember/recall, handoff, GitNexus, OMEGA | | |

## 工具去重

| 能力 | Matt Pocock | oh-my-claude | langgraph-cli | 优先 |
|------|------------|-------------|--------------|------|
| 需求对齐 | grill-with-docs | advisor | — | grill-with-docs |
| 代码审查 | — | code-reviewer | `review <file>` | `langgraph-cli review` |
| 计划审查 | grill-me | critic | — | critic（自动）|
| 实现后验证 | verify | validator | `detect_changes` | validator + detect_changes（并行）|
| TDD | tdd | — | `test <code>` | tdd skill |
| 安全审查 | — | security-auditor | `review`（含安全）| 并行：两者都跑 |
| 上下文记忆 | handoff | — | remember/recall | 三套互补 |

## 项目级 opt-in

工作流仅在运行过 `langgraph-cli init` 的项目目录中生效。
不引入的项目不受影响。
