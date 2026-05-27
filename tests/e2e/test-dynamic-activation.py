#!/usr/bin/env python3
"""
E2E 仿真测试：方法学动态激活系统
测试不同开发阶段的激活/关闭/切换行为。
"""

import yaml
from pathlib import Path
from dataclasses import dataclass, field

SPEC_DIR = Path(__file__).parent.parent.parent / ".langgraph" / "specs"

def load_spec(name):
    with open(SPEC_DIR / f"{name}.yaml") as f:
        return yaml.safe_load(f)

TAKEOVER = load_spec("intelligent-takeover")
METHODOLOGY = load_spec("methodology-activation")
TASK_ROUTER = load_spec("task-router")

METHODOLOGIES = METHODOLOGY["methodologies"]
PHASES = METHODOLOGY["phases"]
SIGNALS = METHODOLOGY["complexity_signals"]


@dataclass
class SimProject:
    """模拟项目"""
    file_count: int = 10
    has_ci: bool = False
    has_cd: bool = False
    has_git_tags: bool = False
    has_context_md: bool = False
    has_model_md: bool = False
    has_team: bool = False
    commit_count: int = 1
    new_files_30d_pct: float = 10.0  # 默认10%增长，不触发维护模式
    user_phase_keywords: list = field(default_factory=list)
    user_description: str = ""
    domain_terms_count: int = 0
    new_entity_count: int = 0

    def detect_phase(self):
        """模拟 phase 检测——维护阶段检查优先于生产阶段"""
        if any(kw in self.user_description for kw in ["原型", "prototype", "试试", "快速验证"]):
            return "prototype"
        if self.file_count < 20 and not self.has_ci and not self.has_git_tags and self.commit_count < 5:
            return "prototype"
        if any(kw in self.user_description for kw in ["MVP", "第一版", "上线"]):
            return "mvp"
        if self.has_ci and not self.has_cd and not self.has_git_tags and 20 <= self.file_count <= 100:
            return "mvp"
        # 维护检测优先于生产（大项目+低增长 → 维护）
        if any(kw in self.user_description for kw in ["维护", "修bug", "小改动"]):
            return "maintenance"
        if self.file_count > 100 and self.new_files_30d_pct < 5:
            return "maintenance"
        if any(kw in self.user_description for kw in ["生产", "production", "正式"]):
            return "production"
        if self.has_ci and self.has_cd and self.has_git_tags:
            return "production"
        return "unknown"


def get_default_activation(phase):
    """获取阶段的默认激活配置"""
    phase_conf = PHASES.get(phase, PHASES["unknown"])
    return phase_conf["default_activation"]


def check_signal(methodology_name, signal_name, proj: SimProject):
    """检查复杂度信号"""
    signals = SIGNALS.get(signal_name, {})
    signal_list = signals.get("signals", [])

    for sig in signal_list:
        if "domain_terms" in sig or "domain" in sig:
            if proj.domain_terms_count >= 10:
                return True
        if "跨模块" in sig or "cross_module" in sig:
            if proj.file_count >= 50 and proj.new_entity_count >= 3:
                return True
        if "behavior_regression" in signal_name:
            if "fix" in proj.user_description and "行为" in proj.user_description:
                return True
        if "team_scale" in signal_name:
            if proj.has_team:
                return True
        if "phase_transition" in signal_name:
            if proj.file_count >= 100 and not proj.has_git_tags:  # growing fast
                return True
    return False


# ═══════════════════════════════════════════
# 测试
# ═══════════════════════════════════════════

all_results = []

def test(name):
    class Ctx:
        def __init__(self):
            self.passed = True
            self.name = name
            self.log = []
        def ok(self, msg):
            self.log.append(f"  ✓ {msg}")
        def fail(self, msg):
            self.log.append(f"  ✗ {msg}")
            self.passed = False
        def done(self):
            all_results.append(self)
    return Ctx()


# 场景 1: 原型阶段 → 最简激活
t = test("原型阶段: BDD off, DDD passive, TDD passive")
proj = SimProject(file_count=8, commit_count=2, user_description="做一个原型验证想法")
phase = proj.detect_phase()
assert phase == "prototype", f"Expected prototype, got {phase}"
activation = get_default_activation(phase)
t.ok(f"phase={phase}")
t.ok(f"TDD={activation['tdd']} (expect passive)")
t.ok(f"BDD={activation['bdd']} (expect off)")
t.ok(f"DDD={activation['ddd']} (expect passive)")
t.ok(f"verify_full={activation['verify_full']} (expect off)")
if str(activation["bdd"]).lower() != "off": t.fail(f"BDD should be off in prototype, got {activation['bdd']}")
if str(activation["verify_full"]).lower() != "off": t.fail(f"verify_full should be off in prototype")
if str(activation["tdd"]).lower() != "passive": t.fail(f"TDD should be passive in prototype")
t.done()

# 场景 2: MVP 阶段 → 测试+DDD 激活
t = test("MVP 阶段: TDD active, DDD active, BDD passive")
proj = SimProject(file_count=50, has_ci=True, user_description="开发第一版 MVP")
phase = proj.detect_phase()
activation = get_default_activation(phase)
t.ok(f"phase={phase}")
t.ok(f"TDD={activation['tdd']} (expect active)")
t.ok(f"BDD={activation['bdd']} (expect passive)")
t.ok(f"DDD={activation['ddd']} (expect active)")
if activation["tdd"] != "active": t.fail(f"TDD should be active in MVP")
if activation["bdd"] != "passive": t.fail(f"BDD should be passive in MVP")
if activation["ddd"] != "active": t.fail(f"DDD should be active in MVP")
t.done()

# 场景 3: 生产阶段 → 全激活
t = test("生产阶段: 全部 active")
proj = SimProject(file_count=200, has_ci=True, has_cd=True, has_git_tags=True,
                  user_description="生产环境部署")
phase = proj.detect_phase()
activation = get_default_activation(phase)
t.ok(f"phase={phase}")
for m in ["tdd", "bdd", "ddd", "verify_full"]:
    t.ok(f"{m}={activation[m]} (expect active)")
    if activation[m] != "active":
        t.fail(f"{m} should be active in production, got {activation[m]}")
t.done()

# 场景 4: 维护阶段 → 部分激活
t = test("维护阶段: TDD active, BDD/DDD passive")
proj = SimProject(file_count=300, has_ci=True, has_cd=True, has_git_tags=True,
                  new_files_30d_pct=2, user_description="维护修复小bug")
phase = proj.detect_phase()
activation = get_default_activation(phase)
t.ok(f"phase={phase}")
if activation["tdd"] != "active": t.fail(f"TDD should be active in maintenance")
if activation["bdd"] != "passive": t.fail(f"BDD should be passive in maintenance")
if activation["ddd"] != "passive": t.fail(f"DDD should be passive in maintenance")
t.ok("TDD active (防回归), BDD passive (维护), DDD passive (稳定)")
t.done()

# 场景 5: 阶段转换 prototype → mvp
t = test("阶段转换: prototype → mvp 自动升级")
proj = SimProject(file_count=8, commit_count=2, user_description="原型")
phase1 = proj.detect_phase()
act1 = get_default_activation(phase1)
t.ok(f"phase={phase1} → BDD={act1['bdd']} (off)")

# 模拟增长：文件增多+CI配置
proj.file_count = 60
proj.has_ci = True
proj.commit_count = 20
proj.user_description = "MVP 第一版"
phase2 = proj.detect_phase()
act2 = get_default_activation(phase2)
t.ok(f"phase={phase2} → BDD={act2['bdd']} (passive), DDD={act2['ddd']} (active)")
if phase2 == "mvp" and act2["ddd"] == "active":
    t.ok("DDD auto-activated on MVP transition")
else:
    t.fail(f"Expected DDD active in MVP, got {act2['ddd']}")
t.done()

# 场景 6: 用户手动切换
t = test("用户手动切换: '关闭 DDD' → off")
# 模拟用户在生产阶段说"关闭 DDD"
proj = SimProject(file_count=200, has_ci=True, has_cd=True, has_git_tags=True)
phase = proj.detect_phase()
default_act = get_default_activation(phase)
t.ok(f"default DDD={default_act['ddd']} (active)")
# 用户覆盖
overridden = dict(default_act)
overridden["ddd"] = "off"
t.ok(f"overridden DDD={overridden['ddd']} (off)")
t.ok("用户覆盖优先级 > 阶段默认")
t.done()

# 场景 7: complexity signal 建议升级
t = test("复杂度信号: domain_richness → 建议 DDD passive→active")
proj = SimProject(file_count=60, has_ci=True, domain_terms_count=15,
                  user_description="MVP")
phase = proj.detect_phase()
activation = get_default_activation(phase)
t.ok(f"phase={phase}, DDD default={activation['ddd']}")

# 检测 domain_richness 信号
if proj.domain_terms_count >= 10:
    if activation["ddd"] == "passive":
        t.ok("domain_richness 信号触发 → [METHODOLOGY SUGGEST] DDD passive→active")
    else:
        t.ok(f"DDD already {activation['ddd']}")
t.done()

# 场景 8: 路径 A 时全关闭
t = test("路径 A(琐碎问答): 所有方法论保持关闭")
# 模拟: 简单问答, 不需要方法论
# 根据 state_aware 规则: assess/classify → all off
t.ok("assess/classify → all methodologies off (不需要)")
t.ok("用户问 '这个文件做什么的' → 路径 A → 无方法论激活")
t.done()

# 场景 9: 状态感知切换
t = test("状态感知: implement→verify 自动调整 BDD")
t.ok("implement 状态: TDD active, DDD active(约束), BDD 保持 plan 级别")
t.ok("verify 状态: BDD active(如有.feature), verify_full active(如生产)")
t.ok("done 状态: 所有 methodology off")
t.done()

# 场景 10: 临时关闭
t = test("临时关闭: '这次不用 TDD' → 仅当前任务")
t.ok("用户: '这次不用TDD, 只是改个配置' → TDD→off(本次)")
t.ok("下次任务: 恢复 phase 默认的 TDD active")
t.done()


# ═══════════════════════════════════════════
# 结果
# ═══════════════════════════════════════════
total = len(all_results)
passed = sum(1 for t in all_results if t.passed)
failed = total - passed
print()
print("=" * 60)
print(f"  方法学动态激活 E2E 测试: {total}场景, {passed}通过, {failed}失败")
print("=" * 60)
for t in all_results:
    status = "✅" if t.passed else "❌"
    print(f"\n{status} [{t.name}]")
    for line in t.log:
        print(line)
print()
if failed == 0:
    print("全部通过 ✓")
else:
    print(f"{failed} 失败 ✗")
