# database/database.py
import asyncio
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional, Tuple, Union

import aiosqlite


class Database:
    def __init__(self, db_path: str, max_connections: int = 10):
        self.db_path = db_path
        self.max_connections = max_connections
        self._pool: asyncio.Queue = asyncio.Queue(maxsize=max_connections)
        self._all_connections: List[aiosqlite.Connection] = []

    async def _create_connection(self) -> aiosqlite.Connection:
        conn = await aiosqlite.connect(self.db_path)
        conn.row_factory = aiosqlite.Row
        await conn.execute("PRAGMA journal_mode=WAL")
        await conn.execute("PRAGMA foreign_keys=ON")
        await conn.execute("PRAGMA synchronous=NORMAL")
        return conn

    async def _put_back(self, conn: aiosqlite.Connection) -> None:
        try:
            self._pool.put_nowait(conn)
        except asyncio.QueueFull:
            await conn.close()

    @asynccontextmanager
    async def connection(self) -> aiosqlite.Connection:
        conn = None
        try:
            if self._pool.empty():
                if len(self._all_connections) < self.max_connections:
                    conn = await self._create_connection()
                    self._all_connections.append(conn)
                else:
                    conn = await self._pool.get()
            else:
                conn = self._pool.get_nowait()
            yield conn
        finally:
            if conn is not None:
                await self._put_back(conn)

    @asynccontextmanager
    async def transaction(self) -> aiosqlite.Connection:
        async with self.connection() as conn:
            try:
                yield conn
                await conn.commit()
            except Exception:
                await conn.rollback()
                raise

    async def execute(self, query: str, params: Union[Tuple, Dict, None] = None) -> List[Dict]:
        async with self.connection() as conn:
            async with conn.execute(query, params or ()) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

    async def execute_many(self, query: str, params_list: List[Union[Tuple, Dict]]) -> None:
        async with self.connection() as conn:
            await conn.executemany(query, params_list)
            await conn.commit()

    async def execute_script(self, script: str) -> None:
        async with self.connection() as conn:
            await conn.executescript(script)
            await conn.commit()

    async def close_all(self) -> None:
        while not self._pool.empty():
            conn = self._pool.get_nowait()
            await conn.close()
        for conn in self._all_connections:
            await conn.close()
        self._all_connections.clear()


async def init_db(db: Database):
    await db.execute_script("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            hashed_password TEXT NOT NULL,
            is_active BOOLEAN NOT NULL DEFAULT 1,
            agreed_to_anonymous BOOLEAN NOT NULL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE INDEX IF NOT EXISTS idx_username ON users(username);

        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            type TEXT NOT NULL CHECK(type IN ('income','expense')),
            icon TEXT DEFAULT '💳',
            color TEXT DEFAULT '#F4633A'
        );

        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            category_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            type TEXT NOT NULL CHECK(type IN ('income','expense')),
            description TEXT DEFAULT '',
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (category_id) REFERENCES categories(id)
        );
        CREATE INDEX IF NOT EXISTS idx_transactions_user_date ON transactions(user_id, date);
        CREATE INDEX IF NOT EXISTS idx_transactions_category ON transactions(category_id);
    """)
    await seed_categories(db)

async def seed_categories(db: Database):
    from core.categories import CATEGORIES
    for cat in CATEGORIES:
        await db.execute(
            "INSERT OR IGNORE INTO categories (name, type, icon, color) VALUES (?, ?, ?, ?)",
            (cat["name"], cat["type"], cat["icon"], cat["color"])
        )