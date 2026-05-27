#!/usr/bin/env python3
"""
E2E 仿真测试：BDD/DDD 方法学集成
模拟不同项目类型、生命周期阶段、用户场景的完整状态机流转。
"""

import os
import sys
import yaml
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional
from enum import Enum

# ── 加载 spec ──
SPEC_DIR = Path(__file__).parent.parent.parent / ".langgraph" / "specs"

def load_spec(name):
    path = SPEC_DIR / f"{name}.yaml"
    if not path.exists():
        return None
    with open(path) as f:
        return yaml.safe_load(f)

TASK_ROUTER = load_spec("task-router")
CODE_IMPL = load_spec("code-implementation")
DESIGN_PLAN = load_spec("design-planning")
DIAGNOSE = load_spec("diagnose")
OPS_ANALYSIS = load_spec("ops-analysis")
PLATFORM_OP = load_spec("platform-operation")

TOOL_LIBRARY = TASK_ROUTER["tool_library"]
CONTEXT_ASSESSMENT = TASK_ROUTER["context_assessment"]
STATES = TASK_ROUTER["states"]


# ═══════════════════════════════════════════
# 仿真模型
# ═══════════════════════════════════════════

class Lifecycle(Enum):
    NEWBORN = "newborn"
    GROWING = "growing"
    MATURE = "mature"

class Activity(Enum):
    ACTIVE = "active"
    IDLE = "idle"
    DORMANT = "dormant"

class Integrity(Enum):
    CLEAN = "clean"
    DIRTY = "dirty"
    BROKEN = "broken"

class Recovery(Enum):
    HOT = "hot"
    WARM = "warm"
    COLD = "cold"

class Health(Enum):
    FULL = "full"
    DEGRADED = "degraded"
    BROKEN = "broken"

@dataclass
class ProjectState:
    lifecycle: Lifecycle = Lifecycle.NEWBORN
    activity: Activity = Activity.ACTIVE
    integrity: Integrity = Integrity.CLEAN
    recovery: Recovery = Recovery.COLD
    health: Health = Health.FULL
    file_count: int = 0
    has_context_md: bool = False
    has_adr: bool = False
    has_handoff: bool = False
    has_omega_context: bool = False
    has_state_json: bool = False
    has_feature_files: bool = False
    has_model_md: bool = False
    new_entity_count: int = 0
    last_commit_days: int = 30
    has_dirty_workspace: bool = False
    domain_terms: list = field(default_factory=list)
    active_task: Optional[str] = None
    current_path: Optional[str] = None
    current_state: Optional[str] = None

    @property
    def mode(self):
        if self.has_handoff or self.has_omega_context:
            return "midstream"
        if self.has_context_md or self.has_adr:
            return "brownfield_docs"
        if self.file_count >= 10:
            return "brownfield_nodocs"
        return "greenfield"


@dataclass
class SimulationResult:
    scenario: str
    path_classified: str
    mode_detected: str
    tools_triggered: list = field(default_factory=list)
    tools_skipped: list = field(default_factory=list)
    deconflict_decisions: list = field(default_factory=list)
    state_transitions: list = field(default_factory=list)
    violations: list = field(default_factory=list)
    errors: list = field(default_factory=list)
    passed: bool = True


# ═══════════════════════════════════════════
# 仿真引擎
# ═══════════════════════════════════════════

class SimulationEngine:
    def __init__(self):
        self.tool_library = TOOL_LIBRARY
        self.context_assessment = CONTEXT_ASSESSMENT
        self.states = STATES

    def assess_project(self, proj: ProjectState):
        mode = proj.mode
        takeover = self._simulate_takeover(proj)
        return mode, takeover

    def _simulate_takeover(self, proj: ProjectState):
        if proj.file_count == 0:
            proj.lifecycle = Lifecycle.NEWBORN
        elif proj.file_count < 200:
            proj.lifecycle = Lifecycle.GROWING
        else:
            proj.lifecycle = Lifecycle.MATURE

        if proj.last_commit_days < 2 or proj.has_dirty_workspace:
            proj.activity = Activity.ACTIVE
        elif proj.last_commit_days < 14:
            proj.activity = Activity.IDLE
        else:
            proj.activity = Activity.DORMANT

        if proj.has_dirty_workspace:
            proj.integrity = Integrity.DIRTY
        else:
            proj.integrity = Integrity.CLEAN

        if proj.has_state_json and proj.activity == Activity.ACTIVE:
            proj.recovery = Recovery.HOT
        elif proj.has_omega_context or proj.has_handoff:
            proj.recovery = Recovery.WARM
        else:
            proj.recovery = Recovery.COLD

        return {
            "lifecycle": proj.lifecycle.value,
            "activity": proj.activity.value,
            "integrity": proj.integrity.value,
            "recovery": proj.recovery.value,
            "health": proj.health.value,
        }

    def classify(self, user_input: str, proj: ProjectState):
        patterns = {
            "C": ["提交", "同步", "标记", "API", "批量", "batch", "PATCH", "/check", "挖掘", "升阶",
                   "upgrade", "favorite", "星标", "submit", "simulate"],
            "D": ["实现", "开发", "新功能", "重构", "写代码", "添加模块", "加功能", "写库",
                  "脚本", "添加", "修改代码"],
            "E": ["bug", "报错", "不工作", "修复", "调试", "诊断", "error", "异常", "性能"],
            "F": ["设计", "架构", "方案", "规划", "怎么实现", "技术选型"],
            "B": ["审计", "扫描", "清理", "安全审查", "冗余", "代码质量", "依赖检查", "项目健康"],
        }
        for path, keywords in patterns.items():
            for kw in keywords:
                if kw in user_input:
                    return path
        return "A"

    def evaluate_tool_trigger(self, tool_name: str, path: str, state: str,
                               proj: ProjectState, user_input: str = ""):
        if tool_name not in self.tool_library:
            return {"triggered": None, "reason": f"工具 {tool_name} 不存在"}

        tool = self.tool_library[tool_name]
        trigger = tool.get("trigger", {})
        must = trigger.get("must", "")
        skip = trigger.get("skip", "")

        must_conditions = [c.strip() for c in must.split("|")]
        skip_conditions = [c.strip() for c in skip.split("|")]

        # ── 特殊：grill-with-docs 在 greenfield 模式强制触发 ──
        if tool_name == "grill-with-docs" and proj.mode == "greenfield":
            return {"triggered": True, "reason": "must: greenfield 强制触发 (context_assessment)"}

        # 评估跳过条件
        for cond in skip_conditions:
            if self._match_condition(cond, path, state, proj, user_input):
                return {"triggered": False, "reason": f"skip: {cond}"}

        # 评估必须条件
        for cond in must_conditions:
            if self._match_condition(cond, path, state, proj, user_input):
                return {"triggered": True, "reason": f"must: {cond}"}

        return {"triggered": False, "reason": "no must condition matched"}

    def _match_condition(self, cond: str, path: str, state: str,
                          proj: ProjectState, user_input: str):
        """逐条条件评估。条件可能包含 AND 语义（如 "路径 D plan 完成"）。"""
        cond_lower = cond.lower()

        # ── 路径限定符（负向优先：条件指定路径但当前不在该路径 → False）──
        path_prefixes = {
            "路径 d": "D", "路径 f": "F", "路径 e": "E", "路径 c": "C", "路径 b": "B",
        }
        for prefix, required_path in path_prefixes.items():
            if prefix in cond_lower:
                if path != required_path:
                    return False
                # 路径匹配成功，继续检查条件其余部分
                remaining = cond_lower.split(prefix, 1)[1].strip()
                if not remaining:
                    return True  # 仅路径条件，已匹配
                # 递归评估剩余子条件（如 "plan 完成"）
                return self._match_condition(remaining, path, state, proj, user_input)

        # ── 状态条件 ──
        if "plan 完成" in cond_lower:
            return state in ("plan", "review", "verify", "done")
        if "review 状态" in cond_lower:
            return state == "review"
        if "design 完成" in cond_lower and path == "F":
            return state in ("plan", "review", "verify", "done")
        if cond_lower == "design" or cond_lower == "设计阶段":
            return state == "plan" and path == "F"
        if "plan 阶段" in cond_lower:
            return state == "plan"
        if "implement 中" in cond_lower:
            return state == "execute"

        # ── 项目上下文 ──
        if "无 .feature 文件" in cond_lower:
            return not proj.has_feature_files
        if "bdd-acceptance 生成了" in cond_lower or ".feature 文件" in cond_lower:
            return proj.has_feature_files

        # ── 功能范围 ──
        if "新功能涉及用户可见行为" in cond:
            return any(kw in user_input for kw in ["新功能", "添加", "实现", "功能模块"])
        if "跨模块交互" in cond:
            return proj.file_count >= 20
        if "纯内部重构" in cond:
            return "重构" in user_input and "新功能" not in user_input and "添加" not in user_input

        # ── 领域概念 ──
        if "新领域概念" in cond and "≥3" in cond:
            return proj.new_entity_count >= 3
        if "无新领域概念" in cond:
            return proj.new_entity_count == 0
        if "纯 crud" in cond_lower:
            return "crud" in user_input.lower() or "增删改查" in user_input

        # ── 项目类型 ──
        if "brownfield" in cond_lower and "首次建立领域模型" in cond:
            return proj.mode == "brownfield_nodocs"
        if "greenfield" in cond_lower:
            return proj.mode == "greenfield"

        # ── 文档 ──
        if "context.md 或" in cond_lower or ("context.md" in cond_lower and "adr" in cond_lower):
            return proj.has_context_md or proj.has_adr
        if "context.md" in cond_lower and "更新" in cond_lower:
            return proj.has_context_md
        if "context.md" in cond_lower and "存在" in cond_lower:
            return proj.has_context_md

        # ── 需求变更 ──
        if "需求变了" in cond or "改成" in cond:
            return any(kw in user_input for kw in ["改成", "需求变", "改一下"])
        if "与已有 spec 冲突" in cond or "spec 冲突" in cond:
            return state == "plan" and "冲突" in user_input
        if "行为与 spec 偏离" in cond or "spec 偏离" in cond:
            return state == "execute" and "需求" in user_input

        # ── 用户关键词 ──
        if "用户说" in cond:
            keyword = cond.split("用户说")[1].strip().strip("'\"")
            return keyword in user_input

        # ── 用户报错 ──
        if "用户报" in cond or "报错" in cond:
            bug_kw = ["bug", "error", "报错", "异常", "报", "错误", "不工作", "修复"]
            return any(kw in user_input for kw in bug_kw)
        if "性能" in cond:
            return "性能" in user_input or "慢" in user_input

        # ── 任务类型 ──
        if "新功能实现" in cond or "新功能" in cond:
            return any(kw in user_input for kw in ["新功能", "添加", "实现", "开发"])
        if "非琐碎 bugfix" in cond:
            return path == "E"
        if "纯配置修改" in cond:
            return "配置" in user_input

        # ── 文件范围 ──
        if "单文件修改" in cond:
            return proj.file_count < 5
        if "跨文件修改" in cond and "≥3" in cond:
            return proj.file_count >= 15
        if "配置修改" in cond or "文档更新" in cond:
            return "配置" in user_input or "文档" in user_input

        return False

    def evaluate_deconflict(self, tool_a: str, tool_b: str):
        if tool_a not in self.tool_library or tool_b not in self.tool_library:
            return None
        deconflict_a = self.tool_library[tool_a].get("deconflict", {})
        deconflict_b = self.tool_library[tool_b].get("deconflict", {})
        for key, rule in deconflict_a.items():
            if tool_b in key or tool_b.replace("-", "_") in key:
                return {"type": "resolved", "rule": rule, "source": tool_a}
        for key, rule in deconflict_b.items():
            if tool_a in key or tool_a.replace("-", "_") in key:
                return {"type": "resolved", "rule": rule, "source": tool_b}
        return {"type": "no_conflict_declared"}

    def get_path_tools(self, path: str, state: str):
        path_specs = {"D": CODE_IMPL, "F": DESIGN_PLAN, "E": DIAGNOSE,
                       "B": OPS_ANALYSIS, "C": PLATFORM_OP}
        spec = path_specs.get(path)
        if not spec:
            return []
        return spec.get("states", {}).get(state, {}).get("tools_from_library", [])


# ═══════════════════════════════════════════
# 测试辅助
# ═══════════════════════════════════════════

engine = SimulationEngine()
all_results = []

def test(name):
    class _Ctx:
        def __init__(self):
            self.result = SimulationResult(scenario=name, path_classified="?", mode_detected="?")
        def __enter__(self): return self
        def __exit__(self, *a): all_results.append(self.result)
    return _Ctx()

def assert_true(cond, msg, result: SimulationResult):
    if cond:
        result.tools_triggered.append(f"✓ {msg}")
    else:
        result.errors.append(f"✗ {msg}")
        result.passed = False

def assert_false(cond, msg, result: SimulationResult):
    if not cond:
        result.tools_skipped.append(f"✓ {msg}")
    else:
        result.errors.append(f"✗ {msg} (应跳过但触发了)")
        result.passed = False


# ═══════════════════════════════════════════
# 场景 1: Greenfield 新功能开发 (路径 D)
# ═══════════════════════════════════════════
with test("Greenfield 新功能开发 (路径 D)") as t:
    r = t.result
    proj = ProjectState(file_count=5, has_context_md=False, has_adr=False,
                        new_entity_count=3)
    mode, takeover = engine.assess_project(proj)
    r.mode_detected = mode
    assert_true(mode == "greenfield", "检测为 greenfield", r)

    user_input = "开发用户登录功能"
    path = engine.classify(user_input, proj)
    r.path_classified = path
    assert_true(path == "D", f"分类为路径 D (实际: {path})", r)

    # greenfield 强制触发 grill-with-docs
    trigger = engine.evaluate_tool_trigger("grill-with-docs", path, "plan", proj, user_input)
    assert_true(trigger["triggered"], f"grill-with-docs 触发(greenfield强制): {trigger['reason']}", r)

    # bdd-acceptance: 路径 D plan 完成 → 触发
    trigger = engine.evaluate_tool_trigger("bdd-acceptance", path, "plan", proj, user_input)
    assert_true(trigger["triggered"], f"bdd-acceptance 触发: {trigger['reason']}", r)

    # ddd-tenets: ≥3 新实体 → 触发
    trigger = engine.evaluate_tool_trigger("ddd-tenets", path, "plan", proj, user_input)
    assert_true(trigger["triggered"], f"ddd-tenets 触发 (≥3 新实体): {trigger['reason']}", r)

    # implement: ddd-tenets 自检
    trigger = engine.evaluate_tool_trigger("ddd-tenets", path, "execute", proj, user_input)
    assert_true(trigger["triggered"], f"ddd-tenets implement 自检: {trigger['reason']}", r)

    # review: 模拟 feature 已生成
    proj.has_feature_files = True
    trigger = engine.evaluate_tool_trigger("bdd-evaluate", path, "review", proj, user_input)
    assert_true(trigger["triggered"], f"bdd-evaluate 触发: {trigger['reason']}", r)

    # deconflict
    d = engine.evaluate_deconflict("grill-with-docs", "ddd-tenets")
    assert_true(d and d["type"] == "resolved", f"grill-with-docs vs ddd-tenets: {d.get('rule', '') if d else 'N/A'}", r)
    d = engine.evaluate_deconflict("verify", "bdd-evaluate")
    assert_true(d and d["type"] == "resolved", f"verify vs bdd-evaluate: {d.get('rule', '') if d else 'N/A'}", r)


# ═══════════════════════════════════════════
# 场景 2: Brownfield 内部重构 (路径 D)
# ═══════════════════════════════════════════
with test("Brownfield 内部重构 (路径 D)") as t:
    r = t.result
    proj = ProjectState(file_count=80, has_context_md=True, has_adr=True,
                        last_commit_days=1, new_entity_count=0)
    mode, _ = engine.assess_project(proj)
    r.mode_detected = mode
    assert_true(mode == "brownfield_docs", f"检测为 brownfield_docs (实际: {mode})", r)

    user_input = "重构用户模块内部数据结构"
    path = engine.classify(user_input, proj)
    r.path_classified = path
    assert_true(path == "D", "分类为路径 D", r)

    # grill-with-docs: CONTEXT.md 存在 → 对齐检查
    trigger = engine.evaluate_tool_trigger("grill-with-docs", path, "plan", proj, user_input)
    assert_true(trigger["triggered"], f"grill-with-docs 触发(对齐检查): {trigger['reason']}", r)

    # bdd-acceptance: 纯内部重构 → 跳过
    trigger = engine.evaluate_tool_trigger("bdd-acceptance", path, "plan", proj, user_input)
    assert_false(trigger["triggered"], f"bdd-acceptance 跳过(内部重构无行为变更): {trigger['reason']}", r)

    # ddd-tenets: 无新实体 → 跳过
    trigger = engine.evaluate_tool_trigger("ddd-tenets", path, "plan", proj, user_input)
    assert_false(trigger["triggered"], f"ddd-tenets 跳过(无新领域概念): {trigger['reason']}", r)

    # bdd-evaluate: 无 feature → 跳过
    trigger = engine.evaluate_tool_trigger("bdd-evaluate", path, "review", proj, user_input)
    assert_false(trigger["triggered"], f"bdd-evaluate 跳过(无 .feature): {trigger['reason']}", r)


# ═══════════════════════════════════════════
# 场景 3: Brownfield 领域架构设计 (路径 F)
# ═══════════════════════════════════════════
with test("Brownfield 领域架构设计 (路径 F)") as t:
    r = t.result
    proj = ProjectState(file_count=150, has_context_md=True, has_adr=True,
                        last_commit_days=3, new_entity_count=5)
    mode, _ = engine.assess_project(proj)
    r.mode_detected = mode
    assert_true(mode == "brownfield_docs", "检测为 brownfield_docs", r)

    user_input = "设计订单系统的领域架构"
    path = engine.classify(user_input, proj)
    r.path_classified = path
    assert_true(path == "F", f"分类为路径 F (实际: {path})", r)

    # ddd-tenets: 路径 F 设计阶段 → 触发
    trigger = engine.evaluate_tool_trigger("ddd-tenets", path, "plan", proj, user_input)
    assert_true(trigger["triggered"], f"ddd-tenets 触发(设计阶段): {trigger['reason']}", r)

    # ddd-model: design 完成 → 触发
    trigger = engine.evaluate_tool_trigger("ddd-model", path, "plan", proj, user_input)
    assert_true(trigger["triggered"], f"ddd-model 触发: {trigger['reason']}", r)

    # bdd-acceptance: 非路径 D → 不触发
    trigger = engine.evaluate_tool_trigger("bdd-acceptance", path, "plan", proj, user_input)
    assert_false(trigger["triggered"], f"bdd-acceptance 不触发(非路径 D): {trigger['reason']}", r)

    # 验证路径 F 工具列表
    tools = engine.get_path_tools("F", "plan")
    assert_true("ddd-tenets" in tools, "ddd-tenets 在路径 F plan 工具列表", r)
    assert_true("ddd-model" in tools, "ddd-model 在路径 F plan 工具列表", r)


# ═══════════════════════════════════════════
# 场景 4: Bug 修复 (路径 E) — BDD/DDD 不触发
# ═══════════════════════════════════════════
with test("Bug 修复 (路径 E) - BDD/DDD 不触发") as t:
    r = t.result
    proj = ProjectState(file_count=100, has_context_md=True, last_commit_days=1)
    mode, _ = engine.assess_project(proj)
    r.mode_detected = mode

    user_input = "修复用户登录报500错误"
    path = engine.classify(user_input, proj)
    r.path_classified = path
    assert_true(path == "E", f"分类为路径 E (实际: {path})", r)

    # BDD/DDD 都不应触发
    for tool_name in ["bdd-acceptance", "bdd-evaluate", "ddd-tenets", "ddd-model"]:
        trigger = engine.evaluate_tool_trigger(tool_name, path, "plan", proj, user_input)
        assert_false(trigger["triggered"], f"{tool_name} 不触发(非 D/F): {trigger['reason']}", r)

    # diagnose 应触发
    trigger = engine.evaluate_tool_trigger("diagnose", path, "plan", proj, user_input)
    assert_true(trigger["triggered"], f"diagnose 触发: {trigger['reason']}", r)

    # bdd-reconcile: 非需求变更场景
    trigger = engine.evaluate_tool_trigger("bdd-reconcile", path, "plan", proj, user_input)
    assert_false(trigger["triggered"], f"bdd-reconcile 不触发(非变更): {trigger['reason']}", r)


# ═══════════════════════════════════════════
# 场景 5: 需求变更级联 (bdd-reconcile)
# ═══════════════════════════════════════════
with test("需求变更级联 (bdd-reconcile)") as t:
    r = t.result
    proj = ProjectState(file_count=80, has_context_md=True, has_feature_files=True)
    mode, _ = engine.assess_project(proj)
    r.mode_detected = mode

    # implement 中途需求变更（需要同时命中路径 D + 需求变更关键词）
    user_input = "开发用户模块需求改成也支持手机号登录"
    path = engine.classify(user_input, proj)
    r.path_classified = path
    assert_true(path == "D", f"分类为路径 D (实际: {path})", r)
    trigger = engine.evaluate_tool_trigger("bdd-reconcile", path, "execute", proj, user_input)
    assert_true(trigger["triggered"], f"bdd-reconcile 触发(implement 变更): {trigger['reason']}", r)

    # plan 阶段 spec 冲突
    user_input2 = "这个方案与已有的支付 spec 冲突，改一下设计"
    trigger2 = engine.evaluate_tool_trigger("bdd-reconcile", "D", "plan", proj, user_input2)
    assert_true(trigger2["triggered"], f"bdd-reconcile 触发(plan spec 冲突): {trigger2['reason']}", r)


# ═══════════════════════════════════════════
# 场景 6: Midstream 热恢复
# ═══════════════════════════════════════════
with test("Midstream 热恢复 (hot recovery)") as t:
    r = t.result
    proj = ProjectState(file_count=100, has_state_json=True, last_commit_days=0,
                        has_dirty_workspace=True, active_task="gross_profitability_batch",
                        current_path="C", current_state="execute", has_omega_context=True)
    mode, takeover = engine.assess_project(proj)
    r.mode_detected = mode
    assert_true(mode == "midstream", f"检测为 midstream (实际: {mode})", r)
    assert_true(takeover["recovery"] == "hot", f"hot recovery (实际: {takeover['recovery']})", r)
    assert_true(takeover["activity"] == "active", "activity=active", r)
    assert_true(takeover["integrity"] == "dirty", "integrity=dirty", r)


# ═══════════════════════════════════════════
# 场景 7: 运维审计 (路径 B) — BDD/DDD 不触发
# ═══════════════════════════════════════════
with test("运维审计 (路径 B) - BDD/DDD 不触发") as t:
    r = t.result
    proj = ProjectState(file_count=150, has_context_md=True)
    mode, _ = engine.assess_project(proj)
    r.mode_detected = mode

    user_input = "审计项目安全性"
    path = engine.classify(user_input, proj)
    r.path_classified = path
    assert_true(path == "B", f"分类为路径 B (实际: {path})", r)

    for tool_name in ["bdd-acceptance", "bdd-evaluate", "ddd-tenets", "ddd-model"]:
        trigger = engine.evaluate_tool_trigger(tool_name, path, "plan", proj, user_input)
        assert_false(trigger["triggered"], f"{tool_name} 不触发(路径 B): {trigger['reason']}", r)


# ═══════════════════════════════════════════
# 场景 8: Brownfield_nodocs 首次建立领域模型
# ═══════════════════════════════════════════
with test("Brownfield_nodocs 首次建立领域模型") as t:
    r = t.result
    proj = ProjectState(file_count=60, has_context_md=False, has_adr=False,
                        new_entity_count=3)
    mode, _ = engine.assess_project(proj)
    r.mode_detected = mode
    assert_true(mode == "brownfield_nodocs", f"检测为 brownfield_nodocs (实际: {mode})", r)

    user_input = "实现用户支付功能模块"
    path = engine.classify(user_input, proj)
    r.path_classified = path
    assert_true(path == "D", "分类为路径 D", r)

    trigger = engine.evaluate_tool_trigger("ddd-tenets", path, "plan", proj, user_input)
    assert_true(trigger["triggered"], f"ddd-tenets 触发(首次建模): {trigger['reason']}", r)

    trigger = engine.evaluate_tool_trigger("bdd-acceptance", path, "plan", proj, user_input)
    assert_true(trigger["triggered"], f"bdd-acceptance 触发(新功能): {trigger['reason']}", r)


# ═══════════════════════════════════════════
# 场景 9: 琐碎问答 (路径 A) — 不触发任何方法学工具
# ═══════════════════════════════════════════
with test("琐碎问答 (路径 A) - 不触发方法学工具") as t:
    r = t.result
    proj = ProjectState(file_count=80, has_context_md=True)
    mode, _ = engine.assess_project(proj)
    r.mode_detected = mode

    user_input = "这个文件是做什么的"
    path = engine.classify(user_input, proj)
    r.path_classified = path
    assert_true(path == "A", f"分类为路径 A (实际: {path})", r)

    for tool_name in ["bdd-acceptance", "bdd-evaluate", "bdd-reconcile", "ddd-tenets", "ddd-model"]:
        trigger = engine.evaluate_tool_trigger(tool_name, path, "plan", proj, user_input)
        assert_false(trigger["triggered"], f"{tool_name} 不触发(路径 A): {trigger['reason']}", r)


# ═══════════════════════════════════════════
# 场景 10: 纯 CRUD — DDD 跳过
# ═══════════════════════════════════════════
with test("纯 CRUD 场景 - DDD 跳过") as t:
    r = t.result
    proj = ProjectState(file_count=80, has_context_md=True, new_entity_count=0)
    mode, _ = engine.assess_project(proj)
    r.mode_detected = mode

    user_input = "添加一个用户列表的增删改查页面"
    path = engine.classify(user_input, proj)
    r.path_classified = path
    assert_true(path == "D", f"分类为路径 D (实际: {path})", r)

    trigger = engine.evaluate_tool_trigger("ddd-tenets", path, "plan", proj, user_input)
    assert_false(trigger["triggered"], f"ddd-tenets 跳过(纯 CRUD): {trigger['reason']}", r)


# ═══════════════════════════════════════════
# 场景 11: 配置修改 — 方法学工具全部跳过
# ═══════════════════════════════════════════
with test("配置修改 - 方法学工具全部跳过") as t:
    r = t.result
    proj = ProjectState(file_count=100, has_context_md=True)
    mode, _ = engine.assess_project(proj)
    r.mode_detected = mode

    user_input = "修改数据库连接配置"
    path = engine.classify(user_input, proj)
    r.path_classified = path

    for tool_name in ["bdd-acceptance", "tdd"]:
        trigger = engine.evaluate_tool_trigger(tool_name, path, "plan", proj, user_input)
        assert_false(trigger["triggered"], f"{tool_name} 跳过(配置修改): {trigger['reason']}", r)


# ═══════════════════════════════════════════
# 场景 12: 全工具 deconflict 完整性
# ═══════════════════════════════════════════
with test("工具 deconflict 完整性") as t:
    r = t.result
    bdd_ddd_tools = ["bdd-acceptance", "bdd-evaluate", "bdd-reconcile", "ddd-tenets", "ddd-model"]

    for tool_name in bdd_ddd_tools:
        tool = engine.tool_library.get(tool_name)
        assert_true(tool is not None, f"{tool_name} 在工具库", r)
        assert_true("trigger" in tool, f"{tool_name} 有 trigger", r)
        assert_true("protocol" in tool, f"{tool_name} 有 protocol", r)
        assert_true("exit" in tool, f"{tool_name} 有 exit", r)

    # 关键 deconflict 对
    for a, b in [("grill-with-docs", "ddd-tenets"), ("verify", "bdd-evaluate"),
                  ("grill-with-docs", "bdd-acceptance")]:
        d = engine.evaluate_deconflict(a, b)
        assert_true(d and d["type"] != "no_conflict_declared",
                   f"{a} vs {b} 有 deconflict 规则", r)

    d = engine.evaluate_deconflict("bdd-evaluate", "verify")
    assert_true(d and "互补" in str(d.get("rule", "")), "bdd-evaluate vs verify 互补", r)


# ═══════════════════════════════════════════
# 场景 13: 路径 D 完整状态流转 (黄金路径)
# ═══════════════════════════════════════════
with test("路径 D 完整状态流转 (黄金路径)") as t:
    r = t.result
    proj = ProjectState(file_count=80, has_context_md=True, has_adr=True,
                        last_commit_days=1, new_entity_count=4)
    mode, _ = engine.assess_project(proj)
    r.mode_detected = mode
    r.state_transitions.append(("assess", mode))

    user_input = "实现商品推荐功能模块"
    path = engine.classify(user_input, proj)
    r.path_classified = path
    r.state_transitions.append(("classify", path))

    plan_tools = engine.get_path_tools(path, "plan")
    r.state_transitions.append(("plan", plan_tools))
    assert_true("bdd-acceptance" in plan_tools, "plan: bdd-acceptance", r)
    assert_true("ddd-tenets" in plan_tools, "plan: ddd-tenets", r)
    assert_true("grill-with-docs" in plan_tools, "plan: grill-with-docs", r)

    proj.has_feature_files = True
    r.state_transitions.append(("plan_done", ".feature generated"))

    impl_tools = engine.get_path_tools(path, "implement")
    r.state_transitions.append(("implement", impl_tools))
    assert_true("tdd" in impl_tools, "implement: tdd", r)
    assert_true("ddd-tenets" in impl_tools, "implement: ddd-tenets(自检)", r)

    review_tools = engine.get_path_tools(path, "review")
    r.state_transitions.append(("review", review_tools))
    assert_true("bdd-evaluate" in review_tools, "review: bdd-evaluate", r)
    assert_true("langgraph-cli-review" in review_tools, "review: langgraph-cli-review", r)

    verify_tools = engine.states["verify"].get("tools", [])
    r.state_transitions.append(("verify", verify_tools))
    assert_true(any("verify" in str(t) for t in verify_tools), "verify: verify skill", r)

    r.state_transitions.append(("done", "omega_store + summary"))


# ═══════════════════════════════════════════
# 结果报告
# ═══════════════════════════════════════════
def print_report():
    total = len(all_results)
    passed = sum(1 for r in all_results if r.passed)
    failed = total - passed

    print()
    print("=" * 70)
    print(f"  BDD/DDD 方法学集成 E2E 仿真测试报告")
    print(f"  场景: {total} | 通过: {passed} | 失败: {failed}")
    print("=" * 70)

    for r in all_results:
        status = "✅" if r.passed else "❌"
        print(f"\n{status} [{r.scenario}]")
        print(f"   模式: {r.mode_detected} | 路径: {r.path_classified}")
        for t in r.tools_triggered:
            print(f"   {t}")
        for t in r.tools_skipped:
            print(f"   {t}")
        for e in r.errors:
            print(f"   {e}")

    print()
    print("=" * 70)
    if failed == 0:
        print("  全部测试通过 ✓")
    else:
        print(f"  {failed} 个场景失败 ✗")
    print("=" * 70)
    return failed == 0


if __name__ == "__main__":
    success = print_report()
    sys.exit(0 if success else 1)
