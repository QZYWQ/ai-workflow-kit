# AI Workflow Kit

面向 Claude Code 的通用 AI 辅助开发工作流套件。安装一次，所有项目按需引入。

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)

## 解决的问题

Claude Code + oh-my-claude 让 AI 可以"快速执行"，但面对复杂任务时缺乏**结构化的执行协议**——AI 倾向于跳过分析直接编码，跳过 plan 直接跑 API。纯文档规则（"你必须先分类"）在上下文衰减后约束力接近零。

v2 方案：**spec 状态机 + Skill 运行时**。
- Skill("langgraph-cli") 不再是权限声明，而是**执行协议运行时**
- 加载后锁定主会话到状态机（classify → plan → execute → verify），每个状态定义 {允许, 禁止, 工具, 产出}
- 自检清单注入每次回复末尾，AI 无法跳过
- 与 oh-my-claude 共存：协议激活时覆盖 "just start working"

## 快速开始

```bash
# 1. 克隆到任意位置（不是你的项目目录）
git clone https://github.com/QZYWQ/ai-workflow-kit.git
cd ai-workflow-kit

# 2. 在 Claude Code 中打开本目录，AI 自动执行安装
#    或手动：
bash install.sh
```

安装完成后本目录可以删除——工具已全局部署。

## 在项目中使用

```bash
cd /你的项目
langgraph-cli init --deep     # 生成 .langgraph/ 工作流体系，自动检测项目特征
```

然后用 Claude Code 打开项目。AI 会读取路由规则，自动匹配任务类型到对应执行路径。

### 初始化后检查

`init --deep` 会自动检测项目特征，但**自动检测有边界**——它只能识别文件模式（API 客户端、脚本语言、凭据文件），不会理解你的领域规则。init 完成后建议做一次对齐检查：

```bash
# 1. 检查项目专属覆盖区域
cat .langgraph/CLAUDE.md | grep -A30 "项目专属覆盖"

# 2. 用 Claude Code 跑一次模拟测试
#    对新项目说："帮我分析项目结构，看看工作流引入是否有遗漏"
```

**常见需要手动补的**：

| 检测项 | 自动检测能做到 | 需要手动补 |
|--------|-------------|----------|
| API 客户端路径 | ✅ 检测到文件存在 | ⚠️ 调用方式、限流规则、关键字段格式 |
| 凭据文件 | ✅ 检测到文件名 | ⚠️ 认证方式、环境变量名 |
| 脚本数量 | ✅ 统计数量 | ⚠️ 核心脚本 vs 辅助脚本的分类 |
| 领域规则 | ❌ 检测不到 | ⚠️ 平台特定限制、业务约束、经验教训 |
| 项目专属 workflow | ❌ 检测不到 | ⚠️ 通用 api-batch.yaml 之外需要定制化 YAML |
| 已有项目现有规则冲突 | ❌ 检测不到 | ⚠️ 路由门规则 vs 已有 CLAUDE.md/AGENTS.md 规则去重 |

> 示例：一个 WorldQuant BRAIN 项目 init 后自动检测到了 API 客户端和凭证，但 `favorite: true` 字段格式限制、`/check` 端点限流规则、已提交 alpha 列表——这些都是手动补进项目专属覆盖区域的。

然后用 Claude Code 打开项目。AI 会读取路由规则，自动匹配任务类型到对应执行路径：

| 你说 | AI 走 | 执行链 |
|------|------|--------|
| "解释这段代码" | 路径 A | 直接执行 |
| "调用 API 批量操作" | 路径 C | Skill 加载 spec → classify → plan → execute |
| "实现新功能" | 路径 D | Skill 加载 spec → classify → GitNexus → grill → plan → TDD → review |
| "修这个 bug" | 路径 E | Skill(diagnose) 加载 spec → classify → 重现 → 修复 → 验证 |
| "设计架构方案" | 路径 F | Skill 加载 spec → classify → analyze → 方案对比 |

## 不引入的项目

没有 `.langgraph/` 目录的项目完全不受影响——Claude Code 保持原生行为。

## 命令参考

```bash
langgraph-cli init [--deep]           # 项目初始化
langgraph-cli analyze .               # 项目结构分析
langgraph-cli review <文件>           # 并行安全+质量审查
langgraph-cli run workflow.yaml       # 执行 YAML 工作流
langgraph-cli remember "决策" -t "标签" # 长期记忆
langgraph-cli recall "关键词"         # 记忆搜索
langgraph-cli health                  # 全组件健康检查
```

## 架构

```
收到任务
  → Skill("langgraph-cli") 激活执行协议
    → 读取 .langgraph/specs/task-router.yaml
    → 锁定 classify → plan → execute → verify → done
    → 每个状态有 {允许, 禁止, 工具分配, 产出要求}
    → 自检清单注入每次回复末尾

spec 目录（可复用规范）
  ├── task-router.yaml      # 通用分类+分发
  ├── platform-operation.yaml  # 路径 C
  ├── code-implementation.yaml # 路径 D
  ├── diagnose.yaml            # 路径 E
  ├── design-planning.yaml     # 路径 F
  └── ops-analysis.yaml        # 路径 B

工具栈
  ├── langgraph-cli（CLI + 运行时）
  ├── OMEGA（自动长期记忆）
  ├── GitNexus（代码知识图谱）
  ├── oh-my-claude（编排纪律、agents、hooks）
  └── Matt Pocock skills（13 个方法论）

项目级 opt-in
  └── 有 .langgraph/ → 路由门激活
      └── 无 .langgraph/ → 原生 Claude Code
```

## 文档

| 文档 | 内容 |
|------|------|
| [CLAUDE.md](CLAUDE.md) | AI 入口协议 |
| [docs/TOOL-LAYERING.md](docs/TOOL-LAYERING.md) | 工具分层 + 去重 |
| [docs/COEXISTENCE.md](docs/COEXISTENCE.md) | 多系统共存 + 冲突解决 |
