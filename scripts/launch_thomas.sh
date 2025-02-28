#!/bin/bash

echo "========================================"
echo "    Thomas AI Management System"
echo "========================================"

# Make sure we're in the proper directory
cd ~/thomas_app

# Verify the virtual environment exists
if [ ! -d "thomas_venv" ]; then
    echo "Creating virtual environment..."
    python -m venv thomas_venv
fi

# Activate the virtual environment
source thomas_venv/bin/activate

# Install required packages if needed
echo "Checking dependencies..."
echo "Installing core packages..."
pip install streamlit==1.25.0 protobuf==3.20.3 pandas==1.5.3 > /dev/null 2>&1
pip install -r requirements.txt > /dev/null 2>&1
pip install psutil > /dev/null 2>&1  # For memory usage stats

# Run the module compatibility test
echo "Testing module compatibility..."
python test_modules.py || {
    echo "❌ Module compatibility test failed. Trying to fix known issues..."
    # Add numpy compatibility fix if needed
    python -c "
import sys
try:
    import numpy as np
    if not hasattr(np, 'bool8'):
        print('Adding numpy.bool8 compatibility fix')
        np.bool8 = np.bool_
    print('Numpy compatibility check: OK')
except Exception as e:
    print(f'Numpy compatibility error: {e}')
    sys.exit(1)
"
}

# Kill any existing processes
echo "Stopping any existing processes..."
pkill -f "python api/main.py" 2>/dev/null || true
pkill -f "streamlit run" 2>/dev/null || true
sleep 1

# Initialize the database
echo "Initializing database..."
python init_db.py
if [ $? -ne 0 ]; then
    echo "❌ Database initialization failed! Check the logs for details."
    exit 1
fi

# Start API server
echo "Starting API server on port 8002..."
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

# Verify API is responding
echo "Verifying API connectivity..."
curl -s http://localhost:8002/health > /dev/null
if [ $? -ne 0 ]; then
    echo "❌ API server is not responding! Check api_server.log for details."
    tail -n 20 api_server.log
    kill $API_PID
    exit 1
fi

# Start Streamlit dashboard
echo "Starting Streamlit dashboard on port 8003..."
STREAMLIT_DEPRECATION_WARNING=0 python -m streamlit run ui/dashboard.py --server.port=8003 --server.address=0.0.0.0 > dashboard.log 2>&1 &
STREAMLIT_PID=$!
echo "Streamlit dashboard started with PID: $STREAMLIT_PID"
sleep 3

# Check if Streamlit is running
if ! ps -p $STREAMLIT_PID > /dev/null; then
    echo "❌ Streamlit dashboard failed to start! Check dashboard.log for details."
    tail -n 20 dashboard.log
    kill $API_PID
    exit 1
fi

echo ""
echo "✅ Thomas AI System is now running!"
echo "   API server: http://localhost:8002"
echo "   API documentation: http://localhost:8002/docs"
echo "   Dashboard: http://localhost:8003"
echo ""
echo "To stop the system, run: bash stop_thomas.sh"
