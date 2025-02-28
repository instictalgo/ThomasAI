#!/bin/bash

echo "========================================"
echo "  Stopping Thomas AI Management System"
echo "========================================"

# Kill the API server
echo "Stopping API server..."
pkill -f "python api/main.py" || echo "No API server process found"

# Kill the Streamlit dashboard
echo "Stopping Streamlit dashboard..."
pkill -f "streamlit run" || echo "No Streamlit process found"

# Verify all processes are stopped
sleep 2
if pgrep -f "python api/main.py" > /dev/null || pgrep -f "streamlit run" > /dev/null; then
    echo "Some processes are still running. Forcing termination..."
    pkill -9 -f "python api/main.py" 2>/dev/null || true
    pkill -9 -f "streamlit run" 2>/dev/null || true
fi

echo "✅ Thomas AI System has been stopped"
echo "   To restart the system, run: ./run_wrapper.sh"
