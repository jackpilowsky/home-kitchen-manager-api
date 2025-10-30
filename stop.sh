#!/bin/bash

# Home Kitchen Manager API - Development Environment Stop Script
# This script stops the development environment and cleans up resources

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
    if docker-compose -f docker-compose.dev.yml ps -q | grep -q .; then
        return 0  # Services are running
    else
        return 1  # No services running
    fi
}

# Function to show current service status
show_current_status() {
    print_status "Current service status:"
    docker-compose -f docker-compose.dev.yml ps
    echo ""
}

# Function to stop services gracefully
stop_services() {
    print_status "Stopping development services..."
    
    if docker-compose -f docker-compose.dev.yml stop; then
        print_success "Services stopped successfully"
    else
        print_warning "Some services may not have stopped cleanly"
    fi
}

# Function to remove containers
remove_containers() {
    print_status "Removing containers..."
    
    if docker-compose -f docker-compose.dev.yml down; then
        print_success "Containers removed successfully"
    else
        print_warning "Some containers may not have been removed cleanly"
    fi
}

# Function to remove volumes (data cleanup)
remove_volumes() {
    print_status "Removing development volumes and data..."
    print_warning "This will delete all development database data!"
    
    read -p "Are you sure you want to remove all data? (y/N): " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if docker-compose -f docker-compose.dev.yml down -v; then
            print_success "Volumes removed successfully"
        else
            print_warning "Some volumes may not have been removed cleanly"
        fi
    else
        print_status "Volume removal cancelled"
    fi
}

# Function to remove images
remove_images() {
    print_status "Removing development images..."
    
    read -p "Are you sure you want to remove development images? (y/N): " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # Remove only the API image (keep PostgreSQL and Redis images)
        api_image=$(docker-compose -f docker-compose.dev.yml config | grep "image:" | grep -v "postgres\|redis" | head -1 | awk '{print $2}')
        
        if [ ! -z "$api_image" ]; then
            if docker rmi "$api_image" 2>/dev/null; then
                print_success "API image removed successfully"
            else
                print_warning "API image may not exist or couldn't be removed"
            fi
        fi
        
        # Remove any dangling images
        if docker image prune -f > /dev/null 2>&1; then
            print_success "Dangling images cleaned up"
        fi
    else
        print_status "Image removal cancelled"
    fi
}

# Function to show cleanup summary
show_cleanup_summary() {
    print_status "Cleanup Summary:"
    echo "  ✅ Services stopped"
    echo "  ✅ Containers removed"
    
    if [ "$REMOVE_VOLUMES" = "true" ]; then
        echo "  ✅ Volumes and data removed"
    else
        echo "  ⏭️  Volumes preserved (data kept)"
    fi
    
    if [ "$REMOVE_IMAGES" = "true" ]; then
        echo "  ✅ Images removed"
    else
        echo "  ⏭️  Images preserved"
    fi
    
    echo ""
    print_status "To start again, run: ./start.sh"
}

# Function to show logs before stopping (if requested)
show_logs() {
    print_status "Showing recent logs from all services..."
    docker-compose -f docker-compose.dev.yml logs --tail=20
    echo ""
}

# Function for quick stop (just stop services)
quick_stop() {
    print_status "Quick stop - stopping services only..."
    stop_services
    print_success "Services stopped. Containers and data preserved."
    print_status "To start again: ./start.sh"
    print_status "To fully clean up: ./stop.sh --clean"
}

# Function for full cleanup
full_cleanup() {
    print_status "Full cleanup - removing everything..."
    stop_services
    remove_containers
    
    if [ "$1" = "--with-volumes" ]; then
        REMOVE_VOLUMES="true"
        remove_volumes
    fi
    
    if [ "$1" = "--with-images" ] || [ "$2" = "--with-images" ]; then
        REMOVE_IMAGES="true"
        remove_images
    fi
    
    show_cleanup_summary
}

# Main execution function
main() {
    echo "🛑 Stopping Home Kitchen Manager API Development Environment"
    echo "============================================================="
    
    # Check if services are running
    if ! check_services; then
        print_warning "No development services are currently running"
        exit 0
    fi
    
    # Show current status
    show_current_status
    
    # Parse arguments and execute appropriate action
    case "$1" in
        --quick|-q)
            quick_stop
            ;;
        --clean|-c)
            full_cleanup
            ;;
        --clean-all|--full)
            full_cleanup --with-volumes --with-images
            ;;
        --logs|-l)
            show_logs
            stop_services
            remove_containers
            show_cleanup_summary
            ;;
        *)
            # Default behavior - ask user what they want to do
            echo "What would you like to do?"
            echo "  1) Quick stop (preserve containers and data)"
            echo "  2) Stop and remove containers (preserve data)"
            echo "  3) Full cleanup (remove containers and data)"
            echo "  4) Show logs then stop"
            echo "  5) Cancel"
            echo ""
            
            read -p "Choose an option (1-5): " -n 1 -r
            echo ""
            echo ""
            
            case $REPLY in
                1)
                    quick_stop
                    ;;
                2)
                    stop_services
                    remove_containers
                    show_cleanup_summary
                    ;;
                3)
                    full_cleanup --with-volumes
                    ;;
                4)
                    show_logs
                    stop_services
                    remove_containers
                    show_cleanup_summary
                    ;;
                5)
                    print_status "Operation cancelled"
                    exit 0
                    ;;
                *)
                    print_error "Invalid option. Defaulting to quick stop."
                    quick_stop
                    ;;
            esac
            ;;
    esac
}

# Help function
show_help() {
    echo "Home Kitchen Manager API - Development Stop Script"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -h, --help       Show this help message"
    echo "  -q, --quick      Quick stop (preserve containers and data)"
    echo "  -c, --clean      Stop and remove containers (preserve data)"
    echo "  --clean-all      Full cleanup (remove everything including data)"
    echo "  --full           Same as --clean-all"
    echo "  -l, --logs       Show logs before stopping"
    echo ""
    echo "Examples:"
    echo "  $0               Interactive mode (asks what to do)"
    echo "  $0 --quick       Just stop services"
    echo "  $0 --clean       Stop and remove containers"
    echo "  $0 --clean-all   Remove everything including data"
    echo "  $0 --logs        Show logs then stop"
    echo ""
    echo "Data Preservation:"
    echo "  --quick:     Keeps containers and data"
    echo "  --clean:     Removes containers, keeps data"
    echo "  --clean-all: Removes everything (containers, data, volumes)"
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