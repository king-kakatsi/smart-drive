# OAuth Authentication Flow

This document describes the complete OAuth 2.0 authentication flow in the SmartDrive backend, including Google OAuth integration and JWT token management.

## Architecture Overview

The authentication system follows a layered architecture:

- **Routers**: API endpoints and HTTP request handling
- **Core**: Business logic, external API integrations, and complex operations
- **Services**: Database operations and data persistence

## Complete Authentication Flow

### Frontend Layer (Vue.js Application)

#### `stores/auth.js` - Authentication State Management

**Store State:**
- `user`: Current user profile (null when not authenticated)
- `isLoading`: Loading state for auth operations
- `error`: Authentication error messages

**Key Actions:**
- `initializeAuthentication()`: Checks existing auth state on app load
- `initiateGoogleLogin()`: Starts OAuth flow
- `handleOAuthCallback()`: Processes OAuth return with JWT token
- `fetchCurrentUser()`: Gets fresh user profile from API
- `refreshAccessToken()`: Manually refreshes JWT token

**Initialization Flow:**
```
App Start (main.js)
    ↓
useAuthStore().initializeAuthentication()
    ↓
Check localStorage for existing token
    ↓
If token exists → fetchCurrentUser()
    ↓
Store user profile + set authenticated state
```

#### `services/api/authenticationService.js` - API Communication

**Token Management:**
- `storeAccessToken(token)`: Stores JWT in localStorage
- `getAccessToken()`: Retrieves JWT from localStorage
- `clearTokens()`: Removes all stored tokens
- `isAuthenticated()`: Checks if user has valid token

**API Calls:**
- `getGoogleAuthorizationUrl()`: GET `/api/v1/auth/google/login`
- `getCurrentUserProfile()`: GET `/api/v1/auth/me`
- `refreshAccessToken()`: POST `/api/v1/auth/refresh`

#### `router/index.js` - Route Protection

**Navigation Guard:**
```javascript
router.beforeEach((to, from, next) => {
  const isAuthenticated = authenticationService.isAuthenticated()
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)

  if (requiresAuth && !isAuthenticated) {
    next({ name: 'Login' })
  } else if (to.name === 'Login' && isAuthenticated) {
    next({ name: 'Dashboard' })
  } else {
    next()
  }
})
```

**Protected Routes:** Dashboard, FileExplorer, AIChat, Settings, etc.
**Public Routes:** Login, AuthCallback

### OAuth Flow Diagrams

#### Phase 1: OAuth Initiation (Frontend → Backend)

```
User clicks "Sign in with Google" (Login.vue)
    ↓
stores/auth.js::initiateGoogleLogin()
    ↓
services/api/authenticationService.js::getGoogleAuthorizationUrl()
    ↓
apiClient.get('/api/v1/auth/google/login')
    ↓
routers/auth.py::google_login()
    ↓
core/drive_client.py::get_google_auth_url()
    ↓
GoogleDriveClient.get_auth_url()
    ↓
Returns: {"auth_url": "https://accounts.google.com/o/oauth2/v2/auth?..."}

Frontend Action:
window.location.href = response.auth_url
    ↓
HTTP Redirect to Google OAuth Consent Screen
```

#### Phase 2: OAuth Callback & Token Processing (Backend)

```
Google OAuth Consent → Redirect to /api/v1/auth/google/callback?code=...&state=...
    ↓
routers/auth.py::google_callback(code, state, db)
    │
    ├─ core/drive_client.py::exchange_code_for_tokens(code)
    │   └─ GoogleDriveClient.exchange_code_for_tokens(code)
    │       └─ POST https://oauth2.googleapis.com/token
    │           Returns: {access_token, refresh_token, expires_in}
    │
    ├─ core/drive_client.py::get_google_user_info(access_token)
    │   └─ GoogleDriveClient.get_user_info(access_token)
    │       └─ GET https://www.googleapis.com/oauth2/v2/userinfo
    │           Returns: {email, name, id, picture}
    │
    ├─ services/user_service.py::create_or_update_user(user_data, db)
    │   └─ Creates or updates user record in database
    │
    ├─ services/google_token_service.py::store_google_tokens_for_user(...)
    │   └─ Stores Google access_token and refresh_token in database
    │
    └─ core/auth.py::create_access_token({"sub": user.id})
        └─ Generates JWT token for application authentication

Backend Response:
HTTP 302 Redirect to: http://localhost:5173/auth/callback?token={JWT}&user_id={id}
```

#### Phase 3: Frontend OAuth Callback Processing

```
Browser redirected to /auth/callback?token=JWT&user_id=123 (AuthCallback.vue)
    ↓
onMounted() → stores/auth.js::handleOAuthCallback()
    ↓
Extract token and user_id from URL parameters
    ↓
services/api/authenticationService.js::storeAccessToken(JWT)
    ↓
Stores JWT token in localStorage
    ↓
stores/auth.js::fetchCurrentUser()
    ↓
services/api/authenticationService.js::getCurrentUserProfile()
    ↓
apiClient.get('/api/v1/auth/me') with Authorization: Bearer JWT
    ↓
routers/auth.py::get_current_user_info() → Returns user profile
    ↓
stores/auth.js: Store user profile + set authenticated state
    ↓
router.push({ name: 'Dashboard' })
    ↓
Navigation guard allows access to protected routes
```

#### Phase 4: Ongoing Authentication Management

```
App Initialization (main.js)
    ↓
useAuthStore().initializeAuthentication()
    │
    ├─ Check localStorage for existing JWT token
    │   ↓
    │   If token exists → fetchCurrentUser()
    │   ↓
    │   GET /api/v1/auth/me → Validate token + get fresh user profile
    │   ↓
    │   Store user profile in Pinia store
    │
    └─ If no token → Stay in unauthenticated state

Route Navigation (router/index.js)
    ↓
Navigation Guard: router.beforeEach()
    │
    ├─ Check if route requires authentication
    │   ↓
    │   If requires auth && not authenticated → Redirect to /login
    │
    └─ If authenticated && accessing /login → Redirect to /dashboard

Token Expiration Handling:
Any API call with expired JWT → 401 Unauthorized
    ↓
stores/auth.js::handleLogout()
    ↓
Clear localStorage + redirect to login
```

## Detailed Component Analysis

### 1. Routers Layer (API Endpoints)

#### `routers/auth.py`

**Endpoints:**
- `GET /api/v1/auth/google/login` - Initiates OAuth flow
- `GET /api/v1/auth/google/callback` - Handles OAuth callback
- `POST /api/v1/auth/refresh` - Refreshes JWT tokens
- `GET /api/v1/auth/me` - Returns current user info
- `POST /api/v1/auth/logout` - Handles logout

**Responsibilities:**
- HTTP request/response handling
- Input validation
- Error handling and HTTP status codes
- Orchestration of authentication flow

### 2. Core Layer (Business Logic & External APIs)

#### `core/auth.py` - JWT Token Management

**Functions:**
- `create_access_token(data)` - Generates signed JWT tokens
- `verify_token(token, db)` - Validates JWT and retrieves user
- `decode_token(token)` - Decodes JWT without validation

**Responsibilities:**
- JWT token creation and validation
- User authentication state management
- Cryptographic operations

#### `core/drive_client.py` - Google OAuth Integration

**GoogleDriveClient Class:**
- `get_auth_url(state)` - Constructs Google OAuth authorization URL
- `exchange_code_for_tokens(code)` - Exchanges authorization code for tokens
- `get_user_info(access_token)` - Retrieves user information from Google

**OAuth Configuration:**
```python
scope = "openid https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/userinfo.profile https://www.googleapis.com/auth/drive"
access_type = "offline"  # Requests refresh token
prompt = "consent"       # Forces consent screen for refresh token
```

**Responsibilities:**
- Google OAuth 2.0 protocol implementation
- HTTP communication with Google APIs
- Token exchange and user data retrieval

### 3. Services Layer (Data Persistence)

#### `services/user_service.py` - User Management

**Functions:**
- `create_or_update_user(user_data, db)` - Creates new users or updates existing ones
- `get_user_by_id(user_id, db)` - Retrieves user by ID
- `get_user_by_email(email, db)` - Retrieves user by email

**Responsibilities:**
- User data persistence
- Account creation and updates
- User lookup operations

#### `services/google_token_service.py` - Google Token Management

**Functions:**
- `store_google_tokens_for_user(db, user_id, tokens...)` - Stores Google tokens
- `get_valid_access_token_for_user(db, user_id)` - Retrieves valid access token with auto-refresh
- `refresh_expired_google_token(db, user_id)` - Refreshes expired tokens via Google API

**Auto-refresh Logic:**
```python
# Checks if token expires within 5 minutes
if datetime.utcnow() >= token.expires_at - timedelta(minutes=5):
    if token.refresh_token:
        new_token = refresh_via_google_api(db, user_id)
        return new_token
```

**Responsibilities:**
- Google token persistence
- Automatic token refresh
- Token expiration management

## Token Management

### JWT Tokens (Application Authentication)

- **Lifetime**: Configurable via `JWT_EXPIRATION_HOURS` (default: 24 hours)
- **Storage**: Client-side (localStorage)
- **Refresh**: Manual via `/auth/refresh` endpoint
- **Format**: Standard JWT with user ID in `sub` claim

### Google OAuth Tokens

- **Access Token**: Short-lived (1 hour), used for API calls
- **Refresh Token**: Long-lived, used to obtain new access tokens
- **Storage**: Server-side database
- **Refresh**: Automatic when access token expires

## Security Considerations

1. **Token Storage**:
   - JWT tokens stored client-side
   - Google tokens stored server-side for security

2. **Auto-refresh**:
   - Google tokens refreshed automatically server-side
   - JWT tokens require manual refresh

3. **Scopes**:
   - Minimal required scopes for functionality
   - `offline` access for refresh tokens

4. **State Protection**:
   - OAuth state parameter supported for CSRF protection

## Error Handling

- **Token Expiration**: Automatic refresh for Google tokens, manual for JWT
- **Network Errors**: Proper error propagation and user feedback
- **Invalid Tokens**: Graceful logout and re-authentication

## API Endpoints Summary

| Endpoint | Method | Purpose | Frontend Usage |
|----------|--------|---------|----------------|
| `/auth/google/login` | GET | Initiate OAuth flow | `authenticationService.getGoogleAuthorizationUrl()` |
| `/auth/google/callback` | GET | Handle OAuth callback | Backend redirect only |
| `/auth/refresh` | POST | Refresh JWT token | `authenticationService.refreshAccessToken()` |
| `/auth/me` | GET | Get current user info | `authenticationService.getCurrentUserProfile()` |
| `/auth/logout` | POST | Logout user | `authenticationService.logout()` |

## Frontend Architecture

### Vue.js Components

**Authentication Views:**
- `Login.vue`: Google OAuth initiation page
- `AuthCallback.vue`: OAuth callback processing page

**State Management:**
- `stores/auth.js`: Pinia store for authentication state
- Reactive user profile, loading states, and error handling

### Route Protection

**Navigation Guards:**
- Automatic redirect to login for protected routes
- Automatic redirect to dashboard when already authenticated
- Applied to all routes with `meta: { requiresAuth: true }`

**Protected Routes:** Dashboard, FileExplorer, AIChat, Settings, Recent, Starred, Trash
**Public Routes:** Login, AuthCallback

### Token Storage

**localStorage Management:**
- JWT tokens stored client-side for persistence across browser sessions
- User profiles cached locally for performance
- Automatic cleanup on logout

This authentication system provides secure, seamless integration with Google OAuth while maintaining application-specific JWT token management and a smooth user experience across the Vue.js frontend.
