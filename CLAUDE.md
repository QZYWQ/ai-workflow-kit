# AI Workflow Kit

面向 Claude Code 的通用 AI 辅助开发工作流套件。

> ⛔ 强制路由规则见 `.langgraph/CLAUDE.md` —— **任何非琐碎任务之前必须过路由门**，禁止跳过直接 Bash/编码。

## 安装（AI 首次读取时执行）

1. `bash install.sh` — 安装 langgraph-cli、OMEGA、GitNexus、skills
2. 检查 `~/.claude/settings.json` 中的 `ANTHROPIC_BASE_URL` 和 `ANTHROPIC_AUTH_TOKEN`
3. 如果 oh-my-claude 未安装：引导用户运行 `/plugin marketplace add oh-my-claude && /plugin install oh-my-claude@oh-my-claude`
4. 完成后回复："工作流就绪。在项目中使用：`langgraph-cli init --deep`"
5. **提醒用户**：init 完成后，自动检测有边界——领域规则、API 注意事项、项目专属 workflow 需手动补齐（见 README "初始化后检查"）

## 项目工作流

进入任何项目目录时，如果项目含有 `.langgraph/CLAUDE.md`，必须首先读取——它包含强制路由规则（路径 A-F）。

| 路径 | 任务类型 | 执行链 |
|------|---------|--------|
| A | 琐碎 | 自由发挥，不走工作流 |
| B | 运维/审计/分析 | Skill("langgraph-cli") → analyze → 计划 → 确认 |
| C | 平台/API 操作 | Skill("langgraph-cli") → 计划 → 逐步执行 |
| D | 编码实现 | Skill("langgraph-cli") → GitNexus → grill-with-docs → TDD → review |
| E | 故障诊断 | Skill("diagnose") → 重现 → 修复 → 回归 |
| F | 设计/规划 | Skill("langgraph-cli") → analyze → 方案 → 确认 |

## 安装的组件

| 组件 | 来源 | 作用 |
|------|------|------|
| langgraph-cli | Python 脚本 | 审查/测试/YAML 工作流（14 命令） |
| OMEGA | pip | 自动长期记忆（Semantic Search + Consolidate + SessionStart 注入） |
| GitNexus | npm | 代码知识图谱（context/impact） |
| Matt Pocock skills | skills marketplace | grill-with-docs/tdd/diagnose 等 13 个方法论 skill |
| oh-my-claude | plugin marketplace | 编排纪律、validator/critic/code-reviewer agent |
| langgraph-cli skill | 本地注册 | Claude Code 识别 langgraph-cli 命令 |

## 记忆系统

三套互补，互不冲突：

- **OMEGA**（自动）— 捕获教训/决策，语义搜索，定期 consolidate 清理
- **langgraph-cli remember/recall**（手动）— 用户明确"记住这个"时
- **handoff**（会话）— "下次继续这个任务"的上下文快照

## 项目级 opt-in

工作流仅在运行过 `langgraph-cli init` 的项目目录中生效。不引入的项目完全不受影响。

详见 `docs/TOOL-LAYERING.md`
