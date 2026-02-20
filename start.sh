#!/bin/bash

# CoPipes Infrastructure Management Script
# Usage: ./start.sh [command]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SUPABASE_DIR="$SCRIPT_DIR/supabase"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[*]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[+]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[-]${NC} $1"
}

# Wait for a container to be healthy
wait_for_healthy() {
    local container=$1
    local timeout=${2:-60}
    local count=0

    print_status "Waiting for $container to be healthy..."
    while [ $count -lt $timeout ]; do
        if docker inspect --format='{{.State.Health.Status}}' "$container" 2>/dev/null | grep -q "healthy"; then
            print_success "$container is healthy"
            return 0
        fi
        sleep 1
        count=$((count + 1))
    done
    print_error "$container did not become healthy within ${timeout}s"
    return 1
}

# Start Supabase services
start_supabase() {
    print_status "Starting Supabase services..."
    cd "$SUPABASE_DIR"
    docker compose up -d

    # Wait for database to be healthy before proceeding
    wait_for_healthy "supabase-db" 120

    print_success "Supabase services started"
    cd "$SCRIPT_DIR"
}

# Start CoPipes application services
start_app() {
    print_status "Starting CoPipes application services..."

    # Check if Supabase network exists
    if ! docker network ls | grep -q "supabase_default"; then
        print_error "Supabase network not found. Please start Supabase first with: ./start.sh supabase"
        exit 1
    fi

    # Check if Supabase DB is running
    if ! docker ps | grep -q "supabase-db"; then
        print_error "Supabase database is not running. Please start Supabase first with: ./start.sh supabase"
        exit 1
    fi

    docker compose up -d
    print_success "CoPipes application services started"
}

# Start all services
start_all() {
    print_status "Starting all CoPipes infrastructure..."
    start_supabase
    sleep 5  # Give Supabase a moment to fully initialize
    start_app
    print_success "All services started successfully!"
    echo ""
    show_urls
}

# Stop all services
stop_all() {
    print_status "Stopping all services..."

    # Stop CoPipes services first
    print_status "Stopping CoPipes application services..."
    docker compose down 2>/dev/null || true

    # Stop Supabase services
    print_status "Stopping Supabase services..."
    cd "$SUPABASE_DIR"
    docker compose down 2>/dev/null || true
    cd "$SCRIPT_DIR"

    print_success "All services stopped"
}

# Show service URLs
show_urls() {
    echo -e "${GREEN}Service URL:${NC}"
    #echo "  FastAPI (App API):  http://localhost:8000"
    echo "  CoPipes:           http://localhost:3000"
    #echo "  Airflow:            http://localhost:8080"
    #echo "  Supabase API:       http://localhost:8001"
    #echo "  Supabase Studio:    http://localhost:8001"
    #echo "  Postgres:           localhost:5432"
}

# Show container status
show_status() {
    print_status "Container Status:"
    echo ""
    echo -e "${BLUE}Supabase Services:${NC}"
    docker compose -f "$SUPABASE_DIR/docker-compose.yml" ps 2>/dev/null || echo "  Not running"
    echo ""
    echo -e "${BLUE}CoPipes Services:${NC}"
    docker compose ps 2>/dev/null || echo "  Not running"
}

# Show logs
show_logs() {
    local service=$1
    if [ -z "$service" ]; then
        print_status "Showing logs for all CoPipes services (Ctrl+C to exit)..."
        docker compose logs -f
    else
        print_status "Showing logs for $service (Ctrl+C to exit)..."
        docker compose logs -f "$service"
    fi
}

# Full reset - remove containers and volumes
full_reset() {
    print_warning "This will remove all containers and volumes (data will be lost)!"
    read -p "Are you sure? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Performing full reset..."

        # Stop and remove CoPipes
        docker compose down -v --remove-orphans 2>/dev/null || true

        # Stop and remove Supabase
        cd "$SUPABASE_DIR"
        docker compose down -v --remove-orphans 2>/dev/null || true
        cd "$SCRIPT_DIR"

        print_success "Full reset complete"
    else
        print_status "Reset cancelled"
    fi
}

# Open psql shell to Supabase Postgres
db_shell() {
    print_status "Opening psql shell to Supabase Postgres..."
    docker exec -it supabase-db psql -U postgres
}

# Show help
show_help() {
    echo "CoPipes Infrastructure Management"
    echo ""
    echo "Usage: ./start.sh [command]"
    echo ""
    echo "Commands:"
    echo "  up        Start all services (Supabase first, then CoPipes)"
    echo "  down      Stop all services gracefully"
    echo "  supabase  Start only Supabase services"
    echo "  app       Start only CoPipes application (requires Supabase running)"
    echo "  logs      Follow logs for all services"
    echo "  logs <s>  Follow logs for specific service"
    echo "  status    Show container status"
    echo "  reset     Full cleanup (containers + volumes)"
    echo "  db        Open psql shell to Supabase Postgres"
    echo "  help      Show this help message"
    echo ""
    show_urls
}

# Main command handler
case "${1:-help}" in
    up)
        start_all
        ;;
    down)
        stop_all
        ;;
    supabase)
        start_supabase
        ;;
    app)
        start_app
        ;;
    logs)
        show_logs "$2"
        ;;
    status)
        show_status
        ;;
    reset)
        full_reset
        ;;
    db)
        db_shell
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac
