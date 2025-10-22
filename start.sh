#!/bin/bash

# Start script for Trend Collector Agent

echo "=========================================="
echo "  Agentic Trend Collector"
echo "=========================================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Creating..."
    python3 -m venv venv
    echo "Installing dependencies..."
    ./venv/bin/pip install -r requirements.txt
    echo ""
fi

echo "Starting Trend Collector Agent..."
echo "Press Ctrl+C to stop"
echo ""

# Start the application
./venv/bin/python main.py
