# Choose a base image (e.g., Ubuntu, Python, Node.js)
FROM mcr.microsoft.com/devcontainers/base:ubuntu

# Install additional OS packages
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends \
    curl \
    git \
    vim \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN bash install_firefox.sh