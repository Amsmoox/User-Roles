# Accounts API Documentation [By Mharrech Ayoub]

The Accounts API provides a comprehensive user and role management system with role-based permissions.

## Key Features

- **Email-based Authentication**: Users authenticate with email instead of username
- **Role-based Permission System**: Hierarchical roles with permission inheritance
- **Permission Auditing**: Complete audit trail of all permission changes
- **API Throttling**: Rate limiting to prevent abuse
- **Performance Optimizations**: Caching and query optimization
- **Bulk Operations**: Support for batch processing
- **Multiple Response Formats**: Support for JSON, API, and more

## Authentication

All endpoints require authentication except where noted. Use Django's session authentication or token-based authentication.

## Rate Limiting

API requests are subject to rate limiting:
- **Authenticated Users**: 60 requests per minute
- **Anonymous Users**: 20 requests per minute

When limits are exceeded, a `429 Too Many Requests` response will be returned.

## Pagination

All list endpoints are paginated with 10 items per page by default. You can adjust the page size (up to 100 items) using the `?page_size=` parameter.

## API Endpoints

### User Management

#### List Users
```
GET /api/v1/accounts/users/
```
- **Permissions**: Authenticated users
- **Filters**: `?search=` (email, first/last name)
- **Ordering**: `?ordering=email`, `?ordering=-date_joined`, etc.
- **Format options**: Add .json, .api (e.g., `/users.json`)

#### Get User Details
```
GET /api/v1/accounts/users/{id}/
```
- **Permissions**: Authenticated users

#### Create User
```
POST /api/v1/accounts/users/
```
- **Permissions**: Admin users only
- **Fields**:
  - email (required, unique)
  - first_name (required)
  - last_name (required)
  - password (required)
  - password_confirm (required)
  - role (optional)
  - bio (optional)
  - profile_image (optional)

#### Update User
```
PUT/PATCH /api/v1/accounts/users/{id}/
```
- **Permissions**: Admin users only
- **Note**: When updating passwords, both `password` and `password_confirm` must be provided

#### Delete User
```
DELETE /api/v1/accounts/users/{id}/
```
- **Permissions**: Admin users only

#### Get Current User
```
GET /api/v1/accounts/users/me/
```
- **Permissions**: Authenticated users
- **Cache**: Responses are cached for 5 minutes

#### Activate User
```
POST /api/v1/accounts/users/{id}/activate/
```
- **Permissions**: Admin users only

#### Deactivate User
```
POST /api/v1/accounts/users/{id}/deactivate/
```
- **Permissions**: Admin users only
- **Note**: Users cannot deactivate their own accounts

#### Bulk Create Users
```
POST /api/v1/accounts/users/bulk_create/
```
- **Permissions**: Admin users only
- **Input**: List of user objects
- **Response**: Summary of created users and any errors
- **Note**: Uses transactions to ensure consistency

### Role Management

#### List Roles
```
GET /api/v1/accounts/roles/
```
- **Permissions**: Authenticated users (read), Admin users (write)
- **Filters**: `?search=` (name, description)
- **Ordering**: `?ordering=name`, `?ordering=created_at`

#### Get Role Details
```
GET /api/v1/accounts/roles/{id}/
```
- **Permissions**: Authenticated users
- **Response includes**:
  - Direct permissions
  - Permission count
  - User count
  - Parent role (if any)
  - Child roles (if any)

#### Create Role
```
POST /api/v1/accounts/roles/
```
- **Permissions**: Admin users only
- **Fields**:
  - name (required, unique)
  - description (optional)
  - parent (optional, reference to another role)
- **Note**: Creates audit trail with creator information

#### Update Role
```
PUT/PATCH /api/v1/accounts/roles/{id}/
```
- **Permissions**: Admin users only
- **Note**: Creates audit trail with updater information

#### Delete Role
```
DELETE /api/v1/accounts/roles/{id}/
```
- **Permissions**: Admin users only

#### Add Permissions to Role
```
POST /api/v1/accounts/roles/{id}/add_permissions/
```
- **Permissions**: Admin users only
- **Input**: `permission_ids` (list of permission IDs)
- **Note**: 
  - Creates audit trail for each permission added
  - Invalidates cache for all affected users

#### Remove Permissions from Role
```
POST /api/v1/accounts/roles/{id}/remove_permissions/
```
- **Permissions**: Admin users only
- **Input**: `permission_ids` (list of permission IDs)
- **Note**: 
  - Creates audit trail for each permission removed
  - Invalidates cache for all affected users

#### List Users with Role
```
GET /api/v1/accounts/roles/{id}/users/
```
- **Permissions**: Authenticated users
- **Pagination**: Standard pagination applies

#### List All Permissions of Role
```
GET /api/v1/accounts/roles/{id}/all_permissions/
```
- **Permissions**: Authenticated users
- **Note**: Includes permissions inherited from parent roles

### Permission Management

#### List Permissions
```
GET /api/v1/accounts/permissions/
```
- **Permissions**: Admin users only
- **Filters**: `?search=` (name, codename, app_label)
- **Ordering**: `?ordering=name`, `?ordering=codename`
- **Cache**: Responses are cached for 1 hour when no filters are applied

#### Get Permission Details
```
GET /api/v1/accounts/permissions/{id}/
```
- **Permissions**: Admin users only

#### List Permissions by App
```
GET /api/v1/accounts/permissions/by_app/
```
- **Permissions**: Admin users only
- **Response**: Permissions grouped by Django app

### Permission Change Logs

#### List Permission Changes
```
GET /api/v1/accounts/permission-logs/
```
- **Permissions**: Admin users only
- **Filters**: 
  - `?search=` (role name, permission name, user email)
  - `?role_id=` (filter by role)
  - `?date_from=` and `?date_to=` (filter by date range)
- **Ordering**: `?ordering=changed_at`, `?ordering=action`

#### Get Permission Change Details
```
GET /api/v1/accounts/permission-logs/{id}/
```
- **Permissions**: Admin users only

## Error Handling

All endpoints return appropriate HTTP status codes:
- `200 OK` for successful GET requests
- `201 Created` for successful resource creation
- `204 No Content` for successful deletions
- `400 Bad Request` for invalid input
- `401 Unauthorized` for authentication failures
- `403 Forbidden` for permission failures
- `404 Not Found` for non-existent resources
- `429 Too Many Requests` for rate limit exceeded

## Data Validation

- Email addresses are validated for format and uniqueness
- Passwords are validated using Django's password validation system
- Role hierarchies are validated to prevent circular references

## Performance Considerations

- API responses are cached where appropriate
- Database queries are optimized with select_related/prefetch_related
- Cache invalidation occurs automatically when permissions change
- Bulk operations are available for creating multiple users

## Example Usage

### Creating a User
```json
POST /api/v1/accounts/users/
{
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "password": "SecurePassword123",
  "password_confirm": "SecurePassword123",
  "role": 1,
  "bio": "User biography"
}
```

### Creating a Role
```json
POST /api/v1/accounts/roles/
{
  "name": "Editor",
  "description": "Can edit content",
  "parent": 2
}
```

### Adding Permissions to a Role
```json
POST /api/v1/accounts/roles/1/add_permissions/
{
  "permission_ids": [1, 2, 3]
}
```

## Authentication API

This app also provides complete authentication functionality:

- **User Registration**
- **Email-based Login/Logout**
- **Password Reset**
- **Password Change**

For detailed documentation of authentication endpoints, see [AUTH_README.md](AUTH_README.md). 