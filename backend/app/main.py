from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from app.config import settings
from app.database import db_manager
from app.cache import redis_manager
from app.routes import auth, calculator, coach, chat, simulator, score, challenges, reports
from app.features.prediction_engine.routes import router as prediction_router
from app.features.receipt_analyzer.routes import router as receipt_router
from app.features.bill_analyzer.routes import router as bill_router
from app.features.recommendation_engine.routes import router as recommendation_router
from app.features.sdg_dashboard.routes import router as sdg_router
from app.features.leaderboard.routes import router as leaderboard_router
from fastapi import Response

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title=settings.APP_NAME, version="1.0.0")

# Setup CORS middleware for local dev cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_db_client():
    logger.info("Starting up FastAPI application...")
    await db_manager.connect()
    # Attempt connecting to Redis if configured
    await redis_manager.connect()

@app.get("/health")
async def health_check():
    redis_ok = await redis_manager.ping() if redis_manager else False
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "database_type": "MongoDB" if db_manager.is_mongodb else "SQLite Fallback",
        "redis": "available" if redis_ok else "unavailable"
    }

@app.get("/metrics")
async def metrics():
    # Basic metrics stub
    return {"uptime_seconds": 0, "requests": 0}

# Register application routers
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