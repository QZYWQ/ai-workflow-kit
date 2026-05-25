# 工具分层

```
理解层 → 计划层 → 编码层 → 审查层 → 执行层
  │                                              │
  └────────── 上下文层（全程）───────────────────┘
```

| 层 | 工具 | 对应路由路径 |
|----|------|-------------|
| 理解 | grill-with-docs, zoom-out | 路径 D/F |
| 计划 | to-prd, langgraph-cli analyze | 路径 B/F |
| 编码 | tdd, prototype, caveman | 路径 D |
| 审查 | langgraph-cli review, oh-my-claude code-reviewer/validator | 路径 D |
| 上下文 | langgraph-cli remember/recall, handoff, GitNexus | 全部 |
| 执行 | langgraph-cli run (YAML), Agent() 并行 | 路径 C |

## 路由门规则（见 .langgraph/CLAUDE.md）

路径 A：琐碎任务 → 自由发挥，不走工作流
路径 B：运维分析 → Skill("langgraph-cli") → analyze → 计划 → 确认
路径 C：平台操作 → Skill("langgraph-cli") → run api-batch.yaml 或声明计划
路径 D：编码实现 → TDD + GitNexus + review
路径 E：故障诊断 → diagnose 闭环
路径 F：设计规划 → analyze → 方案 → 确认

## 两阶段协议

【阶段1】理解 — grill-with-docs 优先，暂停 ultrawork "不问"
【阶段2】执行 — grill 完成后 ultrawork 接管

## 项目级 opt-in

工作流仅在运行过 `langgraph-cli init` 的项目目录中生效。
不引入的项目不受任何影响。
