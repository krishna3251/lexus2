"""
Centralized MongoDB helper for Lexus bot.
Fixed for Python 3.14 SSL compatibility.
"""

import os
import ssl
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

MONGO_URI = os.getenv("MONGO_URI", "")
DB_NAME   = os.getenv("MONGO_DB_NAME", "lexus_bot")

_client = None
_db     = None


async def connect():
    """Connect to MongoDB. Call once at bot startup."""
    global _client, _db
    if not MONGO_URI:
        logger.warning("MONGO_URI not set – MongoDB features disabled.")
        return None
    try:
        # tlsInsecure=True fixes SSL handshake errors on Python 3.14
        _client = AsyncIOMotorClient(
            MONGO_URI,
            serverSelectionTimeoutMS=5000,
            tlsInsecure=True,
        )
        await _client.admin.command("ping")
        _db = _client[DB_NAME]
        logger.info(f"✅ Connected to MongoDB: {DB_NAME}")
        return _db
    except Exception as e:
        logger.error(f"❌ MongoDB connection failed: {e}")
        _client = None
        _db     = None
        return None


async def disconnect():
    global _client, _db
    if _client:
        _client.close()
        _client = None
        _db     = None


def get_db():
    return _db


def get_collection(name: str):
    if _db is None:
        return None
    return _db[name]


# ─── Guild config ──────────────────────────────────────────────────

async def get_guild_config(guild_id: int) -> dict:
    col = get_collection("guild_config")
    if col is None:
        return {}
    doc = await col.find_one({"guild_id": guild_id})
    return doc or {}


async def update_guild_config(guild_id: int, update: dict):
    col = get_collection("guild_config")
    if col is None:
        return
    await col.update_one({"guild_id": guild_id}, {"$set": update}, upsert=True)


# ─── Anti-nuke ────────────────────────────────────────────────────

async def get_antinuke(guild_id: int) -> dict:
    col = get_collection("antinuke")
    if col is None:
        return {}
    doc = await col.find_one({"guild_id": guild_id})
    return doc or {}


async def update_antinuke(guild_id: int, update: dict):
    col = get_collection("antinuke")
    if col is None:
        return
    await col.update_one({"guild_id": guild_id}, {"$set": update}, upsert=True)


# ─── Warnings ────────────────────────────────────────────────────

async def get_warnings(guild_id: int, user_id: int) -> list:
    col = get_collection("warnings")
    if col is None:
        return []
    cursor = col.find({"guild_id": guild_id, "user_id": user_id}).sort("timestamp", -1)
    return await cursor.to_list(length=100)


async def add_warning(doc: dict):
    col = get_collection("warnings")
    if col is None:
        return
    await col.insert_one(doc)


# ─── Karma ───────────────────────────────────────────────────────

async def get_karma(guild_id: int, user_id: int) -> dict:
    col = get_collection("karma")
    if col is None:
        return {}
    doc = await col.find_one({"guild_id": guild_id, "user_id": user_id})
    return doc or {}


async def update_karma(guild_id: int, user_id: int, update: dict):
    col = get_collection("karma")
    if col is None:
        return
    await col.update_one(
        {"guild_id": guild_id, "user_id": user_id},
        {"$set": update}, upsert=True
    )


async def inc_karma(guild_id: int, user_id: int, increments: dict):
    col = get_collection("karma")
    if col is None:
        return
    await col.update_one(
        {"guild_id": guild_id, "user_id": user_id},
        {"$inc": increments}, upsert=True
    )


# ─── Levels ──────────────────────────────────────────────────────

async def get_levels(guild_id: int, user_id: int) -> dict:
    col = get_collection("levels")
    if col is None:
        return {}
    doc = await col.find_one({"guild_id": guild_id, "user_id": user_id})
    return doc or {}


async def update_levels(guild_id: int, user_id: int, update: dict):
    col = get_collection("levels")
    if col is None:
        return
    await col.update_one(
        {"guild_id": guild_id, "user_id": user_id},
        {"$set": update}, upsert=True
    )


async def inc_levels(guild_id: int, user_id: int, increments: dict):
    col = get_collection("levels")
    if col is None:
        return
    await col.update_one(
        {"guild_id": guild_id, "user_id": user_id},
        {"$inc": increments}, upsert=True
    )
