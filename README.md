# User Roles System

[![Built with Django](https://img.shields.io/badge/Built%20with-Django-green.svg)](https://www.djangoproject.com/)
[![Python 3.9](https://img.shields.io/badge/Python-3.9-blue.svg)](https://www.python.org/downloads/release/python-390/)
[![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-blue.svg)](https://www.postgresql.org/)
[![REST API](https://img.shields.io/badge/API-REST-orange.svg)](https://www.django-rest-framework.org/)

A professional Django project implementing an advanced role-based permission system with optimal performance, security features, and comprehensive authentication.

**Author:** Mharrech Ayoub  
**LinkedIn:** [https://www.linkedin.com/in/ayoubmharrech/](https://www.linkedin.com/in/ayoubmharrech/)  
**Email:** mharrech.ayoub@gmail.com

## Features

- **Email-based Authentication**: 
  - Secure registration and login
  - Password reset functionality
  - Token-based authentication for APIs
  - Rate limiting protection

- **Role-based Authorization**: 
  - Hierarchical roles with permission inheritance
  - Granular permission control
  - Dynamic role assignment

- **Performance Optimizations**: 
  - Extensive caching system
  - Optimized database queries
  - Automatic cache invalidation

- **Security**: 
  - Comprehensive input validation
  - Rate limiting to prevent abuse
  - Secure password handling
  - IP logging for audit trails

- **Complete Audit Trail**: 
  - Track all permission changes
  - Monitor who changed what and when

- **RESTful API**: 
  - Complete API for managing users and roles
  - Comprehensive documentation
  - Format suffixes support (.json)

- **Scalable Architecture**: 
  - Professional Django setup suitable for enterprise applications
  - Separation of concerns
  - Modular design

## Getting Started

### Prerequisites

- Python 3.9+
- PostgreSQL 13+
- pip (Python package manager)

### Installation

1. **Clone the repository**

```bash
git clone <repository-url>
cd User-Roles
```

2. **Create and activate a virtual environment**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Configure environment variables**

Create a `.env` file based on the `.env.example` file:

```bash
cp .env.example .env
```

Then edit the `.env` file to set your database credentials, email settings, and other configurations.

5. **Set up the database**

```bash
# Create the database (if using PostgreSQL)
createdb user_roles

# Run migrations
python manage.py migrate
```

6. **Create a superuser**

```bash
python manage.py createsuperuser
```

7. **Run the development server**

```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000/admin/` to access the admin interface.

## Project Structure

```
User-Roles/
├── accounts/               # Main app for user and role management
│   ├── api.py              # API endpoints
│   ├── auth.py             # Authentication views & serializers
│   ├── models.py           # Database models
│   ├── serializers.py      # API serializers
│   ├── urls.py             # URL configurations
│   ├── README.md           # Detailed API documentation
│   └── AUTH_README.md      # Authentication documentation
├── config/                 # Project configuration
│   ├── settings.py         # Django settings
│   ├── urls.py             # Main URL routing
│   └── wsgi.py             # WSGI configuration
├── static/                 # Static files
├── media/                  # User uploaded files
│   └── accounts/
│       └── emails/         # Email templates
├── .env                    # Environment variables
├── .gitignore              # Git ignore file
├── manage.py               # Django management script
├── README.md               # Project documentation
└── requirements.txt        # Python dependencies
```

## API Usage

### Role-Based Permission API

The API provides comprehensive endpoints for managing users and roles. For detailed documentation, see [accounts/README.md](accounts/README.md).

Key Endpoints:
- `/api/v1/accounts/users/` - User management
- `/api/v1/accounts/roles/` - Role management
- `/api/v1/accounts/permissions/` - Permission management

### Authentication API

The system provides a complete authentication solution with:

- User registration and email verification
- Secure login/logout functionality
- Password reset and change capabilities

Key Endpoints:
- `/api/v1/accounts/auth/register/` - User registration
- `/api/v1/accounts/auth/login/` - User login
- `/api/v1/accounts/auth/password/reset/` - Password reset

For detailed authentication documentation, see [accounts/AUTH_README.md](accounts/AUTH_README.md).

## Performance Considerations

This system is designed for optimal performance:

- **Caching**: Responses are cached to minimize database queries
- **Query Optimization**: Proper use of select_related and prefetch_related
- **Bulk Operations**: Support for batch processing of users and permissions

## Security Features

- **Authentication Security**:
  - Rate limiting on login/registration (5 requests/minute)
  - Rate limiting on password reset (3 requests/hour)
  - Secure token generation and validation
  - Protection against email enumeration

- **Authorization Security**:
  - Hierarchical roles for flexible security policies
  - Permission inheritance
  - Audit logging for all changes

## Development

### Running Tests

```bash
pytest
```

### Checking Code Style

```bash
flake8
black .
```

## Frontend Integration

The API is designed to work seamlessly with modern frontend frameworks:

- **React**: All authentication and permission endpoints are React-ready
- **Vue.js/Angular**: Complete RESTful API works with any frontend framework
- **Mobile Apps**: Token authentication for mobile clients

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

© 2024 Mharrech Ayoub. All rights reserved. 