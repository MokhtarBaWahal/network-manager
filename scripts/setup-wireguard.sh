#!/bin/bash
# WireGuard Installation Script for Render
# Run this on the Render backend server

set -e

echo "Installing WireGuard..."
apt-get update
apt-get install -y wireguard wireguard-tools

# Generate keys
umask 077
mkdir -p /etc/wireguard

# Server keys
wg genkey | tee /etc/wireguard/server_private.key | wg pubkey > /etc/wireguard/server_public.key

# Client keys (for Yemen)
wg genkey | tee /etc/wireguard/client_private.key | wg pubkey > /etc/wireguard/client_public.key

echo "Keys generated. Add these to your environment:"
echo ""
echo "SERVER_PRIVATE_KEY=$(cat /etc/wireguard/server_private.key)"
echo "SERVER_PUBLIC_KEY=$(cat /etc/wireguard/server_public.key)"
echo "CLIENT_PRIVATE_KEY=$(cat /etc/wireguard/client_private.key)"
echo "CLIENT_PUBLIC_KEY=$(cat /etc/wireguard/client_public.key)"
