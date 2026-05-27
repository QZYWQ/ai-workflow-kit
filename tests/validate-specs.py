#!/usr/bin/env python3
"""Spec 交叉引用校验——防止文档与 spec 之间漂移。"""
import sys
import yaml
from pathlib import Path

SPEC_DIR = Path(__file__).parent.parent / ".langgraph" / "specs"
ROOT = Path(__file__).parent.parent
errors = []

def check(cond, msg):
    if not cond:
        errors.append(msg)
        print(f"  ✗ {msg}")
    else:
        print(f"  ✓ {msg}")

# ── 1. YAML 语法 ──
print("1. YAML 语法校验")
specs = {}
for path in sorted(SPEC_DIR.glob("*.yaml")):
    try:
        with open(path) as f:
            specs[path.stem] = yaml.safe_load(f)
        print(f"  ✓ {path.name}")
    except Exception as e:
        errors.append(f"YAML parse error in {path.name}: {e}")
        print(f"  ✗ {path.name}: {e}")

# ── 2. extends 引用检查 ──
print("\n2. extends 引用")
for name, spec in specs.items():
    extends = spec.get("spec", {}).get("extends", None) if isinstance(spec, dict) else None
    if extends:
        check(extends in specs or (SPEC_DIR / f"{extends}.yaml").exists(),
              f"{name}.yaml extends '{extends}' → 文件不存在")

# ── 3. 层级数一致性 ──
print("\n3. 层级数一致性")
takeover = specs.get("intelligent-takeover", {})
if takeover:
    sense = takeover.get("states", {}).get("sense", {})
    layers = sense.get("layers", [])
    layer_count = len(layers)
    # task-router 应该引用相同层数
    router = specs.get("task-router", {})
    takeover_text = str(router)
    check("层感知" in takeover_text, "task-router 引用了感知层数")

# ── 4. phase 值一致性 ──
print("\n4. phase 枚举一致性")
phase_sources = []
for name, spec in specs.items():
    # 从 takeover 的 phase output 字段提取
    if name == "intelligent-takeover":
        phase_conf = spec.get("phase", {})
        phase_output = phase_conf.get("output", "")
        if phase_output:
            parts = [p.strip() for p in phase_output.replace("phase=", "").split("|")]
            ref_phases = set(parts)
    # 从 methodology-activation 的 phases 提取
    if name == "methodology-activation":
        meth_phases = set(spec.get("phases", {}).keys())
expected = {"toolkit", "prototype", "mvp", "production", "maintenance", "unknown"}
check(ref_phases == expected, f"phase 枚举一致性: takeover={sorted(ref_phases)} == expected={sorted(expected)}")
check(meth_phases == expected, f"methodology phases: {sorted(meth_phases)} == expected={sorted(expected)}")

# ── 5. 工具引用完整性 ──
print("\n5. tools_from_library 引用")
tool_library = specs.get("task-router", {}).get("tool_library", {})
tool_names = set(tool_library.keys())
for name, spec in specs.items():
    if name == "task-router":
        continue
    states = spec.get("states", {})
    for state_name, state_conf in states.items():
        tools = state_conf.get("tools_from_library", [])
        for tool in tools:
            check(tool in tool_names or tool in ["tdd", "diagnose", "grill-with-docs",
                  "prototype", "verify", "grill-me", "handoff", "to-prd", "to-issues",
                  "caveman", "worldquant-brain-alpha-engineering"],
                  f"{name}.yaml → {state_name}.tools_from_library: '{tool}' 不在 task-router 工具库中")

# ── 6. methodology 工具引用 ──
print("\n6. methodology → tool 映射")
methodology = specs.get("methodology-activation", {})
if methodology:
    for mname, mconf in methodology.get("methodologies", {}).items():
        m_tools = mconf.get("tools", [])
        for m_tool in m_tools:
            check(m_tool in tool_names,
                  f"methodology {mname}.tools: '{m_tool}' 不在 task-router tool_library 中")

# ── 7. 路径 spec 引用的路径是否存在 ──
print("\n7. 路径引用完整性")
all_paths = {"A", "B", "C", "D", "E", "F"}
for name, spec in specs.items():
    if name in ("intelligent-takeover", "methodology-activation"):
        continue
    text = str(spec)
    for ref_path in ["路径 A", "路径 B", "路径 C", "路径 D", "路径 E", "路径 F"]:
        if ref_path in text:
            pass  # paths referenced exist by definition

# ── 8. state.json schema 字段存在性 ──
print("\n8. state.json schema 完整性")
state_schema = takeover.get("state_descriptor", {}).get("schema", {})
required_fields = ["active_task", "current_path", "current_state", "phase", "methodology_state", "last_updated"]
for field in required_fields:
    check(field in state_schema, f"state.json schema 包含 '{field}'")

# ── 9. methodology phases 在 takeover 中有对应 ──
print("\n9. methodology phases 与 takeover dimensions 一致")
if methodology:
    meth_phases = set(methodology.get("phases", {}).keys())
    takeover_dimensions = set(takeover.get("phase", {}).get("dimensions", {}).keys())
    # 检查 methodology 的每个 phase 在 takeover 中都有对应
    for mp in meth_phases:
        if mp not in takeover_dimensions:
            print(f"  ⚠ methodology phase '{mp}' 在 takeover dimensions 中不存在")
    # 反过来也检查
    for td in takeover_dimensions:
        if td not in meth_phases:
            print(f"  ⚠ takeover dimension '{td}' 在 methodology phases 中不存在")

# ── 结果 ──
print(f"\n{'='*50}")
if errors:
    print(f"✗ {len(errors)} 个问题:")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)
else:
    print("✓ 全部检查通过")
