# Security Guide

Comprehensive security guide for Smart-Drive covering authentication, data protection, and best practices.

## Authentication & Authorization

### JWT Authentication

Smart-Drive uses JSON Web Tokens (JWT) for secure authentication:

```python
# JWT token structure
{
  "sub": "user-uuid",           # Subject (user ID)
  "exp": 1640995200,           # Expiration timestamp
  "iat": 1640991600,           # Issued at timestamp
  "iss": "smart-drive",        # Issuer
  "aud": "smart-drive-api",    # Audience
  "type": "access",            # Token type
  "permissions": ["read", "write"]  # User permissions
}
```

#### Token Security Features

```python
# backend/app/core/auth.py
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))

    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "iss": "smart-drive",
        "aud": "smart-drive-api",
        "type": "access"
    })

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # Validate issuer and audience
        if payload.get("iss") != "smart-drive":
            raise JWTError("Invalid issuer")

        if payload.get("aud") != "smart-drive-api":
            raise JWTError("Invalid audience")

        # Check expiration
        if datetime.fromtimestamp(payload["exp"]) < datetime.utcnow():
            raise JWTError("Token expired")

        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

### OAuth2 Integration (Google Drive)

Secure Google Drive integration using OAuth2:

```python
# Google OAuth2 flow
class GoogleOAuthService:
    def __init__(self):
        self.client_id = settings.google_client_id
        self.client_secret = settings.google_client_secret
        self.redirect_uri = settings.google_redirect_uri

    def get_authorization_url(self, state: str) -> str:
        """Generate secure authorization URL."""
        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'scope': 'https://www.googleapis.com/auth/drive.readonly',
            'response_type': 'code',
            'state': state,  # CSRF protection
            'access_type': 'offline',  # For refresh tokens
            'prompt': 'consent'  # Force consent screen
        }
        return f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"

    def exchange_code_for_tokens(self, code: str, state: str) -> dict:
        """Exchange authorization code for access tokens."""
        # Verify state parameter for CSRF protection
        if not self.verify_state(state):
            raise HTTPException(400, "Invalid state parameter")

        token_data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': self.redirect_uri
        }

        response = requests.post(
            'https://oauth2.googleapis.com/token',
            data=token_data,
            timeout=30
        )

        if response.status_code != 200:
            raise HTTPException(400, "Token exchange failed")

        return response.json()
```

### Session Management

Secure session handling with automatic cleanup:

```python
# Session security middleware
class SessionSecurityMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "websocket":
            # WebSocket session security
            headers = dict(scope.get("headers", []))
            auth_header = headers.get(b"authorization", b"").decode()

            if not auth_header.startswith("Bearer "):
                await self._close_connection(send, 4001, "Authentication required")
                return

            token = auth_header[7:]  # Remove "Bearer "
            try:
                payload = verify_token(token)
                scope["user"] = payload
            except JWTError:
                await self._close_connection(send, 4001, "Invalid token")
                return

        await self.app(scope, receive, send)

    async def _close_connection(self, send, code, reason):
        await send({
            "type": "websocket.close",
            "code": code,
            "reason": reason
        })
```

## Data Protection

### File Upload Security

Comprehensive file upload validation and security:

```python
# backend/app/services/file_service.py
class SecureFileService:
    # Allowed file types with MIME type validation
    ALLOWED_TYPES = {
        'pdf': ['application/pdf'],
        'docx': ['application/vnd.openxmlformats-officedocument.wordprocessingml.document'],
        'txt': ['text/plain'],
        'mp4': ['video/mp4'],
        'jpg': ['image/jpeg'],
        'png': ['image/png'],
        # ... more types
    }

    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    VIRUS_SCAN_ENABLED = True

    async def validate_and_save_file(self, upload_file: UploadFile, user_id: str) -> str:
        """Secure file upload with comprehensive validation."""

        # 1. Filename security
        safe_filename = self._sanitize_filename(upload_file.filename)

        # 2. File type validation
        content_type = upload_file.content_type
        file_extension = self._get_file_extension(safe_filename)

        if file_extension not in self.ALLOWED_TYPES:
            raise HTTPException(400, "File type not allowed")

        if content_type not in self.ALLOWED_TYPES[file_extension]:
            raise HTTPException(400, "Invalid file content type")

        # 3. Content validation (magic numbers)
        file_content = await upload_file.read(1024)  # Read first 1KB
        await upload_file.seek(0)  # Reset file pointer

        if not self._validate_file_signature(file_content, file_extension):
            raise HTTPException(400, "Invalid file format")

        # 4. Size validation
        file_size = 0
        content_chunks = []
        while chunk := await upload_file.read(8192):
            file_size += len(chunk)
            if file_size > self.MAX_FILE_SIZE:
                raise HTTPException(400, "File too large")
            content_chunks.append(chunk)

        # 5. Virus scanning (if enabled)
        if self.VIRUS_SCAN_ENABLED:
            full_content = b''.join(content_chunks)
            if await self._scan_for_viruses(full_content):
                raise HTTPException(400, "File contains malware")

        # 6. Secure storage
        file_path = self._generate_secure_path(user_id, safe_filename)
        await self._save_file_securely(file_path, content_chunks)

        return file_path

    def _sanitize_filename(self, filename: str) -> str:
        """Remove dangerous characters from filename."""
        # Remove path separators and dangerous characters
        safe_name = re.sub(r'[<>:"/\\|?*]', '', filename)
        # Limit length
        return safe_name[:255] if len(safe_name) > 255 else safe_name

    def _validate_file_signature(self, content: bytes, extension: str) -> bool:
        """Validate file magic numbers."""
        signatures = {
            'pdf': b'%PDF',
            'png': b'\x89PNG\r\n\x1a\n',
            'jpg': b'\xff\xd8\xff',
            'mp4': b'ftyp',
            # ... more signatures
        }

        expected_signature = signatures.get(extension)
        return content.startswith(expected_signature) if expected_signature else True
```

### Database Security

Secure database operations with parameterized queries:

```python
# backend/app/database.py
from sqlalchemy import create_engine, text
from sqlalchemy.pool import QueuePool

# Secure database configuration
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    pool_recycle=3600,
    echo=False,  # Never enable in production
    connect_args={
        "check_same_thread": False,  # SQLite specific
        # PostgreSQL SSL: "sslmode": "require"
    }
)

def execute_secure_query(query: str, params: dict = None):
    """Execute parameterized queries to prevent SQL injection."""
    with engine.connect() as conn:
        try:
            result = conn.execute(text(query), params or {})
            conn.commit()
            return result
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise
```

### API Security

Rate limiting and request validation:

```python
# backend/app/core/rate_limiting.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])

# Apply rate limiting to routes
@router.post("/files/upload")
@limiter.limit("10/minute")  # Stricter limit for uploads
async def upload_file(file: UploadFile):
    # Upload logic here
    pass

# AI-specific rate limiting
@router.websocket("/ws/chat")
@limiter.limit("50/minute")  # AI requests per minute
async def chat_websocket(websocket: WebSocket):
    # Chat logic here
    pass
```

## Encryption & Key Management

### Data Encryption at Rest

```python
# backend/app/core/encryption.py
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os

class DataEncryption:
    def __init__(self, master_key: str):
        """Initialize encryption with master key."""
        # Derive encryption key from master key
        salt = b'smart_drive_salt_2024'  # Store salt securely
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(master_key.encode()))
        self.fernet = Fernet(key)

    def encrypt_sensitive_data(self, data: str) -> str:
        """Encrypt sensitive data like API keys."""
        encrypted = self.fernet.encrypt(data.encode())
        return encrypted.decode()

    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data."""
        decrypted = self.fernet.decrypt(encrypted_data.encode())
        return decrypted.decode()

# Usage for storing OAuth tokens
class SecureTokenStorage:
    def __init__(self, encryption: DataEncryption):
        self.encryption = encryption

    def store_google_tokens(self, user_id: str, tokens: dict):
        """Securely store Google OAuth tokens."""
        encrypted_access = self.encryption.encrypt_sensitive_data(tokens['access_token'])
        encrypted_refresh = self.encryption.encrypt_sensitive_data(tokens['refresh_token'])

        # Store in database
        db.execute_secure_query("""
            INSERT INTO google_tokens (user_id, access_token, refresh_token, expires_at)
            VALUES (:user_id, :access_token, :refresh_token, :expires_at)
        """, {
            'user_id': user_id,
            'access_token': encrypted_access,
            'refresh_token': encrypted_refresh,
            'expires_at': tokens['expires_at']
        })
```

### Secure Key Storage

```python
# Environment variable validation
def validate_secret_key():
    """Validate that secret key meets security requirements."""
    secret = os.getenv('SECRET_KEY')

    if not secret:
        raise ValueError("SECRET_KEY environment variable is required")

    if len(secret) < 32:
        raise ValueError("SECRET_KEY must be at least 32 characters long")

    if secret == "your-secret-key":
        raise ValueError("Please change the default SECRET_KEY")

    return secret

# Secure key rotation
class KeyRotationManager:
    def __init__(self):
        self.current_key_id = "key_v1"
        self.keys = {
            "key_v1": os.getenv('CURRENT_SECRET_KEY'),
            "key_v2": os.getenv('PREVIOUS_SECRET_KEY'),  # For gradual rotation
        }

    def get_current_key(self):
        return self.keys[self.current_key_id]

    def rotate_keys(self):
        """Gradually rotate to new key."""
        new_key_id = f"key_v{int(self.current_key_id.split('_v')[1]) + 1}"
        self.keys[new_key_id] = self._generate_new_key()
        self.current_key_id = new_key_id

        # Remove old keys after grace period
        old_keys = [k for k in self.keys.keys() if k != new_key_id]
        # Schedule cleanup after token expiration
```

## Network Security

### HTTPS Configuration

```python
# backend/app/main.py
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

# Security middleware
app.add_middleware(HTTPSRedirectMiddleware)
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["smart-drive.com", "*.smart-drive.com"]
)

# SSL/TLS configuration for production
ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
ssl_context.load_cert_chain(
    certfile="/path/to/certificate.pem",
    keyfile="/path/to/private_key.pem"
)

# Run with SSL
if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=443,
        ssl_certfile="/path/to/certificate.pem",
        ssl_keyfile="/path/to/private_key.pem"
    )
```

### CORS Security

```python
# backend/app/main.py
from fastapi.middleware.cors import CORSMiddleware

# CORS configuration with security
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://smart-drive.com",
        "https://app.smart-drive.com",
        # Development origins (only in dev mode)
        "http://localhost:5173" if settings.debug else None,
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=[
        "Authorization",
        "Content-Type",
        "X-Requested-With",
    ],
    max_age=86400,  # 24 hours
)
```

### WebSocket Security

```python
# WebSocket connection validation
async def validate_websocket_connection(websocket: WebSocket, token: str):
    """Comprehensive WebSocket security validation."""

    # 1. Origin validation
    origin = websocket.headers.get("origin")
    allowed_origins = settings.allowed_origins

    if origin not in allowed_origins:
        await websocket.close(code=4003, reason="Origin not allowed")
        return False

    # 2. Token validation
    try:
        payload = verify_token(token)
        user_id = payload.get("sub")
    except JWTError:
        await websocket.close(code=4001, reason="Invalid authentication")
        return False

    # 3. User session validation
    user = await get_user_by_id(user_id)
    if not user or not user.is_active:
        await websocket.close(code=4001, reason="User not active")
        return False

    # 4. Rate limiting per user
    if not await check_user_rate_limit(user_id, "websocket"):
        await websocket.close(code=4002, reason="Rate limit exceeded")
        return False

    # 5. Connection limits
    active_connections = await get_user_connection_count(user_id)
    if active_connections >= settings.max_websocket_connections_per_user:
        await websocket.close(code=4002, reason="Connection limit exceeded")
        return False

    return True
```

## Security Headers

### Comprehensive Security Headers

```python
# backend/app/middleware/security_headers.py
from fastapi.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)

        # Content Security Policy
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self'; "
            "connect-src 'self' wss: https:;"
        )

        # HTTPS Strict Transport Security
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        # X-Frame-Options
        response.headers["X-Frame-Options"] = "DENY"

        # X-Content-Type-Options
        response.headers["X-Content-Type-Options"] = "nosniff"

        # Referrer-Policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Permissions-Policy
        response.headers["Permissions-Policy"] = (
            "geolocation=(), microphone=(), camera=()"
        )

        return response
```

## Input Validation & Sanitization

### Request Validation

```python
# backend/app/models/validation.py
from pydantic import BaseModel, validator, Field
from typing import Optional, List
import re

class FileUploadRequest(BaseModel):
    filename: str = Field(..., min_length=1, max_length=255)
    content_type: str
    size: int = Field(..., gt=0, le=10*1024*1024)  # Max 10MB

    @validator('filename')
    def validate_filename(cls, v):
        if not re.match(r'^[a-zA-Z0-9._\-\s]+$', v):
            raise ValueError('Invalid filename characters')
        return v

    @validator('content_type')
    def validate_content_type(cls, v):
        allowed_types = [
            'application/pdf', 'text/plain',
            'video/mp4', 'image/jpeg', 'image/png'
        ]
        if v not in allowed_types:
            raise ValueError('Unsupported content type')
        return v

class ChatMessageRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    file_ids: Optional[List[str]] = []
    conversation_id: Optional[str] = None

    @validator('message')
    def sanitize_message(cls, v):
        # Remove potentially dangerous content
        v = re.sub(r'<[^>]+>', '', v)  # Remove HTML tags
        v = v.strip()
        if not v:
            raise ValueError('Message cannot be empty after sanitization')
        return v

    @validator('file_ids')
    def validate_file_ids(cls, v):
        if v and len(v) > 10:  # Limit number of files
            raise ValueError('Too many files selected')
        return v
```

### SQL Injection Prevention

```python
# Secure database queries
def get_user_files_secure(user_id: str, limit: int = 50):
    """Secure parameterized query."""
    query = """
        SELECT id, filename, file_path, upload_date, file_size
        FROM files
        WHERE user_id = :user_id
        ORDER BY upload_date DESC
        LIMIT :limit
    """

    params = {
        'user_id': user_id,
        'limit': min(limit, 100)  # Enforce maximum limit
    }

    return execute_secure_query(query, params)
```

## Monitoring & Logging

### Security Event Logging

```python
# backend/app/core/security_logger.py
import logging
import json
from datetime import datetime

class SecurityLogger:
    def __init__(self):
        self.logger = logging.getLogger('security')
        self.logger.setLevel(logging.INFO)

        # Security-specific log format
        formatter = logging.Formatter(
            '%(asctime)s - SECURITY - %(levelname)s - %(message)s'
        )

        # File handler for security events
        handler = logging.FileHandler('logs/security.log')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def log_auth_event(self, event_type: str, user_id: str = None,
                      ip_address: str = None, details: dict = None):
        """Log authentication events."""
        event = {
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': event_type,
            'user_id': user_id,
            'ip_address': ip_address,
            'details': details or {}
        }

        self.logger.info(json.dumps(event))

    def log_security_violation(self, violation_type: str, user_id: str = None,
                              ip_address: str = None, details: dict = None):
        """Log security violations."""
        self.logger.warning(json.dumps({
            'timestamp': datetime.utcnow().isoformat(),
            'violation_type': violation_type,
            'user_id': user_id,
            'ip_address': ip_address,
            'details': details or {}
        }))

# Usage
security_logger = SecurityLogger()

# Log successful login
security_logger.log_auth_event(
    'login_success',
    user_id=user.id,
    ip_address=request.client.host
)

# Log failed login attempt
security_logger.log_security_violation(
    'failed_login',
    ip_address=request.client.host,
    details={'attempted_username': username}
)

# Log suspicious activity
security_logger.log_security_violation(
    'rate_limit_exceeded',
    user_id=user.id,
    ip_address=request.client.host
)
```

### Intrusion Detection

```python
# backend/app/core/intrusion_detection.py
class IntrusionDetector:
    def __init__(self):
        self.failed_attempts = {}
        self.blocked_ips = set()
        self.suspicious_patterns = []

    def check_failed_login(self, ip_address: str, username: str):
        """Track failed login attempts."""
        key = f"{ip_address}:{username}"

        if key not in self.failed_attempts:
            self.failed_attempts[key] = {'count': 0, 'first_attempt': datetime.utcnow()}

        self.failed_attempts[key]['count'] += 1
        self.failed_attempts[key]['last_attempt'] = datetime.utcnow()

        # Check for brute force attack
        if self.failed_attempts[key]['count'] >= 5:
            self.block_ip(ip_address, "Brute force login attempt")
            return True

        return False

    def check_suspicious_request(self, request, user_id: str = None):
        """Check for suspicious request patterns."""
        # Check for SQL injection patterns
        sql_patterns = [
            r'union\s+select', r';\s*drop', r'--', r'/\*.*\*/',
            r'script\s*>\s*alert', r'on\w+\s*=',
        ]

        request_data = str(request.url) + str(request.query_params)

        for pattern in sql_patterns:
            if re.search(pattern, request_data, re.IGNORECASE):
                self.log_suspicious_activity(
                    'suspicious_pattern_detected',
                    user_id,
                    request.client.host,
                    {'pattern': pattern, 'url': str(request.url)}
                )
                return True

        return False

    def block_ip(self, ip_address: str, reason: str):
        """Block an IP address."""
        self.blocked_ips.add(ip_address)

        # Log blocking
        security_logger.log_security_violation(
            'ip_blocked',
            ip_address=ip_address,
            details={'reason': reason}
        )

    def is_ip_blocked(self, ip_address: str) -> bool:
        """Check if IP is blocked."""
        return ip_address in self.blocked_ips
```

## Incident Response

### Security Incident Handling

```python
# backend/app/core/incident_response.py
class IncidentResponse:
    def __init__(self):
        self.active_incidents = {}
        self.escalation_contacts = [
            'security@smart-drive.com',
            'admin@smart-drive.com'
        ]

    def handle_security_incident(self, incident_type: str, details: dict,
                                severity: str = 'medium'):
        """Handle security incidents systematically."""

        incident_id = str(uuid.uuid4())

        incident = {
            'id': incident_id,
            'type': incident_type,
            'severity': severity,
            'timestamp': datetime.utcnow(),
            'details': details,
            'status': 'investigating',
            'actions_taken': []
        }

        self.active_incidents[incident_id] = incident

        # Log incident
        security_logger.log_security_violation(
            'incident_detected',
            details={
                'incident_id': incident_id,
                'type': incident_type,
                'severity': severity,
                **details
            }
        )

        # Immediate response actions
        if severity in ['high', 'critical']:
            self._trigger_emergency_response(incident)

        # Automated response based on incident type
        self._automated_response(incident_type, details)

        return incident_id

    def _automated_response(self, incident_type: str, details: dict):
        """Execute automated response actions."""
        responses = {
            'brute_force_attack': self._block_attacker_ip,
            'sql_injection_attempt': self._strengthen_waf_rules,
            'unauthorized_access': self._revoke_user_sessions,
            'data_breach_suspicion': self._isolate_system,
        }

        if incident_type in responses:
            responses[incident_type](details)

    def _trigger_emergency_response(self, incident: dict):
        """Trigger emergency response for critical incidents."""
        # Immediate actions for critical incidents
        self._isolate_system(incident['details'])
        self._notify_security_team(incident)
        self._enable_incident_mode()

    def _isolate_system(self, details: dict):
        """Isolate system from external access."""
        # Switch to maintenance mode
        # Block all external connections except monitoring
        # Enable emergency logging
        pass

    def _notify_security_team(self, incident: dict):
        """Notify security team immediately."""
        message = f"""
        🚨 CRITICAL SECURITY INCIDENT 🚨

        Incident ID: {incident['id']}
        Type: {incident['type']}
        Severity: {incident['severity']}
        Time: {incident['timestamp']}

        Details: {json.dumps(incident['details'], indent=2)}

        Immediate action required!
        """

        # Send to all escalation contacts
        for contact in self.escalation_contacts:
            self._send_alert_email(contact, "CRITICAL SECURITY INCIDENT", message)
```

## Compliance & Auditing

### GDPR Compliance

```python
# backend/app/core/gdpr.py
class GDPRCompliance:
    def __init__(self):
        self.data_retention_days = 2555  # 7 years for GDPR

    def handle_data_deletion_request(self, user_id: str):
        """Handle GDPR right to erasure."""
        # 1. Identify all user data
        user_data = self._get_all_user_data(user_id)

        # 2. Anonymize or delete personal data
        self._anonymize_personal_data(user_id)

        # 3. Delete account
        self._delete_user_account(user_id)

        # 4. Log deletion for audit
        security_logger.log_auth_event(
            'gdpr_data_deletion',
            user_id=user_id,
            details={'data_types_deleted': list(user_data.keys())}
        )

        return {
            'status': 'completed',
            'data_deleted': user_data,
            'timestamp': datetime.utcnow()
        }

    def handle_data_export_request(self, user_id: str):
        """Handle GDPR data portability."""
        user_data = self._get_all_user_data(user_id)

        # Export in machine-readable format
        export_data = {
            'user_profile': user_data['profile'],
            'files': user_data['files'],
            'chat_history': user_data['chats'],
            'export_timestamp': datetime.utcnow().isoformat(),
            'gdpr_compliant': True
        }

        # Log export for audit
        security_logger.log_auth_event(
            'gdpr_data_export',
            user_id=user_id,
            details={'export_size': len(json.dumps(export_data))}
        )

        return export_data

    def _get_all_user_data(self, user_id: str) -> dict:
        """Collect all user data for GDPR operations."""
        return {
            'profile': self._get_user_profile(user_id),
            'files': self._get_user_files(user_id),
            'chats': self._get_user_chats(user_id),
            'tokens': self._get_user_tokens(user_id),
        }

    def schedule_data_cleanup(self):
        """Regular cleanup of old data."""
        cutoff_date = datetime.utcnow() - timedelta(days=self.data_retention_days)

        # Delete old inactive accounts
        deleted_accounts = db.execute_secure_query("""
            DELETE FROM users
            WHERE is_active = false
            AND last_login < :cutoff_date
        """, {'cutoff_date': cutoff_date})

        # Anonymize old chat data
        db.execute_secure_query("""
            UPDATE chat_messages
            SET content = '[REDACTED - GDPR]'
            WHERE created_at < :cutoff_date
            AND retention_period_expired = true
        """, {'cutoff_date': cutoff_date})

        security_logger.log_auth_event(
            'gdpr_data_cleanup',
            details={
                'deleted_accounts': deleted_accounts.rowcount,
                'anonymized_messages': True,
                'cutoff_date': cutoff_date.isoformat()
            }
        )
```

### Security Best Practices

1. **Defense in Depth**: Multiple security layers
2. **Principle of Least Privilege**: Minimal required permissions
3. **Fail-Safe Defaults**: Secure defaults, explicit allow
4. **Zero Trust Architecture**: Never trust, always verify
5. **Security by Design**: Security built into architecture
6. **Regular Security Audits**: Periodic security assessments
7. **Incident Response Plan**: Documented response procedures
8. **Security Training**: Regular security awareness training

## Security Checklist

### Development Security
- [ ] Input validation on all endpoints
- [ ] Parameterized database queries
- [ ] Secure authentication implementation
- [ ] Proper error handling (no sensitive data leakage)
- [ ] HTTPS everywhere in production
- [ ] Security headers configured
- [ ] CORS properly configured
- [ ] Rate limiting implemented

### Data Protection
- [ ] Sensitive data encrypted at rest
- [ ] Secure key management
- [ ] File upload validation
- [ ] SQL injection prevention
- [ ] XSS protection
- [ ] CSRF protection

### Infrastructure Security
- [ ] Network segmentation
- [ ] Firewall rules
- [ ] Intrusion detection
- [ ] Regular security updates
- [ ] Backup security
- [ ] Monitoring and alerting

### Compliance
- [ ] GDPR compliance
- [ ] Data retention policies
- [ ] Privacy by design
- [ ] Regular security audits
- [ ] Incident response procedures
