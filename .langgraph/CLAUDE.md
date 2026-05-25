# LangGraph 项目工作流

langgraph-cli 全局安装。本目录含工作流(.langgraph/workflows/)和长期记忆(.langgraph/memory/)。

⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
⛔ 强制路由规则（每次收到任务后，第一个动作不是执行，是分类）
⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

收到任务后，按顺序执行以下步骤。除路径 A 外，其余路径**禁止跳过路由直接 Bash/Python**。

### 步骤 1：任务分类（匹配模式，走对应路径）

路径 A：琐碎任务 — 自由发挥
  匹配：单行修改、拼写、加一行日志、读文件、解释代码、
       改一个变量名、回答简单问题
  条件：≤3 个独立动作 且 不涉及外部 API 且 不涉及破坏性操作
  执行：直接完成。不需要加载 skill，不需要走工作流。

路径 B：运维分析 — langgraph-cli analyze 流程
  匹配：审计、扫描、清理、冗余分析、数据膨胀、安全审查、
       代码质量、依赖检查、项目健康、重构建议
  执行：
    1. Skill("langgraph-cli")   ← 加载 skill，让 analyze/run 可用
    2. langgraph-cli analyze .   ← 全局项目分析
    3. 按结果结构化计划           ← 等待用户确认
    4. 确认后执行

路径 C：平台操作 / API 调用 — 工作流编排
  匹配：提交、标记、同步、批量操作、API 调用、账户管理、
       外部服务交互、数据抓取
  执行：
    1. Skill("langgraph-cli")
    2. 声明步骤计划 → 等待用户确认
    3. 确认后执行（逐步骤，遇错误暂停汇报）
    4. 操作结果写入 runs/ 对应目录

路径 D：编码实现 — TDD + 审查
  匹配：新功能、修改业务逻辑、重构、添加模块、写库代码
  执行：
    1. Skill("langgraph-cli")
    2. GitNexus 查已有实现（避免重复）
    3. Grill-with-docs 需求对齐（非琐碎实现）
    4. TDD：测试 → 失败 → 实现 → 通过
    5. langgraph-cli review 变更

路径 E：故障诊断 — 诊断闭环
  匹配：bug、报错、不工作、调试、异常、性能
  执行：
    1. Skill("diagnose")
    2. 重现 → 定位 → 最小修复 → 回归验证

路径 F：设计规划 — 理解 → 方案
  匹配：架构设计、方案选择、技术决策、怎么实现
  执行：
    1. Skill("langgraph-cli")
    2. langgraph-cli analyze 或 GitNexus context
    3. 输出结构化方案 → 等待确认 → 确认后走路径 D 实现

### 步骤 2：⛔ 硬性禁止（路径 B–F 适用）

在完成上述路由步骤前：
  ✗ 禁止直接使用 Bash 执行分析、操作、API 调用
  ✗ 禁止未加载 skill 就使用 analyze/run/review 命令
  ✗ 禁止跳过"等待用户确认"执行破坏性操作
  ✗ 禁止跳过 GitNexus 检查新增已有能力的代码

路径 A（琐碎任务）不在此限——可自由发挥。

### 步骤 3：路径选择快速参考

| 用户说了 | 路径 | 第一步 |
|---------|------|--------|
| "查/看/读/解释" | A（琐碎） | 直接完成 |
| "审计/扫描/清理/冗余" | B（运维） | Skill("langgraph-cli") |
| "提交/标记/同步/API" | C（平台） | Skill("langgraph-cli") |
| "实现/开发/加功能" | D（编码） | Skill("langgraph-cli") + GitNexus |
| "bug/报错/不工作" | E（诊断） | Skill("diagnose") |
| "设计/架构/方案" | F（规划） | Skill("langgraph-cli") |
| 模糊/无法分类 | 先确认再分类 | AskUserQuestion |

⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
会话启动协议（新窗口/新会话必执行）
⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

**每次新会话开始时，自动执行以下步骤：**

1. OMEGA 已通过 SessionStart hook 自动注入 omega_welcome（近期记忆 + 简报）
   - 你（AI）不需要手动调 recall，OMEGA 已经做了
2. 如果需要更精确搜索：调 omega_query 或 langgraph-cli recall
3. 读取 .langgraph/CLAUDE.md — **此步骤不可跳过**（含强制路由规则）
4. 读取项目 CLAUDE.md 或 AGENTS.md — 了解领域知识和项目专属规则
5. 如果用户提供了 handoff 文件路径 → 读入上次会话状态
6. 会话启动完成，等待用户任务，过强制路由门

⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
记忆系统分层（防 token 爆炸）
⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

- **OMEGA**（自动）— 捕获教训/决策，语义搜索，定期 consolidate/compact 清理
- **langgraph-cli remember/recall**（手动）— 用户明确"记住这个"时
- **handoff**（会话）— "下次继续这个任务"的上下文快照

三套互补，不冲突。OMEGA 自带 token 管理。

⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
两阶段执行协议（路径 D/F 适用）
⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

【阶段1】理解 — grill-with-docs 优先（路径 D 编码前必须）
- 编码前完成需求对齐，ultrawork"不问"规则暂停
- 查 GitNexus 确认无已有代码可复用
- 路径 B/C/E 的理解阶段：analyze/检查/定位 → 结构化计划

【阶段2】执行 — ultrawork 接管
- 阶段1完成后开始，纪律：不降级、不停止、强制验证
- 路径 C（平台操作）的"等待用户确认"不在阶段2范围内，用户确认后方可执行

⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
规则自管理（AI 必读）
⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

收到"加规则"、"记决策"等指令，自动判断类型写入：
- 项目通用规则 → .langgraph/CLAUDE.md（本文件"项目专属覆盖"区域）
- 编码规范 → src/CLAUDE.md
- 测试纪律 → tests/CLAUDE.md
- 可执行工作流 → .langgraph/workflows/ 新建 YAML
- 一次性决策 → langgraph-cli remember "内容" -t "标签"

每次任务前：OMEGA 自动注入 + 需要时 langgraph-cli recall

⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
langgraph-cli 命令速查
⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

- analyze . — 项目结构分析（路径 B/F 第一步）
- review <代码> — 并行安全+质量审查
- impact <符号> — 修改影响范围
- context <符号> — GitNexus 符号上下文
- run workflow.yaml -i — 执行工作流 YAML
- remember "内容" -t "标签" — 长期记忆
- recall "关键词" — 记忆搜索
- test <代码> -o 输出 — 生成测试
- refactor <代码> — 重构建议
- pr — PR 描述生成

⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
通用约束（所有路径）
⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

- 优先使用已有代码：新增加前用 GitNexus 确认无已有能力可复用
- 最小变更：声明假设，歧义停。评估过度工程。手术式修改
- Python: 4空格,snake_case,PascalCase。格式化。不提交凭据
- 未经批准不修改源码。不主动重构。不破坏性命令。不暴露密钥
