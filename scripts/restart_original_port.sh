#!/bin/bash

echo "Stopping existing processes..."
pkill -f "python3 api/main.py" 2>/dev/null || true
pkill -f "streamlit run" 2>/dev/null || true
sleep 1

echo "Starting API server on port 8002..."
cd ~/thomas_app
python3 api/main.py > api_server.log 2>&1 &
API_PID=$!
sleep 3

echo "Starting Streamlit dashboard on port 8003..."
cd ~/thomas_app
python3 -m streamlit run ui/dashboard.py --server.port=8003 > dashboard.log 2>&1 &
STREAMLIT_PID=$!
sleep 1

# Check if processes are running
if ps -p $API_PID > /dev/null; then
    echo "✅ API server started successfully (PID: $API_PID)"
else
    echo "❌ API server failed to start"
    echo "--- Last 20 lines of API log ---"
    tail -n 20 ~/thomas_app/api_server.log
fi

if ps -p $STREAMLIT_PID > /dev/null; then
    echo "✅ Streamlit dashboard started successfully (PID: $STREAMLIT_PID)"
else
    echo "❌ Streamlit dashboard failed to start"
    echo "--- Last 20 lines of dashboard log ---"
    tail -n 20 ~/thomas_app/dashboard.log
fi

echo "System started! Try accessing at:"
echo "API: http://localhost:8002"
echo "API Documentation: http://localhost:8002/docs"
echo "Dashboard: http://localhost:8003"
