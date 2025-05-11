#!/usr/bin/env bash
# Abort if any of the following commands fails or variables are undefined
set -eu

KUBERNETES_VERSION="${KUBERNETES_VERSION:-stable}"

# Setup minikube, requires minikube >= 1.35.0
# Note: embed-certs setting removed as it's no longer supported in Minikube 1.35
# Note: When building directly in Minikube's Docker environment with eval $(minikube docker-env),
# use the image name without registry prefix and set imagePullPolicy: IfNotPresent or Never
minikube start \
    --cni=calico \
    --driver=docker \
    --network=172.17.17.1/24 \
    --kubernetes-version="${KUBERNETES_VERSION}"

if [[ -n "${CI:-}" ]];
then
    sudo chown -R travis: /home/travis/.minikube/
fi
