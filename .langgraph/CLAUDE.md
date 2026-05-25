# LangGraph 项目工作流

langgraph-cli 全局安装。本目录含工作流(.langgraph/workflows/)和长期记忆(.langgraph/memory/)。

══════════════════════════════
会话启动协议（新窗口/新会话必执行）
══════════════════════════════

**每次新会话开始时，自动执行以下步骤：**

1. `langgraph-cli recall "<本次任务关键词>"` — 恢复相关的项目决策和约定
2. 读取 `.langgraph/CLAUDE.md` — 确认当前规则
3. 如果存在 `.langgraph/memory/` 中最近 7 天的记忆 → 摘要给用户确认
4. 如果本目录有 CLAUDE.md 或 AGENTS.md → 读入上下文
5. 如果用户提供了 handoff 文件路径 → 读入上次会话状态

**此步骤不可跳过。** 只有完成以上检查后，才能进入正常的工作流程。

══════════════════════════════
规则自管理（AI 必读）
══════════════════════════════

收到"加规则"、"记决策"等指令，自动判断类型写入：
- 项目通用规则 → .langgraph/CLAUDE.md
- 编码规范 → src/CLAUDE.md
- 测试纪律 → tests/CLAUDE.md
- 可执行工作流 → .langgraph/workflows/ 新建YAML
- 一次性决策 → `langgraph-cli remember "内容" -t "标签"`

每次任务前：`langgraph-cli recall "<关键词>"`

══════════════════════════════
方法论选择
══════════════════════════════

| 任务 | 方法论 |
|------|--------|
| 新功能 | SDD（grill-with-docs → to-prd → 编码）|
| 复杂业务 | DDD（zoom-out → 领域建模 → 架构 → 编码）|
| 所有实现 | TDD（tdd → 测试 → 实现）|
| Bug | diagnose → 重现 → 最小修复 → 回归测试 |
| 原型 | prototype → caveman 极简验证 |

编码前强制检查：已查GitNexus？完成grill-with-docs？评估过度工程？

══════════════════════════════
两阶段执行协议
══════════════════════════════

【阶段1】理解 — grill-with-docs 优先
- 编码前必须通过grill-with-docs完成需求对齐
- 此阶段ultrawork"不问"规则暂停
- 查GitNexus确认无已有代码

【阶段2】执行 — ultrawork 接管
- grill-with-docs完成（文档已更新）后开始
- ultrawork纪律：不降级、不停止、强制验证

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
一、langgraph-cli 命令速查
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

- review <代码> — 并行审查
- test <代码> -o 输出 — 生成测试
- refactor <代码> — 重构建议
- analyze . — 项目分析
- context <符号> — GitNexus上下文
- impact <符号> — 影响范围
- pr — PR描述
- run workflow.yaml -i — 工作流
- remember "内容" -t "标签" — 记忆
- recall "关键词" — 搜索

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
二、标准工程工作流
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. GitNexus图谱对齐
2. 结构化计划，等待确认
3. 确认后开始编码
4. 技能驱动执行
5. TDD：测试→失败→实现→通过
6. 增量提交
7. GitNexus重索引

对应skill（按阶段）：

【理解】grill-with-docs / zoom-out
【计划】to-prd / langgraph-cli analyze
【编码】tdd / prototype / caveman
【审查】langgraph-cli review / oh-my-claude code-reviewer/validator / langgraph-cli impact
【Bug】diagnose / triage
【上下文】langgraph-cli remember-rec / handoff / GitNexus

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
三、最高优先级：优先使用已有代码
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

新增代码前，用GitNexus确认无已有能力可复用。找到→优先连线/配置/测试。无→实现新代码。

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
四、最小变更原则
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

声明假设，歧义停。评估过度工程。最小变更。手术式修改。每行追溯至需求。bug默认本地修复+回归。

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
五、编码规范 / Agent约束
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Python: 4空格,snake_case,PascalCase。格式化。不提交凭据。
未经批准不修改源码。不主动重构。不破坏性命令。不暴露密钥。
