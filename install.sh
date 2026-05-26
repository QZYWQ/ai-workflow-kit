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

# ====== 5. Matt Pocock skills ======
echo "→ Matt Pocock skills..."
SKILLS_DIR="$(pwd)/.agents/skills"
if [ -d "$SKILLS_DIR/grill-with-docs" ] && [ -d "$SKILLS_DIR/diagnose" ]; then
    echo "  (已安装到项目)"
else
    npx --yes skills add mattpocock/skills 2>/dev/null || \
        echo "  ⚠ 手动: npx skills add mattpocock/skills"
fi
# Copy to global so all langgraph-cli init projects can use them
if [ -d "$SKILLS_DIR" ]; then
    mkdir -p "$HOME/.claude/skills"
    for skill_dir in "$SKILLS_DIR"/*/; do
        skill_name=$(basename "$skill_dir")
        if [ ! -e "$HOME/.claude/skills/$skill_name" ]; then
            cp -r "$skill_dir" "$HOME/.claude/skills/$skill_name" 2>/dev/null || true
        fi
    done
    echo "  (已同步到全局 ~/.claude/skills/)"
fi

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
