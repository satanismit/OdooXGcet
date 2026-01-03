#!/bin/bash
# Quick Start Script for Full System Integration
# This script checks and starts all components

echo "🚀 Dayflow HRMS - System Startup"
echo "=================================="

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if a port is in use
port_in_use() {
    netstat -an | grep ":$1" | grep LISTEN >/dev/null 2>&1
}

echo ""
echo "📋 Checking Prerequisites..."
echo ""

# Check MongoDB
if command_exists mongod; then
    echo -e "${GREEN}✅ MongoDB installed${NC}"
    if port_in_use 27017; then
        echo -e "${GREEN}✅ MongoDB is running on port 27017${NC}"
    else
        echo -e "${YELLOW}⚠️  MongoDB not running. Start it with: mongod${NC}"
    fi
else
    echo -e "${RED}❌ MongoDB not installed${NC}"
    echo "   Install from: https://www.mongodb.com/try/download/community"
fi

# Check Python
if command_exists python; then
    PYTHON_VERSION=$(python --version 2>&1)
    echo -e "${GREEN}✅ Python installed: $PYTHON_VERSION${NC}"
else
    echo -e "${RED}❌ Python not installed${NC}"
fi

# Check Node.js
if command_exists node; then
    NODE_VERSION=$(node --version)
    echo -e "${GREEN}✅ Node.js installed: $NODE_VERSION${NC}"
else
    echo -e "${RED}❌ Node.js not installed${NC}"
fi

# Check npm
if command_exists npm; then
    NPM_VERSION=$(npm --version)
    echo -e "${GREEN}✅ npm installed: v$NPM_VERSION${NC}"
else
    echo -e "${RED}❌ npm not installed${NC}"
fi

echo ""
echo "🔧 Checking Project Setup..."
echo ""

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo -e "${GREEN}✅ Virtual environment exists${NC}"
else
    echo -e "${YELLOW}⚠️  Virtual environment not found${NC}"
    echo "   Creating virtual environment..."
    python -m venv venv
fi

# Check if node_modules exists
if [ -d "node_modules" ]; then
    echo -e "${GREEN}✅ Node modules installed${NC}"
else
    echo -e "${YELLOW}⚠️  Node modules not installed${NC}"
    echo "   Run: npm install"
fi

# Check if .env exists
if [ -f ".env" ]; then
    echo -e "${GREEN}✅ Backend .env file exists${NC}"
else
    echo -e "${YELLOW}⚠️  Backend .env not found${NC}"
    echo "   Create .env with MongoDB and secret key configuration"
fi

echo ""
echo "🎯 Next Steps:"
echo ""
echo "1️⃣  Start MongoDB:"
echo "   mongod"
echo ""
echo "2️⃣  Start Backend (in new terminal):"
echo "   cd c:\\Users\\Admin\\OneDrive\\Desktop\\odduBackend\\OdooXGcet"
echo "   .\\venv\\Scripts\\activate  # Windows"
echo "   python main.py"
echo ""
echo "3️⃣  Start Frontend (in new terminal):"
echo "   cd c:\\Users\\Admin\\OneDrive\\Desktop\\odduBackend\\OdooXGcet"
echo "   npm run dev"
echo ""
echo "4️⃣  Run E2E Tests (optional):"
echo "   pytest test_e2e_connection.py -v"
echo ""
echo "5️⃣  Access Application:"
echo "   Frontend: http://localhost:5173"
echo "   Backend API: http://localhost:8000/docs"
echo ""
echo "=================================="
