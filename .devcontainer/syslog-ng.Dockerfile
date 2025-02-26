FROM balabit/syslog-ng:4.2.0

# Install dependencies
RUN apt-get update && apt-get install -y curl

# Download and install latest NATS CLI using .deb package
RUN NATS_CLI_VERSION=$(curl -s https://api.github.com/repos/nats-io/natscli/releases/latest | grep '"tag_name":' | cut -d'"' -f4) && \
    curl -L "https://github.com/nats-io/natscli/releases/latest/download/nats-${NATS_CLI_VERSION#v}-amd64.deb" -o nats.deb && \
    dpkg -i nats.deb && \
    rm nats.deb && \
    rm -rf /var/lib/apt/lists/*

# Verify installation
RUN nats --version
