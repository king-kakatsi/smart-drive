# Deployment Guide

Complete deployment guide for Smart-Drive covering Docker, production setup, scaling, and maintenance.

## Quick Deployment

### Docker Compose (Recommended)

```bash
# Clone repository
git clone <repository-url>
cd smart-drive

# Configure environment
cp docker/.env.example docker/.env
# Edit docker/.env with your API keys

# Deploy with Docker Compose
docker-compose -f docker/docker-compose.prod.yml up -d

# Check deployment status
docker-compose ps
docker-compose logs

# Access application
# Frontend: http://your-server:80
# API: http://your-server:8000
```

### One-Click Deploy Scripts

```bash
# Development deployment
./scripts/deploy-dev.sh

# Production deployment
./scripts/deploy-prod.sh

# Staging deployment
./scripts/deploy-staging.sh
```

## Production Architecture

### Recommended Production Setup

```
┌─────────────────────────────────────────────────────────────┐
│                    Load Balancer (nginx)                     │
│  ┌─────────────────────────────────────────────────────┐    │
│  │                Application Servers                  │    │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐    │    │
│  │  │ FastAPI     │ │ FastAPI     │ │ FastAPI     │    │    │
│  │  │ Worker 1    │ │ Worker 2    │ │ Worker 3    │    │    │
│  │  └─────────────┘ └─────────────┘ └─────────────┘    │    │
│  └─────────────────────────────────────────────────────┘    │
│           │                   │                   │          │
│           ▼                   ▼                   ▼          │
┌─────────────────────────────────────────────────────────────┐
│                 Shared File Storage (NFS/EFS)                │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐ │
│  │   ChromaDB      │ │   SQLite DB     │ │  Redis Cache    │ │
│  │ (Vectors)       │ │ (Metadata)      │ │ (Sessions)      │ │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Docker Deployment

### Production Docker Compose

```yaml
# docker/docker-compose.prod.yml
version: '3.8'

services:
  # Reverse proxy and load balancer
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
      - ./nginx/logs:/var/log/nginx
    depends_on:
      - frontend
      - backend
    restart: unless-stopped

  # Frontend application
  frontend:
    build:
      context: ..
      dockerfile: frontend/Dockerfile.prod
    environment:
      - VITE_API_BASE_URL=https://api.smart-drive.com
    volumes:
      - nginx_cache:/var/cache/nginx
    restart: unless-stopped

  # Backend API (scaled)
  backend:
    build:
      context: ..
      dockerfile: backend/Dockerfile
    environment:
      - ENVIRONMENT=production
      - WORKERS=4
    env_file:
      - .env
    volumes:
      - uploads:/app/uploads
      - chroma_db:/app/chroma_db
      - logs:/app/logs
    depends_on:
      - redis
      - postgres
    restart: unless-stopped
    deploy:
      replicas: 3

  # Vector database
  chromadb:
    image: chromadb/chroma:latest
    volumes:
      - chroma_db:/chroma/chroma
    restart: unless-stopped

  # Cache layer
  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    restart: unless-stopped

  # Database
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: smart_drive
      POSTGRES_USER: smart_drive
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  # Background job processor
  worker:
    build:
      context: ..
      dockerfile: backend/Dockerfile
    command: celery -A app.tasks worker --loglevel=info
    environment:
      - ENVIRONMENT=production
    env_file:
      - .env
    volumes:
      - uploads:/app/uploads
      - chroma_db:/app/chroma_db
    depends_on:
      - redis
      - postgres
    restart: unless-stopped
    deploy:
      replicas: 2

volumes:
  uploads:
  chroma_db:
  redis_data:
  postgres_data:
  nginx_cache:
```

### Multi-Stage Docker Builds

```dockerfile
# backend/Dockerfile
FROM python:3.12-slim as builder

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.12-slim as production

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsm6 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Create non-root user
RUN useradd --create-home --shell /bin/bash app
USER app

# Set working directory
WORKDIR /app

# Copy application code
COPY --chown=app:app . .

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Expose port
EXPOSE 8000

# Start application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

## Infrastructure Setup

### Cloud Provider Setup

#### AWS Deployment

```bash
# EC2 instance setup
aws ec2 run-instances \
  --image-id ami-12345678 \
  --count 1 \
  --instance-type t3.medium \
  --key-name smart-drive-key \
  --security-groups smart-drive-sg \
  --user-data file://scripts/aws-init.sh

# RDS PostgreSQL setup
aws rds create-db-instance \
  --db-instance-identifier smart-drive-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --master-username smartdrive \
  --master-user-password ${DB_PASSWORD} \
  --allocated-storage 20

# S3 bucket for file storage
aws s3 mb s3://smart-drive-uploads \
  --region us-east-1

# CloudFront CDN setup
aws cloudfront create-distribution \
  --distribution-config file://cloudfront-config.json
```

#### DigitalOcean Deployment

```bash
# Droplet creation
doctl compute droplet create smart-drive \
  --region nyc1 \
  --image ubuntu-22-04-x64 \
  --size s-2vcpu-2gb \
  --ssh-keys fingerprint \
  --user-data-file scripts/do-init.sh

# Managed database
doctl databases create smart-drive-db \
  --engine pg \
  --region nyc1 \
  --size db-s-1vcpu-1gb \
  --version 15

# Spaces (S3-compatible) bucket
doctl spaces create smart-drive-uploads \
  --region nyc1
```

### Domain and SSL Setup

#### Nginx Configuration

```nginx
# nginx/nginx.conf
events {
    worker_connections 1024;
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;

    # Logging
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';

    access_log /var/log/nginx/access.log main;
    error_log /var/log/nginx/error.log;

    # Performance
    sendfile        on;
    tcp_nopush      on;
    tcp_nodelay     on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    client_max_body_size 100M;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types
        text/plain
        text/css
        text/xml
        application/json
        application/javascript
        application/xml+rss
        application/atom+xml;

    # Upstream backend servers
    upstream backend {
        least_conn;
        server backend:8000;
        server backend:8001;
        server backend:8002;
    }

    # HTTPS redirect
    server {
        listen 80;
        server_name smart-drive.com www.smart-drive.com;
        return 301 https://$server_name$request_uri;
    }

    # Main application server
    server {
        listen 443 ssl http2;
        server_name smart-drive.com www.smart-drive.com;

        # SSL configuration
        ssl_certificate /etc/nginx/ssl/smart-drive.crt;
        ssl_certificate_key /etc/nginx/ssl/smart-drive.key;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers off;

        # Security headers
        add_header X-Frame-Options "DENY" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header Referrer-Policy "strict-origin-when-cross-origin" always;

        # Frontend static files
        location / {
            proxy_pass http://frontend:80;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # API endpoints
        location /api/ {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;

            # WebSocket support
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
        }

        # File uploads (if not using CDN)
        location /uploads/ {
            alias /app/uploads/;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
}
```

#### SSL Certificate Setup

```bash
# Let's Encrypt SSL certificate
certbot certonly --nginx -d smart-drive.com -d www.smart-drive.com

# Or manual certificate
# Copy certificates to nginx/ssl/
cp /etc/letsencrypt/live/smart-drive.com/fullchain.pem nginx/ssl/smart-drive.crt
cp /etc/letsencrypt/live/smart-drive.com/privkey.pem nginx/ssl/smart-drive.key
```

## Scaling Strategies

### Horizontal Scaling

#### Load Balancing

```nginx
# nginx/upstreams.conf
upstream backend {
    least_conn;  # Load balancing method
    server backend-1:8000 weight=1 max_fails=3 fail_timeout=30s;
    server backend-2:8000 weight=1 max_fails=3 fail_timeout=30s;
    server backend-3:8000 weight=1 max_fails=3 fail_timeout=30s;
    server backend-4:8000 weight=2 max_fails=3 fail_timeout=30s;  # Higher weight
}

upstream websocket {
    ip_hash;  # Session affinity for WebSockets
    server backend-1:8000;
    server backend-2:8000;
    server backend-3:8000;
}
```

#### Auto Scaling with Docker Swarm

```yaml
# docker/docker-compose.swarm.yml
version: '3.8'

services:
  backend:
    image: smart-drive/backend:latest
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
        window: 120s
    environment:
      - ENVIRONMENT=production
    networks:
      - smart-drive-network

  # Auto-scaling based on CPU usage
  backend-scaled:
    image: smart-drive/backend:latest
    deploy:
      replicas: 1
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
      placement:
        constraints:
          - node.role == worker
      restart_policy:
        condition: on-failure
```

### Vertical Scaling

#### Resource Optimization

```python
# backend/app/core/scaling.py
class ResourceManager:
    def __init__(self):
        self.workers = multiprocessing.cpu_count()
        self.memory_limit = self._get_memory_limit()

    def optimize_worker_count(self):
        """Dynamically adjust worker count based on load."""
        cpu_usage = psutil.cpu_percent(interval=1)
        memory_usage = psutil.virtual_memory().percent

        if cpu_usage > 80 or memory_usage > 85:
            # Scale down
            return max(1, self.workers - 1)
        elif cpu_usage < 50 and memory_usage < 70:
            # Scale up
            return min(multiprocessing.cpu_count() * 2, self.workers + 1)

        return self.workers

    def configure_uvicorn(self):
        """Configure Uvicorn based on resources."""
        config = {
            "host": "0.0.0.0",
            "port": 8000,
            "workers": self.workers,
            "loop": "uvloop",  # Faster event loop
            "http": "httptools",  # Faster HTTP parser
        }

        # Adjust for memory constraints
        if self.memory_limit < 1024:  # Less than 1GB
            config["workers"] = 1
            config["loop"] = "asyncio"

        return config
```

### Database Scaling

#### Read Replicas

```python
# backend/app/core/database.py
class DatabaseManager:
    def __init__(self):
        self.writer = self._create_writer_connection()
        self.readers = self._create_reader_connections()
        self.current_reader = 0

    def get_writer(self):
        """Get write connection."""
        return self.writer

    def get_reader(self):
        """Get read connection (round-robin)."""
        if not self.readers:
            return self.writer

        reader = self.readers[self.current_reader]
        self.current_reader = (self.current_reader + 1) % len(self.readers)
        return reader

    def execute_query(self, query, params=None, read_only=True):
        """Execute query on appropriate connection."""
        if read_only:
            conn = self.get_reader()
        else:
            conn = self.get_writer()

        return conn.execute(query, params)
```

#### Connection Pooling

```python
# Database connection pooling
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,          # Base pool size
    max_overflow=30,       # Max additional connections
    pool_timeout=30,       # Connection timeout
    pool_recycle=3600,     # Recycle connections
    pool_pre_ping=True,    # Test connections before use
    echo=False
)
```

## Monitoring and Observability

### Application Monitoring

#### Prometheus Metrics

```python
# backend/app/core/metrics.py
from prometheus_client import Counter, Histogram, Gauge, generate_latest
from fastapi.responses import Response

# Request metrics
REQUEST_COUNT = Counter(
    'smart_drive_requests_total',
    'Total request count',
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'smart_drive_request_duration_seconds',
    'Request duration in seconds',
    ['method', 'endpoint']
)

# AI processing metrics
AI_REQUESTS = Counter(
    'smart_drive_ai_requests_total',
    'Total AI requests',
    ['provider', 'model', 'status']
)

FILE_PROCESSING_TIME = Histogram(
    'smart_drive_file_processing_duration_seconds',
    'File processing time',
    ['file_type']
)

# System metrics
ACTIVE_CONNECTIONS = Gauge(
    'smart_drive_active_connections',
    'Number of active connections'
)

MEMORY_USAGE = Gauge(
    'smart_drive_memory_usage_bytes',
    'Memory usage in bytes'
)

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    return Response(
        generate_latest(),
        media_type="text/plain; charset=utf-8"
    )
```

#### Health Checks

```python
# backend/app/core/health.py
from fastapi import APIRouter, HTTPException
import time
import psutil

router = APIRouter()

START_TIME = time.time()

@router.get("/health")
async def health_check():
    """Comprehensive health check."""
    health_status = {
        "status": "healthy",
        "timestamp": time.time(),
        "uptime": time.time() - START_TIME,
        "version": "1.0.0"
    }

    checks = {
        "database": await check_database(),
        "chromadb": await check_chromadb(),
        "groq_api": await check_groq_api(),
        "disk_space": check_disk_space(),
        "memory": check_memory()
    }

    # Check all dependencies
    all_healthy = all(check["healthy"] for check in checks.values())

    if not all_healthy:
        health_status["status"] = "unhealthy"
        raise HTTPException(503, f"Service unhealthy: {checks}")

    health_status["checks"] = checks
    return health_status

async def check_database():
    """Check database connectivity."""
    try:
        # Test database connection
        db.execute("SELECT 1")
        return {"healthy": True, "response_time": 0.001}
    except Exception as e:
        return {"healthy": False, "error": str(e)}

async def check_groq_api():
    """Check Groq API connectivity."""
    try:
        # Test API key and connectivity
        client = Groq(api_key=settings.groq_api_key)
        await client.models.list()
        return {"healthy": True}
    except Exception as e:
        return {"healthy": False, "error": str(e)}

def check_disk_space():
    """Check available disk space."""
    disk = psutil.disk_usage('/')
    available_gb = disk.free / (1024**3)

    if available_gb < 1:  # Less than 1GB
        return {"healthy": False, "available_gb": available_gb}

    return {"healthy": True, "available_gb": available_gb}
```

### Logging Configuration

```python
# backend/app/core/logging.py
import logging
import json
from pythonjsonlogger import jsonlogger

def setup_logging():
    """Configure structured JSON logging."""

    # Create logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # JSON formatter for production
    formatter = jsonlogger.JsonFormatter(
        "%(asctime)s %(name)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler with rotation
    from logging.handlers import RotatingFileHandler
    file_handler = RotatingFileHandler(
        'logs/smart-drive.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger

# Request logging middleware
@app.middleware("http")
async def log_requests(request, call_next):
    start_time = time.time()

    response = await call_next(request)

    process_time = time.time() - start_time

    logger.info(
        "Request completed",
        extra={
            "method": request.method,
            "url": str(request.url),
            "status_code": response.status_code,
            "process_time": process_time,
            "client_ip": request.client.host,
            "user_agent": request.headers.get("user-agent")
        }
    )

    return response
```

### Distributed Tracing

```python
# backend/app/core/tracing.py
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

def setup_tracing():
    """Setup OpenTelemetry tracing."""

    # Configure tracer
    trace.set_tracer_provider(TracerProvider())
    tracer = trace.get_tracer(__name__)

    # Configure Jaeger exporter
    jaeger_exporter = JaegerExporter(
        agent_host_name="jaeger",
        agent_port=14268,
    )

    # Add span processor
    span_processor = BatchSpanProcessor(jaeger_exporter)
    trace.get_tracer_provider().add_span_processor(span_processor)

    return tracer

# Instrument FastAPI
FastAPIInstrumentor.instrument_app(app)

# Tracing decorator
def trace_function(name):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            with tracer.start_as_span(name):
                return await func(*args, **kwargs)
        return wrapper
    return decorator

# Usage
@trace_function("process_file")
async def process_file(file_id: str):
    # Function implementation
    pass
```

## Backup and Recovery

### Automated Backups

```bash
# scripts/backup.sh
#!/bin/bash

BACKUP_DIR="/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_NAME="smart-drive_$TIMESTAMP"

# Create backup directory
mkdir -p $BACKUP_DIR/$BACKUP_NAME

# Database backup
docker exec smart-drive_postgres_1 pg_dump -U smartdrive smart_drive > $BACKUP_DIR/$BACKUP_NAME/database.sql

# File uploads backup
docker run --rm -v smart-drive_uploads:/data -v $BACKUP_DIR/$BACKUP_NAME:/backup alpine tar czf /backup/uploads.tar.gz -C /data .

# ChromaDB backup
docker run --rm -v smart-drive_chroma_db:/data -v $BACKUP_DIR/$BACKUP_NAME:/backup alpine tar czf /backup/chroma.tar.gz -C /data .

# Configuration backup
cp docker/.env $BACKUP_DIR/$BACKUP_NAME/

# Compress backup
cd $BACKUP_DIR
tar czf ${BACKUP_NAME}.tar.gz $BACKUP_NAME
rm -rf $BACKUP_NAME

# Upload to cloud storage (optional)
aws s3 cp ${BACKUP_NAME}.tar.gz s3://smart-drive-backups/

# Cleanup old backups (keep last 7 days)
find $BACKUP_DIR -name "smart-drive_*.tar.gz" -mtime +7 -delete

echo "Backup completed: $BACKUP_NAME"
```

### Disaster Recovery

```bash
# scripts/restore.sh
#!/bin/bash

BACKUP_FILE=$1

if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: $0 <backup-file>"
    exit 1
fi

# Extract backup
tar xzf $BACKUP_FILE

# Restore database
docker exec -i smart-drive_postgres_1 psql -U smartdrive smart_drive < database.sql

# Restore file uploads
docker run --rm -v smart-drive_uploads:/data -v $(pwd)/uploads.tar.gz:/backup.tar.gz alpine sh -c "tar xzf /backup.tar.gz -C /data"

# Restore ChromaDB
docker run --rm -v smart-drive_chroma_db:/data -v $(pwd)/chroma.tar.gz:/backup.tar.gz alpine sh -c "tar xzf /backup.tar.gz -C /data"

# Restore configuration
cp .env docker/

echo "Restore completed from: $BACKUP_FILE"
```

## Maintenance Procedures

### Zero-Downtime Deployment

```bash
# scripts/deploy-zero-downtime.sh
#!/bin/bash

# Build new images
docker-compose build --parallel

# Start new containers
docker-compose up -d --scale backend=6

# Wait for health checks
sleep 30

# Check health
if curl -f http://localhost/health; then
    # Stop old containers
    docker-compose up -d --scale backend=3

    # Clean up old images
    docker image prune -f

    echo "Zero-downtime deployment successful"
else
    echo "Health check failed, rolling back"
    docker-compose up -d --scale backend=3
    exit 1
fi
```

### Database Maintenance

```sql
-- Regular maintenance queries
-- Vacuum analyze for query optimization
VACUUM ANALYZE;

-- Reindex for performance
REINDEX DATABASE smart_drive;

-- Clean up old data (adjust retention period)
DELETE FROM chat_messages
WHERE created_at < NOW() - INTERVAL '90 days'
AND user_id IN (
    SELECT id FROM users WHERE last_login < NOW() - INTERVAL '1 year'
);

-- Update statistics
ANALYZE;
```

### Log Rotation

```bash
# logrotate configuration
/var/log/smart-drive/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 644 www-data www-data
    postrotate
        docker-compose exec backend kill -USR1 1
    endscript
}
```

## Performance Optimization

### Frontend Optimization

```javascript
// frontend/vite.config.js
import { defineConfig } from 'vite'
import { splitVendorChunkPlugin } from 'vite'

export default defineConfig({
  plugins: [splitVendorChunkPlugin()],
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['vue', 'axios'],
          ai: ['@vueuse/core'], // AI-related libraries
          ui: ['@headlessui/vue', 'heroicons'] // UI libraries
        }
      }
    },
    chunkSizeWarningLimit: 1000,
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true,
        drop_debugger: true
      }
    }
  },
  server: {
    hmr: {
      overlay: false // Disable error overlay in development
    }
  }
})
```

### CDN Integration

```javascript
// frontend/src/services/cdn.js
class CDNService {
  constructor() {
    this.baseUrl = import.meta.env.VITE_CDN_URL || 'https://cdn.smart-drive.com'
  }

  getFileUrl(filePath) {
    return `${this.baseUrl}/${filePath}`
  }

  uploadToCDN(file, path) {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('path', path)

    return fetch(`${this.baseUrl}/upload`, {
      method: 'POST',
      body: formData,
      headers: {
        'Authorization': `Bearer ${this.getAuthToken()}`
      }
    })
  }

  // Preload critical resources
  preloadCriticalResources() {
    const criticalResources = [
      '/css/app.css',
      '/js/vendor.js',
      '/js/app.js'
    ]

    criticalResources.forEach(resource => {
      const link = document.createElement('link')
      link.rel = 'preload'
      link.href = this.getFileUrl(resource)
      link.as = resource.endsWith('.css') ? 'style' : 'script'
      document.head.appendChild(link)
    })
  }
}
```

## Troubleshooting Production Issues

### Common Deployment Issues

#### Container Health Issues

```bash
# Check container status
docker-compose ps

# View container logs
docker-compose logs backend

# Check container resource usage
docker stats

# Restart unhealthy containers
docker-compose restart backend
```

#### Database Connection Issues

```bash
# Check database connectivity
docker-compose exec postgres pg_isready -U smartdrive

# Check database logs
docker-compose logs postgres

# Test database connection from app
docker-compose exec backend python -c "
import psycopg2
conn = psycopg2.connect('postgresql://smartdrive:password@postgres/smart_drive')
print('Database connection successful')
"
```

#### Performance Issues

```bash
# Monitor resource usage
docker stats

# Check application metrics
curl http://localhost:9090/metrics

# Profile application performance
docker-compose exec backend python -m cProfile -s time app/main.py

# Check for memory leaks
docker-compose exec backend python -c "
import tracemalloc
tracemalloc.start()
# Run some operations
snapshot = tracemalloc.take_snapshot()
for stat in snapshot.statistics('lineno')[:10]:
    print(stat)
"
```

### Emergency Procedures

#### Emergency Shutdown

```bash
# Immediate shutdown
docker-compose down

# Force shutdown
docker-compose down -v --remove-orphans

# Emergency cleanup
docker system prune -a --volumes
```

#### Data Recovery

```bash
# Restore from latest backup
./scripts/restore.sh /backups/smart-drive_latest.tar.gz

# Verify data integrity
docker-compose exec backend python -c "
from app.database import SessionLocal
db = SessionLocal()
result = db.execute('SELECT COUNT(*) FROM users')
print(f'Users count: {result.scalar()}')
"

# Recreate search indices if needed
docker-compose exec backend python -c "
from app.core.vector_store import chroma_client
# Recreate indices
"
```

## Security Hardening

### Container Security

```dockerfile
# backend/Dockerfile.prod
FROM python:3.12-slim

# Security: Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Security: Update packages and install security updates
RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
    ffmpeg \
    libsm6 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Security: Don't run as root
USER appuser

# Security: Use read-only filesystem where possible
VOLUME ["/app/uploads", "/app/logs"]

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1
```

### Network Security

```bash
# Firewall configuration
# Allow only necessary ports
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 80
ufw allow 443
ufw --force enable

# Fail2ban for SSH protection
apt-get install fail2ban
cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local

# Configure fail2ban for application
cat >> /etc/fail2ban/jail.local << EOF
[smart-drive]
enabled = true
port = http,https
filter = smart-drive
logpath = /var/log/nginx/access.log
maxretry = 3
bantime = 3600
EOF
```

## Cost Optimization

### Resource Optimization

```yaml
# docker/docker-compose.prod.yml (cost-optimized)
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M

  database:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '1.0'
          memory: 2G
```

### Auto Scaling Based on Load

```python
# backend/app/core/auto_scaling.py
class AutoScaler:
    def __init__(self, docker_client):
        self.docker_client = docker_client
        self.min_instances = 2
        self.max_instances = 10
        self.scale_up_threshold = 70  # CPU usage %
        self.scale_down_threshold = 30

    async def check_and_scale(self):
        """Check system load and scale accordingly."""
        cpu_usage = await self.get_average_cpu_usage()
        current_instances = await self.get_current_instance_count()

        if cpu_usage > self.scale_up_threshold and current_instances < self.max_instances:
            await self.scale_up(current_instances + 1)
        elif cpu_usage < self.scale_down_threshold and current_instances > self.min_instances:
            await self.scale_down(current_instances - 1)

    async def get_average_cpu_usage(self):
        """Get average CPU usage across all instances."""
        containers = self.docker_client.containers.list(filters={'label': 'smart-drive.backend'})
        total_cpu = 0

        for container in containers:
            stats = container.stats(stream=False)
            cpu_usage = self.calculate_cpu_percent(stats)
            total_cpu += cpu_usage

        return total_cpu / len(containers) if containers else 0

    async def scale_up(self, target_count):
        """Scale up to target number of instances."""
        # Use Docker Swarm or Kubernetes scaling
        # For Docker Compose, recreate with new scale
        pass
```

## Deployment Checklist

### Pre-deployment
- [ ] Environment variables configured
- [ ] SSL certificates obtained
- [ ] Domain DNS configured
- [ ] Firewall rules set
- [ ] Backup strategy in place
- [ ] Monitoring configured

### Deployment
- [ ] Docker images built successfully
- [ ] Containers start without errors
- [ ] Health checks pass
- [ ] Database migrations applied
- [ ] File permissions correct
- [ ] SSL certificates installed

### Post-deployment
- [ ] Application accessible via HTTPS
- [ ] API endpoints responding
- [ ] WebSocket connections working
- [ ] File uploads functional
- [ ] AI chat responding
- [ ] Monitoring dashboards working
- [ ] Backup verification completed

### Maintenance
- [ ] Log rotation configured
- [ ] Automated backups scheduled
- [ ] Security updates automated
- [ ] Performance monitoring active
- [ ] Incident response procedures documented
