# dependencies.py
from database.database import Database
from tools.config import DB_PATH

database = Database(DB_PATH)

async def get_db() -> Database:
    return database