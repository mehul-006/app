#!/bin/bash
# minikube-setup.sh
# Script to set up Minikube with NGINX Ingress Controller and deploy our application

# Start Minikube with enough resources
minikube start --cpus=4 --memory=4096 --vm-driver=docker

# Enable the ingress addon
minikube addons enable ingress

# Wait for the ingress controller to be ready
echo "Waiting for ingress controller to be ready..."
kubectl wait --namespace kube-system \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/component=controller \
  --timeout=300s

# Build the Docker image for our Flask app
eval $(minikube docker-env)
docker build -t flask-postgres-app:latest .

# Create namespaced resources
kubectl apply -f postgres-configmap.yaml
kubectl apply -f postgres-secret.yaml
kubectl apply -f postgres-storage.yaml
kubectl apply -f postgres-deployment.yaml
kubectl apply -f postgres-service.yaml

kubectl apply -f pgadmin-configmap.yaml
kubectl apply -f pgadmin-secret.yaml
kubectl apply -f pgadmin-storage.yaml
kubectl apply -f pgadmin-deployment.yaml
kubectl apply -f pgadmin-service.yaml

kubectl apply -f app-configmap.yaml
kubectl apply -f app-secret.yaml
kubectl apply -f app-deployment.yaml
kubectl apply -f app-service.yaml

# Create TLS secret (update this with your actual certificate paths)
# kubectl create secret tls tls-secret --cert=path/to/tls.crt --key=path/to/tls.key
# For now, we're using the pre-created tls-secret.yaml
kubectl apply -f tls-cert-secret.yaml

# Apply the ingress
kubectl apply -f ingress.yaml

# Wait for pods to be ready
echo "Waiting for pods to be ready..."
kubectl wait --for=condition=ready pod --selector=app=postgres --timeout=300s
kubectl wait --for=condition=ready pod --selector=app=pgadmin --timeout=300s
kubectl wait --for=condition=ready pod --selector=app=flask-app --timeout=300s

# Get the IP address of the Minikube cluster
MINIKUBE_IP=$(minikube ip)

# Instructions for accessing the services
echo "=================================================="
echo "Setup complete! Add the following to your /etc/hosts file:"
echo "$MINIKUBE_IP app.example.com pgadmin.example.com"
echo ""
echo "Then access the application at: https://app.example.com"
echo "Access pgAdmin at: https://pgadmin.example.com"
echo "    - Login with: admin@example.com / admin"
echo ""
echo "To connect pgAdmin to PostgreSQL:"
echo "  - Host: postgres"
echo "  - Port: 5432"
echo "  - Username: postgres"
echo "  - Password: postgres"
echo "=================================================="
