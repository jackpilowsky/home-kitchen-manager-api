#!/bin/bash

# Home Kitchen Manager API - Development Utility Script
# This script provides common development tasks and utilities

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
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

print_command() {
    echo -e "${PURPLE}[CMD]${NC} $1"
}

# Function to check if services are running
check_services() {
    if ! docker-compose -f docker-compose.dev.yml ps -q | grep -q .; then
        print_error "Development services are not running"
        print_status "Start services with: ./start.sh"
        exit 1
    fi
}

# Function to run database migrations
run_migrations() {
    print_status "Running database migrations..."
    print_command "docker-compose -f docker-compose.dev.yml exec api alembic upgrade head"
    
    if docker-compose -f docker-compose.dev.yml exec api alembic upgrade head; then
        print_success "Migrations completed successfully"
    else
        print_error "Migration failed"
        exit 1
    fi
}

# Function to create new migration
create_migration() {
    local description="$1"
    
    if [ -z "$description" ]; then
        read -p "Enter migration description: " description
    fi
    
    if [ -z "$description" ]; then
        print_error "Migration description is required"
        exit 1
    fi
    
    print_status "Creating new migration: $description"
    print_command "docker-compose -f docker-compose.dev.yml exec api alembic revision -m \"$description\""
    
    if docker-compose -f docker-compose.dev.yml exec api alembic revision -m "$description"; then
        print_success "Migration created successfully"
        print_status "Don't forget to edit the migration file and add your changes"
    else
        print_error "Failed to create migration"
        exit 1
    fi
}

# Function to rollback migration
rollback_migration() {
    local steps=${1:-1}
    
    print_warning "Rolling back $steps migration(s)"
    print_command "docker-compose -f docker-compose.dev.yml exec api alembic downgrade -$steps"
    
    read -p "Are you sure you want to rollback? (y/N): " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if docker-compose -f docker-compose.dev.yml exec api alembic downgrade -$steps; then
            print_success "Rollback completed successfully"
        else
            print_error "Rollback failed"
            exit 1
        fi
    else
        print_status "Rollback cancelled"
    fi
}

# Function to run tests
run_tests() {
    local test_path="$1"
    local coverage="$2"
    
    print_status "Running tests..."
    
    if [ "$coverage" = "true" ]; then
        print_command "docker-compose -f docker-compose.dev.yml exec api pytest --cov=api $test_path"
        docker-compose -f docker-compose.dev.yml exec api pytest --cov=api $test_path
    else
        print_command "docker-compose -f docker-compose.dev.yml exec api pytest $test_path"
        docker-compose -f docker-compose.dev.yml exec api pytest $test_path
    fi
}

# Function to format code
format_code() {
    print_status "Formatting code with black and isort..."
    
    print_command "docker-compose -f docker-compose.dev.yml exec api black ."
    docker-compose -f docker-compose.dev.yml exec api black .
    
    print_command "docker-compose -f docker-compose.dev.yml exec api isort ."
    docker-compose -f docker-compose.dev.yml exec api isort .
    
    print_success "Code formatting completed"
}

# Function to lint code
lint_code() {
    print_status "Linting code with flake8..."
    
    print_command "docker-compose -f docker-compose.dev.yml exec api flake8 ."
    docker-compose -f docker-compose.dev.yml exec api flake8 . || print_warning "Linting found issues"
}

# Function to open shell
open_shell() {
    local service=${1:-api}
    
    print_status "Opening shell in $service container..."
    print_command "docker-compose -f docker-compose.dev.yml exec $service bash"
    
    docker-compose -f docker-compose.dev.yml exec $service bash
}

# Function to connect to database
connect_db() {
    print_status "Connecting to PostgreSQL database..."
    print_command "docker-compose -f docker-compose.dev.yml exec db psql -U postgres -d kitchen_manager_dev"
    
    docker-compose -f docker-compose.dev.yml exec db psql -U postgres -d kitchen_manager_dev
}

# Function to reset database
reset_database() {
    print_warning "This will completely reset the development database!"
    print_warning "All data will be lost!"
    
    read -p "Are you sure you want to reset the database? (y/N): " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Stopping services..."
        docker-compose -f docker-compose.dev.yml stop
        
        print_status "Removing database volume..."
        docker-compose -f docker-compose.dev.yml down -v
        
        print_status "Starting services..."
        docker-compose -f docker-compose.dev.yml up -d
        
        print_status "Waiting for database..."
        sleep 10
        
        print_status "Running migrations..."
        run_migrations
        
        print_success "Database reset completed"
    else
        print_status "Database reset cancelled"
    fi
}

# Function to backup database
backup_database() {
    local backup_name="backup_$(date +%Y%m%d_%H%M%S).sql"
    
    print_status "Creating database backup: $backup_name"
    print_command "docker-compose -f docker-compose.dev.yml exec -T db pg_dump -U postgres kitchen_manager_dev > $backup_name"
    
    if docker-compose -f docker-compose.dev.yml exec -T db pg_dump -U postgres kitchen_manager_dev > "$backup_name"; then
        print_success "Database backup created: $backup_name"
    else
        print_error "Database backup failed"
        exit 1
    fi
}

# Function to restore database
restore_database() {
    local backup_file="$1"
    
    if [ -z "$backup_file" ]; then
        print_error "Backup file is required"
        echo "Usage: $0 restore-db <backup_file.sql>"
        exit 1
    fi
    
    if [ ! -f "$backup_file" ]; then
        print_error "Backup file not found: $backup_file"
        exit 1
    fi
    
    print_warning "This will restore the database from: $backup_file"
    print_warning "Current data will be lost!"
    
    read -p "Are you sure you want to restore? (y/N): " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Restoring database from $backup_file..."
        print_command "docker-compose -f docker-compose.dev.yml exec -T db psql -U postgres -d kitchen_manager_dev < $backup_file"
        
        if docker-compose -f docker-compose.dev.yml exec -T db psql -U postgres -d kitchen_manager_dev < "$backup_file"; then
            print_success "Database restored successfully"
        else
            print_error "Database restore failed"
            exit 1
        fi
    else
        print_status "Database restore cancelled"
    fi
}

# Function to show API health
show_health() {
    print_status "Checking API health..."
    
    if curl -s http://localhost:8001/api/v1/health | jq . 2>/dev/null; then
        print_success "API is healthy"
    else
        print_warning "API health check failed or jq not available"
        curl -s http://localhost:8001/api/v1/health || print_error "API is not responding"
    fi
}

# Function to create test user
create_test_user() {
    print_status "Creating test user..."
    
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
    else
        print_warning "Test user creation failed or user already exists (HTTP $response)"
        if [ -f /tmp/register_response.json ]; then
            cat /tmp/register_response.json
        fi
    fi
    
    rm -f /tmp/register_response.json
}

# Function to show development menu
show_menu() {
    while true; do
        echo ""
        echo "🛠️  Development Menu"
        echo "==================="
        echo "  1)  Run migrations"
        echo "  2)  Create migration"
        echo "  3)  Rollback migration"
        echo "  4)  Run tests"
        echo "  5)  Run tests with coverage"
        echo "  6)  Format code"
        echo "  7)  Lint code"
        echo "  8)  Open API shell"
        echo "  9)  Connect to database"
        echo "  10) Show API health"
        echo "  11) Create test user"
        echo "  12) Backup database"
        echo "  13) Reset database"
        echo "  14) View logs"
        echo "  15) Exit"
        echo ""
        
        read -p "Choose an option (1-15): " -n 2 -r
        echo ""
        
        case $REPLY in
            1)
                run_migrations
                ;;
            2)
                create_migration
                ;;
            3)
                rollback_migration
                ;;
            4)
                run_tests
                ;;
            5)
                run_tests "" true
                ;;
            6)
                format_code
                ;;
            7)
                lint_code
                ;;
            8)
                open_shell api
                ;;
            9)
                connect_db
                ;;
            10)
                show_health
                ;;
            11)
                create_test_user
                ;;
            12)
                backup_database
                ;;
            13)
                reset_database
                ;;
            14)
                ./logs.sh --interactive
                ;;
            15)
                print_status "Exiting development menu"
                exit 0
                ;;
            *)
                print_error "Invalid option. Please choose 1-15."
                ;;
        esac
        
        echo ""
        read -p "Press Enter to return to menu..."
    done
}

# Main execution function
main() {
    echo "🛠️  Home Kitchen Manager API - Development Utilities"
    echo "===================================================="
    
    # Check if services are running for most commands
    case "$1" in
        --help|-h|help)
            # Don't check services for help
            ;;
        *)
            check_services
            ;;
    esac
    
    # Parse arguments
    case "$1" in
        migrate|migration)
            run_migrations
            ;;
        create-migration|new-migration)
            create_migration "$2"
            ;;
        rollback|rollback-migration)
            rollback_migration "$2"
            ;;
        test|tests)
            run_tests "$2" "$3"
            ;;
        test-cov|coverage)
            run_tests "$2" true
            ;;
        format|fmt)
            format_code
            ;;
        lint)
            lint_code
            ;;
        shell)
            open_shell "$2"
            ;;
        db|database)
            connect_db
            ;;
        health)
            show_health
            ;;
        user|test-user)
            create_test_user
            ;;
        backup|backup-db)
            backup_database
            ;;
        restore|restore-db)
            restore_database "$2"
            ;;
        reset|reset-db)
            reset_database
            ;;
        logs)
            ./logs.sh "${@:2}"
            ;;
        menu|interactive)
            show_menu
            ;;
        "")
            show_menu
            ;;
        *)
            print_error "Unknown command: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
}

# Help function
show_help() {
    echo "Home Kitchen Manager API - Development Utilities"
    echo ""
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  migrate              Run database migrations"
    echo "  create-migration     Create new migration"
    echo "  rollback [N]         Rollback N migrations (default: 1)"
    echo "  test [PATH]          Run tests"
    echo "  test-cov [PATH]      Run tests with coverage"
    echo "  format               Format code with black and isort"
    echo "  lint                 Lint code with flake8"
    echo "  shell [SERVICE]      Open shell (default: api)"
    echo "  db                   Connect to database"
    echo "  health               Show API health status"
    echo "  test-user            Create test user"
    echo "  backup               Backup database"
    echo "  restore FILE         Restore database from backup"
    echo "  reset                Reset database (removes all data)"
    echo "  logs [OPTIONS]       View logs (see logs.sh --help)"
    echo "  menu                 Interactive menu"
    echo ""
    echo "Examples:"
    echo "  $0                   Show interactive menu"
    echo "  $0 migrate           Run migrations"
    echo "  $0 test              Run all tests"
    echo "  $0 shell             Open API shell"
    echo "  $0 db                Connect to database"
    echo "  $0 logs --follow     Follow all logs"
    echo ""
    echo "Services: api, db, redis"
}

# Parse command line arguments
case "$1" in
    -h|--help|help)
        show_help
        exit 0
        ;;
    *)
        main "$@"
        ;;
esac