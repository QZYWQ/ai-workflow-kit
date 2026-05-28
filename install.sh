#!/bin/bash
set -e
echo "━━━ AI Workflow Kit ━━━"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# ====== 1. Python ======
echo "→ Python 环境..."
VENV="$HOME/.venv/langgraph"
[ -d "$VENV" ] || python3 -m venv "$VENV"
"$VENV/bin/pip" install -q langgraph langchain-anthropic typer pyyaml 2>/dev/null

# ====== 2. langgraph-cli ======
echo "→ langgraph-cli..."
mkdir -p "$HOME/.local/bin"
sed "s|#!/Users/zpdedn/.venv/langgraph/bin/python3|#!$VENV/bin/python3|" \
    "$SCRIPT_DIR/langgraph-cli" > "$HOME/.local/bin/langgraph-cli"
chmod +x "$HOME/.local/bin/langgraph-cli"

# ====== 2b. Specs templates ======
echo "→ Specs templates..."
SPECS_DIR="$HOME/.local/share/langgraph-cli/specs"
mkdir -p "$SPECS_DIR"
cp "$SCRIPT_DIR/.langgraph/specs/"*.yaml "$SPECS_DIR/" 2>/dev/null
echo "  (已安装到 $SPECS_DIR)"

# ====== 3. GitNexus ======
if command -v gitnexus &>/dev/null; then
    echo "→ GitNexus (已装)"
else
    echo "→ GitNexus..."
    npm install -g gitnexus 2>/dev/null || \
        echo "  ⚠ 需要 Node.js: npm install -g gitnexus"
fi

# ====== 4. OMEGA 记忆系统 ======
echo "→ OMEGA..."
if python3 -c "import omega" 2>/dev/null; then
    echo "  (已安装)"
else
    python3 -m pip install "omega-memory[server]" -q 2>/dev/null || \
        echo "  ⚠ 手动: pip install omega-memory[server]"
fi
if [ -d "$HOME/.omega" ]; then
    echo "  (已配置)"
else
    ~/.venv/langgraph/bin/omega setup --client claude-code 2>/dev/null || \
        which omega 2>/dev/null && omega setup --client claude-code 2>/dev/null || \
        echo "  ⚠ 手动: omega setup --client claude-code"
fi

# ====== 5. Matt Pocock skills (GitHub: mattpocock/skills) ======
echo "→ Matt Pocock skills (github.com/mattpocock/skills)..."
GLOBAL_SKILLS="$HOME/.claude/skills"
mkdir -p "$GLOBAL_SKILLS"

if [ -d "$GLOBAL_SKILLS/grill-with-docs" ] && [ -d "$GLOBAL_SKILLS/diagnose" ] && [ -d "$GLOBAL_SKILLS/tdd" ]; then
    echo "  (已安装到全局)"
else
    # 安装到临时目录，然后移到全局
    TEMP_SKILLS="/tmp/mattpocock-skills-$$"
    mkdir -p "$TEMP_SKILLS"
    if npx --yes skills add mattpocock/skills --target "$TEMP_SKILLS" 2>/dev/null; then
        for skill_dir in "$TEMP_SKILLS"/*/; do
            skill_name=$(basename "$skill_dir")
            cp -r "$skill_dir" "$GLOBAL_SKILLS/$skill_name" 2>/dev/null || true
        done
        rm -rf "$TEMP_SKILLS"
        echo "  (已安装到 ~/.claude/skills/)"
    else
        echo "  ⚠ npx skills add 失败，手动安装:"
        echo "    git clone https://github.com/mattpocock/skills /tmp/mp-skills"
        echo "    cp -r /tmp/mp-skills/* ~/.claude/skills/"
    fi
fi
# 不安装到项目目录——技能是全局共享的，不应进入项目 git 仓库

# ====== 6. oh-my-claude ======
echo "→ oh-my-claude..."
if [ -d "$HOME/.claude/plugins/cache/oh-my-claude" ]; then
    echo "  (已安装)"
else
    echo "  请在 Claude Code 中运行: /plugin marketplace add oh-my-claude"
    echo "  然后: /plugin install oh-my-claude@oh-my-claude"
fi

# ====== 7. Skill 注册 ======
echo "→ langgraph-cli skill..."
mkdir -p "$HOME/.claude/skills/langgraph-cli"
cp "$SCRIPT_DIR/skills/langgraph-cli/SKILL.md" "$HOME/.claude/skills/langgraph-cli/SKILL.md"

# ====== 8. PATH ======
grep -q '.local/bin' "$HOME/.zshrc" 2>/dev/null || \
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.zshrc"

# ====== 9. 安装后验证 ======
echo "→ 验证安装..."
VERIFY_OK=0
VERIFY_TOTAL=5

# 9.1 langgraph-cli
if [ -x "$HOME/.local/bin/langgraph-cli" ]; then
    echo "  ✅ langgraph-cli"
    VERIFY_OK=$((VERIFY_OK + 1))
else
    echo "  ❌ langgraph-cli 未安装到 ~/.local/bin/"
fi

# 9.2 langgraph-cli skill
if [ -f "$HOME/.claude/skills/langgraph-cli/SKILL.md" ]; then
    echo "  ✅ langgraph-cli skill"
    VERIFY_OK=$((VERIFY_OK + 1))
else
    echo "  ❌ langgraph-cli skill 未注册到 ~/.claude/skills/"
fi

# 9.3 OMEGA
if python3 -c "import omega" 2>/dev/null; then
    echo "  ✅ OMEGA"
    VERIFY_OK=$((VERIFY_OK + 1))
else
    echo "  ⚠ OMEGA not importable"
fi

# 9.4 GitNexus
if command -v gitnexus &>/dev/null; then
    echo "  ✅ GitNexus"
    VERIFY_OK=$((VERIFY_OK + 1))
else
    echo "  ⚠ GitNexus not found"
fi

# 9.5 oh-my-claude
if [ -d "$HOME/.claude/plugins/cache/oh-my-claude" ]; then
    echo "  ✅ oh-my-claude"
    VERIFY_OK=$((VERIFY_OK + 1))
else
    echo "  ⚠ oh-my-claude 未安装（在 Claude Code 中运行 /plugin install oh-my-claude@oh-my-claude）"
fi

echo "━━━━━━━━━━━━━━━━━━━━"
echo "  验证: $VERIFY_OK/$VERIFY_TOTAL 通过"
echo "━━━━━━━━━━━━━━━━━━━━"
if [ $VERIFY_OK -lt $VERIFY_TOTAL ]; then
    echo "  ⚠ 部分组件未安装。查看上方的安装指引。"
fi
echo ""
echo "  新项目: langgraph-cli init --deep"
echo "  健康检查: langgraph-cli health"
echo "  共存说明: docs/COEXISTENCE.md"
