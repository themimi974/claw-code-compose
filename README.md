# claw-code-compose

Claw Code instances manager using Docker/Podman Compose.

## Quick Start

```bash
# Clone this repository
git clone https://github.com/themimi974/claw-code-compose.git
cd claw-code-compose

# Run Claw Code
./start-single.sh
```

## Prerequisites

- Docker OR Podman
- Git

## Installation

### Option 1: Run directly

```bash
./start-single.sh
```

### Option 2: Install `init-claw` globally

```bash
./install-init-claw.sh
```

Then run from any directory:

```bash
init-claw
```

### Uninstall

```bash
./uninstall-init-claw.sh
```

## Features

- **Containerized Claw Code** - Run Claw Code in an isolated Docker/Podman container
- **SSH key support** - Clone private repos by mounting SSH keys
- **Config sync** - Sync global Claw Code config into project
- **Sessions persistence** - Local `.claw-code/` directory preserves sessions

## Scripts

| Script | Description |
|--------|-------------|
| `start-single.sh` | Start Claw Code container |
| `init-claw.sh` | Bootstrap new Claw Code environment |
| `install-init-claw.sh` | Install init-claw to system |
| `uninstall-init-claw.sh` | Uninstall init-claw from system |

## Configuration

### Claw Code Model

Edit `claw.json` to configure Claw Code:

```json
{
  "model": "claude-sonnet-4-20250514",
  "system_prompt": "You are a helpful coding assistant."
}
```

### Environment Variables

- `ANTHROPIC_API_KEY` - Set your Anthropic API key (required)
- `ANTHROPIC_SANDBOX=false` - Sandbox is disabled by default for --rm containers

## License

MIT

## Creator

themimi974