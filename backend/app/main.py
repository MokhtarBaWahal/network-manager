"""
Main FastAPI Application
Unified Network Management Platform - Backend
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import Base, engine, SessionLocal
from app.core.config import settings
from app.api import devices, dashboard

logger = logging.getLogger(__name__)

# Create database tables
Base.metadata.create_all(bind=engine)

# Track last known uptime per device to detect reboots
_last_uptime: dict = {}


def _maybe_create_alert(db, device, info):
    """Create alert if conditions are met, skipping duplicates."""
    from app.models.device import Alert

    def _has_open_alert(keyword: str) -> bool:
        return db.query(Alert).filter(
            Alert.device_id == device.id,
            Alert.resolved == False,
            Alert.message.contains(keyword),
        ).first() is not None

    if info.status == "error":
        if not _has_open_alert("unreachable"):
            db.add(Alert(device_id=device.id, severity="error",
                         message=f"Router unreachable: {device.name}"))

    elif info.cpu_usage is not None and info.cpu_usage > 80:
        if not _has_open_alert("CPU usage high"):
            db.add(Alert(device_id=device.id, severity="warning",
                         message=f"CPU usage high: {info.cpu_usage:.1f}% on {device.name}"))

    if info.uptime is not None:
        prev = _last_uptime.get(device.id)
        if prev is not None and info.uptime < prev:
            db.add(Alert(device_id=device.id, severity="info",
                         message=f"Router rebooted: {device.name}"))
        _last_uptime[device.id] = info.uptime


async def collect_all_metrics():
    """Background task: poll all MikroTik devices every 30 seconds."""
    from app.models.device import Device, DeviceType, DeviceStatus, DeviceMetrics

    await asyncio.sleep(10)  # warm-up delay
    while True:
        try:
            db = SessionLocal()
            try:
                mikrotik_devices = (
                    db.query(Device)
                    .filter(Device.device_type == DeviceType.MIKROTIK)
                    .all()
                )
                logger.info(f"Collector: polling {len(mikrotik_devices)} MikroTik device(s)")
                for device in mikrotik_devices:
                    try:
                        driver = devices.get_device_driver(device)
                        info = await driver.get_status()

                        device.status = DeviceStatus(info.status)
                        device.cpu_usage = info.cpu_usage
                        device.memory_usage = info.memory_usage
                        device.uptime = info.uptime
                        device.last_seen = info.last_updated

                        db.add(DeviceMetrics(
                            device_id=device.id,
                            cpu_usage=info.cpu_usage,
                            memory_usage=info.memory_usage,
                            uptime=info.uptime,
                            timestamp=info.last_updated or datetime.utcnow(),
                        ))

                        _maybe_create_alert(db, device, info)

                    except Exception as e:
                        logger.error(f"Collector error for device {device.id}: {e}")

                db.commit()
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Collector loop error: {e}")

        await asyncio.sleep(30)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle events"""
    print("Starting Unified Network Manager...")
    task = asyncio.create_task(collect_all_metrics())
    yield
    task.cancel()
    print("Shutting down Unified Network Manager...")


# Initialize FastAPI app
app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION,
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(devices.router)
app.include_router(dashboard.router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Unified Network Management Platform",
        "version": settings.API_VERSION,
        "docs": "/docs",
        "endpoints": {
            "devices": "/api/devices",
            "dashboard": "/api/dashboard",
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "network-manager-backend"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
