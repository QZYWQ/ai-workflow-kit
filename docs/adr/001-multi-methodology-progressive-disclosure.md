# ADR 001: Multi-Methodology Architecture with Progressive Disclosure

## Status
Accepted (2026-05-27)

## Context
v2.5 工作流以 TDD 为单一方法学，缺少 BDD（行为验收）和 DDD（领域建模）支持。直接添加新方法学会导致三方面问题：

1. **工具冲突** — 多个工具在同一状态发言，TDD 说"先写最简单的测试"，DDD 说"先设计聚合根"
2. **上下文膨胀** — 所有协议文本始终加载，消耗 token 但不一定使用
3. **项目类型不匹配** — 库/工具项目不需要行为验收，原型阶段不需要完整验证

## Decision
采用**渐进式披露（Progressive Disclosure）**架构：

### 核心机制
- **方法学捆绑**：TDD/BDD/DDD/verify_full 各自作为独立 bundle，包含相关工具
- **三级激活**：active（强制协议）/ passive（建议但不强制）/ off（工具不可用）
- **六阶段匹配**：toolkit/prototype/mvp/production/maintenance/unknown，每阶段有不同默认激活
- **状态感知**：assess/classify 全部 off，plan 恢复激活，done 全部 off
- **用户覆盖**：随时可说"激活/关闭 + 方法学名"切换

### 冲突裁决
- 同一状态内的工具按**串行锁**顺序执行（grill→ddd→bdd），deconflict 声明是文档
- 领域 hard rule 优先级高于执行流程的"继续"
- implement↔review 回退上限 3 次

### 热恢复
- state.json 持久化 task_stack + current_path + current_state
- phase 和 methodology 不信任缓存，每次会话重新评估

## Consequences

### Positive
- toolkit 项目自动关闭 BDD（无用户界面不需要行为验收）
- prototype 阶段关闭 BDD 和 verify_full（降低快速迭代摩擦）
- production 阶段自动激活全部方法学（完整的质量门）
- 用户可手动覆盖，但不覆盖时也有合理默认

### Negative
- 22K tokens 协议开销（仍有优化空间）
- prompt 级约束无程序级强制（AI 可以自律，也可以不）
- phase 检测依赖用户关键词 + 文件结构信号，无法 100% 准确

### Risks
- 多方法学同时激活时，AI 可能忽略部分约束（已记录为已知限制）
- toolkit phase 的 not_detect 信号（无 Web 服务）可能误判边缘项目

## Related
- `methodology-activation.yaml` — 方法学定义 + 阶段默认 + 动态切换
- `intelligent-takeover.yaml` v1.1 — 五维感知中含 phase 检测
- `task-router.yaml` v2.6 — plan 状态含串行锁 + 方法论感知
- `tests/e2e/` — 23 个 E2E 仿真场景覆盖
