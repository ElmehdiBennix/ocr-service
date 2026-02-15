
'''Enterprise OCR Service - Main Application'''\

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from prometheus_client import make_asgi_app

from app.config import settings
from app.database import create_db_and_tables, close_db
from app.routers.v1 import auth, users, api_keys, ocr as ocr_v1, health, admin
from app.routers.v2 import ocr as ocr_v2
from app.middleware.rate_limit import RateLimitMiddleware
from app.middleware.logging_middleware import LoggingMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    '''Application lifespan manager.'''
    # Startup
    print("🚀 Starting Enterprise OCR Service...")
    if settings.DEBUG:
        await create_db_and_tables()
        print("✓ Database tables created (dev mode)")
    print("✓ Application started successfully")

    yield

    # Shutdown
    print("👋 Shutting down...")
    await close_db()
    print("✓ Database connections closed")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Enterprise-grade OCR API with authentication, rate limiting, and usage tracking",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom middleware
app.add_middleware(LoggingMiddleware)
app.add_middleware(RateLimitMiddleware)

# Mount Prometheus metrics
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

# Include API v1 routers
app.include_router(auth.router, prefix=settings.API_V1_PREFIX, tags=["Authentication"])
app.include_router(users.router, prefix=settings.API_V1_PREFIX, tags=["Users"])
app.include_router(api_keys.router, prefix=settings.API_V1_PREFIX, tags=["API Keys"])
app.include_router(ocr_v1.router, prefix=settings.API_V1_PREFIX, tags=["OCR v1"])
app.include_router(health.router, prefix="", tags=["Health"])
app.include_router(admin.router, prefix=settings.API_V1_PREFIX, tags=["Admin"])

# Include API v2 routers
app.include_router(ocr_v2.router, prefix=settings.API_V2_PREFIX, tags=["OCR v2"])

# Serve admin dashboard (mount BEFORE landing page to avoid conflicts)
if os.path.exists("frontend/admin"):
    app.mount("/admin", StaticFiles(directory="frontend/admin", html=True), name="admin")

# Serve frontend static files
if os.path.exists("frontend/landing"):
    app.mount("/", StaticFiles(directory="frontend/landing", html=True), name="landing")


@app.get("/api", include_in_schema=False)
async def api_root():
    '''API root endpoint.'''
    return {
        "message": "Enterprise OCR API",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG)
