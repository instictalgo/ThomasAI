#!/bin/bash

echo "Stopping existing processes..."
pkill -f "python3 api/main.py" 2>/dev/null || true
pkill -f "streamlit run" 2>/dev/null || true
sleep 1

echo "Starting API server..."
cd ~/thomas_app
python3 api/main.py > api_server.log 2>&1 &
sleep 3

echo "Starting Streamlit dashboard..."
cd ~/thomas_app
python3 -m streamlit run ui/dashboard.py > dashboard.log 2>&1 &
sleep 1

echo "System started! Access at:"
echo "Dashboard: http://localhost:8501"
echo "API Documentation: http://localhost:8000/docs"
