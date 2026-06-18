from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from app.config import settings
from app.database import db_manager
from app.routes import auth, calculator, coach, chat, simulator, score, challenges, reports

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

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "database_type": "MongoDB" if db_manager.is_mongodb else "SQLite Fallback"
    }

# Register application routers
app.include_router(auth.router)
app.include_router(calculator.router)
app.include_router(coach.router)
app.include_router(chat.router)
app.include_router(simulator.router)
app.include_router(score.router)
app.include_router(challenges.router)
app.include_router(reports.router)
