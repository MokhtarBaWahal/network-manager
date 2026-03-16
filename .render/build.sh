#!/bin/bash
set -e

echo "Installing system dependencies..."
apt-get update
apt-get install -y wireguard wireguard-tools

echo "Installing Python dependencies..."
cd backend
pip install --upgrade pip
pip install -r requirements.txt
echo "Build complete!"
