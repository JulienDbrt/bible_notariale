#!/bin/bash

# ChatDocAI Development Helper Script
# Usage: ./scripts/dev.sh [command] [service]

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
COMPOSE_FILE="docker-compose.dev.yml"
ENV_FILE="backend/.env"

# Helper functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if environment file exists
check_env() {
    if [ ! -f "$ENV_FILE" ]; then
        log_warning "Environment file $ENV_FILE not found. Creating from template..."
        if [ -f ".env.example" ]; then
            cp .env.example $ENV_FILE
            log_success "Created $ENV_FILE from template. Please review and update values."
        else
            log_error "No .env.example template found. Please create $ENV_FILE manually."
            exit 1
        fi
    fi
}

# Show help
show_help() {
    echo -e "${BLUE}ChatDocAI Development Helper${NC}"
    echo ""
    echo "Usage: $0 [command] [service]"
    echo ""
    echo "Commands:"
    echo "  start              Start all services"
    echo "  stop               Stop all services"
    echo "  restart [service]  Restart service(s)"
    echo "  rebuild [service]  Rebuild and restart service(s)"
    echo "  logs [service]     Show logs for service(s)"
    echo "  shell [service]    Open shell in service container"
    echo "  clean              Clean up containers, images, and volumes"
    echo "  status             Show service status"
    echo "  reset              Reset everything (clean + rebuild all)"
    echo ""
    echo "Services:"
    echo "  frontend           Next.js frontend"
    echo "  backend            FastAPI backend"
    echo "  supabase           PostgreSQL database"
    echo "  supabase-kong      API gateway"
    echo "  supabase-rest      REST API"
    echo ""
    echo "Examples:"
    echo "  $0 start                    # Start all services"
    echo "  $0 rebuild frontend         # Rebuild only frontend"
    echo "  $0 logs backend             # Show backend logs"
    echo "  $0 shell frontend           # Open shell in frontend container"
}

# Start all services
start_services() {
    log_info "Starting all services..."
    check_env
    docker-compose -f $COMPOSE_FILE up -d
    log_success "All services started. Access:"
    echo "  - Frontend: http://localhost:3000"
    echo "  - Backend API: http://localhost:8000"
    echo "  - Supabase: http://localhost:54321"
}

# Stop all services
stop_services() {
    log_info "Stopping all services..."
    docker-compose -f $COMPOSE_FILE down
    log_success "All services stopped"
}

# Restart services
restart_services() {
    local service=$1
    if [ -z "$service" ]; then
        log_info "Restarting all services..."
        docker-compose -f $COMPOSE_FILE restart
        log_success "All services restarted"
    else
        log_info "Restarting $service..."
        docker-compose -f $COMPOSE_FILE restart $service
        log_success "$service restarted"
    fi
}

# Rebuild and restart services
rebuild_services() {
    local service=$1
    if [ -z "$service" ]; then
        log_info "Rebuilding all services..."
        docker-compose -f $COMPOSE_FILE down
        docker-compose -f $COMPOSE_FILE build --no-cache
        docker-compose -f $COMPOSE_FILE up -d
        log_success "All services rebuilt and started"
    else
        log_info "Rebuilding $service..."
        docker-compose -f $COMPOSE_FILE stop $service
        docker-compose -f $COMPOSE_FILE build --no-cache $service
        docker-compose -f $COMPOSE_FILE up -d $service
        log_success "$service rebuilt and started"
    fi
}

# Show logs
show_logs() {
    local service=$1
    if [ -z "$service" ]; then
        log_info "Showing logs for all services..."
        docker-compose -f $COMPOSE_FILE logs -f
    else
        log_info "Showing logs for $service..."
        docker-compose -f $COMPOSE_FILE logs -f $service
    fi
}

# Open shell in container
open_shell() {
    local service=$1
    if [ -z "$service" ]; then
        log_error "Please specify a service for shell access"
        exit 1
    fi
    
    log_info "Opening shell in $service container..."
    case $service in
        frontend)
            docker-compose -f $COMPOSE_FILE exec $service /bin/sh
            ;;
        backend)
            docker-compose -f $COMPOSE_FILE exec $service /bin/bash
            ;;
        supabase*)
            docker-compose -f $COMPOSE_FILE exec $service /bin/bash
            ;;
        *)
            docker-compose -f $COMPOSE_FILE exec $service /bin/sh
            ;;
    esac
}

# Clean up
clean_up() {
    log_warning "This will remove all containers, images, and volumes. Continue? (y/N)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        log_info "Cleaning up..."
        docker-compose -f $COMPOSE_FILE down -v --rmi all
        docker system prune -f
        log_success "Cleanup completed"
    else
        log_info "Cleanup cancelled"
    fi
}

# Show status
show_status() {
    log_info "Service status:"
    docker-compose -f $COMPOSE_FILE ps
}

# Reset everything
reset_all() {
    log_warning "This will reset everything (containers, images, volumes). Continue? (y/N)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        clean_up
        log_info "Rebuilding all services..."
        docker-compose -f $COMPOSE_FILE build --no-cache
        docker-compose -f $COMPOSE_FILE up -d
        log_success "Reset completed"
    else
        log_info "Reset cancelled"
    fi
}

# Main script logic
case $1 in
    start)
        start_services
        ;;
    stop)
        stop_services
        ;;
    restart)
        restart_services $2
        ;;
    rebuild)
        rebuild_services $2
        ;;
    logs)
        show_logs $2
        ;;
    shell)
        open_shell $2
        ;;
    clean)
        clean_up
        ;;
    status)
        show_status
        ;;
    reset)
        reset_all
        ;;
    help|--help|-h)
        show_help
        ;;
    "")
        show_help
        ;;
    *)
        log_error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac