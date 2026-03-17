#!/usr/bin/env python3
"""Test script to debug Yemen MikroTik connection"""

import asyncio
import sys
import json
from app.core.database import SessionLocal
from app.models.device import Device
from app.modules.mikrotik import MikroTikDriver

async def main():
    db = SessionLocal()
    
    # Find Yemen device - try multiple ways
    devices = db.query(Device).all()
    yemen_device = None
    
    for device in devices:
        # Try multiple search patterns
        if "yemen" in device.name.lower() or "209.198" in str(device.ip_address):
            yemen_device = device
            break
    
    # If still not found, just take the last device (might be Yemen)
    if not yemen_device and len(devices) > 1:
        yemen_device = devices[-1]
    
    if not yemen_device:
        print("❌ No Yemen device found in database")
        print("\nDevices in database:")
        for device in devices:
            print(f"  - {device.name} ({device.device_type}) @ {device.ip_address}")
        db.close()
        return
    
    print(f"✅ Found Yemen device: {yemen_device.name}")
    print(f"   IP: {yemen_device.ip_address}")
    print(f"   Type: {yemen_device.device_type}")
    
    if not yemen_device.credentials:
        print("❌ No credentials stored for this device")
        db.close()
        return
    
    print(f"\n📋 Credentials stored:")
    auth_data = yemen_device.credentials.auth_data or {}
    print(f"   Username: {auth_data.get('username', 'NOT SET')}")
    print(f"   Password: {'*' * len(auth_data.get('password', '')) if auth_data.get('password') else 'NOT SET'}")
    print(f"   Port: {auth_data.get('port', 80)}")
    print(f"   Use SSL: {auth_data.get('use_ssl', False)}")
    
    # Try to connect
    print(f"\n🔄 Attempting to connect...")
    try:
        driver = MikroTikDriver(
            yemen_device.id,
            yemen_device.ip_address,
            auth_data
        )
        
        await driver.connect()
        print("✅ Connection successful!")
        
        status = await driver.get_status()
        print(f"\n📊 Device Status:")
        print(f"   Name: {status.name}")
        print(f"   Status: {status.status}")
        print(f"   CPU: {status.cpu_usage}%")
        print(f"   Memory: {status.memory_usage}%")
        print(f"   Uptime: {status.uptime}s")
        
        await driver.disconnect()
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print(f"   Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
    
    db.close()

if __name__ == "__main__":
    asyncio.run(main())
