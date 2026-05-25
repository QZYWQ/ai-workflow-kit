# AI Workflow Kit

面向 Claude Code 的通用 AI 辅助开发工作流套件。安装一次，所有项目按需引入。

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)

## 解决的问题

Claude Code 原生能力强，但面对项目时缺乏**结构化的执行协议**——审计什么时候用 analyze 还是直接 Bash？实现新功能走 TDD 还是直接写？bug 排查靠灵感还是靠闭环？

AI Workflow Kit 提供一套**项目级可插拔的强制路由规则**：AI 收到任务先分类，再按路径加载对应 skill、执行结构化工作流。琐碎任务走自由通道，复杂任务走方法论——该严格的严格，该灵活的灵活。

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
| "解释这段代码" | 路径 A：琐碎 | 直接回答，不走工作流 |
| "审计项目" | 路径 B：运维 | Skill → analyze → 计划 → 确认 |
| "调用 API 批量操作" | 路径 C：平台 | Skill → 计划 → 逐步执行 |
| "实现新功能" | 路径 D：编码 | Skill → GitNexus → grill-with-docs → TDD |
| "修这个 bug" | 路径 E：诊断 | diagnose → 重现 → 修复 → 回归 |
| "设计架构方案" | 路径 F：规划 | Skill → analyze → 方案 → 确认 |

## 不引入的项目

没有 `.langgraph/` 目录的项目完全不受影响——Claude Code 保持原生行为。

## 命令参考

```bash
langgraph-cli init [--deep]           # 项目初始化（--force 强制刷新模板）
langgraph-cli analyze .               # 项目结构分析
langgraph-cli review <文件>           # 并行安全+质量审查
langgraph-cli pr                      # 生成 PR 描述
langgraph-cli run workflow.yaml       # 执行工作流
langgraph-cli remember "决策" -t "标签" # 长期记忆
langgraph-cli recall "关键词"         # 记忆搜索
```

## 架构

```
路由门（6 条强制路径）
  ├── A: 琐碎 → 自由
  ├── B: 运维 → analyze → 计划
  ├── C: 平台 → 工作流 YAML
  ├── D: 编码 → grill-with-docs → TDD → review
  ├── E: 诊断 → 闭环
  └── F: 规划 → analyze → 方案

工具栈
  ├── langgraph-cli（CLI 14 命令）
  ├── OMEGA（自动长期记忆）
  ├── GitNexus（代码知识图谱）
  └── Matt Pocock skills（13 个方法论）

项目级 opt-in
  └── 有 .langgraph/ → 路由门激活
      └── 无 .langgraph/ → 原生 Claude Code
```

## 组件

| 组件 | 用途 |
|------|------|
| `langgraph-cli` | 项目分析、代码审查、YAML 工作流、记忆管理 |
| OMEGA | 自动长期记忆，跨会话保持上下文 |
| GitNexus | 代码知识图谱，context/impact 查询 |
| Matt Pocock skills | grill-with-docs, TDD, diagnose 等 13 个方法论 |
| 工作流 YAML | code-review, fix-bug, add-feature, api-batch |

详见 [CLAUDE.md](CLAUDE.md)（AI 入口协议）和 [docs/TOOL-LAYERING.md](docs/TOOL-LAYERING.md)
