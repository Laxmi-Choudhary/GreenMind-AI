import sqlite3
import json
import logging
import uuid
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

    # ======================================================
    # Connection Management
    # ======================================================

    async def connect(self):
        """Connect to MongoDB or fallback to SQLite."""
        if not settings.MONGODB_URI:
            logger.info(
                "No MongoDB URI configured. Using SQLite fallback."
            )
            self.is_mongodb = False
            self._init_sqlite()
            return

        try:
            logger.info("Connecting to MongoDB...")

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
            logger.warning(
                f"MongoDB connection failed: {e}"
            )
            logger.info("Falling back to SQLite.")

            self.is_mongodb = False
            self._init_sqlite()

    async def close(self):
        """Close database connections."""

        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed.")

        if self.sqlite_conn:
            self.sqlite_conn.close()
            logger.info("SQLite connection closed.")

    async def _create_indexes(self):
        """Create MongoDB indexes."""

        if not self.is_mongodb:
            return

        await self.db.users.create_index(
            "email",
            unique=True
        )

        await self.db.footprints.create_index(
            "user_id"
        )

        await self.db.reports.create_index(
            "user_id"
        )

        await self.db.tokens.create_index(
            "jti",
            unique=True
        )

        logger.info("MongoDB indexes created.")

    # ======================================================
    # SQLite Initialization
    # ======================================================

    def _init_sqlite(self):
        """Initialize SQLite database."""

        self.sqlite_conn = sqlite3.connect(
            settings.SQLITE_DB_PATH,
            check_same_thread=False
        )

        self.sqlite_conn.row_factory = sqlite3.Row

        cursor = self.sqlite_conn.cursor()

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
                user_id TEXT UNIQUE,
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

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS refresh_tokens (
                id TEXT PRIMARY KEY,
                user_id TEXT,
                jti TEXT UNIQUE,
                expires_at TEXT
            )
        """)

        self.sqlite_conn.commit()

        logger.info("SQLite initialized successfully.")

    # ======================================================
    # User Operations
    # ======================================================

    async def get_user_by_email(
        self,
        email: str
    ) -> Optional[dict]:

        email = email.lower()

        if self.is_mongodb:
            user = await self.db.users.find_one(
                {"email": email}
            )

            if user:
                user["id"] = str(user["_id"])

            return user

        cursor = self.sqlite_conn.cursor()

        cursor.execute(
            "SELECT data FROM users WHERE email=?",
            (email,)
        )

        row = cursor.fetchone()

        return json.loads(row[0]) if row else None

    async def get_user_by_id(
        self,
        user_id: str
    ) -> Optional[dict]:

        if self.is_mongodb:
            from bson import ObjectId

            try:
                user = await self.db.users.find_one(
                    {"_id": ObjectId(user_id)}
                )
            except Exception:
                user = await self.db.users.find_one(
                    {"id": user_id}
                )

            if user:
                user["id"] = str(user["_id"])

            return user

        cursor = self.sqlite_conn.cursor()

        cursor.execute(
            "SELECT data FROM users WHERE id=?",
            (user_id,)
        )

        row = cursor.fetchone()

        return json.loads(row[0]) if row else None

    async def create_user(
        self,
        user_data: dict
    ) -> dict:

        user_id = str(uuid.uuid4())

        user_data["id"] = user_id
        user_data["email"] = (
            user_data["email"].lower()
        )

        if self.is_mongodb:
            result = await self.db.users.insert_one(
                user_data
            )

            user_data["id"] = str(
                result.inserted_id
            )

            return user_data

        cursor = self.sqlite_conn.cursor()

        cursor.execute(
            """
            INSERT INTO users (id,email,data)
            VALUES (?,?,?)
            """,
            (
                user_id,
                user_data["email"],
                json.dumps(user_data)
            )
        )

        self.sqlite_conn.commit()

        return user_data

    async def update_user(
        self,
        user_id: str,
        updates: dict
    ) -> Optional[dict]:

        user = await self.get_user_by_id(
            user_id
        )

        if not user:
            return None

        user.update(updates)

        if self.is_mongodb:
            from bson import ObjectId

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
            """
            UPDATE users
            SET data=?
            WHERE id=?
            """,
            (
                json.dumps(user),
                user_id
            )
        )

        self.sqlite_conn.commit()

        return user

    # ======================================================
    # Footprints
    # ======================================================

    async def add_footprint(
        self,
        footprint_data: dict
    ) -> dict:

        footprint_data["id"] = str(uuid.uuid4())

        if self.is_mongodb:
            await self.db.footprints.insert_one(
                footprint_data
            )

            return footprint_data

        cursor = self.sqlite_conn.cursor()

        cursor.execute(
            """
            INSERT INTO footprints
            (id,user_id,date,data)
            VALUES (?,?,?,?)
            """,
            (
                footprint_data["id"],
                footprint_data["user_id"],
                footprint_data["date"],
                json.dumps(footprint_data)
            )
        )

        self.sqlite_conn.commit()

        return footprint_data

    async def get_footprints_by_user(
        self,
        user_id: str
    ) -> List[dict]:

        if self.is_mongodb:

            cursor = self.db.footprints.find(
                {"user_id": user_id}
            )

            data = []

            async for doc in cursor:
                doc["id"] = str(
                    doc.get("_id")
                )
                data.append(doc)

            return sorted(
                data,
                key=lambda x: x.get("date", ""),
                reverse=True
            )

        cursor = self.sqlite_conn.cursor()

        cursor.execute(
            """
            SELECT data
            FROM footprints
            WHERE user_id=?
            ORDER BY date DESC
            """,
            (user_id,)
        )

        return [
            json.loads(row[0])
            for row in cursor.fetchall()
        ]

    # ======================================================
    # Reports
    # ======================================================

    async def add_report(
        self,
        report_data: dict
    ) -> dict:

        report_data["id"] = str(uuid.uuid4())

        if self.is_mongodb:
            await self.db.reports.insert_one(
                report_data
            )

            return report_data

        cursor = self.sqlite_conn.cursor()

        cursor.execute(
            """
            INSERT INTO reports
            (id,user_id,data)
            VALUES (?,?,?)
            """,
            (
                report_data["id"],
                report_data["user_id"],
                json.dumps(report_data)
            )
        )

        self.sqlite_conn.commit()

        return report_data

    async def get_reports_by_user(
        self,
        user_id: str
    ) -> List[dict]:

        if self.is_mongodb:

            cursor = self.db.reports.find(
                {"user_id": user_id}
            )

            reports = []

            async for doc in cursor:
                doc["id"] = str(
                    doc.get("_id")
                )
                reports.append(doc)

            return reports

        cursor = self.sqlite_conn.cursor()

        cursor.execute(
            """
            SELECT data
            FROM reports
            WHERE user_id=?
            """,
            (user_id,)
        )

        reports = [
            json.loads(row[0])
            for row in cursor.fetchall()
        ]

        return sorted(
            reports,
            key=lambda x: x.get(
                "created_at", ""
            ),
            reverse=True
        )

    # ======================================================
    # Refresh Tokens
    # ======================================================

    async def save_refresh_token(
        self,
        user_id: str,
        jti: str,
        expires_at: str
    ):

        if self.is_mongodb:
            await self.db.tokens.insert_one({
                "user_id": user_id,
                "jti": jti,
                "expires_at": expires_at
            })

            return

        cursor = self.sqlite_conn.cursor()

        cursor.execute(
            """
            INSERT OR REPLACE INTO refresh_tokens
            (id,user_id,jti,expires_at)
            VALUES (?,?,?,?)
            """,
            (
                jti,
                user_id,
                jti,
                expires_at
            )
        )

        self.sqlite_conn.commit()

    async def revoke_refresh_token(
        self,
        user_id: str,
        jti: str
    ):

        if self.is_mongodb:
            await self.db.tokens.delete_one({
                "user_id": user_id,
                "jti": jti
            })

            return

        cursor = self.sqlite_conn.cursor()

        cursor.execute(
            """
            DELETE FROM refresh_tokens
            WHERE user_id=? AND jti=?
            """,
            (user_id, jti)
        )

        self.sqlite_conn.commit()

    async def is_refresh_token_valid(
        self,
        user_id: str,
        jti: str
    ) -> bool:

        if self.is_mongodb:
            token = await self.db.tokens.find_one({
                "user_id": user_id,
                "jti": jti
            })

            return token is not None

        cursor = self.sqlite_conn.cursor()

        cursor.execute(
            """
            SELECT jti
            FROM refresh_tokens
            WHERE user_id=? AND jti=?
            """,
            (user_id, jti)
        )

        return cursor.fetchone() is not None


# Global instance
db_manager = DatabaseManager()