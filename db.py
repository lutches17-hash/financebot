import asyncpg

class Database:
    def __init__(self, user, password, database, host, port):
        self.user = user
        self.password = password
        self.database = database
        self.host = host
        self.port = port

    async def connect(self):
        """Підключення до бази"""
        self.conn = await asyncpg.connect(
            user=self.user,
            password=self.password,
            database=self.database,
            host=self.host,
            port=self.port
        )
        return self.conn

    async def create_tables(self):
        """Створення таблиці, якщо її ще немає"""
        conn = await self.connect()
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id SERIAL PRIMARY KEY,
            user_id BIGINT NOT NULL,
            type VARCHAR(10) NOT NULL,
            category VARCHAR(50) NOT NULL,
            amount NUMERIC(10,2) NOT NULL,
            note TEXT,
            created_at TIMESTAMP DEFAULT NOW()
        );
        """)
        await conn.close()

    async def add_transaction(self, user_id, type_, category, amount, note):
        """Додавання транзакції"""
        conn = await self.connect()
        await conn.execute(
            """
            INSERT INTO transactions (user_id, type, category, amount, note)
            VALUES ($1, $2, $3, $4, $5)
            """,
            user_id, type_, category, amount, note
        )
        await conn.close()

    async def get_summary(self, user_id, period=None):
        """Повертає суму витрат/доходів за весь час або за період"""
        conn = await self.connect()
        query = """
        SELECT type, SUM(amount) AS total
        FROM transactions
        WHERE user_id = $1
        """
        params = [user_id]

        if period:
            query += " AND created_at > NOW() - make_interval(days => $2)"
            params.append(period)

        query += " GROUP BY type;"

        rows = await conn.fetch(query, *params)
        await conn.close()

        return {r['type']: float(r['total']) for r in rows}

    async def get_by_category(self, user_id, days=30):
        """Повертає суму витрат по категоріях за останні N днів"""
        conn = await self.connect()
        rows = await conn.fetch(
            """
            SELECT category, SUM(amount) AS total
            FROM transactions
            WHERE user_id = $1
              AND type = 'expense'
              AND created_at > NOW() - make_interval(days => $2)
            GROUP BY category
            ORDER BY total DESC;
            """,
            user_id, days
        )
        await conn.close()
        return [(r['category'], float(r['total'])) for r in rows]

    async def list_transactions(self, user_id, limit=10):
        """Повертає останні N транзакцій користувача"""
        conn = await self.connect()
        rows = await conn.fetch(
            """
            SELECT type, category, amount, note, created_at
            FROM transactions
            WHERE user_id = $1
            ORDER BY created_at DESC
            LIMIT $2;
            """,
            user_id, limit
        )
        await conn.close()
        return rows
