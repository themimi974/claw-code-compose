FROM rust:latest-bookworm

# Install dependencies
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Clone Claw Code
RUN git clone https://github.com/codetwentyfive/claw-code-local /opt/claw-code

WORKDIR /opt/claw-code/rust

# Build Claw Code CLI
RUN cargo build -p rusty-claude-cli --release \
    && cp target/release/claw /usr/local/bin/claw \
    && chmod +x /usr/local/bin/claw

# Disable sandbox for --rm container usage
ENV ANTHROPIC_SANDBOX=false

# Default command - interactive shell
CMD ["/bin/bash"]