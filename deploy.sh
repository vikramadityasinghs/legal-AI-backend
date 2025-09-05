#!/bin/bash

# Legal Document Analysis System - Deployment Script
# This script sets up and runs the complete system

set -e

echo "🏛️  Legal Document Analysis System"
echo "=================================="

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

# Check if Python is available
check_python() {
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
    else
        print_error "Python is not installed or not in PATH"
        exit 1
    fi
    print_success "Python found: $PYTHON_CMD"
}

# Setup backend
setup_backend() {
    print_status "Setting up backend..."
    
    cd backend
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "../.venv" ]; then
        print_status "Creating Python virtual environment..."
        $PYTHON_CMD -m venv ../.venv
    fi
    
    # Activate virtual environment
    source ../.venv/bin/activate
    
    # Install dependencies
    print_status "Installing Python dependencies..."
    pip install -r requirements.txt
    
    print_success "Backend setup complete"
    cd ..
}

# Start backend server
start_backend() {
    print_status "Starting FastAPI backend server..."
    
    cd backend
    source ../.venv/bin/activate
    
    # Kill any existing process on port 8000
    if lsof -ti:8000 > /dev/null 2>&1; then
        print_warning "Killing existing process on port 8000..."
        lsof -ti:8000 | xargs kill -9
        sleep 2
    fi
    
    # Start server in background
    nohup uvicorn main:app --reload --host 0.0.0.0 --port 8000 > ../backend.log 2>&1 &
    BACKEND_PID=$!
    echo $BACKEND_PID > ../backend.pid
    
    # Wait for server to start
    print_status "Waiting for backend to start..."
    sleep 5
    
    # Check if backend is running
    if curl -s http://localhost:8000/ > /dev/null; then
        print_success "Backend server started on http://localhost:8000"
    else
        print_error "Failed to start backend server"
        cat ../backend.log
        exit 1
    fi
    
    cd ..
}

# Start frontend server
start_frontend() {
    print_status "Starting frontend server..."
    
    cd frontend-simple
    
    # Kill any existing process on port 3000
    if lsof -ti:3000 > /dev/null 2>&1; then
        print_warning "Killing existing process on port 3000..."
        lsof -ti:3000 | xargs kill -9
        sleep 2
    fi
    
    # Start simple HTTP server in background
    nohup $PYTHON_CMD -m http.server 3000 > ../frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > ../frontend.pid
    
    # Wait for server to start
    sleep 3
    
    # Check if frontend is running
    if curl -s http://localhost:3000/ > /dev/null; then
        print_success "Frontend server started on http://localhost:3000"
    else
        print_error "Failed to start frontend server"
        cat ../frontend.log
        exit 1
    fi
    
    cd ..
}

# Test the system
test_system() {
    print_status "Testing system endpoints..."
    
    # Test backend health
    if curl -s http://localhost:8000/ | grep -q "AI Legal Document Analysis API"; then
        print_success "Backend health check passed"
    else
        print_error "Backend health check failed"
        return 1
    fi
    
    # Test frontend access
    if curl -s http://localhost:3000/ | grep -q "Legal Document Analysis System"; then
        print_success "Frontend accessibility check passed"
    else
        print_error "Frontend accessibility check failed"
        return 1
    fi
    
    print_success "All system tests passed!"
}

# Stop services
stop_services() {
    print_status "Stopping services..."
    
    # Stop backend
    if [ -f backend.pid ]; then
        BACKEND_PID=$(cat backend.pid)
        if kill -0 $BACKEND_PID 2>/dev/null; then
            kill $BACKEND_PID
            print_success "Backend server stopped"
        fi
        rm -f backend.pid
    fi
    
    # Stop frontend
    if [ -f frontend.pid ]; then
        FRONTEND_PID=$(cat frontend.pid)
        if kill -0 $FRONTEND_PID 2>/dev/null; then
            kill $FRONTEND_PID
            print_success "Frontend server stopped"
        fi
        rm -f frontend.pid
    fi
    
    # Kill any remaining processes
    if lsof -ti:8000 > /dev/null 2>&1; then
        lsof -ti:8000 | xargs kill -9
    fi
    
    if lsof -ti:3000 > /dev/null 2>&1; then
        lsof -ti:3000 | xargs kill -9
    fi
}

# Open browser
open_browser() {
    print_status "Opening system in browser..."
    
    if command -v open &> /dev/null; then
        # macOS
        open http://localhost:3000
    elif command -v xdg-open &> /dev/null; then
        # Linux
        xdg-open http://localhost:3000
    elif command -v start &> /dev/null; then
        # Windows
        start http://localhost:3000
    else
        print_warning "Could not auto-open browser. Please visit http://localhost:3000"
    fi
}

# Show status
show_status() {
    echo ""
    echo "🚀 System Status:"
    echo "=================="
    
    # Check backend
    if curl -s http://localhost:8000/ > /dev/null 2>&1; then
        echo -e "Backend:  ${GREEN}✅ Running${NC} (http://localhost:8000)"
    else
        echo -e "Backend:  ${RED}❌ Not running${NC}"
    fi
    
    # Check frontend
    if curl -s http://localhost:3000/ > /dev/null 2>&1; then
        echo -e "Frontend: ${GREEN}✅ Running${NC} (http://localhost:3000)"
    else
        echo -e "Frontend: ${RED}❌ Not running${NC}"
    fi
    
    echo ""
    echo "📊 System URLs:"
    echo "==============="
    echo "🌐 Frontend:    http://localhost:3000"
    echo "🔧 Backend API: http://localhost:8000"
    echo "📚 API Docs:    http://localhost:8000/docs"
    echo ""
}

# Show help
show_help() {
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  start    - Start the complete system (default)"
    echo "  stop     - Stop all services"
    echo "  restart  - Restart all services"
    echo "  status   - Show system status"
    echo "  test     - Run system tests"
    echo "  logs     - Show service logs"
    echo "  help     - Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0           # Start the system"
    echo "  $0 start     # Start the system"
    echo "  $0 stop      # Stop all services"
    echo "  $0 status    # Check system status"
}

# Show logs
show_logs() {
    echo "📋 Backend Logs:"
    echo "================"
    if [ -f backend.log ]; then
        tail -20 backend.log
    else
        echo "No backend logs found"
    fi
    
    echo ""
    echo "📋 Frontend Logs:"
    echo "================="
    if [ -f frontend.log ]; then
        tail -20 frontend.log
    else
        echo "No frontend logs found"
    fi
}

# Main execution
main() {
    local command=${1:-start}
    
    case $command in
        start)
            check_python
            setup_backend
            start_backend
            start_frontend
            test_system
            show_status
            open_browser
            
            print_success "🎉 Legal Document Analysis System is ready!"
            echo ""
            print_status "Visit http://localhost:3000 to use the application"
            print_status "API documentation: http://localhost:8000/docs"
            print_status "Run '$0 stop' to shut down the system"
            ;;
        stop)
            stop_services
            print_success "System stopped"
            ;;
        restart)
            stop_services
            sleep 2
            main start
            ;;
        status)
            show_status
            ;;
        test)
            check_python
            if [ -f ".venv/bin/activate" ]; then
                source .venv/bin/activate
                $PYTHON_CMD test_api.py
            else
                print_error "Virtual environment not found. Run '$0 start' first."
            fi
            ;;
        logs)
            show_logs
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            print_error "Unknown command: $command"
            show_help
            exit 1
            ;;
    esac
}

# Trap to clean up on exit
trap 'stop_services' EXIT

# Run main function
main "$@"
