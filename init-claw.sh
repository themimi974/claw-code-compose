#!/usr/bin/env bash
set -e

# Resolve symlinks to find the real script location
SOURCE="${BASH_SOURCE[0]}"
while [ -L "$SOURCE" ]; do
   DIR="$(cd -P "$(dirname "$SOURCE")" && pwd)"
   SOURCE="$(readlink "$SOURCE")"
   [[ "$SOURCE" != /* ]] && SOURCE="$DIR/$SOURCE"
done
SCRIPT_DIR="$(cd -P "$(dirname "$SOURCE")" && pwd)"

# Use current working directory where user runs the command
WORKING_DIR="$(pwd)"
CLAW_DIR="$WORKING_DIR/.claw-code-compose"

REPO_URL="https://github.com/themimi974/claw-code-compose.git"

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; NC='\033[0m'

# ═══════════════════════════════════════════════════════════════════
# Step 1: Check if .claw-code-compose exists
# ═══════════════════════════════════════════════════════════════════

if [[ -d "$CLAW_DIR" ]]; then
    echo -e "${CYAN}.claw-code-compose/ already exists in $(pwd)${NC}"
    read -p "Reset (re-clone repo)? [y/N] " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}Removing existing .claw-code-compose/...${NC}"
        rm -rf "$CLAW_DIR"
    else
        echo -e "${GREEN}Using existing .claw-code-compose/${NC}"
    fi
fi

# ═══════════════════════════════════════════════════════════════════
# Step 2: Clone repo if directory was missing or reset
# ═══════════════════════════════════════════════════════════════════

if [[ ! -d "$CLAW_DIR" ]]; then
    echo -e "${CYAN}Cloning repo: $REPO_URL${NC}"
    if git clone "$REPO_URL" "$CLAW_DIR" 2>/dev/null; then
        echo -e "${GREEN}Repository cloned to .claw-code-compose/${NC}"
    else
        echo -e "${RED}Error: Failed to clone repo${NC}"; exit 1
    fi
fi

# ═══════════════════════════════════════════════════════════════════
# Step 3: SSH key selection
# ═══════════════════════════════════════════════════════════════════

USER_SSH_DIR="$HOME/.ssh"
SSH_VOLUME=""

if [[ -d "$USER_SSH_DIR" ]]; then
    echo
    echo -e "${CYAN}SSH key options:${NC}"
    echo "  1) No SSH (local-only, no git remote)"
    echo "  2) Mount specific key"
    echo "  3) Mount entire ~/.ssh"
    read -p "Choose [1-3]: " -n 1 -r
    echo

    case $REPLY in
        1)
            echo -e "${GREEN}No SSH configured (local-only mode)${NC}"
            ;;
        2)
            # List available private keys (exclude .pub, known_hosts, etc.)
            shopt -s nullglob
            keys=()
            for f in "$USER_SSH_DIR"/*; do
                filename="$(basename "$f")"
                if [[ ! "$filename" =~ \.pub$ ]] && [[ ! "$filename" =~ ^known_hosts ]]; then
                    keys+=("$f")
                fi
            done
            
            if [[ ${#keys[@]} -eq 0 ]]; then
                echo -e "${RED}No private keys found in $USER_SSH_DIR${NC}"; exit 1
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
            # Also mount SSH config file for GitHub host key configuration
            if [[ -f "$USER_SSH_DIR/config" ]]; then
                SSH_VOLUME="$SSH_VOLUME\n      - $USER_SSH_DIR/config:/root/.ssh/config:ro,z"
                echo -e "${CYAN}SSH config file will also be mounted${NC}"
            fi
            echo -e "${GREEN}Selected key: $KEY_NAME${NC}"
            ;;
        3)
            SSH_VOLUME="- $USER_SSH_DIR:/root/.ssh:ro,z"
            echo -e "${GREEN}Mounting entire ~/.ssh${NC}"
            ;;
        *)
            echo -e "${RED}Invalid option${NC}"; exit 1
            ;;
    esac
else
    echo -e "${CYAN}No ~/.ssh directory found, skipping SSH config${NC}"
fi

# ═══════════════════════════════════════════════════════════════════
# Step 4: Update docker-compose.yml with SSH volume
# ═══════════════════════════════════════════════════════════════════

COMPOSE_FILE="$CLAW_DIR/docker-compose.yml"
if [[ -n "$SSH_VOLUME" ]]; then
    echo -e "${CYAN}Updating docker-compose.yml with SSH volume...${NC}"
    
    # Check if volumes section already exists
    if grep -q "^    volumes:" "$COMPOSE_FILE"; then
        # Add SSH volume after existing volumes
        sed -i "/^    volumes:/a\\      $SSH_VOLUME" "$COMPOSE_FILE"
    else
        echo -e "${RED}Could not find volumes section in docker-compose.yml${NC}"; exit 1
    fi
    echo -e "${GREEN}SSH volume added${NC}"
fi

# ═══════════════════════════════════════════════════════════════════
# Step 5: Set PROJECT_DIR and load .env
# ═══════════════════════════════════════════════════════════════════

export PROJECT_DIR="$WORKING_DIR"

# Load .env from current working directory
if [ -f "$PROJECT_DIR/.env" ]; then
   set -a; source "$PROJECT_DIR/.env"; set +a
fi

# Detect compose provider
detect_compose() {
   if command -v podman-compose &>/dev/null; then
       echo "podman-compose"
   elif command -v docker &>/dev/null && docker compose version &>/dev/null 2>&1; then
       echo "docker compose"
   elif command -v docker-compose &>/dev/null; then
       echo "docker-compose"
   else echo ""; fi
}

COMPOSE=$(detect_compose)
if [ -z "$COMPOSE" ]; then
    echo -e "${RED}Error: docker compose, podman-compose or docker-compose not found.${NC}"; exit 1
fi

if [ -z "$OPENAI_API_KEY" ] && [ -z "$ANTHROPIC_API_KEY" ]; then
    echo -e "${YELLOW}Warning: No API key set. Edit $PROJECT_DIR/.env${NC}\n"
fi

# ═══════════════════════════════════════════════════════════════════
# Step 6: Build image if missing
# ═══════════════════════════════════════════════════════════════════

if ! podman images --format '{{.Repository}}:{{.Tag}}' 2>/dev/null | grep -q "localhost/claw-code:latest" && \
   ! docker images --format '{{.Repository}}:{{.Tag}}' 2>/dev/null | grep -q "^claw-code:latest$" 2>/dev/null; then
    echo -e "${CYAN}Building claw-code image (first run, ~5 min)...${NC}"
    $COMPOSE -f "$CLAW_DIR/docker-compose.yml" build
    echo -e "${GREEN}Image built.${NC}"
fi

echo -e "${CYAN}Starting claw-code in: ${PROJECT_DIR}${NC}\n"

# ═══════════════════════════════════════════════════════════════════
# Step 7: Run start-single.sh from cloned directory
# ═══════════════════════════════════════════════════════════════════

exec "$CLAW_DIR/start-single.sh" "$@"