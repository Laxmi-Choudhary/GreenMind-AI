from _pytest import assertion
import sqlite3
import json
import logging
import uuid

from typing import List, Optional, Any, Dict

from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

from app.config import settings

logger = logging.getLogger(__name__)


class DatabaseManager:
    def __init__(self):
        self.is_mongodb = False
        self.client = None
        self.db = None
        self.sqlite_conn = None

    # =====================================================
    # Helpers
    # =====================================================

    def _serialize_mongo_doc(self, doc: Optional[dict]) -> Optional[dict]:
        if not doc:
            return None

        doc = dict(doc)

        if "_id" in doc:
            doc["id"] = str(doc["_id"])
            del doc["_id"]

        return doc

    def _json(self, data: Dict[str, Any]) -> str:
        return json.dumps(data, default=str)

    def _parse(self, data: str) -> dict:
        return json.loads(data)

    # =====================================================
    # CONNECTION
    # =====================================================

    async def connect(self):
        if not settings.MONGODB_URI:
            logger.info("MongoDB not found. Using SQLite.")
            self.is_mongodb = False
            self._init_sqlite()
            return

        try:
            self.client = AsyncIOMotorClient(
                settings.MONGODB_URI,
                serverSelectionTimeoutMS=5000
            )

            await self.client.admin.command("ping")

            self.db = self.client[settings.DATABASE_NAME]
            self.is_mongodb = True

            await self._create_indexes()

            logger.info("MongoDB connected successfully.")

        except Exception as e:
            logger.warning(f"MongoDB failed, fallback to SQLite: {e}")
            self.is_mongodb = False
            self._init_sqlite()

    async def close(self):
        if self.client:
            self.client.close()

        if self.sqlite_conn:
            self.sqlite_conn.close()

    # =====================================================
    # INDEXES (MongoDB)
    # =====================================================

    async def _create_indexes(self):
        if not self.is_mongodb:
             return

        try:
            await self.db.users.create_index("email", unique=True)

            await self.db.footprints.create_index(
                [("user_id", 1)],
                name="footprints_user_id"
            )

            await self.db.reports.create_index(
                [("user_id", 1)],
                name="reports_user_id"
            )

            await self.db.challenges.create_index(
                [("user_id", 1)],
                name="challenges_user_id"
            )

            logger.info("MongoDB indexes created successfully.")

        except Exception as e:
            logger.error(f"Index error: {e}")
            raise e   # IMPORTANT → stop fallback to SQLite

    # =====================================================
    # SQLITE INIT
    # =====================================================

    def _init_sqlite(self):
        self.sqlite_conn = sqlite3.connect(
            settings.SQLITE_DB_PATH,
            check_same_thread=False
        )

        self.sqlite_conn.row_factory = sqlite3.Row
        cursor = self.sqlite_conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE,
            data TEXT
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS footprints(
            id TEXT PRIMARY KEY,
            user_id TEXT,
            date TEXT,
            data TEXT
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS reports(
            id TEXT PRIMARY KEY,
            user_id TEXT,
            data TEXT
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS challenges(
            id TEXT PRIMARY KEY,
            user_id TEXT,
            date TEXT,
            data TEXT
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS refresh_tokens(
            id TEXT PRIMARY KEY,
            user_id TEXT,
            jti TEXT UNIQUE,
            expires_at TEXT
        )
        """)

        self.sqlite_conn.commit()
        logger.info("SQLite initialized.")

    # =====================================================
    # USERS
    # =====================================================

    async def get_user_by_email(self, email: str) -> Optional[dict]:
        email = email.lower()

        if self.is_mongodb:
            user = await self.db.users.find_one({"email": email})
            return self._serialize_mongo_doc(user)

        cursor = self.sqlite_conn.cursor()
        cursor.execute("SELECT data FROM users WHERE email=?", (email,))
        row = cursor.fetchone()

        return self._parse(row["data"]) if row else None

    async def get_user_by_id(self, user_id: str) -> Optional[dict]:

        if self.is_mongodb:
            try:
                user = await self.db.users.find_one({"_id": ObjectId(user_id)})
            except Exception:
                user = await self.db.users.find_one({"id": user_id})

            return self._serialize_mongo_doc(user)

        cursor = self.sqlite_conn.cursor()
        cursor.execute("SELECT data FROM users WHERE id=?", (user_id,))
        row = cursor.fetchone()

        return self._parse(row["data"]) if row else None

    async def create_user(self, user_data: dict) -> dict:
        user_data["id"] = str(uuid.uuid4())
        user_data["email"] = user_data["email"].lower()

        if self.is_mongodb:
            result = await self.db.users.insert_one(user_data)
            user_data["id"] = str(result.inserted_id)
            return user_data

        cursor = self.sqlite_conn.cursor()
        cursor.execute(
            "INSERT INTO users(id,email,data) VALUES(?,?,?)",
            (user_data["id"], user_data["email"], self._json(user_data))
        )

        self.sqlite_conn.commit()
        return user_data

    async def update_user(self, user_id: str, updates: dict) -> Optional[dict]:
        user = await self.get_user_by_id(user_id)

        if not user:
            return None

        user.update(updates)

        if self.is_mongodb:
            try:
                await self.db.users.update_one(
                    {"_id": ObjectId(user_id)},
                    {"$set": updates}
                )
            except Exception:
                await self.db.users.update_one(
                    {"id": user_id},
                    {"$set": updates}
                )

            return user

        cursor = self.sqlite_conn.cursor()
        cursor.execute(
            "UPDATE users SET data=? WHERE id=?",
            (self._json(user), user_id)
        )

        self.sqlite_conn.commit()
        return user

    # =====================================================
    # FOOTPRINTS
    # =====================================================

    async def add_footprint(self, footprint: dict) -> dict:
        footprint["id"] = str(uuid.uuid4())

        if self.is_mongodb:
            result = await self.db.footprints.insert_one(footprint)
            footprint["id"] = str(result.inserted_id)
            return footprint

        cursor = self.sqlite_conn.cursor()
        cursor.execute("""
            INSERT INTO footprints(id,user_id,date,data)
            VALUES(?,?,?,?)
        """, (
            footprint["id"],
            footprint["user_id"],
            footprint["date"],
            self._json(footprint)
        ))

        self.sqlite_conn.commit()
        return footprint

    async def get_footprints_by_user(self, user_id: str) -> List[dict]:

        if self.is_mongodb:
            cursor = self.db.footprints.find({"user_id": user_id})
            return [self._serialize_mongo_doc(doc) async for doc in cursor]

        cursor = self.sqlite_conn.cursor()
        cursor.execute("""
            SELECT data FROM footprints
            WHERE user_id=?
            ORDER BY date DESC
        """, (user_id,))

        return [self._parse(row["data"]) for row in cursor.fetchall()]

    # =====================================================
    # REPORTS
    # =====================================================

    async def add_report(self, report: dict) -> dict:
        report["id"] = str(uuid.uuid4())

        if self.is_mongodb:
            result = await self.db.reports.insert_one(report)
            report["id"] = str(result.inserted_id)
            return report

        cursor = self.sqlite_conn.cursor()
        cursor.execute("""
            INSERT INTO reports(id,user_id,data)
            VALUES(?,?,?)
        """, (
            report["id"],
            report["user_id"],
            self._json(report)
        ))

        self.sqlite_conn.commit()
        return report

    async def get_reports_by_user(self, user_id: str) -> List[dict]:

        if self.is_mongodb:
            cursor = self.db.reports.find({"user_id": user_id})
            return [self._serialize_mongo_doc(doc) async for doc in cursor]

        cursor = self.sqlite_conn.cursor()
        cursor.execute("SELECT data FROM reports WHERE user_id=?", (user_id,))
        return [self._parse(row["data"]) for row in cursor.fetchall()]

    # =====================================================
    # CHALLENGES (FIXED - YOUR ERROR)
    # =====================================================

    async def add_challenge(self, challenge: dict) -> dict:
        challenge["id"] = str(uuid.uuid4())

        if self.is_mongodb:
            result = await self.db.challenges.insert_one(challenge)
            challenge["id"] = str(result.inserted_id)
            return challenge

        cursor = self.sqlite_conn.cursor()
        cursor.execute("""
            INSERT INTO challenges(id,user_id,date,data)
            VALUES(?,?,?,?)
        """, (
            challenge["id"],
            challenge["user_id"],
            challenge["date"],
            self._json(challenge)
        ))

        self.sqlite_conn.commit()
        return challenge

    async def get_challenges_by_user(self, user_id: str) -> List[dict]:

        if self.is_mongodb:
            cursor = self.db.challenges.find({"user_id": user_id})
            return [self._serialize_mongo_doc(doc) async for doc in cursor]

        cursor = self.sqlite_conn.cursor()
        cursor.execute("""
            SELECT data FROM challenges
            WHERE user_id=?
            ORDER BY date DESC
        """, (user_id,))

        return [self._parse(row["data"]) for row in cursor.fetchall()]

    # =====================================================
    # REFRESH TOKENS
    # =====================================================

    async def save_refresh_token(self, user_id: str, jti: str, expires_at: str):

        if self.is_mongodb:
            await self.db.refresh_tokens.insert_one({
                "user_id": user_id,
                "jti": jti,
                "expires_at": expires_at
            })
            return

        cursor = self.sqlite_conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO refresh_tokens
            (id,user_id,jti,expires_at)
            VALUES(?,?,?,?)
        """, (jti, user_id, jti, expires_at))

        self.sqlite_conn.commit()

    async def is_refresh_token_valid(self, user_id: str, jti: str) -> bool:

        if self.is_mongodb:
            token = await self.db.refresh_tokens.find_one({
                "user_id": user_id,
                "jti": jti
            })
            return token is not None

        cursor = self.sqlite_conn.cursor()
        cursor.execute("""
            SELECT jti FROM refresh_tokens
            WHERE user_id=? AND jti=?
        """, (user_id, jti))

        return cursor.fetchone() is not None


# =====================================================
# GLOBAL INSTANCE
# =====================================================

db_manager = DatabaseManager()