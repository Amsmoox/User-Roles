# Authentication API Documentation

The Authentication API provides secure user registration, login, logout, and password management functionality.

## Security Features

- **Email Verification**: Users register with email
- **Token-based Authentication**: Secure API access with tokens
- **Rate Limiting**: Protection against brute force attacks
  - Registration/Login: 5 requests per minute
  - Password Reset: 3 requests per hour
- **Secure Password Handling**: Passwords are hashed and never stored in plain text
- **IP Tracking**: Login IP addresses are recorded for security auditing

## API Endpoints

### User Registration

```
POST /api/v1/accounts/auth/register/
```

- **Permissions**: AllowAny
- **Rate Limit**: 5 requests per minute
- **Fields**:
  - email (required, unique)
  - first_name (required)
  - last_name (required)
  - password (required)
  - password_confirm (required)
- **Response**: User details and authentication token
- **Features**:
  - Automatic welcome email
  - Transaction-safe user creation
  - Input validation

### User Login

```
POST /api/v1/accounts/auth/login/
```

- **Permissions**: AllowAny
- **Rate Limit**: 5 requests per minute
- **Fields**:
  - email (required)
  - password (required)
- **Response**: Authentication token and user details
- **Features**:
  - IP address tracking
  - Account status validation

### User Logout

```
POST /api/v1/accounts/auth/logout/
```

- **Permissions**: IsAuthenticated
- **Fields**: None (uses token from Authorization header)
- **Response**: Success message
- **Features**:
  - Token invalidation

### Password Reset Request

```
POST /api/v1/accounts/auth/password/reset/
```

- **Permissions**: AllowAny
- **Rate Limit**: 3 requests per hour
- **Fields**:
  - email (required)
- **Response**: Success message (always the same for security)
- **Features**:
  - Does not reveal if email exists in system
  - Email with secure reset link
  - Unique token generation

### Password Reset Confirmation

```
POST /api/v1/accounts/auth/password/reset/confirm/
```

- **Permissions**: AllowAny
- **Rate Limit**: 3 requests per hour
- **Fields**:
  - uid (required, from reset email)
  - token (required, from reset email)
  - new_password (required)
  - new_password_confirm (required)
- **Response**: Success message
- **Features**:
  - Token validation
  - All existing tokens are invalidated
  - Transaction safety

### Password Change (When Logged In)

```
POST /api/v1/accounts/auth/password/change/
```

- **Permissions**: IsAuthenticated
- **Fields**:
  - current_password (required)
  - new_password (required)
  - new_password_confirm (required)
- **Response**: Success message
- **Features**:
  - Current password verification
  - Other sessions are logged out (tokens invalidated)
  - Current session maintained

## Error Handling

All endpoints return appropriate HTTP status codes:
- `200 OK` for successful operations
- `201 Created` for successful user registration
- `400 Bad Request` for invalid input
- `401 Unauthorized` for authentication failures
- `429 Too Many Requests` for rate limit exceeded

## Example Usage

### Registration

```json
POST /api/v1/accounts/auth/register/
{
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "password": "SecurePassword123",
  "password_confirm": "SecurePassword123"
}
```

Response:
```json
{
  "user": {
    "id": 1,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe"
  },
  "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
  "message": "User registered successfully"
}
```

### Login

```json
POST /api/v1/accounts/auth/login/
{
  "email": "user@example.com",
  "password": "SecurePassword123"
}
```

Response:
```json
{
  "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
  "user_id": 1,
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe"
}
```

### Password Reset Request

```json
POST /api/v1/accounts/auth/password/reset/
{
  "email": "user@example.com"
}
```

Response:
```json
{
  "message": "Password reset email has been sent if the email is registered."
}
``` 