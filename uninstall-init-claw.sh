#!/usr/bin/env bash
set -euo pipefail

# ═══════════════════════════════════════════════════════════════════
# uninstall-init-claw - Remove init-claw from system
# ═══════════════════════════════════════════════════════════════════

ok()   { echo -e "\033[32m✔\033[0m $*"; }
info() { echo -e "\033[34mℹ\033[0m $*"; }

# --- Detect if installed as root or user ---
if [[ $EUID -eq 0 ]]; then
    TARGET_DIR="/usr/local/bin"
else
    TARGET_DIR="$HOME/.local/bin"
fi

# --- Remove script ---
if [[ -f "$TARGET_DIR/init-claw" ]]; then
    rm -f "$TARGET_DIR/init-claw"
    ok "Removed $TARGET_DIR/init-claw"
else
    info "init-claw not found in $TARGET_DIR"
fi

ok "Uninstallation complete!"