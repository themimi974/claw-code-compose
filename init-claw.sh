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

export PROJECT_DIR="$(pwd)"

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; NC='\033[0m'

# Load .env from parent dir (where user runs init-claw)
if [ -f "$PROJECT_DIR/.env" ]; then
   set -a; source "$PROJECT_DIR/.env"; set +a
fi

detect_compose() {
   if command -v docker &>/dev/null && docker compose version &>/dev/null 2>&1; then
       echo "docker compose"
   elif command -v docker-compose &>/dev/null; then
       echo "docker-compose"
   elif command -v podman-compose &>/dev/null; then
       echo "podman-compose"
   else echo ""; fi
}

COMPOSE=$(detect_compose)
if [ -z "$COMPOSE" ]; then
   echo -e "${RED}Error: docker compose or podman-compose not found.${NC}"; exit 1
fi

if [ -z "$OPENAI_API_KEY" ] && [ -z "$ANTHROPIC_API_KEY" ]; then
   echo -e "${YELLOW}Warning: No API key set. Edit $PROJECT_DIR/.env${NC}\n"
fi

# Build image if missing
if ! podman images --format '{{.Repository}}:{{.Tag}}' 2>/dev/null | grep -q "localhost/claw-code:latest" && \
  ! docker images --format '{{.Repository}}:{{.Tag}}' 2>/dev/null | grep -q "^claw-code:latest$" 2>/dev/null; then
   echo -e "${CYAN}Building claw-code image (first run, ~5 min)...${NC}"
   $COMPOSE -f "$SCRIPT_DIR/docker-compose.yml" build
   echo -e "${GREEN}Image built.${NC}"
fi

echo -e "${CYAN}Starting claw-code in: ${PROJECT_DIR}${NC}\n"

# Use start-single.sh which uses docker compose run
exec "$SCRIPT_DIR/start-single.sh" "$@"