import os
import asyncio
import asyncpg
from config import SUPABASE_URL

# Функция для получения соединения
async def get_connection():
    conn = await asyncpg.connect(SUPABASE_URL)
    return conn
