#!/bin/bash

# MLB Analytics Mobile App - Complete Startup Script
# This script starts both the Django backend and React Native frontend

# Add Homebrew lsof to PATH if available
if [ -f "/opt/homebrew/opt/lsof/bin/lsof" ]; then
    export PATH="/opt/homebrew/opt/lsof/bin:$PATH"
fi

echo "🚀 Starting MLB Analytics Mobile App..."
echo "================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to check if a port is in use
check_port() {
    # Try lsof first, fallback to netstat if lsof is not available
    if command -v lsof >/dev/null 2>&1; then
        if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null 2>&1; then
            return 0
        else
            return 1
        fi
    else
        # Fallback to netstat
        if netstat -an | grep -q ":$1.*LISTEN"; then
            return 0
        else
            return 1
        fi
    fi
}

# Function to kill processes on specific ports
cleanup_ports() {
    echo -e "${YELLOW}🧹 Cleaning up existing processes...${NC}"
    
    # Kill Django server (port 8000)
    if command -v lsof >/dev/null 2>&1; then
        if check_port 8000; then
            echo -e "${YELLOW}Stopping Django server on port 8000...${NC}"
            lsof -ti:8000 | xargs kill -9 2>/dev/null || true
        fi
        
        # Kill Expo server (port 8081)
        if check_port 8081; then
            echo -e "${YELLOW}Stopping Expo server on port 8081...${NC}"
            lsof -ti:8081 | xargs kill -9 2>/dev/null || true
        fi
        
        # Kill Metro bundler (port 8082)
        if check_port 8082; then
            echo -e "${YELLOW}Stopping Metro bundler on port 8082...${NC}"
            lsof -ti:8082 | xargs kill -9 2>/dev/null || true
        fi
    else
        # Fallback: kill by process name
        echo -e "${YELLOW}Using process name cleanup (lsof not available)...${NC}"
        pkill -f "runserver 8000" 2>/dev/null || true
        pkill -f "expo start" 2>/dev/null || true
        pkill -f "metro" 2>/dev/null || true
    fi
    
    sleep 2
}

# Cleanup existing processes
cleanup_ports

# Start Django Backend
echo -e "${BLUE}🐍 Starting Django Backend...${NC}"
cd /Users/coletrammell/Documents/GitHub/Big-Brother/mlb-analytics-backend/src

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install requirements if needed
if [ ! -f ".requirements_installed" ]; then
    echo -e "${YELLOW}Installing Python requirements...${NC}"
    pip install -r ../requirements.txt
    touch .requirements_installed
fi

# Run database migrations
echo -e "${YELLOW}Running database migrations...${NC}"
python3 manage.py migrate --noinput

# Create default users if they don't exist
echo -e "${YELLOW}Setting up default users...${NC}"
python3 manage.py shell -c "
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@mlbanalytics.com', 'admin123')
    print('Created admin user: admin/admin123')
if not User.objects.filter(username='testuser').exists():
    User.objects.create_user('testuser', 'test@mlbanalytics.com', 'test123')
    print('Created test user: testuser/test123')
"

# Start Django server in background
echo -e "${GREEN}Starting Django server on http://10.0.0.22:8000${NC}"
python3 manage.py runserver 0.0.0.0:8000 &
DJANGO_PID=$!

# Wait for Django to start
echo -e "${YELLOW}Waiting for Django server to start...${NC}"
sleep 8

# Check if Django is running (try multiple methods)
DJANGO_RUNNING=false
if check_port 8000; then
    DJANGO_RUNNING=true
elif curl -s http://localhost:8000 >/dev/null 2>&1; then
    DJANGO_RUNNING=true
elif kill -0 $DJANGO_PID 2>/dev/null; then
    DJANGO_RUNNING=true
fi

if [ "$DJANGO_RUNNING" = true ]; then
    echo -e "${GREEN}✅ Django server is running!${NC}"
else
    echo -e "${RED}❌ Failed to start Django server${NC}"
    exit 1
fi

# Start React Native Frontend
echo -e "${BLUE}📱 Starting React Native Frontend...${NC}"
cd /Users/coletrammell/Documents/GitHub/Big-Brother/react-native-frontend/mlb-analytics-mobile

# Install npm dependencies if needed
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}Installing npm dependencies...${NC}"
    npm install
fi

# Start Expo development server
echo -e "${GREEN}Starting Expo development server...${NC}"
echo -e "${BLUE}📱 Scan the QR code with Expo Go app on your iPhone!${NC}"
npx expo start --go &
EXPO_PID=$!

# Wait for Expo to start
sleep 3

echo ""
echo -e "${GREEN}🎉 MLB Analytics App is now running!${NC}"
echo "================================================"
echo -e "${BLUE}📊 Django Backend:${NC} http://10.0.0.22:8000"
echo -e "${BLUE}📱 Expo Frontend:${NC} http://localhost:8081"
echo ""
echo -e "${YELLOW}📱 To test on your iPhone:${NC}"
echo "1. Open Expo Go app on your iPhone"
echo "2. Scan the QR code displayed in the terminal"
echo "3. Your MLB Analytics app will load!"
echo ""
echo -e "${YELLOW}💻 To test in simulator:${NC}"
echo "Press 'i' in the Expo terminal to open iOS Simulator"
echo ""
echo -e "${RED}🛑 To stop all servers:${NC}"
echo "Press Ctrl+C or run: ./stop-mlb-app.sh"
echo ""

# Function to handle cleanup on script exit
cleanup() {
    echo -e "\n${YELLOW}🛑 Shutting down MLB Analytics App...${NC}"
    kill $DJANGO_PID 2>/dev/null || true
    kill $EXPO_PID 2>/dev/null || true
    cleanup_ports
    echo -e "${GREEN}✅ All servers stopped!${NC}"
}

# Set trap to cleanup on script exit
trap cleanup EXIT INT TERM

# Keep script running and monitor processes
while true; do
    # Check if Django is still running
    if ! kill -0 $DJANGO_PID 2>/dev/null; then
        echo -e "${RED}❌ Django server stopped unexpectedly${NC}"
        break
    fi
    
    # Check if Expo is still running
    if ! kill -0 $EXPO_PID 2>/dev/null; then
        echo -e "${RED}❌ Expo server stopped unexpectedly${NC}"
        break
    fi
    
    sleep 5
done

echo -e "${YELLOW}Script ended. Cleaning up...${NC}"
