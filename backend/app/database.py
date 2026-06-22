import logging
import uuid
from typing import Optional, List, Dict, Any

from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from pymongo.errors import DuplicateKeyError

from app.config import settings

logger = logging.getLogger(__name__)


class DatabaseManager:
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.db = None

    # =====================================================
    # HELPERS
    # =====================================================

    def serialize_doc(self, doc: Optional[dict]) -> Optional[dict]:
        """Convert MongoDB document to JSON serializable dict."""
        if not doc:
            return None

        doc = dict(doc)

        if "_id" in doc:
            doc["id"] = str(doc["_id"])
            del doc["_id"]

        return doc

    async def serialize_cursor(self, cursor) -> List[dict]:
        documents = []

        async for doc in cursor:
            documents.append(self.serialize_doc(doc))

        return documents

    # =====================================================
    # CONNECTION
    # =====================================================

    async def connect(self):
        try:
            logger.info("Connecting to MongoDB...")

            self.client = AsyncIOMotorClient(
                settings.MONGODB_URI,
                serverSelectionTimeoutMS=5000
            )

            await self.client.admin.command("ping")

            self.db = self.client[settings.DATABASE_NAME]

            await self.create_indexes()

            logger.info("MongoDB connected successfully.")

        except Exception as e:
            logger.error(f"MongoDB connection failed: {e}")
            raise

    async def close(self):
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed.")

    # =====================================================
    # INDEXES
    # =====================================================

    async def create_indexes(self):
        try:
            await self.db.users.create_index(
                [("email", 1)],
                unique=True
            )

            await self.db.footprints.create_index(
                [("user_id", 1)]
            )

            await self.db.reports.create_index(
                [("user_id", 1)]
            )

            await self.db.challenges.create_index(
                [("user_id", 1)]
            )

            await self.db.refresh_tokens.create_index(
                [("jti", 1)],
                unique=True
            )

            logger.info("MongoDB indexes created successfully.")

        except Exception as e:
            logger.warning(f"Index creation warning: {e}")

    # =====================================================
    # USERS
    # =====================================================

    async def create_user(self, user_data: dict) -> dict:
        user_data["id"] = str(uuid.uuid4())
        user_data["email"] = user_data["email"].lower()

        try:
            result = await self.db.users.insert_one(user_data)

            user_data["id"] = str(result.inserted_id)

            return user_data

        except DuplicateKeyError:
            raise ValueError("Email already exists")

    async def get_user_by_email(self, email: str) -> Optional[dict]:
        user = await self.db.users.find_one({
            "email": email.lower()
        })

        return self.serialize_doc(user)

    async def get_user_by_id(self, user_id: str) -> Optional[dict]:
        user = None

        try:
            user = await self.db.users.find_one({
                "_id": ObjectId(user_id)
            })
        except Exception:
            user = await self.db.users.find_one({
                "id": user_id
            })

        return self.serialize_doc(user)

    async def update_user(
        self,
        user_id: str,
        updates: dict
    ) -> Optional[dict]:

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

        return await self.get_user_by_id(user_id)

    # =====================================================
    # FOOTPRINTS
    # =====================================================

    async def add_footprint(self, data: dict) -> dict:
        data["id"] = str(uuid.uuid4())

        result = await self.db.footprints.insert_one(data)

        data["id"] = str(result.inserted_id)

        return data

    async def get_footprints_by_user(
        self,
        user_id: str
    ) -> List[dict]:

        cursor = self.db.footprints.find({
            "user_id": user_id
        }).sort("date", -1)

        return await self.serialize_cursor(cursor)

    # =====================================================
    # REPORTS
    # =====================================================

    async def add_report(self, report: dict) -> dict:
        report["id"] = str(uuid.uuid4())

        result = await self.db.reports.insert_one(report)

        report["id"] = str(result.inserted_id)

        return report

    async def get_reports_by_user(
        self,
        user_id: str
    ) -> List[dict]:

        cursor = self.db.reports.find({
            "user_id": user_id
        }).sort("created_at", -1)

        return await self.serialize_cursor(cursor)

    async def get_report_by_id(
        self,
        report_id: str
    ) -> Optional[dict]:

        report = None

        try:
            report = await self.db.reports.find_one({
                "_id": ObjectId(report_id)
            })
        except Exception:
            report = await self.db.reports.find_one({
                "id": report_id
            })

        return self.serialize_doc(report)

    # =====================================================
    # CHALLENGES
    # =====================================================

    async def save_challenges_by_user(
        self,
        user_id: str,
        challenges: List[dict]
    ):

        await self.db.challenges.delete_many({
            "user_id": user_id
        })

        if challenges:
            for challenge in challenges:
                challenge["user_id"] = user_id

            await self.db.challenges.insert_many(challenges)

    async def get_challenges_by_user(
        self,
        user_id: str
    ) -> List[dict]:

        cursor = self.db.challenges.find({
            "user_id": user_id
        })

        return await self.serialize_cursor(cursor)

    async def create_challenge(self, challenge: dict):
        challenge["id"] = str(uuid.uuid4())

        result = await self.db.challenges.insert_one(challenge)

        challenge["id"] = str(result.inserted_id)

        return challenge

    # =====================================================
    # REFRESH TOKENS
    # =====================================================

    async def save_refresh_token(
        self,
        user_id: str,
        jti: str,
        expires_at: str
    ):

        await self.db.refresh_tokens.insert_one({
            "user_id": user_id,
            "jti": jti,
            "expires_at": expires_at
        })

    async def revoke_refresh_token(
        self,
        user_id: str,
        jti: str
    ):

        await self.db.refresh_tokens.delete_one({
            "user_id": user_id,
            "jti": jti
        })

    async def is_refresh_token_valid(
        self,
        user_id: str,
        jti: str
    ) -> bool:

        token = await self.db.refresh_tokens.find_one({
            "user_id": user_id,
            "jti": jti
        })

        return token is not None


# =====================================================
# GLOBAL INSTANCE
# =====================================================

db_manager = DatabaseManager()