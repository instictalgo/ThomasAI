#!/bin/bash

echo "Stopping Thomas AI System..."
pkill -f 'python api/main.py'
pkill -f 'streamlit run'
echo "All processes stopped."
