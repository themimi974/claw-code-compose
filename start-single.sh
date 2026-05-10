#!/usr/bin/env bash
set -euo pipefail
ok()   { echo -e "\033[32m✔\033[0m $*"; }
info() { echo -e "\033[34mℹ\033[0m $*"; }
err()  { echo -e "\033[31m✘\033[0m $*"; exit 1; }

# --- Detect container runtime ---
COMPOSE_PROVIDER=""
if command -v podman &>/dev/null; then
    # Check if native podman compose is available (not podman-compose)
    if podman compose version &>/dev/null 2>&1; then
        ENGINE=podman
        COMPOSE_PROVIDER="native"
    elif command -v podman-compose &>/dev/null; then
        ENGINE=podman
        COMPOSE_PROVIDER="podman-compose"
    fi
fi

if [[ -z "$ENGINE" ]] && command -v docker &>/dev/null; then
    ENGINE=docker
    COMPOSE_PROVIDER="native"
fi

if [[ -z "$ENGINE" ]]; then
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
info "Using $ENGINE ($COMPOSE_PROVIDER), project: $PROJECT_NAME"

# --- Cleanup old container ---
podman rm -f "$CONTAINER_NAME" 2>/dev/null || true
docker rm -f "$CONTAINER_NAME" 2>/dev/null || true

# --- Run ---
cd "$SCRIPT_DIR"

if [[ "$COMPOSE_PROVIDER" == "podman-compose" ]]; then
    # podman-compose doesn't support --rm, containers auto-remove after exit
    PROJECT_NAME="$PROJECT_NAME" podman-compose -f "$COMPOSE_FILE" up --build claw
else
    # Native docker/podman compose supports --rm
    PROJECT_NAME="$ENGINE"="$ENGINE" $ENGINE compose -f "$COMPOSE_FILE" up --build --rm claw
fi