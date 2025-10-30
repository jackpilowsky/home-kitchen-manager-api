#!/bin/bash

# Home Kitchen Manager API - Development Logs Script
# This script provides easy access to development environment logs

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

# Function to check if services are running
check_services() {
    if ! docker-compose -f docker-compose.dev.yml ps -q | grep -q .; then
        print_error "No development services are currently running"
        print_status "Start services with: ./start.sh"
        exit 1
    fi
}

# Function to show all logs
show_all_logs() {
    local lines=${1:-50}
    local follow=${2:-false}
    
    print_status "Showing logs from all services (last $lines lines)..."
    
    if [ "$follow" = "true" ]; then
        print_status "Following logs (Press Ctrl+C to exit)..."
        docker-compose -f docker-compose.dev.yml logs -f --tail="$lines"
    else
        docker-compose -f docker-compose.dev.yml logs --tail="$lines"
    fi
}

# Function to show API logs
show_api_logs() {
    local lines=${1:-50}
    local follow=${2:-false}
    
    print_status "Showing API logs (last $lines lines)..."
    
    if [ "$follow" = "true" ]; then
        print_status "Following API logs (Press Ctrl+C to exit)..."
        docker-compose -f docker-compose.dev.yml logs -f --tail="$lines" api
    else
        docker-compose -f docker-compose.dev.yml logs --tail="$lines" api
    fi
}

# Function to show database logs
show_db_logs() {
    local lines=${1:-50}
    local follow=${2:-false}
    
    print_status "Showing PostgreSQL logs (last $lines lines)..."
    
    if [ "$follow" = "true" ]; then
        print_status "Following database logs (Press Ctrl+C to exit)..."
        docker-compose -f docker-compose.dev.yml logs -f --tail="$lines" db
    else
        docker-compose -f docker-compose.dev.yml logs --tail="$lines" db
    fi
}

# Function to show Redis logs
show_redis_logs() {
    local lines=${1:-50}
    local follow=${2:-false}
    
    print_status "Showing Redis logs (last $lines lines)..."
    
    if [ "$follow" = "true" ]; then
        print_status "Following Redis logs (Press Ctrl+C to exit)..."
        docker-compose -f docker-compose.dev.yml logs -f --tail="$lines" redis
    else
        docker-compose -f docker-compose.dev.yml logs --tail="$lines" redis
    fi
}

# Function to show error logs only
show_error_logs() {
    local lines=${1:-50}
    
    print_status "Showing error logs from all services (last $lines lines)..."
    docker-compose -f docker-compose.dev.yml logs --tail="$lines" | grep -i "error\|exception\|failed\|fatal" || print_warning "No error logs found"
}

# Function to show service status
show_service_status() {
    print_status "Service Status:"
    docker-compose -f docker-compose.dev.yml ps
    echo ""
    
    print_status "Container Resource Usage:"
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}" $(docker-compose -f docker-compose.dev.yml ps -q) 2>/dev/null || print_warning "Could not get resource usage"
}

# Function for interactive log viewer
interactive_logs() {
    while true; do
        echo ""
        echo "📋 Log Viewer Menu"
        echo "=================="
        echo "  1) All services (follow)"
        echo "  2) API only (follow)"
        echo "  3) Database only (follow)"
        echo "  4) Redis only (follow)"
        echo "  5) Recent errors"
        echo "  6) Service status"
        echo "  7) All services (last 100 lines)"
        echo "  8) API only (last 100 lines)"
        echo "  9) Exit"
        echo ""
        
        read -p "Choose an option (1-9): " -n 1 -r
        echo ""
        
        case $REPLY in
            1)
                show_all_logs 50 true
                ;;
            2)
                show_api_logs 50 true
                ;;
            3)
                show_db_logs 50 true
                ;;
            4)
                show_redis_logs 50 true
                ;;
            5)
                show_error_logs 100
                ;;
            6)
                show_service_status
                ;;
            7)
                show_all_logs 100 false
                ;;
            8)
                show_api_logs 100 false
                ;;
            9)
                print_status "Exiting log viewer"
                exit 0
                ;;
            *)
                print_error "Invalid option. Please choose 1-9."
                ;;
        esac
        
        if [ $REPLY -ne 5 ] && [ $REPLY -ne 6 ]; then
            echo ""
            read -p "Press Enter to return to menu..."
        fi
    done
}

# Main execution function
main() {
    echo "📋 Home Kitchen Manager API - Development Logs"
    echo "=============================================="
    
    # Check if services are running
    check_services
    
    # Parse arguments
    case "$1" in
        --api|-a)
            show_api_logs "${2:-50}" "${3:-false}"
            ;;
        --db|-d)
            show_db_logs "${2:-50}" "${3:-false}"
            ;;
        --redis|-r)
            show_redis_logs "${2:-50}" "${3:-false}"
            ;;
        --errors|-e)
            show_error_logs "${2:-50}"
            ;;
        --status|-s)
            show_service_status
            ;;
        --follow|-f)
            case "$2" in
                api)
                    show_api_logs "${3:-50}" true
                    ;;
                db)
                    show_db_logs "${3:-50}" true
                    ;;
                redis)
                    show_redis_logs "${3:-50}" true
                    ;;
                *)
                    show_all_logs "${2:-50}" true
                    ;;
            esac
            ;;
        --lines|-l)
            show_all_logs "${2:-50}" false
            ;;
        --interactive|-i)
            interactive_logs
            ;;
        "")
            # Default: show recent API logs and offer to follow
            show_api_logs 20 false
            echo ""
            read -p "Would you like to follow the logs? (y/N): " -n 1 -r
            echo ""
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                show_api_logs 50 true
            fi
            ;;
        *)
            print_error "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
}

# Help function
show_help() {
    echo "Home Kitchen Manager API - Development Logs Script"
    echo ""
    echo "Usage: $0 [OPTIONS] [LINES]"
    echo ""
    echo "Options:"
    echo "  -h, --help           Show this help message"
    echo "  -a, --api            Show API logs only"
    echo "  -d, --db             Show database logs only"
    echo "  -r, --redis          Show Redis logs only"
    echo "  -e, --errors         Show error logs only"
    echo "  -s, --status         Show service status and resource usage"
    echo "  -f, --follow [SVC]   Follow logs (optionally specify service)"
    echo "  -l, --lines N        Show last N lines (default: 50)"
    echo "  -i, --interactive    Interactive log viewer menu"
    echo ""
    echo "Examples:"
    echo "  $0                   Show recent API logs (interactive)"
    echo "  $0 --api             Show API logs"
    echo "  $0 --follow          Follow all logs"
    echo "  $0 --follow api      Follow API logs only"
    echo "  $0 --errors          Show recent error logs"
    echo "  $0 --lines 100       Show last 100 lines from all services"
    echo "  $0 --interactive     Interactive menu"
    echo ""
    echo "Services: api, db, redis"
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