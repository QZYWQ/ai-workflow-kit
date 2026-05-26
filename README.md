# AI Workflow Kit

**让 Claude Code 在复杂任务中保持纪律，不跳步、不猜规则、不丢失上下文。**

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)

---

## 为什么需要

Claude Code 的默认模式是"理解需求 → 直接动手"。这在简单任务中高效，但在以下场景会出问题：

- **你的项目有硬性规则**（不能直接调生产 API、必须先验证脱离）——AI 当建议读，不当硬约束
- **任务跨多步骤**（设计→实现→审查→提交）——AI 容易跳过中间的验证
- **多个 AI 工具职责重叠**（grill vs review vs critic）——不知道该用哪个
- **上次做到一半**——新会话打开后 AI 不知道做到哪了

AI Workflow Kit 在 Claude Code 之上加了一层**状态感知 + 门控执行**：知道项目处在什么状态、该做什么、不该做什么、上次做到哪了。

## 核心能力

```
会话启动
  └→ 智能接管：感知项目状态（代码量/文档/活跃度/工具链健康）
       └→ 输出 Takeover Card：一张结构化状态卡
            ├─ 上次未完成 → 直接恢复任务栈（不重跑流程）
            ├─ 有历史上下文 → 从记忆重建
            └─ 全新开始 → 标准接入流程
```

### 五条执行路径

| 你的任务 | AI 自动走 | 保证 |
|----------|---------|------|
| API 调用、批量操作、数据挖掘 | **路径 C** | preflight 先验证 API 可用 → plan → 分步执行 → 错误分级处理 |
| 写新功能、重构 | **路径 D** | 先读已有代码 → 对齐设计文档 → TDD 实现 → 自检审查 |
| 修 bug、诊断问题 | **路径 E** | 重现 → 二分定位 → 最小修复 → 回归验证 |
| 设计架构、做方案 | **路径 F** | 现状分析 → 多方案对比 → 对齐术语表 → 产出设计记录 |
| 安全审计、代码清理 | **路径 B** | 全局扫描 → 问题分级（P0/P1/P2）→ 产出报告 |

### 智能接管

每次会话启动自动感知四层信息：

| 层 | 探测 | 结果 |
|----|------|------|
| **State** | 代码规模 + git 历史 + 产出目录 | lifecycle × activity × integrity |
| **Context** | state.json + OMEGA + handoff | hot/warm/inferred/cold 恢复 |
| **Health** | credential + git + 依赖 | full/degraded/broken |
| **Rules** | CLAUDE.md + AGENTS.md + docs/ | 硬规则数 + 术语表 + 产出路径 |

如果上次任务没完成且有 `state.json` → **热恢复**，直接回到中断点。不需要重新描述项目背景。

### 工具编排

多技能协同工作时避免冲突：

- `langgraph-cli` 先接管（流程控制）→ 按需加载领域 skill（业务规则）
- 同一状态只激活允许的工具，禁止越权（plan 阶段不能写代码，preflight 只能做只读 API）
- 重叠工具去重：`grill-with-docs` vs `grill-me`（有无 CONTEXT.md）、`review` vs `code-reviewer`（不同阶段）

### 错误不再一刀切

| 错误类型 | 例子 | 行为 |
|----------|------|------|
| 预期失败 | API 对特定参数返回 ERROR | 记录 → 跳过 → 继续 |
| 临时限流 | HTTP 429 | 等待 → 重试（最多 3 次） |
| 系统意外 | SSL 错误 | 暂停 → 汇报 → 等决策 |

## 安装

```bash
git clone https://github.com/QZYWQ/ai-workflow-kit.git
cd ai-workflow-kit
bash install.sh
```

安装完成后本目录可以删除——组件已全局部署。

更新：`git pull` 后重跑 `bash install.sh` 即可同步。

## 在项目中使用

```bash
cd /你的项目
langgraph-cli init --deep
```

然后用 Claude Code 打开项目。AI 读到 `.langgraph/` 后自动激活路由门控。

没有 `.langgraph/` 的项目不受任何影响。

## 与其他工具的关系

AI Workflow Kit 不是替代品，是它们之上的**流程编排层**：

```
┌──────────────────────────────────┐
│      AI Workflow Kit（流程编排）    │  何时做、什么顺序、做完没
├──────────────────────────────────┤
│  oh-my-claude（纪律 + agents）     │  并行审查、安全检查
├──────────────────────────────────┤
│  Matt Pocock skills（方法论）       │  grill、TDD、diagnose
├──────────────────────────────────┤
│  OMEGA（长期记忆）                 │  跨会话上下文
├──────────────────────────────────┤
│  GitNexus（代码图谱）              │  影响分析、调用链追溯
└──────────────────────────────────┘
```

详细共存规则见 [docs/COEXISTENCE.md](docs/COEXISTENCE.md)。

## 命令

```bash
langgraph-cli init [--deep]           # 项目接入
langgraph-cli analyze .               # 项目结构分析
langgraph-cli review <文件>           # 代码安全+质量审查
langgraph-cli run workflow.yaml       # YAML 多 agent 工作流
langgraph-cli remember "决策"         # 长期记忆
langgraph-cli recall "关键词"         # 记忆检索
langgraph-cli health                  # 组件健康检查
```

## 文档

| 文档 | 内容 |
|------|------|
| [CLAUDE.md](CLAUDE.md) | AI 入口协议 |
| [docs/TOOL-LAYERING.md](docs/TOOL-LAYERING.md) | 工具分配 + 去重规则 |
| [docs/COEXISTENCE.md](docs/COEXISTENCE.md) | 多系统共存 + 优先级 |

## 许可证

MIT
