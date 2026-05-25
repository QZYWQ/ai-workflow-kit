# AI Workflow Kit

通用 AI 辅助开发工作流套件。

> ⛔ 强制路由规则见 `.langgraph/CLAUDE.md` — **任何非琐碎任务之前必须过路由门**，禁止跳过直接 Bash/编码。

## 你（AI）需要做的第一件事

读取本文件后，按序执行：

1. `bash install.sh` — 一键安装所有组件
2. 检查 `~/.claude/settings.json` 中是否有 `ANTHROPIC_BASE_URL` 和 `ANTHROPIC_AUTH_TOKEN`
3. 如果 oh-my-claude 未安装，引导用户运行：
   `/plugin marketplace add oh-my-claude && /plugin install oh-my-claude@oh-my-claude`
4. 完成后回复："工作流就绪。新项目: `langgraph-cli init`，已有项目: cd 进去后 `langgraph-cli init [--deep]`"
5. 进入任何项目时，如果项目目录含有 `.langgraph/CLAUDE.md`，**必须首先读取它**——它包含强制路由规则

## 安装的完整组件

| 组件 | 来源 | 作用 |
|------|------|------|
| langgraph-cli | Python 脚本 | 审查/测试/YAML 工作流（14 命令）|
| **OMEGA** | pip | **自动长期记忆**（Semantic Search + Consolidate + SessionStart 注入）|
| GitNexus | npm | 代码知识图谱（context/impact）|
| Matt Pocock skills | skills marketplace | grill-with-docs/tdd/diagnose 等 14 个方法论 skill |
| oh-my-claude | plugin marketplace | 编排纪律、validator/critic/code-reviewer agent |
| langgraph-cli skill | 本地注册 | Claude Code 识别 langgraph-cli 命令 |

## 记忆系统分层（防 token 爆炸）

```
OMEGA (auto) — 自动捕获教训/决策，语义搜索，定期 consolidate 清理过期记忆
  ↓ 互补
langgraph-cli remember (manual) — 用户明确说"记住这个"时使用
  ↓ 互补  
handoff (session) — "下次继续这个任务"的上下文快照
```

三套记忆互不冲突。OMEGA 自带的 consolidate/compact 防止 token 累积。
SessionStart 时 OMEGA 自动注入近期相关记忆，不需要手动 recall。

## 纯净 Claude Code 没有、这套补齐的全部东西

- **多智能体并行执行引擎** — langgraph-cli run（YAML 工作流）
- **代码知识图谱** — GitNexus context/impact
- **需求对齐** — grill-with-docs
- **TDD 方法论 skill** — Matt Pocock tdd
- **代码审查 agent** — oh-my-claude code-reviewer
- **验证门禁** — oh-my-claude validator
- **长期记忆** — langgraph-cli remember/recall
- **项目规则体系** — .langgraph/CLAUDE.md（AI 自管理）
- **两阶段执行协议** — 理解（grill）→ 执行（ultrawork）

## 工作流概览

```
理解 → 计划 → 编码 → 审查 → 上下文
 grill    to-prd   tdd     review   remember
 zoom-out analyze  proto   validator recall
                  caveman  impact    handoff
```

详见 `docs/TOOL-LAYERING.md`
