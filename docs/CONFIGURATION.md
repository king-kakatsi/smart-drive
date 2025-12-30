# Configuration Guide

Complete guide to configuring Smart-Drive for development and production environments.

## Environment Variables

Smart-Drive uses environment-based configuration for security and flexibility. All configuration is managed through environment variables and `.env` files.

## Core Configuration

### Application Settings

```bash
# Application Environment
DEBUG=true                                    # Enable debug mode (development only)
ENVIRONMENT=development                       # development, staging, production
SECRET_KEY=your-super-secret-key-change-this  # JWT signing key (32+ characters)

# Server Configuration
HOST=0.0.0.0                                 # Server host (0.0.0.0 for all interfaces)
PORT=8000                                    # Server port
WORKERS=4                                    # Number of FastAPI workers (production)

# CORS Settings
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000  # Frontend URLs
ALLOW_CREDENTIALS=true                       # Allow cookies/credentials
ALLOW_METHODS=GET,POST,PUT,DELETE,OPTIONS    # Allowed HTTP methods
ALLOW_HEADERS=*                              # Allowed headers
```

### Database Configuration

```bash
# SQLite Database (Default)
DATABASE_URL=sqlite:///./smart_drive.db      # SQLite database path

# PostgreSQL (Production Recommended)
# DATABASE_URL=postgresql://user:password@localhost:5432/smart_drive

# Database Connection Pool
DB_POOL_SIZE=10                              # Connection pool size
DB_MAX_OVERFLOW=20                           # Max overflow connections
DB_POOL_TIMEOUT=30                           # Connection timeout (seconds)
DB_POOL_RECYCLE=3600                         # Recycle connections (seconds)
```

### File Storage Configuration

```bash
# Local File Storage
UPLOAD_DIR=./uploads                         # Local upload directory
MAX_FILE_SIZE=10485760                       # Max file size in bytes (10MB)
ALLOWED_EXTENSIONS=pdf,docx,txt,mp4,avi,webm,jpg,jpeg,png,gif,mp3,wav

# File Processing
CHUNK_SIZE=1000                              # Text chunk size for embeddings
CHUNK_OVERLAP=200                            # Chunk overlap for context preservation
MAX_CHUNKS_PER_FILE=1000                     # Max chunks per file

# Temporary Files
TEMP_DIR=./temp                              # Temporary file directory
CLEANUP_INTERVAL=3600                        # Cleanup interval (seconds)
```

## AI & External Services

### Groq AI Configuration

```bash
# Required: Groq API Settings
GROQ_API_KEY=gsk_your-api-key-here           # Your Groq API key
GROQ_BASE_URL=https://api.groq.com           # Groq API base URL

# AI Model Settings
GROQ_MODEL=llama3-70b-8192                   # Default model
GROQ_TEMPERATURE=0.1                         # Response creativity (0.0-1.0)
GROQ_MAX_TOKENS=4096                         # Max response tokens
GROQ_TIMEOUT=60                              # Request timeout (seconds)

# Fallback Models
GROQ_FALLBACK_MODEL=llama3-8b-8192           # Fallback model
GROQ_FALLBACK_ENABLED=true                   # Enable fallback on failure
```

### Vector Database (ChromaDB)

```bash
# ChromaDB Configuration
CHROMA_DB_PATH=./chroma_db                   # Local ChromaDB storage path
CHROMA_HOST=localhost                        # ChromaDB host (for remote)
CHROMA_PORT=8000                             # ChromaDB port (for remote)

# Embedding Settings
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2  # Embedding model
EMBEDDING_DIMENSION=384                     # Embedding vector dimension

# Search Settings
SIMILARITY_THRESHOLD=0.7                     # Minimum similarity score
MAX_SEARCH_RESULTS=10                        # Max search results
SEARCH_TIMEOUT=30                            # Search timeout (seconds)
```

### Google Drive Integration

```bash
# Google Drive API (Optional)
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/google/callback

# OAuth2 Scopes
GOOGLE_SCOPES=https://www.googleapis.com/auth/drive.readonly,https://www.googleapis.com/auth/drive.file

# Drive Sync Settings
DRIVE_SYNC_INTERVAL=3600                     # Sync interval (seconds)
DRIVE_MAX_FILES=10000                        # Max files to sync
DRIVE_BATCH_SIZE=50                          # Batch size for API calls
```

### Video Processing (Whisper)

```bash
# Whisper Configuration
WHISPER_MODEL=base                           # Model size: tiny, base, small, medium, large
WHISPER_DEVICE=cpu                           # cpu or cuda
WHISPER_LANGUAGE=auto                        # auto or specific language code

# Audio Processing
AUDIO_SAMPLE_RATE=16000                      # Audio sample rate
AUDIO_CHANNELS=1                            # Audio channels (mono)
AUDIO_FORMAT=wav                            # Audio format

# Transcription Settings
TRANSCRIBE_TIMEOUT=300                       # Max transcription time (seconds)
TRANSCRIBE_BATCH_SIZE=16                     # Batch processing size
```

## Authentication & Security

### JWT Configuration

```bash
# JWT Settings
JWT_SECRET_KEY=your-jwt-secret-key           # JWT signing key
JWT_ALGORITHM=HS256                          # JWT algorithm
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30           # Access token expiry
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7              # Refresh token expiry

# Password Settings
PASSWORD_MIN_LENGTH=8                        # Minimum password length
PASSWORD_REQUIRE_UPPERCASE=true              # Require uppercase letters
PASSWORD_REQUIRE_LOWERCASE=true              # Require lowercase letters
PASSWORD_REQUIRE_DIGITS=true                 # Require digits
PASSWORD_REQUIRE_SPECIAL=true                # Require special characters
```

### Rate Limiting

```bash
# API Rate Limits
RATE_LIMIT_REQUESTS=100                      # Requests per window
RATE_LIMIT_WINDOW=60                         # Time window (seconds)
RATE_LIMIT_BURST=20                          # Burst allowance

# AI-specific Limits
AI_RATE_LIMIT_REQUESTS=50                    # AI requests per window
AI_RATE_LIMIT_WINDOW=60                      # AI time window (seconds)

# File Upload Limits
UPLOAD_RATE_LIMIT_REQUESTS=10                # Upload requests per window
UPLOAD_RATE_LIMIT_WINDOW=60                  # Upload time window (seconds)
```

### Security Headers

```bash
# Content Security Policy
CSP_DEFAULT_SRC=self                        # Default source
CSP_SCRIPT_SRC=self,unsafe-inline           # Script sources
CSP_STYLE_SRC=self,unsafe-inline            # Style sources
CSP_IMG_SRC=self,data:,https:               # Image sources

# HTTPS Settings (Production)
FORCE_HTTPS=true                            # Force HTTPS redirects
HSTS_MAX_AGE=31536000                       # HSTS max age (1 year)
HSTS_INCLUDE_SUBDOMAINS=true                # Include subdomains in HSTS
```

## Logging Configuration

```bash
# Logging Settings
LOG_LEVEL=INFO                              # DEBUG, INFO, WARNING, ERROR
LOG_FORMAT=json                             # json or text
LOG_FILE=./logs/smart_drive.log             # Log file path
LOG_MAX_SIZE=10485760                       # Max log file size (10MB)
LOG_BACKUP_COUNT=5                          # Number of backup files

# Structured Logging
LOG_INCLUDE_REQUEST_ID=true                  # Include request IDs
LOG_INCLUDE_USER_ID=true                     # Include user IDs
LOG_INCLUDE_FILE_ID=true                     # Include file IDs
```

## Monitoring & Metrics

### Prometheus Metrics

```bash
# Metrics Configuration
METRICS_ENABLED=true                        # Enable Prometheus metrics
METRICS_PORT=9090                           # Metrics server port
METRICS_PATH=/metrics                       # Metrics endpoint path

# Application Metrics
METRICS_REQUEST_LATENCY=true                 # Request latency metrics
METRICS_ERROR_RATE=true                      # Error rate metrics
METRICS_ACTIVE_CONNECTIONS=true              # Active connections
```

### Health Checks

```bash
# Health Check Settings
HEALTH_CHECK_ENABLED=true                   # Enable health checks
HEALTH_CHECK_PATH=/health                   # Health check endpoint
HEALTH_CHECK_DATABASE=true                  # Check database connectivity
HEALTH_CHECK_EXTERNAL_APIS=true             # Check external API connectivity
```

## Caching Configuration

```bash
# Redis Cache (Optional)
REDIS_URL=redis://localhost:6379/0          # Redis connection URL
CACHE_TTL=3600                             # Default cache TTL (seconds)

# File Metadata Cache
FILE_CACHE_TTL=1800                        # File metadata cache (30min)
USER_CACHE_TTL=3600                        # User data cache (1hour)

# AI Response Cache
AI_CACHE_ENABLED=true                      # Cache AI responses
AI_CACHE_TTL=7200                          # AI cache TTL (2hours)
```

## Email Configuration (Optional)

```bash
# SMTP Settings
SMTP_SERVER=smtp.gmail.com                 # SMTP server
SMTP_PORT=587                              # SMTP port
SMTP_USERNAME=your-email@gmail.com         # SMTP username
SMTP_PASSWORD=your-app-password            # SMTP password
SMTP_USE_TLS=true                          # Use TLS encryption

# Email Templates
EMAIL_FROM=Smart-Drive <noreply@smart-drive.com>
EMAIL_SUBJECT_PREFIX=[Smart-Drive]         # Email subject prefix
```

## Development Configuration

### Development Overrides

```bash
# Development-specific settings
DEBUG=true
LOG_LEVEL=DEBUG
CORS_ENABLED=true
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000,http://localhost:8080

# Disable external API calls in tests
MOCK_EXTERNAL_APIS=false
```

### Testing Configuration

```bash
# Test Database
TEST_DATABASE_URL=sqlite:///./test_smart_drive.db

# Test API Keys (use test keys)
TEST_GROQ_API_KEY=test-key
TEST_GOOGLE_CLIENT_ID=test-client-id

# Test Settings
TEST_UPLOAD_DIR=./test_uploads
TEST_CHROMA_DB_PATH=./test_chroma_db
```

## Production Configuration

### Production Optimizations

```bash
# Production settings
DEBUG=false
ENVIRONMENT=production
LOG_LEVEL=WARNING

# Performance settings
WORKERS=8
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=30

# Security settings
FORCE_HTTPS=true
SECURE_COOKIES=true
SESSION_COOKIE_SECURE=true

# Monitoring
METRICS_ENABLED=true
HEALTH_CHECKS_ENABLED=true
```

### Docker Production Configuration

```bash
# Docker-specific settings
DOCKER_CONTAINER_NAME=smart-drive-backend
DOCKER_IMAGE_TAG=latest
DOCKER_NETWORK=smart-drive-network

# Volume mounts
DOCKER_UPLOAD_VOLUME=smart-drive-uploads
DOCKER_CHROMA_VOLUME=smart-drive-chroma
DOCKER_LOGS_VOLUME=smart-drive-logs
```

## Configuration Management

### Environment File Structure

```
smart-drive/
├── backend/
│   ├── .env                    # Main environment file
│   ├── .env.example           # Example/template file
│   └── .env.local             # Local overrides (gitignored)
├── frontend/
│   ├── .env                   # Frontend environment
│   └── .env.example
└── docker/
    ├── .env                   # Docker environment
    └── .env.example
```

### Configuration Loading

```python
# backend/app/config.py
from pydantic import BaseSettings, Field
from typing import List, Optional

class Settings(BaseSettings):
    # Application
    debug: bool = Field(default=False, env="DEBUG")
    environment: str = Field(default="development", env="ENVIRONMENT")
    secret_key: str = Field(..., env="SECRET_KEY")

    # Database
    database_url: str = Field(default="sqlite:///./smart_drive.db", env="DATABASE_URL")

    # AI Services
    groq_api_key: str = Field(..., env="GROQ_API_KEY")
    groq_model: str = Field(default="llama3-70b-8192", env="GROQ_MODEL")

    # CORS
    allowed_origins: List[str] = Field(default=["http://localhost:5173"], env="ALLOWED_ORIGINS")

    # File uploads
    max_file_size: int = Field(default=10*1024*1024, env="MAX_FILE_SIZE")  # 10MB
    upload_dir: str = Field(default="./uploads", env="UPLOAD_DIR")

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
```

### Configuration Validation

```python
# Validate critical settings on startup
def validate_configuration():
    """Validate configuration on application startup."""
    required_settings = [
        'secret_key',
        'groq_api_key',
    ]

    missing = []
    for setting in required_settings:
        value = getattr(settings, setting)
        if not value or value.startswith('your-'):
            missing.append(setting)

    if missing:
        raise ValueError(f"Missing required configuration: {', '.join(missing)}")

    # Validate URLs
    if settings.allowed_origins:
        for origin in settings.allowed_origins:
            if not origin.startswith(('http://', 'https://')):
                raise ValueError(f"Invalid origin URL: {origin}")

    # Validate file paths
    if not os.path.exists(settings.upload_dir):
        os.makedirs(settings.upload_dir, exist_ok=True)
```

## Configuration Best Practices

### Security Best Practices

1. **Never commit secrets**: Use `.env` files that are gitignored
2. **Use strong secrets**: Generate cryptographically secure keys
3. **Environment separation**: Different configs for dev/staging/prod
4. **Principle of least privilege**: Minimal required permissions
5. **Rotate secrets regularly**: Change keys periodically

### Performance Best Practices

1. **Connection pooling**: Configure appropriate pool sizes
2. **Caching strategy**: Cache frequently accessed data
3. **Resource limits**: Set appropriate timeouts and limits
4. **Monitoring**: Monitor configuration impact on performance

### Maintainability Best Practices

1. **Documentation**: Document all configuration options
2. **Validation**: Validate configuration on startup
3. **Defaults**: Provide sensible defaults for all settings
4. **Environment-specific**: Separate concerns by environment
5. **Version control**: Track configuration changes

## Troubleshooting Configuration

### Common Configuration Issues

#### Environment Variables Not Loading

**Problem**: Settings not applied from `.env` file
**Solutions**:
```bash
# Check if .env file exists
ls -la .env

# Check file permissions
chmod 600 .env

# Verify variable names match
grep -E "^[A-Z_]+" .env

# Restart application
```

#### Database Connection Issues

**Problem**: Cannot connect to database
**Solutions**:
```bash
# Check DATABASE_URL format
echo $DATABASE_URL

# Test database connectivity
python -c "from sqlalchemy import create_engine; engine = create_engine('$DATABASE_URL'); engine.connect()"

# Check file permissions for SQLite
ls -la smart_drive.db
chmod 664 smart_drive.db
```

#### API Key Issues

**Problem**: External API calls failing
**Solutions**:
```bash
# Verify API keys are set
echo $GROQ_API_KEY | head -c 10  # Should show start of key

# Test API connectivity
curl -H "Authorization: Bearer $GROQ_API_KEY" https://api.groq.com/v1/models

# Check API key format and permissions
```

### Configuration Debugging

```python
# Add configuration debugging
import logging
logging.basicConfig(level=logging.DEBUG)

# Log current configuration (without secrets)
logger.info(f"Debug mode: {settings.debug}")
logger.info(f"Environment: {settings.environment}")
logger.info(f"Database: {settings.database_url.replace('password', '***')}")
logger.info(f"Upload dir: {settings.upload_dir}")
logger.info(f"Max file size: {settings.max_file_size}")
```

## Advanced Configuration

### Multi-environment Setup

```bash
# Create environment-specific files
cp .env .env.development
cp .env .env.production

# Use different configs
export ENV_FILE=.env.production
python -c "from app.config import settings; print(settings.database_url)"
```

### Configuration Encryption

```bash
# Encrypt sensitive configuration
openssl enc -aes-256-cbc -salt -in .env -out .env.enc

# Decrypt for use
openssl enc -d -aes-256-cbc -in .env.enc -out .env
```

### Dynamic Configuration

```python
# Runtime configuration updates (advanced)
from pydantic import BaseSettings
import redis

class DynamicSettings(BaseSettings):
    # Static settings
    app_name: str = "Smart-Drive"

    # Dynamic settings from Redis
    @property
    def max_file_size(self):
        redis_client = redis.Redis()
        cached = redis_client.get('config:max_file_size')
        return int(cached) if cached else 10*1024*1024
```

## Configuration Checklist

- [ ] Environment variables properly set
- [ ] API keys configured and valid
- [ ] Database connectivity confirmed
- [ ] File permissions correct
- [ ] CORS settings appropriate
- [ ] Security headers configured
- [ ] Logging properly configured
- [ ] Monitoring enabled
- [ ] Rate limiting appropriate
- [ ] Caching configured
- [ ] External services accessible
