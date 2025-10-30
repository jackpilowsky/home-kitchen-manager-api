# Development Scripts Guide

This guide covers the development scripts that make it easy to manage the Home Kitchen Manager API development environment.

## 🚀 Quick Start

```bash
# Start development environment
./start.sh

# View logs
./logs.sh

# Development utilities
./dev.sh

# Stop environment
./stop.sh
```

## 📋 Available Scripts

### 🚀 `start.sh` - Start Development Environment

Starts the complete development environment with Docker Compose.

#### Usage
```bash
./start.sh [OPTIONS]
```

#### Options
- `--with-test-user` or `-u`: Create a test user after startup
- `--help` or `-h`: Show help message

#### What it does
1. ✅ Checks Docker prerequisites
2. 🐳 Starts PostgreSQL, Redis, and API services
3. ⏳ Waits for all services to be ready
4. 🗄️ Runs database migrations
5. 👤 Optionally creates a test user
6. 📊 Displays service information and URLs

#### Examples
```bash
./start.sh                    # Start development environment
./start.sh --with-test-user   # Start and create test user
```

#### Service URLs (after startup)
- **API Documentation**: http://localhost:8001/docs
- **Alternative Docs**: http://localhost:8001/redoc
- **API Health Check**: http://localhost:8001/api/v1/health
- **Database Status**: http://localhost:8001/api/v1/database/status
- **PostgreSQL**: localhost:5433 (postgres/postgres)
- **Redis**: localhost:6380

---

### 🛑 `stop.sh` - Stop Development Environment

Stops the development environment with various cleanup options.

#### Usage
```bash
./stop.sh [OPTIONS]
```

#### Options
- `--quick` or `-q`: Quick stop (preserve containers and data)
- `--clean` or `-c`: Stop and remove containers (preserve data)
- `--clean-all` or `--full`: Full cleanup (remove everything including data)
- `--logs` or `-l`: Show logs before stopping
- `--help` or `-h`: Show help message

#### Interactive Mode
When run without options, presents a menu:
1. Quick stop (preserve containers and data)
2. Stop and remove containers (preserve data)
3. Full cleanup (remove containers and data)
4. Show logs then stop
5. Cancel

#### Examples
```bash
./stop.sh              # Interactive mode
./stop.sh --quick      # Just stop services
./stop.sh --clean      # Stop and remove containers
./stop.sh --clean-all  # Remove everything including data
```

---

### 📋 `logs.sh` - View Development Logs

Provides easy access to development environment logs with various filtering options.

#### Usage
```bash
./logs.sh [OPTIONS] [LINES]
```

#### Options
- `--api` or `-a`: Show API logs only
- `--db` or `-d`: Show database logs only
- `--redis` or `-r`: Show Redis logs only
- `--errors` or `-e`: Show error logs only
- `--status` or `-s`: Show service status and resource usage
- `--follow` or `-f [SERVICE]`: Follow logs (optionally specify service)
- `--lines N` or `-l N`: Show last N lines (default: 50)
- `--interactive` or `-i`: Interactive log viewer menu
- `--help` or `-h`: Show help message

#### Examples
```bash
./logs.sh                 # Show recent API logs (interactive)
./logs.sh --api           # Show API logs
./logs.sh --follow        # Follow all logs
./logs.sh --follow api    # Follow API logs only
./logs.sh --errors        # Show recent error logs
./logs.sh --lines 100     # Show last 100 lines from all services
./logs.sh --interactive   # Interactive menu
```

#### Interactive Menu
1. All services (follow)
2. API only (follow)
3. Database only (follow)
4. Redis only (follow)
5. Recent errors
6. Service status
7. All services (last 100 lines)
8. API only (last 100 lines)
9. Exit

---

### 🛠️ `dev.sh` - Development Utilities

Comprehensive development utilities for common tasks.

#### Usage
```bash
./dev.sh [COMMAND] [OPTIONS]
```

#### Commands

##### Database Operations
- `migrate`: Run database migrations
- `create-migration [DESCRIPTION]`: Create new migration
- `rollback [N]`: Rollback N migrations (default: 1)
- `backup`: Backup database
- `restore FILE`: Restore database from backup
- `reset`: Reset database (removes all data)

##### Testing & Code Quality
- `test [PATH]`: Run tests
- `test-cov [PATH]`: Run tests with coverage
- `format`: Format code with black and isort
- `lint`: Lint code with flake8

##### Development Tools
- `shell [SERVICE]`: Open shell (default: api)
- `db`: Connect to database
- `health`: Show API health status
- `test-user`: Create test user
- `logs [OPTIONS]`: View logs

##### Interactive
- `menu` or no command: Interactive menu

#### Examples
```bash
./dev.sh                    # Show interactive menu
./dev.sh migrate            # Run migrations
./dev.sh test               # Run all tests
./dev.sh test-cov           # Run tests with coverage
./dev.sh shell              # Open API shell
./dev.sh db                 # Connect to database
./dev.sh create-migration "Add new feature"
./dev.sh backup             # Backup database
./dev.sh format             # Format code
./dev.sh lint               # Lint code
```

#### Interactive Menu
1. Run migrations
2. Create migration
3. Rollback migration
4. Run tests
5. Run tests with coverage
6. Format code
7. Lint code
8. Open API shell
9. Connect to database
10. Show API health
11. Create test user
12. Backup database
13. Reset database
14. View logs
15. Exit

## 🔄 Common Development Workflows

### 🚀 Starting Development
```bash
# 1. Start the environment
./start.sh --with-test-user

# 2. View logs to ensure everything is working
./logs.sh --api

# 3. Open API documentation
open http://localhost:8001/docs
```

### 🧪 Testing Workflow
```bash
# Run all tests
./dev.sh test

# Run tests with coverage
./dev.sh test-cov

# Run specific test file
./dev.sh test tests/test_auth.py

# Format code before committing
./dev.sh format
./dev.sh lint
```

### 🗄️ Database Workflow
```bash
# Create new migration
./dev.sh create-migration "Add user preferences table"

# Edit the migration file (in alembic/versions/)
# Then run the migration
./dev.sh migrate

# If something goes wrong, rollback
./dev.sh rollback

# Connect to database for manual queries
./dev.sh db
```

### 🐛 Debugging Workflow
```bash
# Check API health
./dev.sh health

# View recent errors
./logs.sh --errors

# Follow API logs in real-time
./logs.sh --follow api

# Open shell in API container
./dev.sh shell

# Check service status and resource usage
./logs.sh --status
```

### 🧹 Cleanup Workflow
```bash
# Quick stop (preserve data)
./stop.sh --quick

# Clean stop (remove containers, keep data)
./stop.sh --clean

# Full cleanup (remove everything)
./stop.sh --clean-all
```

## 🎯 Script Features

### ✨ Smart Features
- **Color-coded output** for better readability
- **Error handling** with meaningful messages
- **Service health checks** before operations
- **Interactive menus** for ease of use
- **Progress indicators** for long-running operations
- **Automatic service waiting** until ready
- **Resource usage monitoring**
- **Backup and restore capabilities**

### 🛡️ Safety Features
- **Confirmation prompts** for destructive operations
- **Data preservation options** in stop script
- **Error recovery** and rollback capabilities
- **Service dependency checking**
- **Timeout handling** for service startup

### 📊 Monitoring Features
- **Real-time log following**
- **Service status monitoring**
- **Resource usage tracking**
- **Health check integration**
- **Error log filtering**

## 🔧 Customization

### Environment Variables
The scripts respect these environment variables:
- `COMPOSE_FILE`: Override docker-compose file
- `API_PORT`: Override API port (default: 8001)
- `DB_PORT`: Override database port (default: 5433)

### Script Modification
All scripts are designed to be easily customizable:
- Modify colors by changing the color variables at the top
- Add new commands by extending the case statements
- Customize timeouts and retry logic
- Add new service monitoring

## 🆘 Troubleshooting

### Common Issues

#### Docker Not Running
```bash
# Error: Docker is not running
# Solution: Start Docker Desktop and try again
```

#### Port Already in Use
```bash
# Error: Port 8001 is already in use
# Solution: Check what's using the port
lsof -i :8001

# Or modify docker-compose.dev.yml to use different ports
```

#### Services Won't Start
```bash
# Check service logs
./logs.sh --errors

# Check Docker resources
docker system df
docker system prune  # Clean up if needed
```

#### Database Connection Issues
```bash
# Check database status
./logs.sh --db

# Reset database if corrupted
./dev.sh reset
```

### Getting Help
- Use `--help` flag with any script for detailed usage
- Check service logs with `./logs.sh`
- Use interactive menus when unsure of options
- Check service status with `./logs.sh --status`

## 📝 Tips & Best Practices

### Development Tips
1. **Always use `./start.sh`** instead of manual docker-compose commands
2. **Check logs regularly** with `./logs.sh` to catch issues early
3. **Use interactive menus** when learning the commands
4. **Create backups** before major database changes
5. **Format code regularly** with `./dev.sh format`

### Performance Tips
1. **Use `--quick` stop** for faster restart cycles
2. **Follow specific service logs** instead of all logs
3. **Use test coverage** to identify untested code
4. **Monitor resource usage** with `./logs.sh --status`

### Safety Tips
1. **Always backup** before database resets
2. **Use confirmation prompts** for destructive operations
3. **Check service health** before making changes
4. **Keep data separate** from containers (use volumes)

These scripts provide a complete development environment management solution, making it easy to work with the Home Kitchen Manager API while maintaining best practices for Docker-based development.