# AI Workflow Kit v2.6

**让 Claude Code 在复杂任务中保持纪律——知道项目处在什么状态、该做什么、不该做什么、上次做到哪了。**

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)

---

## 为什么需要

Claude Code 的默认模式是"理解需求 → 直接动手"。这在简单任务中高效，但在以下场景会出问题：

- **项目有硬性规则**（不能直接调生产 API、必须先验证脱离）——AI 当建议读
- **任务跨多步骤**（设计→实现→审查→提交）——AI 容易跳过中间验证
- **多个工具职责重叠**（grill vs review vs critic）——不知道该用哪个
- **上次做到一半**——新会话打开后不知道做到哪了
- **开发阶段变了**（原型→生产）但约束没变——AI 按同样的规则对待不同阶段

AI Workflow Kit 在 Claude Code 之上加了**五维感知 + 门控执行 + 方法学动态激活**。

## 核心能力

### 智能接管（五维感知）

每次会话启动自动感知：

| 层 | 探测 | 结果 |
|----|------|------|
| **State** | 代码规模 + git 历史 + 产出目录 | lifecycle × activity × integrity |
| **Context** | state.json + OMEGA + handoff | hot/warm/cold 恢复 |
| **Health** | credential + git + 依赖 | full/degraded/broken |
| **Rules** | CLAUDE.md + AGENTS.md + docs/ | 硬规则数 + 术语表 |
| **Phase** | git tag + CI/CD + 文件结构 | toolkit/prototype/mvp/production/maintenance |

上次任务未完成且有 `state.json` → **热恢复**，直接回到中断点。

### 六条执行路径

| 任务 | 路径 | 保证 |
|------|------|------|
| API 调用、批量操作、数据挖掘 | **C** | preflight 验证 → plan → 分步执行 → 错误分级 |
| 写新功能、重构 | **D** | 读已有代码 → 对齐文档 → 方法学实现 → 审查 |
| 修 bug、诊断问题 | **E** | 重现 → 二分定位 → 最小修复 → 回归验证 |
| 设计架构、做方案 | **F** | 现状分析 → 多方案对比 → 对齐术语表 → 设计记录 |
| 安全审计、代码清理 | **B** | 全局扫描 → 问题分级（P0/P1/P2）→ 报告 |
| 琐碎问答、读文件 | **A** | 自由执行（涉及写操作自动升级到对应路径） |

### 多方法学动态激活

不同项目类型和开发阶段，自动激活不同方法学：

| 阶段 | TDD | BDD | DDD | 完整验证 | 适用场景 |
|------|-----|-----|-----|---------|---------|
| **toolkit** | active | off | passive | passive | 库/CLI/工具项目 |
| **prototype** | passive | off | passive | off | 快速验证想法 |
| **mvp** | active | passive | active | passive | 第一个可用版本 |
| **production** | active | active | active | active | 用户在生产环境使用 |
| **maintenance** | active | passive | passive | passive | 稳定运行，修 bug 为主 |

- **手动覆盖**：随时说"激活/关闭 + 方法学名"切换
- **自动建议**：检测到复杂度信号（跨模块增长、行为回归）时提示升级
- **状态感知**：assess/classify 阶段全部关闭，plan 恢复，done 清空

### 工具编排（防冲突）

- **串行锁**：plan 状态工具按 `grill-with-docs → ddd-tenets → bdd-acceptance` 顺序执行
- **回退上限**：implement↔review 循环最多 3 次，超限暂停汇报
- **职责分离**：DDD 负责类型分类（每实体一次），TDD 负责行为验证（每步骤一次）
- **领域优先**：hard rule > 执行流程的"继续"

### 错误分级

| 类型 | 例子 | 行为 |
|------|------|------|
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
更新：`git pull` 后重跑 `bash install.sh`。

## 在项目中使用

```bash
cd /你的项目
langgraph-cli init --deep
```

然后用 Claude Code 打开项目。AI 读到 `.langgraph/` 后自动激活路由门控和方法学动态匹配。

无 `.langgraph/` 的项目不受任何影响——AI 按默认行为工作。

## 架构

```
收到任务
  ├─ 智能接管（五维感知 → Takeover Card）
  ├─ 方法学激活（phase + complexity → Methodology Card）
  ├─ 路径分类（关键词 → A/B/C/D/E/F）
  ├─ 状态机执行
  │   assess → classify → plan → execute → verify → done
  │   每个状态有 {允许, 禁止, 工具, 产出}
  └─ 记忆持久化（OMEGA + state.json）
```

### 组件栈

```
┌──────────────────────────────────────┐
│   AI Workflow Kit（流程编排 + 方法学激活） │
├──────────────────────────────────────┤
│   oh-my-claude（纪律 + agents）         │
├──────────────────────────────────────┤
│   Matt Pocock skills（grill/tdd/diagnose）│
├──────────────────────────────────────┤
│   OMEGA（长期记忆）+ GitNexus（代码图谱）  │
└──────────────────────────────────────┘
```

### 集成的外部工具

| 工具 | 来源 | 安装方式 |
|------|------|---------|
| langgraph-cli | 本项目 | `install.sh` 拷贝到 `~/.local/bin/` |
| Matt Pocock skills (grill-with-docs, tdd, diagnose, grill-me 等) | [github.com/mattpocock/skills](https://github.com/mattpocock/skills) | `npx skills add` → `~/.claude/skills/` |
| GitNexus | [npm: gitnexus](https://www.npmjs.com/package/gitnexus) | `npm install -g gitnexus` |
| OMEGA | [pypi: omega-memory](https://pypi.org/project/omega-memory/) | `pip install omega-memory[server]` |
| oh-my-claude | Claude Code 插件市场 | `/plugin install oh-my-claude@oh-my-claude` |

所有外部工具安装到全局（`~/.claude/`、`~/.local/`），不污染项目目录。

## 配置

### 工作流 spec（`.langgraph/specs/`）

| 文件 | 职责 |
|------|------|
| `task-router.yaml` | 通用路由 + 工具库（25+ 工具） + 状态机定义 |
| `intelligent-takeover.yaml` | 五维感知协议 + 热/温/冷恢复 |
| `methodology-activation.yaml` | 方法学定义 + 6 阶段激活矩阵 + 复杂度信号 |
| `code-implementation.yaml` | 路径 D：plan(串行锁)→implement(TDD+DDD)→review(BDD验收) |
| `design-planning.yaml` | 路径 F：多方案对比 + DDD 领域建模 |
| `diagnose.yaml` | 路径 E：诊断闭环 |
| `platform-operation.yaml` | 路径 C：preflight→execute→analyze 循环 |
| `ops-analysis.yaml` | 路径 B：P0/P1/P2 审计 |

### 多 Agent 工作流（`.langgraph/workflows/`）

```bash
langgraph-cli run .langgraph/workflows/add-feature.yaml    # 设计→实现→测试
langgraph-cli run .langgraph/workflows/fix-bug.yaml        # 分析→修复→审查
langgraph-cli run .langgraph/workflows/api-batch.yaml      # 计划→验证→执行→记录
langgraph-cli run .langgraph/workflows/code-review.yaml    # 并行安全+质量审查
```

### 方法学激活自定义

默认激活级别适配大多数场景。如需自定义，编辑 `methodology-activation.yaml` 的 `phases` 部分，或在开发时手动切换。

### 项目状态描述符（`.langgraph/state.json`）

```json
{
  "active_task": "当前任务描述",
  "task_stack": ["未完成任务列表"],
  "current_path": "D",
  "current_state": "execute",
  "phase": "toolkit",
  "methodology_state": {
    "tdd": "active", "bdd": "off", "ddd": "passive", "verify_full": "passive"
  },
  "last_updated": "ISO8601"
}
```

热恢复时恢复 `task_stack` 和 `current_path`，`phase` 和 `methodology_state` 每次会话重新评估。

## 命令

```bash
langgraph-cli init [--deep]           # 项目接入
langgraph-cli analyze .               # 项目结构分析
langgraph-cli review <文件>           # 代码安全+质量审查
langgraph-cli run workflow.yaml       # YAML 多 agent 工作流
langgraph-cli model                   # 领域模型管理
langgraph-cli pr                      # PR 描述生成
langgraph-cli remember "决策"         # 长期记忆
langgraph-cli recall "关键词"         # 记忆检索
langgraph-cli health                  # 组件健康检查
```

## 测试

```bash
python3 tests/validate-specs.py                       # spec 交叉引用校验（9 类）
python3 tests/e2e/test-methodology-integration.py     # 方法学集成仿真（13 场景）
python3 tests/e2e/test-dynamic-activation.py          # 动态激活仿真（10 场景）
```

## 文档

| 文档 | 内容 |
|------|------|
| [CLAUDE.md](CLAUDE.md) | AI 入口协议 |
| [.langgraph/CLAUDE.md](.langgraph/CLAUDE.md) | 执行协议 + 方法学速查 |
| [docs/TOOL-LAYERING.md](docs/TOOL-LAYERING.md) | 工具分配 + 去重规则 |
| [docs/COEXISTENCE.md](docs/COEXISTENCE.md) | 多系统共存 + 优先级 |
| [docs/adr/001-multi-methodology-progressive-disclosure.md](docs/adr/001-multi-methodology-progressive-disclosure.md) | ADR：架构决策记录 |
| [docs/LESSONS-LEARNED.md](docs/LESSONS-LEARNED.md) | 踩坑全记录：14 个已验证的架构/实现陷阱 |

## 许可证

MIT
