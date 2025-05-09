# Quickstart Guide: Flask PostgreSQL App with Kubernetes

This guide will help you quickly set up and run the Flask PostgreSQL application on Minikube with HTTPS access.

## Prerequisites

- Minikube installed
- kubectl installed
- Docker installed
- 4GB RAM and 4 CPU cores available for Minikube

## Setup Instructions

### 1. Clone and Set Up the Project

```bash
# Clone the repository (or copy all provided files to a directory)
git clone https://github.com/yourusername/flask-postgres-k8s.git
cd flask-postgres-k8s
```

### 2. Generate TLS Certificate

```bash
# Make the script executable
chmod +x generate-self-signed-cert.sh

# Generate certificate
./generate-self-signed-cert.sh
```

### 3. Deploy to Minikube

```bash
# Make the setup script executable
chmod +x minikube-setup.sh

# Run the setup script
./minikube-setup.sh
```

### 4. Update Your Hosts File

Add these entries to your hosts file:
```
<minikube-ip> app.example.com pgadmin.example.com
```

Replace `<minikube-ip>` with the IP shown at the end of the setup script.

## Accessing the Application

- **Flask API**: [https://app.example.com](https://app.example.com)
  - Available endpoints:
    - `/healthz` - Health check
    - `/api/data` - Get data from database
    - `/api/setup` - Initialize database

- **pgAdmin**: [https://pgadmin.example.com](https://pgadmin.example.com)
  - Login: admin@example.com / admin
  - To connect to PostgreSQL:
    - Host: postgres
    - Port: 5432
    - Username: postgres
    - Password: postgres

## Architecture Summary

- **Flask Application**: Python web API that talks to PostgreSQL
- **PostgreSQL**: Database with persistent storage
- **pgAdmin**: Web-based PostgreSQL admin console
- **NGINX Ingress**: Provides HTTPS access with TLS termination

## Project Structure

```
├── app.py                   # Flask application source
├── Dockerfile               # Docker image definition
├── requirements.txt         # Python dependencies
├── generate-self-signed-cert.sh # TLS certificate generator
├── minikube-setup.sh        # Deployment script
└── kubernetes/              # Kubernetes manifests
    ├── postgres-*.yaml      # PostgreSQL resources
    ├── pgadmin-*.yaml       # pgAdmin resources  
    ├── app-*.yaml           # Flask app resources
    ├── tls-cert-secret.yaml # TLS certificate
    └── ingress.yaml         # Ingress configuration
```

## Basic Operations

### Viewing Application Logs

```bash
# Flask application logs
kubectl logs -l app=flask-app

# PostgreSQL logs
kubectl logs -l app=postgres

# pgAdmin logs
kubectl logs -l app=pgadmin
```

### Scaling the Application

```bash
# Scale to 3 replicas
kubectl scale deployment flask-app --replicas=3
```

### Restarting Components

```bash
# Restart Flask application
kubectl rollout restart deployment flask-app
```

## Troubleshooting

If you encounter issues:

1. Check pod status: `kubectl get pods`
2. Verify services: `kubectl get svc`
3. Check ingress: `kubectl describe ingress app-ingress`

For detailed troubleshooting, refer to the main documentation.

## Next Steps

- Review the full documentation for detailed information
- Customize the Flask application for your needs
- Replace self-signed certificates with valid ones for production
- Add monitoring and logging solutions

---

For more information, see the full documentation in [README.md](README.md).
