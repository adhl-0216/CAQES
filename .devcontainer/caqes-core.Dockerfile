FROM mcr.microsoft.com/devcontainers/python:1-3.12-bullseye

# Install poetry using pipx
RUN python3 -m pip install --user pipx && \
    python3 -m pipx ensurepath && \
    pipx install poetry==2.1.1

# Verify installation
RUN poetry --version