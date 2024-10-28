
# Use an official Python 3.12 image as the base
FROM python:3.12-slim

# Define build arguments with default values
ARG BUILD_DATE
ARG GIT_COMMIT

# Recommended labels for GitHub Registry
LABEL org.opencontainers.image.source="https://github.com/felmoltor/updog2" \
      org.opencontainers.image.description="A lightweight file server in Python." \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.authors="Felipe Molina de la Torre" \
      org.opencontainers.image.version="0.1.0" \
      org.opencontainers.image.revision="${GIT_COMMIT}" \
      org.opencontainers.image.created="${BUILD_DATE}" \
      org.opencontainers.image.title="Updog2" \
      org.opencontainers.image.documentation="https://github.com/felmoltor/updog2#readme" \
      org.opencontainers.image.url="https://github.com/felmoltor/updog2"

# Set environment variables to prevent pyc files and enable virtual environments
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Install pipenv and git
RUN apt-get update && \
    apt-get install -y --no-install-recommends git && \
    pip install --upgrade pip && \
    pip install pipenv && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy the current directory (updog2 project) into the container
COPY . .

# Install dependencies using pipenv
RUN pipenv install .

# Make sure pipenv shell uses the correct Python environment
SHELL ["pipenv", "run", "bash", "-c"]

# Verify the installation of updog
RUN which updog2 && updog2 --version

# Define the entry point to allow running updog commands
ENTRYPOINT ["pipenv", "run", "updog2"]
