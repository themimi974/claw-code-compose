#!/usr/bin/env bash
set -euo pipefail
ok()   { echo -e "\033[32m✔\033[0m $*"; }
info() { echo -e "\033[34mℹ\033[0m $*"; }
err()  { echo -e "\033[31m✘\033[0m $*"; exit 1; }

# --- Detect container runtime ---
if command -v podman &>/dev/null; then
    ENGINE=podman
elif command -v docker &>/dev/null; then
    ENGINE=docker
else
    err "No container runtime found (need docker or podman)"
fi

# --- Find compose file ---
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPOSE_FILE="$SCRIPT_DIR/docker-compose.yml"
if [[ ! -f "$COMPOSE_FILE" ]]; then
    err "docker-compose.yml not found in $SCRIPT_DIR"
fi

# --- Dynamic container name from project dir ---
PROJECT_NAME="${PWD##*/}"
CONTAINER_NAME="claw-${PROJECT_NAME//-/}"
info "Using $ENGINE, project: $PROJECT_NAME"

# --- Cleanup old container ---
$ENGINE rm -f "$($ENGINE ps -q --filter "name=$CONTAINER_NAME")" 2>/dev/null || true

# --- Run ---
cd "$SCRIPT_DIR"
PROJECT_NAME="$PROJECT_NAME" $ENGINE compose up --build --rm claw