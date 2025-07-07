#!/bin/bash

# MLB Analytics Mobile App - Stop Script
# This script stops both the Django backend and React Native frontend

# Add Homebrew lsof to PATH if available
if [ -f "/opt/homebrew/opt/lsof/bin/lsof" ]; then
    export PATH="/opt/homebrew/opt/lsof/bin:$PATH"
fi

echo "🛑 Stopping MLB Analytics Mobile App..."
echo "========================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
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

echo -e "${YELLOW}🧹 Stopping all MLB Analytics services...${NC}"

# Stop Django server (port 8000)
if command -v lsof >/dev/null 2>&1; then
    if check_port 8000; then
        echo -e "${YELLOW}Stopping Django server on port 8000...${NC}"
        lsof -ti:8000 | xargs kill -9 2>/dev/null || true
        echo -e "${GREEN}✅ Django server stopped${NC}"
    else
        echo -e "${YELLOW}Django server was not running${NC}"
    fi
    
    # Stop Expo server (port 8081)
    if check_port 8081; then
        echo -e "${YELLOW}Stopping Expo server on port 8081...${NC}"
        lsof -ti:8081 | xargs kill -9 2>/dev/null || true
        echo -e "${GREEN}✅ Expo server stopped${NC}"
    else
        echo -e "${YELLOW}Expo server was not running${NC}"
    fi
    
    # Stop Metro bundler (port 8082)
    if check_port 8082; then
        echo -e "${YELLOW}Stopping Metro bundler on port 8082...${NC}"
        lsof -ti:8082 | xargs kill -9 2>/dev/null || true
        echo -e "${GREEN}✅ Metro bundler stopped${NC}"
    else
        echo -e "${YELLOW}Metro bundler was not running${NC}"
    fi
else
    # Fallback: kill by process name
    echo -e "${YELLOW}Using process name cleanup (lsof not available)...${NC}"
    if pkill -f "runserver 8000" 2>/dev/null; then
        echo -e "${GREEN}✅ Django server stopped${NC}"
    else
        echo -e "${YELLOW}Django server was not running${NC}"
    fi
    
    if pkill -f "expo start" 2>/dev/null; then
        echo -e "${GREEN}✅ Expo server stopped${NC}"
    else
        echo -e "${YELLOW}Expo server was not running${NC}"
    fi
    
    if pkill -f "metro" 2>/dev/null; then
        echo -e "${GREEN}✅ Metro bundler stopped${NC}"
    else
        echo -e "${YELLOW}Metro bundler was not running${NC}"
    fi
fi

# Kill any remaining Python processes
pkill -f "python3 manage.py runserver" 2>/dev/null || true

# Kill any remaining Node/Expo processes
pkill -f "expo start" 2>/dev/null || true
pkill -f "metro" 2>/dev/null || true

sleep 2

echo ""
echo -e "${GREEN}🎉 All MLB Analytics services have been stopped!${NC}"
echo "============================================="
echo ""
echo -e "${BLUE}To restart the app, run:${NC}"
echo "./start-mlb-app.sh"
echo ""
