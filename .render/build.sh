#!/bin/bash
set -e

echo "Installing Python dependencies..."
cd backend
pip install --upgrade pip
pip install -r requirements.txt
echo "Build complete!"
