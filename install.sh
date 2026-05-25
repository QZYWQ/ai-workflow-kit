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
npx --yes skills add mattpocock/skills 2>/dev/null || \
    echo "  ⚠ 手动: npx skills add mattpocock/skills"

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

# ====== 9. 全局路由门规则 ======
echo "→ 全局路由门规则..."
GLOBAL_CLAUDE="$HOME/.claude/CLAUDE.md"
ROUTING_RULE="项目目录如果含有 .langgraph/CLAUDE.md，必须在任何非琐碎任务之前首先读取它——它包含强制路由规则（路径 A-F），禁止跳过路由直接 Bash/编码。"
if [ -f "$GLOBAL_CLAUDE" ]; then
    if ! grep -q ".langgraph/CLAUDE.md" "$GLOBAL_CLAUDE" 2>/dev/null; then
        # Insert after the OMEGA block
        sed -i '' '/<!-- OMEGA:END -->/a\
\
<!-- AI-WORKFLOW-KIT: 路由门 -->\
'"$ROUTING_RULE" "$GLOBAL_CLAUDE" 2>/dev/null || true
    fi
fi

echo "✅ 完成。新项目: langgraph-cli init"
