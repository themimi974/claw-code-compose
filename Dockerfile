FROM rust:latest

# Install system dependencies (git + Python for TUI)
RUN apt-get update && apt-get install -y git python3 python3-pip && rm -rf /var/lib/apt/lists/*

# Clone Claw Code
RUN git clone https://github.com/ultraworkers/claw-code /opt/claw-code

WORKDIR /opt/claw-code/rust

# Build Claw Code CLI
RUN cargo build -p rusty-claude-cli --release \
    && cp target/release/claw /usr/local/bin/claw \
    && chmod +x /usr/local/bin/claw

# Install TUI dependencies
RUN pip3 install --no-cache-dir textual

# Copy TUI code
COPY claw-tui /opt/claw-tui
RUN chmod +x /opt/claw-tui/main.py

# Disable sandbox for --rm container usage
ENV ANTHROPIC_SANDBOX=false

# Default command - launch TUI
CMD ["python3", "/opt/claw-tui/main.py"]