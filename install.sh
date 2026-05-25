#!/bin/bash
set -e
echo "━━━ AI Workflow Kit ━━━"

if [ ! -d "$HOME/.venv/langgraph" ]; then
    echo "→ 创建虚拟环境..."
    python3 -m venv "$HOME/.venv/langgraph"
fi
source "$HOME/.venv/langgraph/bin/activate"
pip install -q langgraph langchain-anthropic typer pyyaml 2>/dev/null

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$HOME/.local/bin"
cp "$SCRIPT_DIR/langgraph-cli" "$HOME/.local/bin/langgraph-cli"
chmod +x "$HOME/.local/bin/langgraph-cli"

command -v gitnexus &>/dev/null || npm install -g gitnexus 2>/dev/null || echo "⚠ GitNexus 手动装: npm install -g gitnexus"
npx skills add mattpocock/skills 2>/dev/null || echo "⚠ skills 手动装: npx skills add mattpocock/skills"

grep -q '.local/bin' "$HOME/.zshrc" 2>/dev/null || echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.zshrc"
echo "✅ 完成。新项目: langgraph-cli init"
