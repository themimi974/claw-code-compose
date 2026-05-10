#!/usr/bin/env bash
set -euo pipefail

# ═══════════════════════════════════════════════════════════════════
# init-claw - Bootstrap Claw Code environment
# ═══════════════════════════════════════════════════════════════════

ok()   { echo -e "\033[32m✔\033[0m $*"; }
info() { echo -e "\033[34mℹ\033[0m $*"; }
err()  { echo -e "\033[31m✘\033[0m $*"; exit 1; }

# Use current working directory, not script location
# This ensures .claw-code-compose is created where the user runs the command
WORKING_DIR="$(pwd)"
CLAW_DIR="$WORKING_DIR/.claw-code-compose"

# --- Placeholder repo ---
PLACEHOLDER_REPO="https://github.com/themimi974/claw-code-compose.git"

# ═══════════════════════════════════════════════════════════════════
# Step 1: Check if .claw-code-compose exists
# ═══════════════════════════════════════════════════════════════════

if [[ -d "$CLAW_DIR" ]]; then
    info ".claw-code-compose/ already exists in $(pwd)"
    read -p "Reset (re-clone repo)? [y/N] " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        info "Removing existing .claw-code-compose/..."
        rm -rf "$CLAW_DIR"
    else
        ok "Using existing .claw-code-compose/"
    fi
fi

# ═══════════════════════════════════════════════════════════════════
# Step 2: Git clone if directory was missing or reset
# ═══════════════════════════════════════════════════════════════════

if [[ ! -d "$CLAW_DIR" ]]; then
    info "Cloning placeholder repo..."
    if git clone "$PLACEHOLDER_REPO" "$CLAW_DIR" 2>/dev/null; then
        ok "Repository cloned to .claw-code-compose/"
    else
        # Fallback: copy local template if clone fails
        info "Clone failed, using local template..."
        LOCAL_TEMPLATE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
        if [[ -d "$LOCAL_TEMPLATE" ]]; then
            cp -r "$LOCAL_TEMPLATE" "$WORKING_DIR/.claw-code-compose"
            ok "Local template copied to .claw-code-compose/"
        else
            err "No template found. Please create .claw-code-compose/ manually."
        fi
    fi
fi

# ═══════════════════════════════════════════════════════════════════
# Step 3: SSH key selection
# ═══════════════════════════════════════════════════════════════════

USER_SSH_DIR="$HOME/.ssh"
SSH_VOLUME=""

if [[ -d "$USER_SSH_DIR" ]]; then
    echo
    info "SSH key options:"
    echo "  1) No SSH (local-only, no git remote)"
    echo "  2) Mount specific key"
    echo "  3) Mount entire ~/.ssh"
    read -p "Choose [1-3]: " -n 1 -r
    echo

    case $REPLY in
        1)
            ok "No SSH configured (local-only mode)"
            ;;
        2)
            # List available private keys
            shopt -s nullglob
            keys=()
            for f in "$USER_SSH_DIR"/*; do
                filename="$(basename "$f")"
                if [[ ! "$filename" =~ \.pub$ ]] && [[ ! "$filename" =~ ^known_hosts ]]; then
                    keys+=("$f")
                fi
            done
            
            if [[ ${#keys[@]} -eq 0 ]]; then
                err "No private keys found in $USER_SSH_DIR"
            fi
            
            echo "Available keys:"
            select key in "${keys[@]}"; do
                if [[ -z "$key" ]]; then
                    echo "Invalid selection. Please enter a number."
                elif [[ -n "$key" ]]; then
                    break
                fi
            done
            
            KEY_NAME="$(basename "$key")"
            SSH_VOLUME="- $key:/root/.ssh/$KEY_NAME:ro,z"
            if [[ -f "$USER_SSH_DIR/config" ]]; then
                SSH_VOLUME="$SSH_VOLUME\n      - $USER_SSH_DIR/config:/root/.ssh/config:ro,z"
                info "SSH config file will also be mounted"
            fi
            ok "Selected key: $KEY_NAME"
            ;;
        3)
            SSH_VOLUME="- $USER_SSH_DIR:/root/.ssh:ro,z"
            ok "Mounting entire ~/.ssh"
            ;;
        *)
            err "Invalid option"
            ;;
    esac
else
    info "No ~/.ssh directory found, skipping SSH config"
fi

# ═══════════════════════════════════════════════════════════════════
# Step 4: Update docker-compose.yml with SSH volume
# ═══════════════════════════════════════════════════════════════════

COMPOSE_FILE="$CLAW_DIR/docker-compose.yml"
if [[ -n "$SSH_VOLUME" ]]; then
    info "Updating docker-compose.yml with SSH volume..."
    
    if grep -q "^    volumes:" "$COMPOSE_FILE"; then
        sed -i "/^    volumes:/a\\      $SSH_VOLUME" "$COMPOSE_FILE"
    else
        err "Could not find volumes section in docker-compose.yml"
    fi
    ok "SSH volume added"
fi

# ═══════════════════════════════════════════════════════════════════
# Step 5: Global config detection and sync
# ═══════════════════════════════════════════════════════════════════

GLOBAL_CONFIG="$HOME/.config/claw/claw.json"
GLOBAL_DATA="$HOME/.local/share/claw"
LOCAL_CLAW="$CLAW_DIR/.claw-code"

echo
if [[ -f "$GLOBAL_CONFIG" ]] || [[ -d "$GLOBAL_DATA" ]]; then
    info "Found global Claw Code config/data"
    if [[ -d "$LOCAL_CLAW" ]] && [[ -n "$(ls -A "$LOCAL_CLAW" 2>/dev/null)" ]]; then
        info "Local .claw-code/ already has data (sessions preserved)"
        read -p "Sync global config? This will merge/overwrite some files. [y/N] " -n 1 -r
        echo
    else
        read -p "Sync global config into project? [y/N] " -n 1 -r
        echo
    fi
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        mkdir -p "$LOCAL_CLAW"
        [[ -f "$GLOBAL_CONFIG" ]] && cp "$GLOBAL_CONFIG" "$LOCAL_CLAW/" && ok "Copied global config"
        [[ -d "$GLOBAL_DATA" ]] && cp -rn "$GLOBAL_DATA"/* "$LOCAL_CLAW/" 2>/dev/null && ok "Copied global data (-n prevents overwrite)"
    fi
else
    info "No global config found at $GLOBAL_CONFIG"
    read -p "Initialize fresh local config? [Y/n] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        mkdir -p "$LOCAL_CLAW"
        ok "Created local .claw-code/ directory"
    fi
fi

# ═══════════════════════════════════════════════════════════════════
# Step 6: Run start-single.sh
# ═══════════════════════════════════════════════════════════════════

echo
START_SCRIPT="$CLAW_DIR/start-single.sh"
if [[ -f "$START_SCRIPT" ]]; then
    info "Launching Claw Code..."
    cd "$CLAW_DIR"
    bash "$START_SCRIPT"
else
    err "start-single.sh not found in .claw-code-compose/"
fi