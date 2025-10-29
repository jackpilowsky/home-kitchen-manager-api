# Home Kitchen Manager API

A comprehensive REST API for managing kitchen operations including shopping lists, inventory management, and user authentication.

## 🚀 Features

- **🏠 Multi-Kitchen Management** - Create and manage multiple kitchens
- **📝 Shopping Lists** - Organize and track shopping items
- **📦 Inventory Tracking** - Manage pantry, refrigerator, and freezer items
- **🔍 Advanced Search** - Full-text search with filtering and pagination
- **👥 User Authentication** - JWT-based secure authentication
- **📊 Monitoring** - Health checks and system metrics
- **🛡️ Security** - Input validation, rate limiting, and CORS support

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [Docker Setup](#docker-setup)
- [API Documentation](#api-documentation)
- [Development](#development)
- [Production Deployment](#production-deployment)
- [Testing](#testing)
- [Contributing](#contributing)

## 🚀 Quick Start

### Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- Git

### 1. Clone Repository

```bash
git clone <repository-url>
cd home-kitchen-manager-api
```

### 2. Environment Setup

```bash
cp .env.example .env
# Edit .env with your configuration
```

### 3. Start Development Environment

```bash
# Start all services
docker-compose -f docker-compose.dev.yml up -d

# Run database migrations
docker-compose -f docker-compose.dev.yml exec api alembic upgrade head

# Create a test user (optional)
docker-compose -f docker-compose.dev.yml exec api python -c "
from api.v1.auth import create_user
create_user('admin', 'admin@example.com', 'admin123')
"
```

### 4. Access the Application

- **API**: http://localhost:8001
- **Interactive Docs**: http://localhost:8001/docs
- **Alternative Docs**: http://localhost:8001/redoc
- **Health Check**: http://localhost:8001/api/v1/health

## 🐳 Docker Setup

### Development Environment

```bash
# Start development environment with hot reload
docker-compose -f docker-compose.dev.yml up -d

# View logs
docker-compose -f docker-compose.dev.yml logs -f api

# Stop environment
docker-compose -f docker-compose.dev.yml down
```

**Services:**
- **API**: FastAPI with hot reload (port 8001)
- **Database**: PostgreSQL 15 (port 5433)
- **Cache**: Redis 7 (port 6380)

### Production Environment

```bash
# Start production environment
docker-compose up -d

# Run migrations
docker-compose exec api alembic upgrade head

# View logs
docker-compose logs -f
```

**Services:**
- **API**: FastAPI production build
- **Database**: PostgreSQL 15 with persistence
- **Cache**: Redis 7 with persistence
- **Proxy**: Nginx with rate limiting and SSL support

For detailed Docker setup instructions, see [DOCKER_SETUP.md](DOCKER_SETUP.md).

## 📚 API Documentation

### Interactive Documentation

- **Swagger UI**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc

### API Endpoints Overview

| Category | Endpoints | Description |
|----------|-----------|-------------|
| 🔐 **Authentication** | `/api/v1/auth/*` | User registration, login, token management |
| 🏠 **Kitchens** | `/api/v1/kitchens/*` | Kitchen management and organization |
| 📝 **Shopping Lists** | `/api/v1/shopping-lists/*` | Shopping list and item management |
| 📦 **Inventory** | `/api/v1/{pantry,refrigerator,freezer}-items/*` | Inventory tracking by storage location |
| 🔍 **Search** | `/api/v1/search/*` | Advanced search and filtering |
| 🏥 **Health** | `/api/v1/health/*` | System health and monitoring |

### Quick API Examples

```bash
# Register a new user
curl -X POST "http://localhost:8001/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"username": "john", "email": "john@example.com", "password": "secure123"}'

# Login and get token
curl -X POST "http://localhost:8001/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "john", "password": "secure123"}'

# Create a kitchen (replace TOKEN with actual token)
curl -X POST "http://localhost:8001/api/v1/kitchens/" \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "My Kitchen", "description": "Main kitchen"}'
```

For complete API documentation, see [API_DOCUMENTATION.md](API_DOCUMENTATION.md).

## 💻 Development

### Local Development Setup

1. **Install Python dependencies**:
```bash
pip install -r requirements.txt
```

2. **Setup database**:
```bash
# Start PostgreSQL and Redis
docker-compose -f docker-compose.dev.yml up -d db redis

# Run migrations
alembic upgrade head
```

3. **Start development server**:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Database Migrations

```bash
# Create new migration
alembic revision -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Code Quality

```bash
# Format code
black .
isort .

# Lint code
flake8 .

# Type checking
mypy .
```

## 🧪 Testing

### Run Tests

```bash
# Run all tests
docker-compose -f docker-compose.dev.yml exec api pytest

# Run with coverage
docker-compose -f docker-compose.dev.yml exec api pytest --cov=api

# Run specific test file
docker-compose -f docker-compose.dev.yml exec api pytest tests/test_auth.py

# Run tests with verbose output
docker-compose -f docker-compose.dev.yml exec api pytest -v
```

### Test Categories

- **Unit Tests**: Individual function and method testing
- **Integration Tests**: API endpoint testing
- **Authentication Tests**: JWT and permission testing
- **Database Tests**: Model and migration testing

## 🚀 Production Deployment

### Environment Configuration

1. **Create production environment file**:
```bash
cp .env.example .env
```

2. **Configure production values**:
```bash
# Security
SECRET_KEY=your-super-secure-secret-key-minimum-32-characters
DATABASE_PASSWORD=your-secure-database-password

# Database
DATABASE_HOST=your-database-host
DATABASE_NAME=kitchen_manager_prod

# Application
ENVIRONMENT=production
DEBUG=false
ALLOWED_HOSTS=your-domain.com,api.your-domain.com
```

### Deployment Steps

1. **Start production environment**:
```bash
docker-compose up -d
```

2. **Run database migrations**:
```bash
docker-compose exec api alembic upgrade head
```

3. **Verify deployment**:
```bash
# Check health
curl http://your-domain.com/health

# Check services
docker-compose ps
```

### SSL/TLS Setup

1. **Obtain SSL certificates** (Let's Encrypt recommended)
2. **Update nginx.conf** with SSL configuration
3. **Mount certificates** in docker-compose.yml

### Monitoring and Maintenance

```bash
# View logs
docker-compose logs -f

# Monitor resources
docker stats

# Backup database
docker-compose exec db pg_dump -U postgres kitchen_manager > backup.sql

# Update application
git pull
docker-compose build
docker-compose up -d
```

## 🔧 Configuration

### Environment Variables

Key configuration options:

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | - |
| `REDIS_URL` | Redis connection string | - |
| `SECRET_KEY` | JWT signing key | - |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration | 30 |
| `ENVIRONMENT` | Environment mode | development |
| `DEBUG` | Debug mode | false |

See [.env.example](.env.example) for complete configuration options.

### Database Configuration

The application uses PostgreSQL with the following features:
- **Alembic migrations** for schema management
- **Connection pooling** for performance
- **Foreign key constraints** for data integrity
- **Indexes** for query optimization

### Caching Configuration

Redis is used for:
- **Session storage** (future enhancement)
- **Rate limiting** counters
- **Query result caching** (future enhancement)

## 🛡️ Security

### Authentication & Authorization
- **JWT tokens** with configurable expiration
- **Password hashing** with bcrypt
- **Kitchen-based ownership** validation
- **Input validation** with Pydantic

### API Security
- **Rate limiting** (100 req/min per IP)
- **CORS configuration** for cross-origin requests
- **Security headers** (XSS, CSRF protection)
- **Input sanitization** and validation

### Data Protection
- **SQL injection prevention** with SQLAlchemy ORM
- **Environment variable secrets** management
- **Database connection encryption** support
- **Audit logging** for sensitive operations

## 📊 Monitoring

### Health Checks
- **Basic health**: `/api/v1/health`
- **Detailed health**: `/api/v1/health/detailed`
- **Database connectivity** validation
- **Redis connectivity** validation

### Metrics
- **System metrics**: CPU, memory, disk usage
- **Application metrics**: Request count, response times
- **Database metrics**: Connection pool, query performance
- **Custom metrics**: User activity, API usage

### Logging
- **Structured logging** with JSON format
- **Log levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Request/response logging** for debugging
- **Error tracking** with stack traces

## 🤝 Contributing

### Development Workflow

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/amazing-feature`
3. **Make changes** and add tests
4. **Run tests**: `pytest`
5. **Format code**: `black . && isort .`
6. **Commit changes**: `git commit -m 'Add amazing feature'`
7. **Push to branch**: `git push origin feature/amazing-feature`
8. **Open Pull Request**

### Code Standards

- **Python**: Follow PEP 8 style guide
- **Type hints**: Use type annotations
- **Documentation**: Add docstrings for functions/classes
- **Tests**: Write tests for new features
- **Commits**: Use conventional commit messages

### Issue Reporting

When reporting issues, please include:
- **Environment details** (OS, Docker version, etc.)
- **Steps to reproduce** the issue
- **Expected vs actual behavior**
- **Error logs** and stack traces
- **Configuration details** (sanitized)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **FastAPI** - Modern, fast web framework for building APIs
- **SQLAlchemy** - Python SQL toolkit and ORM
- **Alembic** - Database migration tool
- **PostgreSQL** - Advanced open source database
- **Redis** - In-memory data structure store
- **Docker** - Containerization platform

## 📞 Support

- **Documentation**: Available at `/docs` endpoint
- **Health Status**: Check `/api/v1/health`
- **Issues**: GitHub Issues for bug reports
- **Discussions**: GitHub Discussions for questions

---

**Happy Cooking! 👨‍🍳👩‍🍳**