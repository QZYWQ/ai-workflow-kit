# 工具分层

```
理解层 → 计划层 → 编码层 → 审查层
  │                              │
  └────── 上下文层（全程）─────────┘
```

| 层 | 工具 |
|----|------|
| 理解 | grill-with-docs, zoom-out |
| 计划 | to-prd, langgraph-cli analyze |
| 编码 | tdd, prototype, caveman |
| 审查 | langgraph-cli review, oh-my-claude code-reviewer/validator |
| 上下文 | langgraph-cli remember/recall, handoff, GitNexus |
| 执行 | langgraph-cli run (YAML), Agent() 并行 |

## 两阶段协议

【阶段1】理解 — grill-with-docs 优先，暂停 ultrawork "不问"
【阶段2】执行 — grill 完成后 ultrawork 接管
