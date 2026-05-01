# crud/transaction.py
from database.database import Database
from core.logging_config import logger


class TransactionCRUD:
    def __init__(self, db: Database):
        self.db = db

    async def create(self, user_id: int, category_id: int, amount: float,
                     type_: str, description: str = "", date: str = None) -> int:
        try:
            query = """INSERT INTO transactions (user_id, category_id, amount, type, description, date)
                    VALUES (?, ?, ?, ?, ?, COALESCE(?, CURRENT_TIMESTAMP))"""
            params = (user_id, category_id, amount, type_, description, date)
            async with self.db.connection() as conn:
                cursor = await conn.execute(query, params)
                await conn.commit()
                tid = cursor.lastrowid
            logger.info(f"Транзакция создана: id={tid}, user_id={user_id}, сумма={amount}")
            return tid
        except Exception as e:
            logger.error(f"Ошибка создания транзакции: {e}")
            raise

    async def get_stats_summary(self, user_id: int, period: str = "month") -> dict:
        period_map = {"week": "-7 days", "month": "-1 month", "year": "-1 year", "all": None}
        date_offset = period_map.get(period, "-1 month")
        if date_offset:
            query = """SELECT type, SUM(amount) as total FROM transactions
                    WHERE user_id = ? AND date >= date('now', ?) GROUP BY type"""
            rows = await self.db.execute(query, (user_id, date_offset))
        else:
            query = """SELECT type, SUM(amount) as total FROM transactions
                    WHERE user_id = ? GROUP BY type"""
            rows = await self.db.execute(query, (user_id,))
        result = {"income": 0.0, "expense": 0.0}
        for row in rows:
            result[row["type"]] = row["total"]
        return result

    async def get_by_category(self, user_id: int, period: str = "month", type_: str = "expense"):
        period_map = {"week": "-7 days", "month": "-1 month", "year": "-1 year", "all": None}
        date_offset = period_map.get(period, "-1 month")
        if date_offset:
            query = """SELECT c.id as category_id, c.name, c.icon, c.color, SUM(t.amount) as total
                    FROM transactions t JOIN categories c ON t.category_id = c.id
                    WHERE t.user_id = ? AND t.type = ? AND t.date >= date('now', ?)
                    GROUP BY c.id ORDER BY total DESC"""
            rows = await self.db.execute(query, (user_id, type_, date_offset))
        else:
            query = """SELECT c.id as category_id, c.name, c.icon, c.color, SUM(t.amount) as total
                        FROM transactions t JOIN categories c ON t.category_id = c.id
                        WHERE t.user_id = ? AND t.type = ?
                        GROUP BY c.id ORDER BY total DESC"""
            rows = await self.db.execute(query, (user_id, type_))
        return [dict(row) for row in rows]

    async def get_monthly_trend(self, user_id: int, months: int = 6):
        if months == 0:
            query = """SELECT strftime('%Y-%m', date) as month,
                            SUM(CASE WHEN type='income' THEN amount ELSE 0 END) as income,
                            SUM(CASE WHEN type='expense' THEN amount ELSE 0 END) as expense
                    FROM transactions WHERE user_id = ?
                    GROUP BY month ORDER BY month ASC"""
            rows = await self.db.execute(query, (user_id,))
        else:
            query = """SELECT strftime('%Y-%m', date) as month,
                            SUM(CASE WHEN type='income' THEN amount ELSE 0 END) as income,
                            SUM(CASE WHEN type='expense' THEN amount ELSE 0 END) as expense
                    FROM transactions WHERE user_id = ? AND date >= date('now', ? || ' months')
                    GROUP BY month ORDER BY month ASC"""
            rows = await self.db.execute(query, (user_id, f"-{months}"))
        return [dict(row) for row in rows]
    
    async def get_total_volume(self, user_id: int, period: str = "month") -> float:
        period_map = {"week": "-7 days", "month": "-1 month", "year": "-1 year", "all": None}
        date_offset = period_map.get(period, "-1 month")
        if date_offset:
            query = """SELECT COALESCE(SUM(amount), 0) as total FROM transactions
                        WHERE user_id = ? AND date >= date('now', ?)"""
            rows = await self.db.execute(query, (user_id, date_offset))
        else:
            query = """SELECT COALESCE(SUM(amount), 0) as total
                        FROM transactions
                        WHERE user_id = ?"""
            rows = await self.db.execute(query, (user_id,))
        return rows[0]["total"]