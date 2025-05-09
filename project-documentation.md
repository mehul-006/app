# PostgreSQL Flask Application on Kubernetes

## Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Components](#components)
3. [Prerequisites](#prerequisites)
4. [Installation](#installation)
5. [Configuration](#configuration)
6. [Usage Guide](#usage-guide)
7. [Development](#development)
8. [Troubleshooting](#troubleshooting)
9. [Security Considerations](#security-considerations)
10. [Performance Optimization](#performance-optimization)

## Architecture Overview

This project implements a containerized Flask application that connects to a PostgreSQL database with a pgAdmin interface, all running on Kubernetes (Minikube). The entire solution is accessible via HTTPS endpoints.

### Architecture Diagram

```
                                  ┌───────────────────┐
                                  │   HTTPS Ingress   │
                                  │  (TLS Enabled)    │
                                  └─────────┬─────────┘
                                            │
                     ┌─────────────────┬────┴────┬────────────────┐
                     │                 │         │                │
           ┌─────────▼─────────┐      │         │       ┌────────▼────────┐
           │                   │      │         │       │                 │
           │  Flask App Pods   │      │         │       │  pgAdmin Pod    │
           │  (2+ replicas)    │      │         │       │                 │
           │                   │      │         │       │                 │
           └─────────┬─────────┘      │         │       └────────┬────────┘
                     │                │         │                │
                     │                │         │                │
                     │         ┌──────▼─────────▼──────┐         │
                     │         │                       │         │
                     └────────►│   PostgreSQL Pod      │◄────────┘
                               │                       │
                               │                       │
                               └───────────┬───────────┘
                                           │
                                           │
                               ┌───────────▼───────────┐
                               │                       │
                               │ Persistent Volumes    │
                               │                       │
                               └───────────────────────┘
```

## Components

### 1. Flask Application
- **Purpose**: RESTful API service that connects to PostgreSQL
- **Features**:
  - Health check endpoints
  - Database interaction API
  - Setup functionality
- **Implementation**: Python Flask application with psycopg2 for PostgreSQL connectivity

### 2. PostgreSQL Database
- **Purpose**: Data storage
- **Features**:
  - Persistent storage
  - Kubernetes health probes
  - Configured for high-availability
- **Implementation**: Official PostgreSQL Docker image running as a Kubernetes StatefulSet

### 3. pgAdmin
- **Purpose**: Web-based PostgreSQL administration tool
- **Features**:
  - Full database management interface
  - Accessible via HTTPS
  - User authentication
- **Implementation**: Official pgAdmin4 Docker image

### 4. Ingress Controller
- **Purpose**: Provides external access with TLS termination
- **Features**:
  - HTTPS support with TLS certificates
  - Path-based routing
  - Host-based virtual hosting
- **Implementation**: NGINX Ingress Controller as Minikube addon

## Prerequisites

- [Minikube](https://minikube.sigs.k8s.io/docs/start/) v1.23.0 or higher
- [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/) v1.22.0 or higher
- [Docker](https://docs.docker.com/get-docker/) v20.10.0 or higher
- [OpenSSL](https://www.openssl.org/) (for certificate generation)
- Minimum 4GB RAM and 4 CPU cores available for Minikube

## Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/postgres-flask-kubernetes.git
cd postgres-flask-kubernetes
```

### Step 2: Generate Self-Signed TLS Certificate

```bash
chmod +x generate-self-signed-cert.sh
./generate-self-signed-cert.sh
```

### Step 3: Start Minikube and Deploy the Application

```bash
chmod +x minikube-setup.sh
./minikube-setup.sh
```

### Step 4: Update Hosts File

Add the following entry to your `/etc/hosts` file (Linux/Mac) or `C:\Windows\System32\drivers\etc\hosts` file (Windows):

```
<minikube-ip> app.example.com pgadmin.example.com
```

Replace `<minikube-ip>` with the IP address displayed at the end of the setup script execution.

## Configuration

### Environment Variables

#### Flask Application
| Variable | Description | Default |
|----------|-------------|---------|
| DB_HOST | PostgreSQL hostname | postgres |
| DB_NAME | Database name | postgres |
| DB_USER | Database username | postgres |
| DB_PASSWORD | Database password | postgres |
| DB_PORT | Database port | 5432 |

#### PostgreSQL
| Variable | Description | Default |
|----------|-------------|---------|
| POSTGRES_DB | Default database name | postgres |
| POSTGRES_USER | Admin username | postgres |
| POSTGRES_PASSWORD | Admin password | postgres |
| PGDATA | Data directory | /var/lib/postgresql/data/pgdata |

#### pgAdmin
| Variable | Description | Default |
|----------|-------------|---------|
| PGADMIN_DEFAULT_EMAIL | Admin login email | admin@example.com |
| PGADMIN_DEFAULT_PASSWORD | Admin password | admin |

### Kubernetes Resources

Default resource limits for containers:

| Component | CPU Limit | Memory Limit | CPU Request | Memory Request |
|-----------|-----------|--------------|------------|----------------|
| Flask App | 300m | 256Mi | 100m | 128Mi |
| PostgreSQL | 500m | 512Mi | 250m | 256Mi |
| pgAdmin | 500m | 512Mi | 250m | 256Mi |

### Storage

| Component | Storage Size | Storage Class | Access Mode |
|-----------|--------------|---------------|-------------|
| PostgreSQL | 5Gi | standard (default) | ReadWriteOnce |
| pgAdmin | 1Gi | standard (default) | ReadWriteOnce |

## Usage Guide

### Accessing the Flask Application API

#### Base URL
```
https://app.example.com
```

#### Endpoints

**Health Check**
```
GET /healthz
```
Response: `{"status": "healthy"}`

**Get Data from PostgreSQL**
```
GET /api/data
```
Response: `{"data": [{"id": 1, "name": "Initial Record", "created_at": "2025-05-09T12:00:00"}]}`

**Initialize Database Tables**
```
GET /api/setup
```
Response: `{"status": "Database setup successful"}`

### Accessing pgAdmin

1. Navigate to `https://pgadmin.example.com` in your browser
2. Login using:
   - Email: `admin@example.com`
   - Password: `admin`

#### Connecting to PostgreSQL from pgAdmin

1. Right-click on "Servers" in the left pane and select "Create" > "Server"
2. In the "General" tab, enter a name (e.g., "Local PostgreSQL")
3. In the "Connection" tab, enter:
   - Host: `postgres`
   - Port: `5432`
   - Maintenance database: `postgres`
   - Username: `postgres`
   - Password: `postgres`
4. Click "Save"

## Development

### Local Development Workflow

1. **Modify Flask Application**:
   - Edit `app.py` to add/modify endpoints or functionality
   - Update `requirements.txt` if new dependencies are needed

2. **Rebuild and Deploy**:
   ```bash
   eval $(minikube docker-env)
   docker build -t flask-postgres-app:latest .
   kubectl rollout restart deployment flask-app
   ```

3. **View Logs**:
   ```bash
   # For Flask App
   kubectl logs -f -l app=flask-app
   
   # For PostgreSQL
   kubectl logs -f -l app=postgres
   
   # For pgAdmin
   kubectl logs -f -l app=pgadmin
   ```

### Adding New API Endpoints

To add new API endpoints to the Flask application:

1. Edit `app.py`:

```python
@app.route('/api/new-endpoint', methods=['GET', 'POST'])
def new_endpoint():
    # Implementation here
    return jsonify({"result": "Data processed"})
```

2. Rebuild and redeploy as described above

### Database Schema Changes

To modify the database schema:

1. Update the table creation logic in `app.py`
2. Access pgAdmin to execute additional SQL commands
3. Consider implementing proper database migrations for production use

## Troubleshooting

### Common Issues

#### Cannot Access Applications via HTTPS

**Issue**: Browser shows certificate warning or refuses connection

**Solutions**:
- Verify hosts file has correct Minikube IP
- Check if ingress controller is running: `kubectl get pods -n ingress-nginx`
- Verify TLS secret exists: `kubectl get secret tls-secret`
- Check ingress configuration: `kubectl describe ingress app-ingress`

#### PostgreSQL Connection Issues

**Issue**: Flask application cannot connect to PostgreSQL

**Solutions**:
- Check if PostgreSQL pod is running: `kubectl get pods -l app=postgres`
- Verify secrets are correctly created: `kubectl get secret postgres-secret -o yaml`
- Check PostgreSQL logs: `kubectl logs -l app=postgres`
- Test connection from within the cluster: 
  ```bash
  kubectl exec -it $(kubectl get pod -l app=flask-app -o name | head -n 1) -- bash -c "psql -h postgres -U postgres"
  ```

#### pgAdmin Cannot Connect to PostgreSQL

**Issue**: Cannot establish connection from pgAdmin to PostgreSQL

**Solutions**:
- Ensure you're using the correct hostname (`postgres`, not localhost)
- Check if PostgreSQL service is correctly defined: `kubectl get svc postgres`
- Verify network policies allow communication between namespaces if used

### Viewing Pod Status

```bash
# Get all pods status
kubectl get pods

# Get detailed information about a specific pod
kubectl describe pod <pod-name>

# Check pod events
kubectl get events --sort-by='.lastTimestamp'
```

### Restarting Components

```bash
# Restart Flask application
kubectl rollout restart deployment flask-app

# Restart PostgreSQL
kubectl rollout restart deployment postgres

# Restart pgAdmin
kubectl rollout restart deployment pgadmin
```

## Security Considerations

### TLS Certificate Management

- The provided self-signed certificates are intended for development only
- For production, replace with certificates from a trusted Certificate Authority
- Update the TLS secret with production certificates:
  ```bash
  kubectl create secret tls tls-secret --cert=/path/to/tls.crt --key=/path/to/tls.key --dry-run=client -o yaml | kubectl apply -f -
  ```

### Password Management

- Default passwords are set for demonstration purposes
- For production:
  - Generate strong random passwords
  - Update Kubernetes secrets with secure values
  - Consider using a secrets management solution like HashiCorp Vault
  - Use Kubernetes Secrets Encryption at Rest

### Network Security

- Implement network policies to restrict pod-to-pod communication
- Enable mTLS for service-to-service communication
- Consider using a service mesh like Istio for advanced security features

## Performance Optimization

### Scaling the Application

To scale the Flask application horizontally:

```bash
kubectl scale deployment flask-app --replicas=5
```

### Resource Management

Adjust resource requests and limits based on observed usage:

```bash
kubectl top pods
```

Then update the deployment YAML files accordingly.

### PostgreSQL Optimization

1. **Connection Pooling**: Consider adding PgBouncer for connection pooling
2. **Query Optimization**: 
   - Add indexes for frequently queried columns 
   - Use EXPLAIN ANALYZE to identify slow queries
3. **Configuration Tuning**:
   - Adjust `shared_buffers`, `work_mem`, and other PostgreSQL parameters
   - Create a ConfigMap with a custom `postgresql.conf`

### Monitoring and Metrics

- Add Prometheus and Grafana for monitoring
- Instrument the Flask application with Prometheus client
- Set up alerts for critical conditions

---

## License

[MIT License](LICENSE)

## Support

For support, please file an issue in the GitHub repository or contact the maintainers at support@example.com.
