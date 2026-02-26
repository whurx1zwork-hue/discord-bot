import asyncpg
import json
import os
from datetime import datetime

class Database:
    def __init__(self):
        self.pool = None
        self.DATABASE_URL = os.getenv('DATABASE_URL')
    
    async def connect(self):
        """Подключение к базе данных"""
        try:
            self.pool = await asyncpg.create_pool(self.DATABASE_URL)
            print("✅ Подключение к БД установлено")
            await self.create_tables()
            return True
        except Exception as e:
            print(f"❌ Ошибка подключения к БД: {e}")
            return False
    
    async def create_tables(self):
        """Создание таблиц, если их нет"""
        async with self.pool.acquire() as conn:
            # Таблица для уровней
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS levels (
                    user_id TEXT PRIMARY KEY,
                    username TEXT,
                    level INTEGER DEFAULT 0,
                    xp INTEGER DEFAULT 0,
                    total_xp INTEGER DEFAULT 0,
                    voice_xp INTEGER DEFAULT 0,
                    message_xp INTEGER DEFAULT 0,
                    messages INTEGER DEFAULT 0,
                    voice_time INTEGER DEFAULT 0,
                    coins INTEGER DEFAULT 0,
                    total_coins_earned INTEGER DEFAULT 0,
                    items TEXT DEFAULT '[]',
                    last_message_time TIMESTAMP,
                    last_bonus TIMESTAMP DEFAULT '1970-01-01'
                )
            ''')
            
            # Таблица для магазина
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS shop (
                    item_id TEXT PRIMARY KEY,
                    name TEXT,
                    price INTEGER,
                    description TEXT,
                    duration INTEGER,
                    role_id TEXT
                )
            ''')
            
            # Таблица для временных ролей
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS temp_roles (
                    id SERIAL PRIMARY KEY,
                    user_id TEXT,
                    role_id TEXT,
                    expires TIMESTAMP,
                    item_id TEXT,
                    saved_roles TEXT DEFAULT '[]'
                )
            ''')
            
            # Таблица для предупреждений
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS warns (
                    id SERIAL PRIMARY KEY,
                    user_id TEXT,
                    guild_id TEXT,
                    moderator_id TEXT,
                    reason TEXT,
                    date TIMESTAMP
                )
            ''')
            
            # Таблица для приглашений
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS invites (
                    user_id TEXT PRIMARY KEY,
                    username TEXT,
                    invites INTEGER DEFAULT 0,
                    joined_users TEXT DEFAULT '[]'
                )
            ''')
            
            # Таблица для бустеров
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS boost_roles (
                    role_id TEXT PRIMARY KEY,
                    multiplier REAL
                )
            ''')
            
            print("✅ Таблицы созданы/проверены")
    
    # ============== УРОВНИ ==============
    async def load_levels(self):
        """Загрузка всех уровней"""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch('SELECT * FROM levels')
            data = {}
            for row in rows:
                user_id = row['user_id']
                data[user_id] = {
                    'xp': row['xp'],
                    'level': row['level'],
                    'total_xp': row['total_xp'],
                    'voice_xp': row['voice_xp'],
                    'message_xp': row['message_xp'],
                    'username': row['username'],
                    'messages': row['messages'],
                    'voice_time': row['voice_time'],
                    'coins': row['coins'],
                    'total_coins_earned': row['total_coins_earned'],
                    'items': json.loads(row['items']),
                    'last_message_time': row['last_message_time'].isoformat() if row['last_message_time'] else None,
                    'last_bonus': row['last_bonus'].timestamp() if row['last_bonus'] else 0
                }
            return data
    
    async def save_level(self, user_id, data):
        """Сохранение данных одного пользователя"""
        async with self.pool.acquire() as conn:
            await conn.execute('''
                INSERT INTO levels (
                    user_id, username, level, xp, total_xp, voice_xp, message_xp,
                    messages, voice_time, coins, total_coins_earned, items,
                    last_message_time, last_bonus
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, to_timestamp($14))
                ON CONFLICT (user_id) DO UPDATE SET
                    username = EXCLUDED.username,
                    level = EXCLUDED.level,
                    xp = EXCLUDED.xp,
                    total_xp = EXCLUDED.total_xp,
                    voice_xp = EXCLUDED.voice_xp,
                    message_xp = EXCLUDED.message_xp,
                    messages = EXCLUDED.messages,
                    voice_time = EXCLUDED.voice_time,
                    coins = EXCLUDED.coins,
                    total_coins_earned = EXCLUDED.total_coins_earned,
                    items = EXCLUDED.items,
                    last_message_time = EXCLUDED.last_message_time,
                    last_bonus = EXCLUDED.last_bonus
            ''',
                user_id, data['username'], data['level'], data['xp'], data['total_xp'],
                data['voice_xp'], data['message_xp'], data['messages'], data['voice_time'],
                data['coins'], data['total_coins_earned'], json.dumps(data['items']),
                datetime.fromisoformat(data['last_message_time']) if data['last_message_time'] else None,
                data.get('last_bonus', 0)
            )
    
    # ============== МАГАЗИН ==============
    async def load_shop(self):
        """Загрузка всех товаров магазина"""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch('SELECT * FROM shop')
            data = {}
            for row in rows:
                item = {
                    'name': row['name'],
                    'price': row['price'],
                    'description': row['description']
                }
                if row['duration']:
                    item['duration'] = row['duration']
                if row['role_id']:
                    item['role_id'] = int(row['role_id'])
                data[row['item_id']] = item
            return data
    
    async def save_shop(self, shop_data):
        """Сохранение всех товаров магазина"""
        async with self.pool.acquire() as conn:
            # Очищаем таблицу
            await conn.execute('DELETE FROM shop')
            
            # Вставляем все товары
            for item_id, item in shop_data.items():
                await conn.execute('''
                    INSERT INTO shop (item_id, name, price, description, duration, role_id)
                    VALUES ($1, $2, $3, $4, $5, $6)
                ''',
                    item_id, item['name'], item['price'], item.get('description', ''),
                    item.get('duration'), str(item.get('role_id')) if item.get('role_id') else None
                )
    
    # ============== ВРЕМЕННЫЕ РОЛИ ==============
    async def load_temp_roles(self):
        """Загрузка всех временных ролей"""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch('SELECT * FROM temp_roles')
            data = {}
            for row in rows:
                user_id = row['user_id']
                if user_id not in data:
                    data[user_id] = []
                
                role_data = {
                    'role_id': int(row['role_id']),
                    'expires': row['expires'].timestamp(),
                    'item_id': row['item_id'],
                    'saved_roles': json.loads(row['saved_roles'])
                }
                data[user_id].append(role_data)
            return data
    
    async def save_temp_roles(self, temp_data):
        """Сохранение всех временных ролей"""
        async with self.pool.acquire() as conn:
            await conn.execute('DELETE FROM temp_roles')
            
            for user_id, roles in temp_data.items():
                for role in roles:
                    await conn.execute('''
                        INSERT INTO temp_roles (user_id, role_id, expires, item_id, saved_roles)
                        VALUES ($1, $2, to_timestamp($3), $4, $5)
                    ''',
                        user_id, role['role_id'], role['expires'],
                        role['item_id'], json.dumps(role.get('saved_roles', []))
                    )
    
    # ============== ПРИГЛАШЕНИЯ ==============
    async def load_invites(self):
        """Загрузка всех приглашений"""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch('SELECT * FROM invites')
            data = {}
            for row in rows:
                data[row['user_id']] = {
                    'username': row['username'],
                    'invites': row['invites'],
                    'joined_users': json.loads(row['joined_users'])
                }
            return data
    
    async def save_invites(self, invites_data):
        """Сохранение всех приглашений"""
        async with self.pool.acquire() as conn:
            for user_id, data in invites_data.items():
                await conn.execute('''
                    INSERT INTO invites (user_id, username, invites, joined_users)
                    VALUES ($1, $2, $3, $4)
                    ON CONFLICT (user_id) DO UPDATE SET
                        username = EXCLUDED.username,
                        invites = EXCLUDED.invites,
                        joined_users = EXCLUDED.joined_users
                ''',
                    user_id, data['username'], data['invites'],
                    json.dumps(data.get('joined_users', []))
                )
    
    # ============== БУСТЕРЫ ==============
    async def load_boosts(self):
        """Загрузка всех бустеров"""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch('SELECT * FROM boost_roles')
            return {int(row['role_id']): row['multiplier'] for row in rows}
    
    async def save_boosts(self, boosts):
        """Сохранение всех бустеров"""
        async with self.pool.acquire() as conn:
            await conn.execute('DELETE FROM boost_roles')
            for role_id, mult in boosts.items():
                await conn.execute('''
                    INSERT INTO boost_roles (role_id, multiplier) VALUES ($1, $2)
                ''', str(role_id), mult)
    
    # ============== ПРЕДУПРЕЖДЕНИЯ ==============
    async def load_warns(self):
        """Загрузка всех предупреждений"""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch('SELECT * FROM warns')
            data = {}
            for row in rows:
                key = f"{row['guild_id']}_{row['user_id']}"
                if key not in data:
                    data[key] = []
                data[key].append({
                    'id': row['id'],
                    'moderator_id': int(row['moderator_id']),
                    'reason': row['reason'],
                    'date': row['date'].isoformat(),
                    'timestamp': row['date'].timestamp()
                })
            return data
