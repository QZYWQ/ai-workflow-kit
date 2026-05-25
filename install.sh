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

# ====== 4. Matt Pocock skills ======
echo "→ Matt Pocock skills..."
npx --yes skills add mattpocock/skills 2>/dev/null || \
    echo "  ⚠ 手动: npx skills add mattpocock/skills"

# ====== 5. oh-my-claude ======
echo "→ oh-my-claude..."
if [ -f "$HOME/.claude.json" ]; then
    python3 -c "
import json
with open('$HOME/.claude.json') as f: c=json.load(f)
plugins=c.get('projects',{}).get('$HOME',{}).get('enabledPlugins',{})
print('已装' if 'oh-my-claude@oh-my-claude' in plugins else \
      '请运行: /plugin marketplace add oh-my-claude && /plugin install oh-my-claude@oh-my-claude')
" 2>/dev/null
else
    echo "  请运行: /plugin marketplace add oh-my-claude && /plugin install oh-my-claude@oh-my-claude"
fi

# ====== 6. Skill 注册 ======
echo "→ langgraph-cli skill..."
mkdir -p "$HOME/.claude/skills/langgraph-cli"
cp "$SCRIPT_DIR/skills/langgraph-cli/SKILL.md" "$HOME/.claude/skills/langgraph-cli/SKILL.md"

# ====== 7. PATH ======
grep -q '.local/bin' "$HOME/.zshrc" 2>/dev/null || \
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.zshrc"

echo "✅ 完成。新项目: langgraph-cli init"
