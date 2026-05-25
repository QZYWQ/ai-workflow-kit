# AI Workflow Kit

可复用的 AI 辅助开发工作流模板。**安装一次，所有项目按需引入**。项目级 opt-in，不引入的项目完全不受影响。

## 快速开始

```bash
# 1. 克隆到任意位置（不是你的项目目录）
git clone https://github.com/QZYWQ/ai-workflow-kit /tmp/ai-workflow-kit
cd /tmp/ai-workflow-kit

# 2. 在 Claude Code 中打开本目录，AI 自动执行安装
#    或手动运行：
bash install.sh
```

安装完成后，kit 目录可以删除——工具已全局安装。

## 在项目中使用（按需引入）

```bash
cd 你的项目目录
langgraph-cli init [--deep]      # 生成 .langgraph/ 工作流体系
gitnexus analyze .                # 建立代码知识图谱
```

然后在 Claude Code 中打开你的项目——AI 会自动读取路由规则，按任务类型选择对应工作流。

| 你说… | AI 会… |
|--------|--------|
| "审计一下项目" | 加载 langgraph-cli → analyze → 结构化计划 |
| "修这个 bug" | 加载 diagnose → 重现 → 修复 → 回归测试 |
| "实现这个功能" | 加载 grill-with-docs → TDD → review |
| "提交 alpha" | 声明步骤 → 等待确认 → 执行 |
| "这个代码什么意思" | 直接回答（琐碎任务，不走工作流） |

## 不引入的项目

没有 `.langgraph/` 目录的项目不受任何影响，Claude Code 保持原生行为。

## 命令速查

```bash
langgraph-cli review file.py        # 并行安全+质量审查
langgraph-cli analyze .             # 项目结构分析
langgraph-cli pr                    # 生成 PR 描述
langgraph-cli remember "决策" -t "标签"  # 长期记忆
langgraph-cli recall "关键词"       # 记忆搜索
langgraph-cli run workflow.yaml -i k=v  # 执行工作流
```

## 包含

- **langgraph-cli** — 14 命令的 CLI（审查/测试/工作流/init）
- **OMEGA** — 自动长期记忆
- **GitNexus** — 代码知识图谱
- **6 条强制路由规则** — 自动识别任务类型并匹配方法论
- **4 个工作流模板** — code-review / fix-bug / add-feature / api-batch
- **Matt Pocock skills** — grill-with-docs / tdd / diagnose 等 13 个方法论 skill

详见 [CLAUDE.md](CLAUDE.md)（AI 入口）和 [docs/TOOL-LAYERING.md](docs/TOOL-LAYERING.md)
