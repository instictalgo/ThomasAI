#!/bin/bash

# Make sure we're in the right directory
cd "$(dirname "$0")"

# Ensure the virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Activating virtual environment..."
    source ~/thomas_venv/bin/activate
fi

# Stop any existing processes
echo "Stopping any existing processes..."
pkill -f 'python api/main.py' 2>/dev/null
pkill -f 'streamlit run' 2>/dev/null
sleep 1

# Create database tables if they don't exist
echo "Initializing database..."
python init_db.py

# Start the API server
echo "Starting API server..."
python api/main.py > api_server.log 2>&1 &
API_PID=$!
echo "API server started with PID $API_PID"

# Wait for API server to start
echo "Waiting for API server to initialize..."
sleep 3

# Check if API server is running
if ! ps -p $API_PID > /dev/null; then
    echo "❌ API server failed to start! Check api_server.log for details."
    exit 1
fi

# Start the Streamlit dashboard
echo "Starting Streamlit dashboard..."
streamlit run ui/dashboard.py > dashboard.log 2>&1 &
STREAMLIT_PID=$!
echo "Streamlit dashboard started with PID $STREAMLIT_PID"

# Wait for Streamlit to start
echo "Waiting for Streamlit to initialize..."
sleep 3

# Check if Streamlit is running
if ! ps -p $STREAMLIT_PID > /dev/null; then
    echo "❌ Streamlit dashboard failed to start! Check dashboard.log for details."
    exit 1
fi

echo ""
echo "✅ Thomas AI System is now running!"
echo "   API server: http://localhost:8000"
echo "   API documentation: http://localhost:8000/docs"
echo "   Dashboard: http://localhost:8501"
echo ""
echo "To stop the system, run: bash stop.sh"
echo "To view logs, run: tail -f api_server.log or tail -f dashboard.log"
