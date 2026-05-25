# AI Workflow Kit

通用 AI 辅助开发工作流套件。克隆后按下方说明自动安装。

## 你（AI）需要做的第一件事

读这个文件后，自动执行：
1. `bash install.sh` — 安装所有依赖
2. 完成后回复用户"工作流已就绪，在任何项目目录下运行 `langgraph-cli init` 即可初始化"
3. 如果用户在已有项目中，cd 到项目目录后运行 `langgraph-cli init [--deep]`

## 这是什么

一套可复用的 AI 辅助开发工作流，包含：
- **langgraph-cli** — 多智能体编排 CLI（代码审查、测试、记忆、YAML 工作流）
- **Matt Pocock skills** — 需求对齐、TDD、调试等 14 个方法论 skill
- **GitNexus** — 代码知识图谱（跨会话持久化代码结构理解）
- **两阶段执行协议** — grill-with-docs 理解阶段 + ultrawork 执行阶段

## 安装包含

| 组件 | 用途 | 安装方式 |
|------|------|---------|
| langgraph-cli | 14 个命令的 CLI | Python venv + pip |
| GitNexus | 代码知识图谱 | npm -g |
| Matt Pocock skills | 14 个方法论 skill | npx skills add |
| pyyaml | YAML 工作流解析 | pip |

## 使用流程

```bash
# 新项目
cd 新项目
langgraph-cli init [--deep]     # 生成 .langgraph/ 规则+工作流
gitnexus analyze .               # 建代码图谱
langgraph-cli remember "项目定位" -t "概况"  # 种初始记忆

# 已有项目
langgraph-cli init [--deep]

# CLI 手动使用
langgraph-cli review file.py    # 并行安全+质量审查
langgraph-cli pr                 # 生成 PR 描述
langgraph-cli context 函数名     # 查代码图谱上下文
langgraph-cli impact 函数名      # 查修改影响范围
langgraph-cli remember "决策" -t "标签"  # 持久化记忆
langgraph-cli recall "关键词"    # 搜索记忆
langgraph-cli run workflow.yaml -i x=y  # 执行工作流
langgraph-cli analyze .          # 项目结构分析
```

## Skill 触发时机

| 阶段 | 工具 |
|------|------|
| 理解 | grill-with-docs、zoom-out |
| 计划 | to-prd、langgraph-cli analyze |
| 编码 | tdd、prototype、caveman |
| 审查 | langgraph-cli review、oh-my-claude code-reviewer/validator |
| Bug | diagnose、triage |
| 上下文 | langgraph-cli remember/recall、handoff、GitNexus |

详见 `docs/TOOL-LAYERING.md`
