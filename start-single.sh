#!/usr/bin/env bash
set -euo pipefail

# Resolve script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(pwd)"

export PROJECT_DIR

RED='\033[0;31m'; GREEN='\033[0;32m'; CYAN='\033[0;36m'; NC='\033[0m'

# Load .env from parent dir
if [ -f "$PROJECT_DIR/.env" ]; then
   set -a; source "$PROJECT_DIR/.env"; set +a
fi

# Detect compose
detect_compose() {
   if command -v docker &>/dev/null && docker compose version &>/dev/null 2>&1; then
       echo "docker compose"
   elif command -v podman-compose &>/dev/null; then
       echo "podman-compose"
   elif command -v docker-compose &>/dev/null; then
       echo "docker-compose"
   else echo ""; fi
}

COMPOSE=$(detect_compose)
if [ -z "$COMPOSE" ]; then
   echo -e "${RED}Error: docker compose or podman-compose not found.${NC}"; exit 1
fi

echo -e "${CYAN}Using $COMPOSE in: ${PROJECT_DIR}${NC}\n"

# Build if needed
$COMPOSE -f "$SCRIPT_DIR/docker-compose.yml" build

# Run with compose
if command -v podman &>/dev/null; then
    RUNTIME="podman"
    EXTRA_FLAGS="--userns=keep-id"
elif command -v docker &>/dev/null; then
    RUNTIME="docker"
    EXTRA_FLAGS=""
else
    echo -e "${RED}Error: neither podman nor docker found.${NC}"; exit 1
fi

MODEL_FLAG=""
if [ -n "$CLAW_MODEL" ]; then
   MODEL_FLAG="--model $CLAW_MODEL"
fi

exec $RUNTIME run \
   --rm -it \
   $EXTRA_FLAGS \
   --network=host \
   -e ANTHROPIC_API_KEY="${ANTHROPIC_API_KEY:-}" \
   -e container= \
   -e ANTHROPIC_BASE_URL="${ANTHROPIC_BASE_URL:-}" \
   -e OPENAI_API_KEY="${OPENAI_API_KEY:-dummy}" \
   -e OPENAI_BASE_URL="${OPENAI_BASE_URL:-}" \
   -e CLAW_MODEL="${CLAW_MODEL:-}" \
   -v "${PROJECT_DIR}:/workspace:Z" \
   -v "${SCRIPT_DIR}/claw-config.json:/root/.config/claw-code/config.json:Z" \
   -w /workspace \
   claw-code:latest $MODEL_FLAG "$@"