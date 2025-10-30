#!/bin/bash

# Home Kitchen Manager API - Development Environment Startup Script
# This script starts the development environment with Docker Compose

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker Desktop and try again."
        exit 1
    fi
    print_success "Docker is running"
}

# Function to check if docker-compose is available
check_docker_compose() {
    if ! command -v docker-compose &> /dev/null; then
        print_error "docker-compose is not installed or not in PATH"
        exit 1
    fi
    print_success "docker-compose is available"
}

# Function to create .env file if it doesn't exist
setup_env_file() {
    if [ ! -f .env ]; then
        print_warning ".env file not found. Creating from .env.example..."
        if [ -f .env.example ]; then
            cp .env.example .env
            print_success "Created .env file from .env.example"
            print_warning "Please review and update .env file with your configuration"
        else
            print_error ".env.example file not found. Cannot create .env file."
            exit 1
        fi
    else
        print_success ".env file exists"
    fi
}

# Function to start services
start_services() {
    print_status "Starting development services..."
    
    # Start services in detached mode
    docker-compose -f docker-compose.dev.yml up -d
    
    if [ $? -eq 0 ]; then
        print_success "Services started successfully"
    else
        print_error "Failed to start services"
        exit 1
    fi
}

# Function to wait for services to be ready
wait_for_services() {
    print_status "Waiting for services to be ready..."
    
    # Wait for database to be ready
    print_status "Waiting for PostgreSQL..."
    timeout=60
    counter=0
    
    while ! docker-compose -f docker-compose.dev.yml exec -T db pg_isready -U postgres > /dev/null 2>&1; do
        if [ $counter -ge $timeout ]; then
            print_error "PostgreSQL failed to start within $timeout seconds"
            exit 1
        fi
        sleep 1
        counter=$((counter + 1))
        echo -n "."
    done
    echo ""
    print_success "PostgreSQL is ready"
    
    # Wait for Redis to be ready
    print_status "Waiting for Redis..."
    counter=0
    
    while ! docker-compose -f docker-compose.dev.yml exec -T redis redis-cli ping > /dev/null 2>&1; do
        if [ $counter -ge $timeout ]; then
            print_error "Redis failed to start within $timeout seconds"
            exit 1
        fi
        sleep 1
        counter=$((counter + 1))
        echo -n "."
    done
    echo ""
    print_success "Redis is ready"
    
    # Wait for API to be ready
    print_status "Waiting for API..."
    counter=0
    
    while ! curl -s http://localhost:8001/api/v1/health > /dev/null 2>&1; do
        if [ $counter -ge $timeout ]; then
            print_error "API failed to start within $timeout seconds"
            print_status "Checking API logs..."
            docker-compose -f docker-compose.dev.yml logs --tail=20 api
            exit 1
        fi
        sleep 2
        counter=$((counter + 2))
        echo -n "."
    done
    echo ""
    print_success "API is ready"
}

# Function to run database migrations
run_migrations() {
    print_status "Running database migrations..."
    
    if docker-compose -f docker-compose.dev.yml exec -T api alembic upgrade head; then
        print_success "Database migrations completed"
    else
        print_error "Database migrations failed"
        print_status "Checking migration logs..."
        docker-compose -f docker-compose.dev.yml logs --tail=10 api
        exit 1
    fi
}

# Function to show service status
show_status() {
    print_status "Service Status:"
    docker-compose -f docker-compose.dev.yml ps
    echo ""
    
    print_status "Service URLs:"
    echo "  🌐 API Documentation: http://localhost:8001/docs"
    echo "  🌐 Alternative Docs:  http://localhost:8001/redoc"
    echo "  🌐 API Health Check:  http://localhost:8001/api/v1/health"
    echo "  🌐 Database Status:   http://localhost:8001/api/v1/database/status"
    echo "  🗄️  PostgreSQL:       localhost:5433 (postgres/postgres)"
    echo "  🔴 Redis:             localhost:6380"
    echo ""
    
    print_status "Useful Commands:"
    echo "  📋 View logs:         ./logs.sh"
    echo "  🛑 Stop services:     ./stop.sh"
    echo "  🔄 Restart API:       docker-compose -f docker-compose.dev.yml restart api"
    echo "  🐚 API Shell:         docker-compose -f docker-compose.dev.yml exec api bash"
    echo "  🗄️  Database Shell:    docker-compose -f docker-compose.dev.yml exec db psql -U postgres -d kitchen_manager_dev"
}

# Function to create a test user
create_test_user() {
    print_status "Creating test user..."
    
    # Wait a moment for API to be fully ready
    sleep 2
    
    response=$(curl -s -w "%{http_code}" -X POST "http://localhost:8001/api/v1/auth/register" \
        -H "Content-Type: application/json" \
        -d '{
            "username": "testuser",
            "email": "test@example.com",
            "password": "TestPass123"
        }' -o /tmp/register_response.json)
    
    if [ "$response" = "201" ]; then
        print_success "Test user created successfully"
        print_status "  Username: testuser"
        print_status "  Email: test@example.com"
        print_status "  Password: TestPass123"
    elif [ "$response" = "400" ]; then
        # User might already exist
        if grep -q "already exists" /tmp/register_response.json 2>/dev/null; then
            print_warning "Test user already exists"
        else
            print_warning "Failed to create test user (user might already exist)"
        fi
    else
        print_warning "Failed to create test user (HTTP $response)"
    fi
    
    # Clean up temp file
    rm -f /tmp/register_response.json
}

# Main execution
main() {
    echo "🚀 Starting Home Kitchen Manager API Development Environment"
    echo "============================================================"
    
    # Pre-flight checks
    check_docker
    check_docker_compose
    setup_env_file
    
    # Start services
    start_services
    wait_for_services
    run_migrations
    
    # Optional: Create test user
    if [ "$1" = "--with-test-user" ] || [ "$1" = "-u" ]; then
        create_test_user
    fi
    
    # Show final status
    echo ""
    echo "🎉 Development environment is ready!"
    echo "============================================"
    show_status
    
    # Offer to show logs
    echo ""
    read -p "Would you like to view the API logs? (y/N): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Showing API logs (Press Ctrl+C to exit)..."
        docker-compose -f docker-compose.dev.yml logs -f api
    fi
}

# Help function
show_help() {
    echo "Home Kitchen Manager API - Development Startup Script"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -h, --help           Show this help message"
    echo "  -u, --with-test-user Create a test user after startup"
    echo ""
    echo "Examples:"
    echo "  $0                   Start development environment"
    echo "  $0 --with-test-user  Start and create test user"
    echo ""
    echo "This script will:"
    echo "  1. Check Docker prerequisites"
    echo "  2. Start PostgreSQL, Redis, and API services"
    echo "  3. Wait for all services to be ready"
    echo "  4. Run database migrations"
    echo "  5. Optionally create a test user"
    echo "  6. Display service information and URLs"
}

# Parse command line arguments
case "$1" in
    -h|--help)
        show_help
        exit 0
        ;;
    *)
        main "$@"
        ;;
esac