#!/usr/bin/env bash
set -euo pipefail

echo "=== Setting up MicroK8s for AgriSecure ==="

# Install MicroK8s
sudo snap install microk8s --classic --channel=1.29/stable

# Add current user to microk8s group
sudo usermod -aG microk8s "$USER"
sudo mkdir -p ~/.kube
sudo chown -R "$USER" ~/.kube

# Wait for MicroK8s to be ready
microk8s status --wait-ready

# Enable required addons
microk8s enable dns storage ingress

# Alias kubectl
sudo snap alias microk8s.kubectl kubectl

echo "=== MicroK8s ready ==="
echo "Applying AgriSecure manifests..."

MANIFEST_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../k8s" && pwd)"

kubectl apply -f "$MANIFEST_DIR/namespace.yaml"
kubectl apply -f "$MANIFEST_DIR/postgres/"
kubectl apply -f "$MANIFEST_DIR/redis/"
kubectl apply -f "$MANIFEST_DIR/api/"
kubectl apply -f "$MANIFEST_DIR/etl/"

echo "=== AgriSecure deployed to MicroK8s ==="
kubectl get all -n agri-secure
