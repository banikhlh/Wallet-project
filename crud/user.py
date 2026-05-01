# crud/user.py
from typing import List, Optional
from datetime import datetime
from schemas.user import UserCreate, UserResponse, UserInDB
from database.database import Database
from core.security import hash_password, verify_password
from core.logging_config import logger

class UserCRUD:
    def __init__(self, db: Database):
        self.db = db

    async def create(self, user_create: UserCreate) -> UserResponse:
            try:
                hashed = hash_password(user_create.password)
                query = "INSERT INTO users (username, hashed_password, is_active) VALUES (?, ?, ?)"
                params = (user_create.username, hashed, user_create.is_active)
                async with self.db.transaction() as conn:
                    cursor = await conn.execute(query, params)
                    user_id = cursor.lastrowid
                logger.info(f"Пользователь создан: {user_create.username} (id={user_id})")
                return await self.get_by_id(user_id)
            except Exception as e:
                logger.error(f"Ошибка создания пользователя: {e}")
                raise

    async def get_by_id(self, user_id: int) -> Optional[UserResponse]:
        query = "SELECT id, username, is_active, created_at FROM users WHERE id = ?"
        rows = await self.db.execute(query, (user_id,))
        if not rows:
            return None
        return UserResponse(**rows[0])

    async def get_by_username(self, username: str) -> Optional[UserResponse]:
        query = "SELECT id, username, is_active, created_at FROM users WHERE username = ?"
        rows = await self.db.execute(query, (username,))
        if not rows:
            return None
        return UserResponse(**rows[0])

    async def get_in_db_by_username(self, username: str) -> Optional[UserInDB]:
        query = "SELECT id, username, hashed_password, is_active, created_at FROM users WHERE username = ?"
        rows = await self.db.execute(query, (username,))
        if not rows:
            return None
        return UserInDB(**rows[0])

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[UserResponse]:
        query = """
            SELECT id, username, is_active, created_at
            FROM users
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        """
        rows = await self.db.execute(query, (limit, skip))
        return [UserResponse(**row) for row in rows]

    async def update(self, user_id: int, **fields) -> Optional[UserResponse]:
        allowed_fields = {"username", "is_active", "password"}
        update_data = {k: v for k, v in fields.items() if k in allowed_fields}
        if not update_data:
            return await self.get_by_id(user_id)

        if "password" in update_data:
            update_data["hashed_password"] = hash_password(update_data.pop("password"))

        set_clause = ", ".join(f"{key} = ?" for key in update_data.keys())
        query = f"UPDATE users SET {set_clause} WHERE id = ?"
        params = list(update_data.values()) + [user_id]

        async with self.db.transaction() as conn:
            await conn.execute(query, params)

        return await self.get_by_id(user_id)

    async def update_is_active(self, user_id: int, is_active: bool) -> Optional[UserResponse]:
        return await self.update(user_id, is_active=is_active)

    async def delete(self, user_id: int) -> bool:
        query = "DELETE FROM users WHERE id = ?"
        async with self.db.transaction() as conn:
            cursor = await conn.execute(query, (user_id,))
            return cursor.rowcount > 0

    async def authenticate(self, username: str, password: str) -> Optional[UserResponse]:
        user_db = await self.get_in_db_by_username(username)
        if not user_db or not user_db.is_active:
            return None
        if verify_password(password, user_db.hashed_password):
            return UserResponse(
                id=user_db.id,
                username=user_db.username,
                is_active=user_db.is_active,
                created_at=user_db.created_at
            )
        return None