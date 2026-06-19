import sqlite3
import json
import logging
from typing import Dict, List, Optional
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        self.is_mongodb = False
        self.client: Optional[AsyncIOMotorClient] = None
        self.db = None
        self.sqlite_conn = None

    async def connect(self):
        try:
            logger.info(f"Attempting to connect to MongoDB at {settings.MONGODB_URI}...")
            self.client = AsyncIOMotorClient(settings.MONGODB_URI, serverSelectionTimeoutMS=2000)
            # Force validation by running ping
            await self.client.admin.command('ping')
            self.db = self.client[settings.DATABASE_NAME]
            self.is_mongodb = True
            logger.info("Connected to MongoDB successfully!")
        except Exception as e:
            logger.warning(f"Failed to connect to MongoDB ({e}). Falling back to local SQLite database: {settings.SQLITE_DB_PATH}")
            self.is_mongodb = False
            self._init_sqlite()

    def _init_sqlite(self):
        self.sqlite_conn = sqlite3.connect(settings.SQLITE_DB_PATH, check_same_thread=False)
        self.sqlite_conn.row_factory = sqlite3.Row
        cursor = self.sqlite_conn.cursor()
        
        # We store documents as JSON text in a flat table to match MongoDB style structure.
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE,
                data TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS footprints (
                id TEXT PRIMARY KEY,
                user_id TEXT,
                date TEXT,
                data TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS challenges (
                id TEXT PRIMARY KEY,
                user_id TEXT,
                data TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reports (
                id TEXT PRIMARY KEY,
                user_id TEXT,
                data TEXT
            )
        """)
        self.sqlite_conn.commit()
        logger.info("SQLite database initialized successfully.")

    # --- User Helpers ---
    async def get_user_by_email(self, email: str) -> Optional[dict]:
        if self.is_mongodb:
            user = await self.db.users.find_one({"email": email})
            if user and "_id" in user:
                user["id"] = str(user["_id"])
            return user
        else:
            cursor = self.sqlite_conn.cursor()
            cursor.execute("SELECT data FROM users WHERE email = ?", (email.lower(),))
            row = cursor.fetchone()
            if row:
                return json.loads(row[0])
            return None

    async def get_user_by_id(self, user_id: str) -> Optional[dict]:
        if self.is_mongodb:
            from bson.objectid import ObjectId
            try:
                user = await self.db.users.find_one({"_id": ObjectId(user_id)})
            except Exception:
                user = await self.db.users.find_one({"id": user_id})
            if user and "_id" in user:
                user["id"] = str(user["_id"])
            return user
        else:
            cursor = self.sqlite_conn.cursor()
            cursor.execute("SELECT data FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            if row:
                return json.loads(row[0])
            return None

    async def create_user(self, user_data: dict) -> dict:
        user_id = user_data.get("id") or user_data.get("_id")
        if not user_id:
            import uuid
            user_id = str(uuid.uuid4())
            user_data["id"] = user_id
        
        email = user_data["email"].lower()
        user_data["email"] = email

        if self.is_mongodb:
            res = await self.db.users.insert_one(user_data)
            user_data["id"] = str(res.inserted_id)
            return user_data
        else:
            cursor = self.sqlite_conn.cursor()
            cursor.execute(
                "INSERT INTO users (id, email, data) VALUES (?, ?, ?)",
                (user_id, email, json.dumps(user_data))
            )
            self.sqlite_conn.commit()
            return user_data

    async def update_user(self, user_id: str, updates: dict) -> Optional[dict]:
        user = await self.get_user_by_id(user_id)
        if not user:
            return None
        
        # Merge updates
        for k, v in updates.items():
            user[k] = v

        if self.is_mongodb:
            from bson.objectid import ObjectId
            try:
                await self.db.users.update_one({"_id": ObjectId(user_id)}, {"$set": updates})
            except Exception:
                await self.db.users.update_one({"id": user_id}, {"$set": updates})
            return user
        else:
            cursor = self.sqlite_conn.cursor()
            cursor.execute(
                "UPDATE users SET data = ? WHERE id = ?",
                (json.dumps(user), user_id)
            )
            self.sqlite_conn.commit()
            return user

    # --- Footprint Helpers ---
    async def add_footprint(self, footprint_data: dict) -> dict:
        import uuid
        fp_id = str(uuid.uuid4())
        footprint_data["id"] = fp_id

        if self.is_mongodb:
            await self.db.footprints.insert_one(footprint_data)
            return footprint_data
        else:
            cursor = self.sqlite_conn.cursor()
            cursor.execute(
                "INSERT INTO footprints (id, user_id, date, data) VALUES (?, ?, ?, ?)",
                (fp_id, footprint_data["user_id"], footprint_data["date"], json.dumps(footprint_data))
            )
            self.sqlite_conn.commit()
            return footprint_data

    async def get_footprints_by_user(self, user_id: str) -> List[dict]:
        if self.is_mongodb:
            cursor = self.db.footprints.find({"user_id": user_id})
            fps = []
            async for doc in cursor:
                doc["id"] = str(doc.get("_id", doc.get("id")))
                fps.append(doc)
            # Sort by date
            fps.sort(key=lambda x: x.get("date", ""), reverse=True)
            return fps
        else:
            cursor = self.sqlite_conn.cursor()
            cursor.execute("SELECT data FROM footprints WHERE user_id = ? ORDER BY date DESC", (user_id,))
            rows = cursor.fetchall()
            return [json.loads(row[0]) for row in rows]

    # --- Challenges & Badges Helpers ---
    async def get_challenges_by_user(self, user_id: str) -> List[dict]:
        if self.is_mongodb:
            doc = await self.db.challenges.find_one({"user_id": user_id})
            return doc.get("challenges", []) if doc else []
        else:
            cursor = self.sqlite_conn.cursor()
            cursor.execute("SELECT data FROM challenges WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            if row:
                return json.loads(row[0]).get("challenges", [])
            return []

    async def save_challenges_by_user(self, user_id: str, challenges: List[dict]):
        if self.is_mongodb:
            await self.db.challenges.update_one(
                {"user_id": user_id},
                {"$set": {"challenges": challenges}},
                upsert=True
            )
        else:
            cursor = self.sqlite_conn.cursor()
            cursor.execute("SELECT id FROM challenges WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            doc_data = {"user_id": user_id, "challenges": challenges}
            if row:
                cursor.execute(
                    "UPDATE challenges SET data = ? WHERE user_id = ?",
                    (json.dumps(doc_data), user_id)
                )
            else:
                import uuid
                ch_id = str(uuid.uuid4())
                cursor.execute(
                    "INSERT INTO challenges (id, user_id, data) VALUES (?, ?, ?)",
                    (ch_id, user_id, json.dumps(doc_data))
                )
            self.sqlite_conn.commit()

    # --- Weekly Reports Helpers ---
    async def add_report(self, report_data: dict) -> dict:
        import uuid
        rep_id = str(uuid.uuid4())
        report_data["id"] = rep_id

        if self.is_mongodb:
            await self.db.reports.insert_one(report_data)
            return report_data
        else:
            cursor = self.sqlite_conn.cursor()
            cursor.execute(
                "INSERT INTO reports (id, user_id, data) VALUES (?, ?, ?)",
                (rep_id, report_data["user_id"], json.dumps(report_data))
            )
            self.sqlite_conn.commit()
            return report_data

    async def get_reports_by_user(self, user_id: str) -> List[dict]:
        if self.is_mongodb:
            cursor = self.db.reports.find({"user_id": user_id})
            reps = []
            async for doc in cursor:
                doc["id"] = str(doc.get("_id", doc.get("id")))
                reps.append(doc)
            reps.sort(key=lambda x: x.get("created_at", ""), reverse=True)
            return reps
        else:
            cursor = self.sqlite_conn.cursor()
            cursor.execute("SELECT data FROM reports WHERE user_id = ?", (user_id,))
            rows = cursor.fetchall()
            reps = [json.loads(row[0]) for row in rows]
            reps.sort(key=lambda x: x.get("created_at", ""), reverse=True)
            return reps

    # --- Refresh Tokens Helpers ---
    async def save_refresh_token(self, user_id: str, jti: str, expires_at: str):
        if self.is_mongodb:
            await self.db.tokens.insert_one({"user_id": user_id, "jti": jti, "expires_at": expires_at})
        else:
            cursor = self.sqlite_conn.cursor()
            cursor.execute("CREATE TABLE IF NOT EXISTS refresh_tokens (id TEXT PRIMARY KEY, user_id TEXT, jti TEXT, expires_at TEXT)")
            token_id = jti
            cursor.execute(
                "INSERT OR REPLACE INTO refresh_tokens (id, user_id, jti, expires_at) VALUES (?, ?, ?, ?)",
                (token_id, user_id, jti, expires_at)
            )
            self.sqlite_conn.commit()

    async def revoke_refresh_token(self, user_id: str, jti: str):
        if self.is_mongodb:
            await self.db.tokens.delete_one({"user_id": user_id, "jti": jti})
        else:
            cursor = self.sqlite_conn.cursor()
            cursor.execute("DELETE FROM refresh_tokens WHERE user_id = ? AND jti = ?", (user_id, jti))
            self.sqlite_conn.commit()

    async def is_refresh_token_valid(self, user_id: str, jti: str) -> bool:
        if self.is_mongodb:
            doc = await self.db.tokens.find_one({"user_id": user_id, "jti": jti})
            return doc is not None
        else:
            cursor = self.sqlite_conn.cursor()
            cursor.execute("SELECT jti FROM refresh_tokens WHERE user_id = ? AND jti = ?", (user_id, jti))
            row = cursor.fetchone()
            return row is not None

db_manager = DatabaseManager()
