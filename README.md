# User Roles System

[![Built with Django](https://img.shields.io/badge/Built%20with-Django-green.svg)](https://www.djangoproject.com/)
[![Python 3.9](https://img.shields.io/badge/Python-3.9-blue.svg)](https://www.python.org/downloads/release/python-390/)
[![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-blue.svg)](https://www.postgresql.org/)

A professional Django project implementing an advanced role-based permission system with optimal performance and security features.

**Author:** Mharrech Ayoub  
**LinkedIn:** [https://www.linkedin.com/in/ayoubmharrech/](https://www.linkedin.com/in/ayoubmharrech/)  
**Email:** mharrech.ayoub@gmail.com

## Features

- **Email-based Authentication**: Secure login system using email instead of username
- **Role-based Authorization**: Hierarchical roles with permission inheritance
- **Performance Optimizations**: 
  - Extensive caching system
  - Optimized database queries
  - Automatic cache invalidation
- **Security**: 
  - Comprehensive input validation
  - Rate limiting to prevent abuse
  - Secure password handling
- **Complete Audit Trail**: Track all permission changes
- **RESTful API**: Complete API for managing users and roles
- **Scalable Architecture**: Professional Django setup suitable for enterprise applications

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

Then edit the `.env` file to set your database credentials and other settings.

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
│   ├── models.py           # Database models
│   ├── serializers.py      # API serializers
│   ├── urls.py             # URL configurations
│   └── README.md           # Detailed API documentation
├── config/                 # Project configuration
│   ├── settings.py         # Django settings
│   ├── urls.py             # Main URL routing
│   └── wsgi.py             # WSGI configuration
├── static/                 # Static files
├── media/                  # User uploaded files
├── templates/              # HTML templates
├── .env                    # Environment variables
├── .gitignore              # Git ignore file
├── manage.py               # Django management script
├── README.md               # Project documentation
└── requirements.txt        # Python dependencies
```

## API Usage

The API provides comprehensive endpoints for managing users and roles. For detailed documentation, see [accounts/README.md](accounts/README.md).

### Key Endpoints

- `/api/v1/accounts/users/` - User management
- `/api/v1/accounts/roles/` - Role management
- `/api/v1/accounts/permissions/` - Permission management

## Performance Considerations

This system is designed for optimal performance:

- **Caching**: Responses are cached to minimize database queries
- **Query Optimization**: Proper use of select_related and prefetch_related
- **Bulk Operations**: Support for batch processing of users and permissions

## Security Features

- **Rate Limiting**: Protection against brute force and DoS attacks
- **Permission Inheritance**: Hierarchical roles for flexible security policies
- **Audit Logging**: Complete tracking of all permission changes

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

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

© 2024 Mharrech Ayoub. All rights reserved. 