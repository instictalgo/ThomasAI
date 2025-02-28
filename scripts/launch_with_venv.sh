#!/bin/bash

echo "========================================"
echo "    Thomas AI Management System"
echo "========================================"

# Activate virtual environment
source ~/thomas_app/thomas_venv/bin/activate

# Kill any existing processes
echo "Stopping any existing processes..."
pkill -f "python3 api/main.py" 2>/dev/null || true
pkill -f "streamlit run" 2>/dev/null || true
sleep 1

# Start API server
echo "Starting API server on port 8002..."
cd ~/thomas_app
python api/main.py --port 8002 > api_server.log 2>&1 &
API_PID=$!
echo "API server started with PID: $API_PID"
sleep 3

# Check if API server is running
if ! ps -p $API_PID > /dev/null; then
    echo "❌ API server failed to start! Check api_server.log for details."
    tail -n 20 api_server.log
    exit 1
fi

# Start Streamlit dashboard
echo "Starting Streamlit dashboard on port 8003..."
cd ~/thomas_app
python -m streamlit run ui/dashboard.py --server.port=8003 --server.address=0.0.0.0 > dashboard.log 2>&1 &
STREAMLIT_PID=$!
echo "Streamlit dashboard started with PID: $STREAMLIT_PID"
sleep 3

# Check if Streamlit is running
if ! ps -p $STREAMLIT_PID > /dev/null; then
    echo "❌ Streamlit dashboard failed to start! Check dashboard.log for details."
    tail -n 20 dashboard.log
    exit 1
fi

echo ""
echo "✅ Thomas AI System is now running!"
echo "   API server: http://localhost:8002"
echo "   API documentation: http://localhost:8002/docs"
echo "   Dashboard: http://localhost:8003"
echo ""
echo "To stop the system, run: bash stop_thomas.sh"
