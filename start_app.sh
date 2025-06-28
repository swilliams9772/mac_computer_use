#!/bin/bash

# Enhanced Streamlit App Startup Script
# Handles port conflicts and ensures clean startup

echo "🚀 Starting Claude Computer Use for Mac..."

# Kill any existing Streamlit processes
echo "🔍 Checking for existing Streamlit processes..."
pkill -f "streamlit run app.py" 2>/dev/null
sleep 2

# Change to app directory
cd "$(dirname "$0")"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "📦 Activating virtual environment..."
    source venv/bin/activate
fi

# Check for required dependencies
echo "🔧 Checking dependencies..."
python -c "import streamlit, anthropic" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Missing dependencies. Installing..."
    pip install -r requirements.txt
fi

# Find available port
PORT=8501
while lsof -i:$PORT >/dev/null 2>&1; do
    echo "⚠️  Port $PORT is in use, trying $((PORT+1))..."
    ((PORT++))
done

echo "✅ Using port $PORT"

# Start Streamlit with optimized settings
echo "🎯 Starting Streamlit app..."
streamlit run app.py \
    --server.port=$PORT \
    --server.headless=true \
    --browser.gatherUsageStats=false \
    --server.enableCORS=false \
    --server.enableXsrfProtection=false \
    --logger.level=info

echo "🎉 App started successfully at http://localhost:$PORT" 