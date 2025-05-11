#!/usr/bin/env bash

# Abort if any of the following commands fails or variables are undefined
set -eu

# Set image name for illuminatio runner - no registry prefix as we'll build directly in Minikube
ILLUMINATIO_IMAGE="illuminatio-runner:dev"

echo "===== Building the illuminatio runner image in Minikube's Docker ====="
# Point the local Docker client to the Minikube Docker daemon
eval "$(minikube docker-env)"

# Build the Docker image directly in Minikube's environment
docker build -t "${ILLUMINATIO_IMAGE}" .

echo "===== Verifying the image is available in Minikube ====="
docker images | grep illuminatio-runner

echo "===== Installing illuminatio locally ====="
pip install -e .

echo "===== Running E2E tests ====="
# Run the E2E tests with coverage - using pytest directly
pytest -m e2e
