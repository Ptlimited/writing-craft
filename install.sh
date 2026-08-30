#!/bin/bash
# writing-craft: install the skill into Claude Code.
# Usage:  ./install.sh            install for all projects (~/.claude)
#         ./install.sh --project  install into ./.claude in the current repo
set -e

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; CYAN='\033[0;36m'; NC='\033[0m'

echo ""
echo -e "${CYAN}writing-craft${NC}: nine signals three blind judges rewarded"
echo ""

# Resolve the source directory, cloning first if piped through curl.
if [ -n "$BASH_SOURCE" ] && [ "$BASH_SOURCE" != "bash" ] && [ -f "$BASH_SOURCE" ]; then
    SRC="$(cd "$(dirname "$BASH_SOURCE")" && pwd)"
else
    echo -e "${YELLOW}Remote install, cloning...${NC}"
    TMP=$(mktemp -d)
    git clone --depth 1 https://github.com/Ptlimited/writing-craft.git "$TMP/writing-craft" >/dev/null 2>&1 || {
        echo "Failed to clone. Is git installed and the repo reachable?"; exit 1; }
    SRC="$TMP/writing-craft"
fi

if [ "$1" = "--project" ]; then
    DEST="$(pwd)/.claude/skills/writing-craft"
    SCOPE="this project"
else
    DEST="$HOME/.claude/skills/writing-craft"
    SCOPE="all projects"
fi

for f in SKILL.md check.py; do
    [ -f "$SRC/$f" ] || { echo "Missing $f in $SRC, aborting."; exit 1; }
done

mkdir -p "$DEST"
cp "$SRC/SKILL.md" "$DEST/SKILL.md"
cp "$SRC/check.py" "$DEST/check.py"
chmod +x "$DEST/check.py"

echo -e "  ${GREEN}✓${NC} SKILL.md"
echo -e "  ${GREEN}✓${NC} check.py"
echo ""
echo -e "${BLUE}Installed for ${SCOPE}:${NC} $DEST"

if command -v python3 >/dev/null 2>&1; then
    echo -e "  ${GREEN}✓${NC} python3 found, the gate will run (no dependencies needed)"
else
    echo -e "  ${YELLOW}!${NC} python3 not found. The nine rules still work; check.py will not."
fi

[ -n "$TMP" ] && rm -rf "$TMP"

echo ""
echo "Next:"
echo "  1. Start a new Claude Code session so it picks the skill up."
echo "  2. Ask for a draft as usual. The skill loads itself."
echo "  3. Check any file by hand:  python3 $DEST/check.py draft.md"
echo ""
echo "Triggering is deliberately wide. To narrow it, edit the description: line"
echo "at the top of $DEST/SKILL.md"
echo ""
