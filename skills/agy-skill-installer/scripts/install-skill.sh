#!/usr/bin/env bash
# Automated Skill Installer for Anti-Gravity IDE (Linux / macOS)

set -euo pipefail

SOURCE="${1:?Error: Source URL or local path required}"
SKILL_NAME="${2:-}"
WORKSPACE_ROOT="${3:-$PWD}"

GLOBAL_SKILLS="$HOME/.gemini/config/skills"
LOCAL_SKILLS="$WORKSPACE_ROOT/.agents/skills"
TEMP_DIR="$(mktemp -d)"

mkdir -p "$GLOBAL_SKILLS" "$LOCAL_SKILLS"

echo "====================================================="
echo "  Anti-Gravity IDE Skill Installer (Bash)"
echo "====================================================="
echo "Source:        $SOURCE"
echo "Global Target: $GLOBAL_SKILLS"
echo "Local Target:  $LOCAL_SKILLS"
echo ""

if [[ "$SOURCE" =~ ^https?:// ]]; then
    echo "[1/4] Cloning repository..."
    git clone "$SOURCE" "$TEMP_DIR" --quiet
    SOURCE_DIR="$TEMP_DIR"
elif [[ -d "$SOURCE" ]]; then
    echo "[1/4] Using local path..."
    SOURCE_DIR="$(cd "$SOURCE" && pwd)"
else
    echo "Error: Source not found: $SOURCE" >&2
    exit 1
fi

copy_skill() {
    local src="$1"
    local name="$2"
    local g_target="$GLOBAL_SKILLS/$name"
    local l_target="$LOCAL_SKILLS/$name"

    rm -rf "$g_target" "$l_target"
    mkdir -p "$g_target" "$l_target"

    cp -R "$src/"* "$g_target/"
    cp -R "$src/"* "$l_target/"

    rm -rf "$g_target/.git" "$l_target/.git"

    if [[ -f "$g_target/SKILL.md" && -f "$l_target/SKILL.md" ]]; then
        echo "✓ Skill '$name' installed successfully (Slash command: /$name)"
    else
        echo "✗ Warning: SKILL.md missing in '$name'"
    fi
}

echo "[2/4] Processing skills..."

if [[ -n "$SKILL_NAME" && -d "$SOURCE_DIR/skills/$SKILL_NAME" ]]; then
    copy_skill "$SOURCE_DIR/skills/$SKILL_NAME" "$SKILL_NAME"
elif [[ -f "$SOURCE_DIR/SKILL.md" ]]; then
    NAME="${SKILL_NAME:-$(basename "$SOURCE" .git)}"
    copy_skill "$SOURCE_DIR" "$NAME"
elif [[ -d "$SOURCE_DIR/skills" ]]; then
    for dir in "$SOURCE_DIR/skills"/*; do
        if [[ -d "$dir" && -f "$dir/SKILL.md" ]]; then
            copy_skill "$dir" "$(basename "$dir")"
        fi
    done
fi

rm -rf "$TEMP_DIR"

echo "[3/4] Installation complete!"
