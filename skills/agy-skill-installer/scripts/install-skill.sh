#!/usr/bin/env bash
# Automated Skill & Plugin Installer for Anti-Gravity IDE (Linux / macOS)

set -euo pipefail

SOURCE="${1:?Error: Source URL or local path required}"
SKILL_NAME="${2:-}"
WORKSPACE_ROOT="${3:-$PWD}"
AS_PLUGIN=false

for arg in "$@"; do
    if [[ "$arg" == "--plugin" || "$arg" == "-p" ]]; then
        AS_PLUGIN=true
    fi
done

GLOBAL_SKILLS="$HOME/.gemini/config/skills"
LOCAL_SKILLS="$WORKSPACE_ROOT/.agents/skills"
GLOBAL_PLUGINS="$HOME/.gemini/config/plugins"
LOCAL_PLUGINS="$WORKSPACE_ROOT/.agents/plugins"
CONFIG_JSON="$HOME/.gemini/config/config.json"
TEMP_DIR="$(mktemp -d)"

mkdir -p "$GLOBAL_SKILLS" "$LOCAL_SKILLS" "$GLOBAL_PLUGINS" "$LOCAL_PLUGINS"

echo "====================================================="
echo "  Anti-Gravity IDE Skill & Plugin Installer (Bash)"
echo "====================================================="
echo "Source:        $SOURCE"
echo "Global Skills: $GLOBAL_SKILLS"
echo "Local Skills:  $LOCAL_SKILLS"
echo "Global Plugin: $GLOBAL_PLUGINS"
echo "Local Plugin:  $LOCAL_PLUGINS"
echo ""

if [[ "$SOURCE" =~ ^https?:// ]]; then
    echo "[1/4] Cloning repository..."
    git clone --depth 1 "$SOURCE" "$TEMP_DIR" --quiet
    SOURCE_DIR="$TEMP_DIR"
elif [[ "$SOURCE" =~ ^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$ ]]; then
    echo "[1/4] Cloning GitHub shorthand (https://github.com/$SOURCE)..."
    git clone --depth 1 "https://github.com/$SOURCE" "$TEMP_DIR" --quiet
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

register_plugin_config() {
    local plugin_name="$1"
    node -e "
const fs = require('fs');
const p = '$CONFIG_JSON';
const name = '$plugin_name';
let cfg = {};
if (fs.existsSync(p)) {
    try { cfg = JSON.parse(fs.readFileSync(p, 'utf8')); } catch(e){}
}
if (!cfg.plugins) cfg.plugins = {};
cfg.plugins[name] = { enabled: true };
fs.writeFileSync(p, JSON.stringify(cfg, null, 2) + '\n', 'utf8');
console.log('Registered plugin in config.json: ' + name);
"
}

echo "[2/4] Analyzing repository structure..."

IS_PLUGIN=false
if [[ "$AS_PLUGIN" == true || (-z "$SKILL_NAME" && (-f "$SOURCE_DIR/plugin.json" || -f "$SOURCE_DIR/gemini-extension.json")) ]]; then
    IS_PLUGIN=true
fi

if [[ "$IS_PLUGIN" == true ]]; then
    echo "[3/4] Installing Native Antigravity Plugin (Ponytail Standard)..."
    PLUGIN_NAME=""
    if [[ -f "$SOURCE_DIR/plugin.json" ]]; then
        PLUGIN_NAME=$(node -e "try { console.log(require('$SOURCE_DIR/plugin.json').name || ''); } catch(e){}" 2>/dev/null || echo "")
    elif [[ -f "$SOURCE_DIR/gemini-extension.json" ]]; then
        PLUGIN_NAME=$(node -e "try { console.log(require('$SOURCE_DIR/gemini-extension.json').name || ''); } catch(e){}" 2>/dev/null || echo "")
    fi
    if [[ -z "$PLUGIN_NAME" ]]; then
        PLUGIN_NAME="${SKILL_NAME:-$(basename "$SOURCE" .git)}"
    fi

    echo "Plugin Name: $PLUGIN_NAME"
    rm -rf "$GLOBAL_PLUGINS/$PLUGIN_NAME" "$LOCAL_PLUGINS/$PLUGIN_NAME"
    mkdir -p "$GLOBAL_PLUGINS/$PLUGIN_NAME" "$LOCAL_PLUGINS/$PLUGIN_NAME"

    cp -R "$SOURCE_DIR/"* "$GLOBAL_PLUGINS/$PLUGIN_NAME/"
    cp -R "$SOURCE_DIR/"* "$LOCAL_PLUGINS/$PLUGIN_NAME/"
    rm -rf "$GLOBAL_PLUGINS/$PLUGIN_NAME/.git" "$LOCAL_PLUGINS/$PLUGIN_NAME/.git"

    # Ensure plugin.json
    if [[ ! -f "$GLOBAL_PLUGINS/$PLUGIN_NAME/plugin.json" ]]; then
        echo "{\"name\":\"$PLUGIN_NAME\"}" > "$GLOBAL_PLUGINS/$PLUGIN_NAME/plugin.json"
        echo "{\"name\":\"$PLUGIN_NAME\"}" > "$LOCAL_PLUGINS/$PLUGIN_NAME/plugin.json"
    fi

    # Register in config.json
    register_plugin_config "$PLUGIN_NAME"

    echo "✓ Plugin '$PLUGIN_NAME' installed cleanly (Bundled skills managed inside plugin)"
else
    echo "[3/4] Installing skills..."
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
fi

rm -rf "$TEMP_DIR"

echo "[4/4] Installation complete!"
