from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import logging
import time

from app.config import settings
from app.database import db_manager
from app.cache import redis_manager

from app.routes import (
    auth,
    calculator,
    coach,
    chat,
    simulator,
    score,
    challenges,
    reports
)

from app.features.prediction_engine.routes import router as prediction_router
from app.features.receipt_analyzer.routes import router as receipt_router
from app.features.bill_analyzer.routes import router as bill_router
from app.features.recommendation_engine.routes import router as recommendation_router
from app.features.sdg_dashboard.routes import router as sdg_router
from app.features.leaderboard.routes import router as leaderboard_router

# ---------------------------------------------------
# Logging
# ---------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------
# FastAPI App
# ---------------------------------------------------

app = FastAPI(
    title=settings.APP_NAME,
    description="GreenMind AI - Sustainability Intelligence Platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# ---------------------------------------------------
# Uptime Tracking
# ---------------------------------------------------

START_TIME = time.time()

# ---------------------------------------------------
# CORS Configuration
# ---------------------------------------------------

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://greenmind-ai.vercel.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=[
        "GET",
        "POST",
        "PUT",
        "DELETE",
        "PATCH",
        "OPTIONS"
    ],
    allow_headers=[
        "Authorization",
        "Content-Type",
        "Accept",
        "Origin",
        "X-Requested-With"
    ],
    expose_headers=[
        "Content-Length",
        "Content-Type"
    ],
    max_age=3600
)

# ---------------------------------------------------
# Security Headers
# ---------------------------------------------------

@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)

    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = (
        "camera=(), microphone=(), geolocation=()"
    )

    return response

# ---------------------------------------------------
# Startup Event
# ---------------------------------------------------

@app.on_event("startup")
async def startup_db_client():
    logger.info("Starting GreenMind AI...")

    await db_manager.connect()

    try:
        await redis_manager.connect()
        logger.info("Redis connected successfully")
    except Exception as e:
        logger.warning(f"Redis connection failed: {e}")

# ---------------------------------------------------
# Shutdown Event
# ---------------------------------------------------

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down GreenMind AI...")

    try:
        await db_manager.close()
    except Exception:
        pass

    try:
        await redis_manager.close()
    except Exception:
        pass

# ---------------------------------------------------
# Root Endpoint
# ---------------------------------------------------

@app.get("/", tags=["System"])
async def root():
    return {
        "name": settings.APP_NAME,
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health"
    }

# ---------------------------------------------------
# Health Check
# ---------------------------------------------------

@app.get("/health", tags=["System"])
async def health_check():

    try:
        redis_ok = await redis_manager.ping()
    except Exception:
        redis_ok = False

    return {
        "status": "healthy",
        "application": settings.APP_NAME,
        "database_type": (
            "MongoDB"
            if db_manager.is_mongodb
            else "SQLite Fallback"
        ),
        "redis": (
            "available"
            if redis_ok
            else "unavailable"
        )
    }

# ---------------------------------------------------
# Metrics Endpoint
# ---------------------------------------------------

@app.get("/metrics", tags=["Monitoring"])
async def metrics():

    uptime = int(time.time() - START_TIME)

    return {
        "uptime_seconds": uptime,
        "service": settings.APP_NAME,
        "version": "1.0.0"
    }

# ---------------------------------------------------
# Register Routers
# ---------------------------------------------------

app.include_router(auth.router)
app.include_router(calculator.router)
app.include_router(coach.router)
app.include_router(chat.router)
app.include_router(simulator.router)
app.include_router(score.router)
app.include_router(challenges.router)
app.include_router(reports.router)

app.include_router(prediction_router)
app.include_router(receipt_router)
app.include_router(bill_router)
app.include_router(recommendation_router)
app.include_router(sdg_router)
app.include_router(leaderboard_router)
