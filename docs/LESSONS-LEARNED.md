# Lessons Learned: Building a Multi-Methodology AI Workflow Kit

从 Alpha 研究项目中长出来的通用工作流，v2.0 到 v2.6 全程踩坑记录。
每个问题都是真实撞上的，不是纸面推演。

---

## 零、起源：这不是设计出来的，是长出来的

工作流并非在 `ai-workflow-kit` 仓库中从零设计。它最初在
`/Users/zpdedn/Documents/project/Worldquantbrain` ——一个
WorldQuant BRAIN alpha 研究项目中自然演化。

### v2.0-v2.5：Worldquantbrain 时期（104 次提交）

**痛点驱动**：Alpha 研究有三个刚性需求，通用 AI 编码助手无法满足：
1. **API 操作不可逆**——提交 alpha 后无法撤回，必须有 preflight 验证
2. **领域规则复杂**——alpha 有效性有 20+ 条硬规则（field 类型、sign-flip、数据覆盖率），AI 不知道
3. **长任务跨会话**——batch mining 跑 2 小时，会话断了不知道做到哪

**演化路径**：
```
原始状态: 60+ 脚本, main.py 入口, 无规则
    ↓
第 1 步: 加 AGENTS.md + CLAUDE.md（写规则）
    ↓
第 2 步: 规则太多 → 引入 langgraph-cli skill（路由）
    ↓
第 3 步: 路径 C 最常用 → platform-operation.yaml 优先完善（preflight+错误分级+循环）
    ↓
第 4 步: 需要领域规则 → skill composition 诞生（路径 spec + 领域 skill 并行）
    ↓
第 5 步: 好用 → 提取为 ai-workflow-kit（去 WorldQuant 特定用语，泛化）
```

**关键洞察**：
- **Skill composition 是被发现的，不是被发明的**。路径 C 的 batch 操作需要 platform-operation spec 控制执行流程，但 alpha 的业务规则（"ts_rank 在季度数据上返回 ERROR 是预期行为"）不属于任何通用 spec。两个独立的 skill 并行加载是唯一解。
- **路径 C 最成熟是有原因的**——它最先遇到真实痛点的极限压力（API 限流、不可逆操作、长任务）。路径 D/E/F 后来才跟进。
- **Worldquantbrain 有 6 个 workflow，其中 2 个是自定义的**（batch-check.yaml, sync-account.yaml）——说明通用 workflow 覆盖 80%，但项目特有的 20% 需要自定义。

### v2.5→v2.6：ai-workflow-kit 时期（本仓库）

从 Worldquantbrain 提取后，进行了通用化改造：
- 去掉 WorldQuant 特定用语（decontaminate）
- 加入多方法学（BDD/DDD）
- 加入动态激活（phase + methodology）
- 加入模式门控（greenfield/brownfield）
- 自托管开发（用工作流开发工作流本身）

以下 14 个坑覆盖了从 Worldquantbrain 的原型阶段到 ai-workflow-kit 的通用化阶段。

---

## 一、架构设计

### 1. Trigger 条件永远不该用"项目已有的东西"做门槛

**坑**：`ddd-tenets` 的 trigger 是"≥3 个新实体"，`bdd-acceptance` 是"≥2 个跨模块交互"。但工具的价值恰恰在"还没有这些东西时帮你建立"。空白项目（0 实体 0 模块）→ 全部跳过 → 空白项目永远触发不了设计工具。

**教训**：trigger 条件应该区分"项目状态条件"和"任务类型条件"。状态条件（"有多少实体"）不应该阻塞建立型工具。用模式门控（mode_gated_activation）替代数量门槛。

**发现方式**：用户直觉——"空白项目是不是应该先设计？"

---

### 2. Deconflict 矩阵是文档，串行锁才是执行

**坑**：声明了 18 对 deconflict 规则，期望 AI 在调用工具前逐对检查。但 AI 不会。deconflict 声明的实际效果趋近于零。

**教训**：防止工具冲突的有效方式不是"声明不冲突"，而是"规定谁先谁后"。`grill → ddd → model → bdd` 串行锁的效果远超 18 对 deconflict 声明。deconflict 保留作为文档，但不要依赖它防止冲突。

**发现方式**：自托管开发——写 deconflict 时感觉"这样应该够了"，跑仿真时发现"AI 不会逐对检查"。

---

### 3. Prompt 级约束没有牙齿

**坑**：状态机的 forbid 列表（`forbid: [Bash, Write, Edit]`）只是 YAML 中的文本。AI 读完后可以遵守，也可以不遵守。没有程序级拦截。

**教训**：prompt 级约束对配合的 AI 有效，对不配合的无效。这是架构天花板，不是 bug。补偿机制：
- 事后审计（done 状态对照 forbid 检查实际行为）
- 显式 override 机制（用户有权覆盖，但必须有记录）
- 关键 forbid（如凭据泄露）应该加 pre-commit hook，不靠 prompt

**发现方式**：自托管——"如果 AI 不走 path A 分类，直接写代码，谁能拦住？"

---

### 4. Phase 模型是应用项目视角，不是通用视角

**坑**：prototype/mvp/production/maintenance 四个阶段假设项目是一个"会部署给用户的应用程序"。但工具/库/CLI 项目没有这些阶段——它们永远被分类为 unknown，动态激活退化为静态默认。

**教训**：项目类型分类要先于阶段分类。先问"这是什么类型的项目（toolkit/web app/data pipeline）"，再问"它处于什么阶段"。加 toolkit phase 解决了表象，但 root cause 是 project type ≠ development phase。

**发现方式**：用工作流接管自己——然后发现自己的项目永远是 phase=unknown。

---

### 5. Complexity Signals 定义但从不检查 = 死代码

**坑**：`methodology-activation.yaml` 定义了 5 个 complexity signal（domain_richness、cross_module_growth、behavior_regression、team_scale、phase_transition），trigger condition 写得很详细。但没有任何代码在运行时检查它们。它们是放在 spec 里的文档，不是活的信号。

**教训**：在 spec 中定义信号 ≠ 信号会被检测。每个 signal 必须明确声明"在什么时机由谁检查"。我们补了 `check_on: [接管完成, plan 进入, scope creep]`，把死代码激活了。

**发现方式**：模式扫描——用"定义但从未被引用"的 grep 发现。

---

## 二、多方法学协同

### 6. 新方法学不是"加工具"，是"定义协作"

**坑**：加 BDD 时第一反应是"加 3 个新工具到 tool_library"。但工具加了之后，跟现有工具的交互矩阵是 C(25,2) = 300 对。没人能维护 300 对 deconflict。

**教训**：新方法学接入的正确方式：
1. 定义方法学 bundle（哪些工具属于它）
2. 定义 activate/deactivate 条件（不是 per-tool trigger，是 bundle 级 gate）
3. 定义和其他 bundle 的串行顺序（不是 pairwise deconflict）
4. 只在需要时才激活（渐进式披露）

**发现方式**：加完 BDD+DDD 后测试，发现 bdd-acceptance 在 path F 也触发了。

---

### 7. TDD 和 DDD 不是竞争关系

**坑**：implement 状态同时激活 TDD（"先写最简单的测试"）和 DDD（"先设计聚合根"），两者给出的第一条指令矛盾。AI 不知道该先做哪个。

**教训**：TDD 和 DDD 操作在不同层面——DDD 是"每实体分类一次"，TDD 是"每步骤验证一次"。声明分工：DDD 在新建类型时触发（一次），TDD 在每个功能步骤触发（多次）。不是谁先谁后，是谁做什么。

**发现方式**：用户问"不会左右脑互搏吗"，然后检查 implement 状态的双重约束。

---

### 8. 模式门控 > 方法论激活优先级

**坑**：两个系统同时控制同一件事——mode gate（基于项目模式）和 methodology activation（基于开发阶段）。greenfield 说 DDD=active，prototype 说 DDD=passive。没有优先级声明。

**教训**：当两个自动化系统冲突时，更具体的那个胜出。"项目是空白的"比"项目处于原型阶段"更具体。声明冲突裁决：mode_gate > methodology_activation。

**发现方式**：用户问"修完后会不会整体不稳定"，系统扫描发现两个激活系统的优先级未声明。

---

## 三、实现细节

### 9. YAML 里的中文 + 特殊字符 = 持续踩坑

**坑**：
- `[✓]` 在 flow sequence 内 → YAML 解析器以为是嵌套数组，Ruby Psych 报错
- `"MUST/MUST NOT/禁止/硬性/Do not/Never"` 中的 `"` → 在未引号字符串内提前闭合
- `Edit` 工具对含中文的文件经常匹配失败 → 需要用 sed/Python 绕过
- PyYAML dump 会重新格式化整个文件，丢失手写注释和排列

**教训**：YAML + 中文 + 特殊字符 = 迟早踩坑。对策：
- flow sequence 中的值都用双引号包裹
- 未引号字符串中的 `"` 改用单引号包裹整个值
- 批量编辑含中文的文件优先用 Python 脚本
- 接受 PyYAML dump 的格式化（牺牲可读性换一致性）

**发现方式**：每次测试跑不过都是 YAML 解析器报错。

---

### 10. Spec 交叉引用没有编译期检查

**坑**：takeover v1.0.1 是"四层感知"，升级到 v1.1 加 phase 后变成五层。但 task-router.yaml 里还在说"四层感知"，SKILL.md 缺 Layer 5 文档。没有机制自动发现这种不一致。

**教训**：spec 之间的引用（extends、layer count、field name、phase enum）必须可以自动校验。写了 `validate-specs.py` 做 9 类检查。但这只是脚本，需要集成到 CI。

**发现方式**：自托管——读 takeover spec 发现五层，读 task-router 发现四层，对不上。

---

### 11. state.json 热恢复会加载过时数据

**坑**：state.json 里的 phase 和 methodology_state 是上次会话写的。如果项目在两个会话间加了 CI、发了版本，phase 应该从 mvp 变成 production，但热恢复会加载旧的 mvp。

**教训**：热恢复只恢复"任务状态"（task_stack、current_path），不恢复"项目状态"（phase、methodology）。项目状态每次会话重新评估。修复：hot recovery 时 re-evaluate phase + methodology。

**发现方式**：第二轮接管时 state.json 里的 phase=unknown 已经过时。

---

### 12. 串行锁漏项——ddd-model 被 force_active 但不在锁里

**坑**：mode gate 的 greenfield force_active 包含 4 个工具，串行锁只声明了 3 个（grill → ddd-tenets → bdd-acceptance）。ddd-model 没有在锁里，AI 不知道它该在第几个执行。

**教训**：每加一个 force_active 工具，必须同时加两处：串行锁顺序 + 路径 spec 的 tools_from_library。缺一不可。

**发现方式**：用户问"四个工具不会相互抢权限吗"，grep 发现 ddd-model 缺了。

---

## 四、自托管与验证

### 13. E2E 仿真发现的问题比设计审查多

**坑**：设计审查时觉得"trigger 条件写得清楚，deconflict 覆盖全面"。E2E 仿真一跑——bdd-acceptance 在 path F 触发了，YAML 引号导致解析失败，缩进错误让 BDD 工具成为 omega-memory 的子节点。

**教训**：spec 驱动的系统必须有仿真测试。不是"测试通过了所以正确"，而是"测试发现了审查没发现的问题"。23 个 E2E 场景是安全网。

**发现方式**：第一次跑仿真就发现了 6 个失败，全是意想不到的。

---

### 14. 工作流对短任务是过度工程

**坑**：修一个明确的小 bug（已知冲突、已知修复方案）时，走完整 assess→classify→plan→execute→verify 仪式消耗的心力超过修 bug 本身。

**教训**：工作流的价值与任务复杂度成正比。短反馈循环不需要完整仪式。这是设计如此，不是失败——path E（diagnose）明确说了"最小修复，不趁机重构"。

**发现方式**：修冲突时发现自己跳过了状态标记，意识到"跳得好"。

---

### 15. 用户的直觉比代码先发现问题

在整个开发过程中，用户提出的问题命中率 100%（9/9）。代码验证了直觉，而不是直觉验证了代码。

这不是谦虚——说明当前设计有系统性盲区，人脑能感知但代码还没覆盖。保持这种直觉驱动的审视是工作流持续改进的最重要机制。

---

## 五、什么做对了

| 决策 | 为什么对 |
|------|---------|
| 渐进式披露（按 phase 激活方法学） | 原型不加载 BDD，工具项目关闭 BDD——减少噪音，AI 专注 |
| 串行锁替代 deconflict 矩阵 | 顺序锁定简单可靠，deconflict 声明对 AI 无效 |
| 模式门控（mode_gated_activation） | 覆盖 trigger 条件中的数量门槛，工具在需要时触发 |
| 自托管开发（用工作流开发工作流） | 发现 9 个问题修了 8 个，比任何外部测试有效 |
| E2E 仿真测试套件 | 3 套 23 场景，发现 YAML bug 和 trigger 逻辑错误 |
| spec 交叉引用自动校验 | 防止文档与 spec 之间漂移 |

## 六、仍然痛的地方

| 痛点 | 为什么修不好 |
|------|------------|
| prompt 级约束无强制力 | 需要程序级 hook，超出当前架构 |
| 20K token 协议税 | 需要按需注入 spec 文本，是下一层重构 |
| phase 检测依赖文件结构信号 | 对某些项目类型（数据管道、嵌入式）不敏感 |
| 复杂度税——新人上手慢 | 需要简化版安装流程，目前只有全量安装 |
| spec 衰退——随时间过时 | 需要 CI 集成 validate-specs.py |

---

## 七、v2.7 起点

基于以上所有教训，v2.7 的核心命题：

**从 prompt 级自律升级到工具级强制**

具体方向：
1. pre-commit hook 检查 forbid 违规
2. CI 集成 validate-specs.py（spec 漂移自动报警）
3. 按 methodlology 级别真正按需注入 spec 文本（off = 不注入上下文）
4. 简化安装——区分"快速开始"和"完整部署"
