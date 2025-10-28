# config/db.py
from motor.motor_asyncio import AsyncIOMotorClient

MONGODB_URL = "mongodb://localhost:27017"
DB_NAME = "user_py_db"

client = AsyncIOMotorClient(MONGODB_URL)
db = client[DB_NAME]
users = db["users"]