# 多系统共存指南

ai-workflow-kit 在 Claude Code 环境中与 oh-my-claude、Matt Pocock skills、OMEGA 共同运行。本指南说明各系统的职责边界和冲突解决。

## 系统职责矩阵

| 职责 | ai-workflow-kit | oh-my-claude | Matt Pocock skills | OMEGA |
|------|:--:|:--:|:--:|:--:|
| 任务分类 + 路由 | ✅ |  |  |  |
| 状态机约束 | ✅ |  |  |  |
| 执行阶段门控 | ✅ |  |  |  |
| 上下文保护 |  | ✅ |  |  |
| 代理编排 |  | ✅ |  |  |
| PreToolUse 安全检查 |  | ✅ |  |  |
| 需求对齐 |  |  | ✅ grill-with-docs |  |
| TDD 方法论 |  |  | ✅ tdd |  |
| 诊断闭环 |  |  | ✅ diagnose |  |
| 长期记忆 |  |  |  | ✅ |
| 代码知识图谱 | ✅ GitNexus |  |  |  |
| YAML 工作流 | ✅ |  |  |  |

## 优先级规则

1. **ai-workflow-kit 执行协议激活时**：状态约束最高优先级。覆盖 oh-my-claude 的 "just start working"。
2. **执行协议未激活时**（Path A / 完成后）：oh-my-claude 恢复默认行为。
3. **PreToolUse 安全 hook**（oh-my-claude）：始终运行，不被覆盖。
4. **OMEGA 记忆**：始终运行，不被覆盖。

## 已知冲突与解决

| 冲突 | oh-my-claude 说 | ai-workflow-kit 说 | 解决 |
|------|----------------|-------------------|------|
| 执行速度 | "No preamble. Just start." | "先分类，再 plan" | kit 激活时覆盖 |
| 提问 | "No unnecessary questions" | "grill 追问每个分支" | grill 阶段覆盖 |
| 状态汇报 | "No status summaries" | "输出 [路径 X \| 状态 Y]" | kit 激活时覆盖 |

## Spec 加载后的行为变化

当 `Skill("langgraph-cli")` 被调用时：
1. 读取 `.langgraph/specs/task-router.yaml`
2. 注入状态约束（最高优先级）
3. 锁定到 classify 状态
4. oh-my-claude 的执行加速指令被暂时挂起
5. 任务完成（done 状态）后恢复

## 安装验证

```bash
langgraph-cli health  # 检查全部组件
# 预期输出: 7/7 通过
# omega ✓, langgraph-cli ✓, gitnexus ✓, omega_db ✓, cli_path ✓, venv ✓, project ✓
```
