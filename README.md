# claw-code-compose

Claw Code instances manager using Docker/Podman Compose.

## Quick Start

```bash
# Clone this repository
git clone https://github.com/themimi974/claw-code-compose.git
cd claw-code-compose

# Create .env file (copy from .env.example)
cp .env.example .env
# Edit .env with your API configuration

# Run Claw Code
./start-single.sh

# Or use the bootstrapper
./init-claw.sh
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
- **OpenAI compatible** - Use with LLM gateways (Ollama, LiteLLM, etc.)

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# OpenAI Compatible API (LLM Gateway)
OPENAI_BASE_URL=http://100.64.0.34:8082/v1
OPENAI_API_KEY=anything
CLAW_MODEL=openai/minimax-m2.5-free

# Or use Anthropic
# ANTHROPIC_API_KEY=sk-ant-...
```

### Claw Config

Edit `claw-config.json` for Claw Code settings:

```json
{
  "model": "openai/qwen3:14b",
  "system_prompt": "You are a helpful coding assistant."
}
```

## Scripts

| Script | Description |
|--------|-------------|
| `start-single.sh` | Start Claw Code container |
| `init-claw.sh` | Bootstrap new Claw Code environment |
| `install-init-claw.sh` | Install init-claw to system |
| `uninstall-init-claw.sh` | Uninstall init-claw from system |

## License

MIT

## Creator

themimi974