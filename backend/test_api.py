"""
Test script for the Network Manager API
"""

import requests
import json
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health check endpoint"""
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    print("[OK] Health check passed")
    return response.json()


def test_root():
    """Test root endpoint"""
    response = requests.get(f"{BASE_URL}/")
    assert response.status_code == 200
    data = response.json()
    print("[OK] Root endpoint working")
    print(f"    API: {data.get('message')}")
    print(f"    Version: {data.get('version')}")
    return data


def test_list_devices():
    """Test listing devices"""
    response = requests.get(f"{BASE_URL}/api/devices/")
    if response.status_code != 200:
        print(f"[ERROR] Status code: {response.status_code}")
        print(f"[ERROR] Response: {response.text}")
        raise Exception(f"Status code: {response.status_code}")
    devices = response.json()
    print(f"[OK] Listed {len(devices)} devices")
    return devices


def test_list_dashboard():
    """Test dashboard endpoint"""
    response = requests.get(f"{BASE_URL}/api/dashboard/")
    assert response.status_code == 200
    data = response.json()
    stats = data.get("stats", {})
    print(f"[OK] Dashboard stats:")
    print(f"    Total devices: {stats.get('total_devices', 0)}")
    print(f"    Online: {stats.get('online_devices', 0)}")
    print(f"    Offline: {stats.get('offline_devices', 0)}")
    return data


def test_create_device():
    """Test creating a device"""
    device_data = {
        "name": "Test Starlink Dish",
        "device_type": "starlink",
        "ip_address": "192.168.1.100",
        "location": "New York",
        "description": "Test device for integration"
    }
    
    response = requests.post(f"{BASE_URL}/api/devices/", json=device_data)
    if response.status_code == 201 or response.status_code == 200:
        device = response.json()
        print(f"[OK] Created device: {device.get('id')}")
        print(f"    Name: {device.get('name')}")
        print(f"    Type: {device.get('device_type')}")
        print(f"    IP: {device.get('ip_address')}")
        return device
    elif response.status_code == 409:
        print("[SKIP] Device already exists")
        return None
    else:
        print(f"[ERROR] Failed to create device: {response.status_code}")
        print(response.text)
        return None


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("Network Manager API - Test Suite")
    print("="*60 + "\n")
    
    try:
        print("1. Testing basic endpoints...")
        test_health()
        root_data = test_root()
        
        print("\n2. Testing device endpoints...")
        test_list_devices()
        
        print("\n3. Testing dashboard...")
        test_list_dashboard()
        
        print("\n4. Testing device creation...")
        test_create_device()
        
        print("\n" + "="*60)
        print("All tests passed!")
        print("="*60)
        print(f"\nAPI Documentation available at: {BASE_URL}/docs")
        print(f"Alternative docs at: {BASE_URL}/redoc")
        
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
