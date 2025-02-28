#!/bin/bash

# Set environment variables to fix compatibility issues
export PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python
export STREAMLIT_DEPRECATION_WARNING=0

# Display startup message
echo "========================================"
echo "  Thomas AI Management System Wrapper"
echo "========================================"
echo "Setting up environment with compatibility fixes..."

# Execute the main launch script
cd ~/thomas_app
bash launch_thomas.sh 