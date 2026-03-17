#!/usr/bin/env python
"""Check and test Yemen MikroTik credentials"""

import asyncio
import json
from app.core.database import SessionLocal
from app.models.device import Device
from app.modules.mikrotik import MikroTikDriver

async def main():
    db = SessionLocal()
    devices = db.query(Device).filter(Device.device_type == 'mikrotik').all()
    
    if not devices:
        print("❌ No MikroTik devices found")
        return
    
    device = devices[0]
    print(f"📱 Device: {device.name}")
    print(f"   IP: {device.ip_address}")
    print(f"   Location: {device.location}")
    print(f"   Device ID: {device.id}")
    
    if not device.credentials:
        print(f"❌ NO CREDENTIALS STORED - this is the problem!")
        db.close()
        return
    
    print(f"\n🔑 Stored Credentials ({len(device.credentials)} entries):")
    for cred in device.credentials:
        auth_data = cred.auth_data or {}
        print(f"   Username: {auth_data.get('username', 'NOT SET')}")
        print(f"   Password: {'*' * len(auth_data.get('password', '')) if auth_data.get('password') else 'NOT SET'}")
        print(f"   Port: {auth_data.get('port', 80)}")
        print(f"   Use SSL: {auth_data.get('use_ssl', False)}")
    
    print(f"\n🔄 Testing connection...")
    try:
        # Get first credential if available
        if device.credentials and len(device.credentials) > 0:
            cred = device.credentials[0]
            auth_data = cred.auth_data or {}
        else:
            auth_data = {}
            
        driver = MikroTikDriver(device.id, device.ip_address, auth_data)
        connected = await driver.connect()
        
        if connected:
            print("✅ Connection successful!")
            
            status = await driver.get_status()
            print(f"\n📊 Device Status:")
            print(f"   Name: {status.name}")
            print(f"   Status: {status.status}")
            print(f"   CPU: {status.cpu_usage}%")
            print(f"   Memory: {status.memory_usage}%")
            print(f"   Uptime: {status.uptime}s")
        else:
            print("❌ Connection failed (returned False)")
        
        await driver.disconnect()
        
    except Exception as e:
        print(f"❌ Connection failed!")
        print(f"   Error: {e}")
        print(f"   Type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
    
    db.close()

if __name__ == "__main__":
    asyncio.run(main())
