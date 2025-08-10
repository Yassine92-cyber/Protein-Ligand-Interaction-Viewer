# Docker Setup for Protein-Ligand Interaction Viewer

This document provides instructions for running the Protein-Ligand Interaction Viewer using Docker containers.

## Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- At least 4GB of available RAM
- At least 2GB of available disk space

## Quick Start

### 1. Build and Start Services

```bash
# Build and start all services
docker-compose up --build

# Or run in detached mode
docker-compose up --build -d
```

### 2. Access the Application

- **Frontend**: http://localhost
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

### 3. Stop Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

## Service Architecture

### Backend Service (`protein-ligand-backend`)
- **Port**: 8000
- **Image**: Python 3.11 with RDKit
- **Health Check**: `/health` endpoint
- **Dependencies**: FastAPI, RDKit, NumPy

### Frontend Service (`protein-ligand-frontend`)
- **Port**: 80
- **Image**: Nginx serving React app
- **Dependencies**: Backend service
- **Proxy**: Routes `/api/*` to backend

## Development Workflow

### 1. Development Mode

For development with hot-reload:

```bash
# Start only the backend in development mode
docker-compose up backend

# In another terminal, start frontend dev server
cd frontend
npm install
npm run dev
```

### 2. Production Build

```bash
# Build production images
docker-compose build

# Start production services
docker-compose up -d
```

### 3. View Logs

```bash
# View all service logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

## Configuration

### Environment Variables

#### Backend
- `PYTHONPATH`: Python module search path
- `PYTHONUNBUFFERED`: Disable Python output buffering

#### Frontend
- `NODE_ENV`: Build environment (production/development)

### Port Configuration

You can modify the ports in `docker-compose.yml`:

```yaml
services:
  backend:
    ports:
      - "8001:8000"  # Host:Container
  frontend:
    ports:
      - "8080:80"    # Host:Container
```

## Troubleshooting

### Common Issues

#### 1. Port Already in Use
```bash
# Check what's using the port
netstat -tulpn | grep :80
netstat -tulpn | grep :8000

# Kill the process or change ports in docker-compose.yml
```

#### 2. Build Failures
```bash
# Clean build cache
docker-compose build --no-cache

# Remove all containers and images
docker-compose down --rmi all
docker system prune -a
```

#### 3. RDKit Installation Issues
The backend Dockerfile includes all necessary system dependencies for RDKit. If you encounter issues:

```bash
# Check backend logs
docker-compose logs backend

# Enter container for debugging
docker-compose exec backend bash
```

#### 4. Frontend Build Issues
```bash
# Check frontend build logs
docker-compose logs frontend

# Verify Node.js version compatibility
docker-compose exec frontend node --version
```

### Health Checks

The backend service includes health checks:

```bash
# Check service health
docker-compose ps

# Manual health check
curl http://localhost:8000/health
```

## Performance Optimization

### 1. Resource Limits

Add resource limits to `docker-compose.yml`:

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1.0'
        reservations:
          memory: 1G
          cpus: '0.5'
```

### 2. Volume Optimization

For production, consider using named volumes instead of bind mounts:

```yaml
volumes:
  - backend_code:/app
  - backend_cache:/app/__pycache__

volumes:
  backend_code:
  backend_cache:
```

### 3. Multi-stage Builds

The frontend Dockerfile uses multi-stage builds to optimize image size.

## Security Considerations

### 1. Network Isolation
- Services communicate through internal Docker network
- Only necessary ports exposed to host

### 2. Security Headers
- Nginx includes security headers
- Rate limiting on API endpoints

### 3. Container Security
- Non-root user execution
- Minimal base images
- Regular security updates

## Monitoring and Logging

### 1. Log Aggregation
```bash
# Follow logs in real-time
docker-compose logs -f --tail=100

# Export logs
docker-compose logs > app.log
```

### 2. Resource Monitoring
```bash
# Monitor container resources
docker stats

# Check disk usage
docker system df
```

## Backup and Recovery

### 1. Data Backup
```bash
# Export container data
docker export protein-ligand-backend > backend.tar
docker export protein-ligand-frontend > frontend.tar
```

### 2. Configuration Backup
```bash
# Backup configuration files
cp docker-compose.yml docker-compose.yml.backup
cp .env .env.backup
```

## Scaling

### 1. Horizontal Scaling
```bash
# Scale backend service
docker-compose up --scale backend=3

# Scale with load balancer
docker-compose up --scale backend=3 --scale frontend=2
```

### 2. Load Balancing
Update nginx.conf to include upstream configuration for multiple backend instances.

## Maintenance

### 1. Regular Updates
```bash
# Update base images
docker-compose pull

# Rebuild with latest base images
docker-compose build --pull
```

### 2. Cleanup
```bash
# Remove unused containers, networks, and images
docker system prune

# Remove all stopped containers
docker container prune

# Remove unused volumes
docker volume prune
```

## Support

For Docker-related issues:
1. Check the troubleshooting section above
2. Review Docker and Docker Compose logs
3. Verify system requirements
4. Check Docker daemon status: `docker info`

For application-specific issues, refer to the main README.md file. 