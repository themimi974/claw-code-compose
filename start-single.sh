#!/usr/bin/env bash
set -euo pipefail
ok()   { echo -e "\033[32m✔\033[0m $*"; }
info() { echo -e "\033[34mℹ\033[0m $*"; }
err()  { echo -e "\033[31m✘\033[0m $*"; exit 1; }

# --- Detect container runtime ---
COMPOSE_PROVIDER=""
if command -v podman &>/dev/null; then
    ENGINE=podman
    # Check for native podman compose (not the podman-compose wrapper)
    # If "podman compose version" shows "podman-compose" in output, it's the wrapper
    if podman compose version 2>&1 | grep -qv "podman-compose"; then
        COMPOSE_PROVIDER="native"
    elif command -v podman-compose &>/dev/null; then
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

# If still can't determine, default to podman-compose
if [[ -z "$COMPOSE_PROVIDER" ]] && command -v podman-compose &>/dev/null; then
    COMPOSE_PROVIDER="podman-compose"
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
    # podman-compose: append "claw" command to run the CLI
    PROJECT_NAME="$PROJECT_NAME" podman-compose -f "$COMPOSE_FILE" up --build claw claw
else
    # Native docker/podman compose: use run instead of up for interactive command
    PROJECT_NAME="$ENGINE"="$ENGINE" $ENGINE compose -f "$COMPOSE_FILE" run --rm claw claw
fi