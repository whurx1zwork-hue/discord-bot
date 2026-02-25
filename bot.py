import discord
from discord.ext import commands, tasks
import json
import os
import random
import asyncio
from datetime import datetime, timedelta  # ЭТО ВАЖНО!
import math
import time

# ============== НАСТРОЙКИ ==============
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.voice_states = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Файлы для данных
DATA_FILE = 'levels_data.json'
SHOP_FILE = 'shop_data.json'
BOOST_FILE = 'boost_data.json'
TEMP_ROLES_FILE = 'temp_roles.json'
REPLACEMENT_FILE = 'replacement_config.json'
WARNS_FILE = 'warns_data.json'
MUTES_FILE = 'mutes_data.json'

# ============== СИСТЕМА ВРЕМЕННЫХ РОЛЕЙ ==============
temp_roles = {}
voice_tracking = {}  # ЭТО ДОЛЖНО БЫТЬ!

# Настройки уровней
LEVEL_UP_BASE = 100
LEVEL_UP_MULTIPLIER = 1.5
XP_PER_VOICE_MINUTE = 2

# ============== УВЕЛИЧЕННЫЕ НАГРАДЫ ЗА УРОВНИ ==============
COINS_PER_LEVEL_UP = {
    # Начальные уровни (быстрый старт)
    1: 25, 2: 40, 3: 55, 4: 70,
    5: 100, 6: 85, 7: 100, 8: 115, 9: 130,
    
    # 10 уровень - можно купить бустер 25%
    10: 200, 11: 160, 12: 175, 13: 190, 14: 205,
    
    # 15 уровень - можно купить бустер 35%
    15: 300, 16: 220, 17: 235, 18: 250, 19: 265,
    
    # 20 уровень - серьёзные накопления
    20: 400, 21: 280, 22: 295, 23: 310, 24: 325,
    25: 450, 26: 340, 27: 355, 28: 370, 29: 385,
    30: 500, 31: 400, 32: 415, 33: 430, 34: 445,
    35: 550, 36: 460, 37: 475, 38: 490, 39: 505,
    40: 600, 41: 520, 42: 535, 43: 550, 44: 565,
    45: 650, 46: 580, 47: 595, 48: 610, 49: 625,
    50: 700, 51: 640, 52: 655, 53: 670, 54: 685,
    55: 750, 56: 700, 57: 715, 58: 730, 59: 745,
    60: 800, 61: 760, 62: 775, 63: 790, 64: 805,
    65: 850, 66: 820, 67: 835, 68: 850, 69: 865,
    70: 900, 71: 880, 72: 895, 73: 910, 74: 925,
    75: 950, 76: 940, 77: 955, 78: 970, 79: 985,
    80: 1000, 81: 1000, 82: 1015, 83: 1030, 84: 1045,
    85: 1060, 86: 1075, 87: 1090, 88: 1105, 89: 1120,
    90: 1135, 91: 1150, 92: 1165, 93: 1180, 94: 1195,
    95: 1210, 96: 1225, 97: 1240, 98: 1255, 99: 1270,
    100: 1300, 101: 1315, 102: 1330, 103: 1345, 104: 1360,
    105: 1375, 106: 1390, 107: 1405, 108: 1420, 109: 1435,
    110: 1450, 111: 1465, 112: 1480, 113: 1495, 114: 1510,
    115: 1525, 116: 1540, 117: 1555, 118: 1570, 119: 1585,
    120: 1600, 121: 1615, 122: 1630, 123: 1645, 124: 1660,
    125: 1675, 126: 1690, 127: 1705, 128: 1720, 129: 1735,
    130: 1750, 131: 1765, 132: 1780, 133: 1795, 134: 1810,
    135: 1825, 136: 1840, 137: 1855, 138: 1870, 139: 1885,
    140: 1900, 141: 1915, 142: 1930, 143: 1945, 144: 1960,
    145: 1975, 146: 1990, 147: 2005, 148: 2020, 149: 2035,
    150: 2050, 151: 2065, 152: 2080, 153: 2095, 154: 2110,
    155: 2125, 156: 2140, 157: 2155, 158: 2170, 159: 2185,
    160: 2200, 161: 2215, 162: 2230, 163: 2245, 164: 2260,
    165: 2275, 166: 2290, 167: 2305, 168: 2320, 169: 2335,
    170: 2350, 171: 2365, 172: 2380, 173: 2395, 174: 2410,
    175: 2425, 176: 2440, 177: 2455, 178: 2470, 179: 2485,
    180: 2500, 181: 2515, 182: 2530, 183: 2545, 184: 2560,
    185: 2575, 186: 2590, 187: 2605, 188: 2620, 189: 2635,
    190: 2650, 191: 2665, 192: 2680, 193: 2695, 194: 2710,
    195: 2725, 196: 2740, 197: 2755, 198: 2770, 199: 2785,
    200: 2800, 201: 2815, 202: 2830, 203: 2845, 204: 2860,
    205: 2875, 206: 2890, 207: 2905, 208: 2920, 209: 2935,
    210: 2950, 211: 2965, 212: 2980, 213: 2995, 214: 3010,
    215: 3025, 216: 3040, 217: 3055, 218: 3070, 219: 3085,
    220: 3100, 221: 3115, 222: 3130, 223: 3145, 224: 3160,
    225: 3175, 226: 3190, 227: 3205, 228: 3220, 229: 3235,
    230: 3250, 231: 3265, 232: 3280, 233: 3295, 234: 3310,
    235: 3325, 236: 3340, 237: 3355, 238: 3370, 239: 3385,
    240: 3400, 241: 3415, 242: 3430, 243: 3445, 244: 3460,
    245: 3475, 246: 3490, 247: 3505, 248: 3520, 249: 3535,
    250: 3550, 251: 3565, 252: 3580, 253: 3595, 254: 3610,
    255: 3625, 256: 3640, 257: 3655, 258: 3670, 259: 3685,
    260: 3700, 261: 3715, 262: 3730, 263: 3745, 264: 3760,
    265: 3775, 266: 3790, 267: 3805, 268: 3820, 269: 3835,
    270: 3850, 271: 3865, 272: 3880, 273: 3895, 274: 3910,
    275: 3925, 276: 3940, 277: 3955, 278: 3970, 279: 3985,
    280: 4000, 281: 4015, 282: 4030, 283: 4045, 284: 4060,
    285: 4075, 286: 4090, 287: 4105, 288: 4120, 289: 4135,
    290: 4150, 291: 4165, 292: 4180, 293: 4195, 294: 4210,
    295: 4225, 296: 4240, 297: 4255, 298: 4270, 299: 4285,
    300: 4300,  # Кастомная роль!
}

# ============== НАСТРОЙКИ ЗАМЕНЫ РОЛЕЙ ==============
WHITELISTED_ROLES = []  # Будут загружены из файла
REPLACEMENT_ROLES = []  # Будут загружены из файла

# ============== НАСТРОЙКИ ДЛЯ СИСТЕМЫ НАКАЗАНИЙ ==============
MAX_WARNS = 3
ACTION_ON_MAX_WARNS = "mute"

# ============== СИСТЕМА МУТА БЕЗ РОЛИ ==============
MUTE_PERMISSIONS = {
    'send_messages': False,
    'add_reactions': False,
    'speak': False,
    'stream': False,
    'use_voice_activation': False,
    'use_soundboard': False,
    'use_external_sounds': False,
    'use_embedded_activities': False,
}

# ============== ФУНКЦИИ ДЛЯ РАБОТЫ С НАСТРОЙКАМИ ЗАМЕНЫ ==============
def load_replacement_config():
    global WHITELISTED_ROLES, REPLACEMENT_ROLES
    if os.path.exists(REPLACEMENT_FILE):
        try:
            with open(REPLACEMENT_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
                WHITELISTED_ROLES = config.get('whitelist', [])
                REPLACEMENT_ROLES = config.get('replacement', [])
                print(f"✅ Загружены настройки замены ролей: {len(WHITELISTED_ROLES)} белых, {len(REPLACEMENT_ROLES)} заменяющих")
        except Exception as e:
            print(f"❌ Ошибка загрузки настроек: {e}")
            WHITELISTED_ROLES = []
            REPLACEMENT_ROLES = []
    else:
        WHITELISTED_ROLES = []
        REPLACEMENT_ROLES = []

def save_replacement_config():
    config = {'whitelist': WHITELISTED_ROLES, 'replacement': REPLACEMENT_ROLES}
    with open(REPLACEMENT_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4, ensure_ascii=False)

# ============== Цвета и эмодзи ==============
RED_COLOR = 0xff0000
EMOJIS = {
    'level': '📊', 'xp': '✨', 'message': '💬', 'voice': '🎤',
    'time': '⏱️', 'crown': '👑', 'medal1': '🥇', 'medal2': '🥈',
    'medal3': '🥉', 'progress_full': '🟥', 'progress_empty': '⬛',
    'up': '⬆️', 'down': '⬇️', 'fire': '🔥', 'boost': '⚡',
    'chart': '📈', 'separator': '▬', 'star': '⭐', 'target': '🎯',
    'coin': '🪙', 'shop': '🏪', 'cart': '🛒', 'box': '📦', 'money': '💰',
    'role': '👑', 'clock': '⏰'
}

# ============== СИСТЕМА БУСТЕРОВ ==============
BOOST_ROLES = {}
user_boost_cache = {}
CACHE_TIME = 30

# ============== СИСТЕМА ВРЕМЕННЫХ РОЛЕЙ ==============
temp_roles = {}
voice_tracking = {}

# ============== СИСТЕМА ПРЕДУПРЕЖДЕНИЙ ==============
warns_data = {}

# ============== СИСТЕМА МУТОВ ==============
active_mutes = {}

# ============== ФУНКЦИИ РАБОТЫ С ФАЙЛАМИ ==============
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def load_shop():
    if os.path.exists(SHOP_FILE):
        with open(SHOP_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_shop(shop):
    with open(SHOP_FILE, 'w', encoding='utf-8') as f:
        json.dump(shop, f, indent=4, ensure_ascii=False)

def load_boosts():
    global BOOST_ROLES
    if os.path.exists(BOOST_FILE):
        with open(BOOST_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            BOOST_ROLES = {int(k): v for k, v in data.items()}
    return BOOST_ROLES

def save_boosts():
    data = {str(k): v for k, v in BOOST_ROLES.items()}
    with open(BOOST_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def load_temp_roles():
    global temp_roles
    if os.path.exists(TEMP_ROLES_FILE):
        with open(TEMP_ROLES_FILE, 'r', encoding='utf-8') as f:
            temp_roles = json.load(f)
    return temp_roles

def save_temp_roles():
    with open(TEMP_ROLES_FILE, 'w', encoding='utf-8') as f:
        json.dump(temp_roles, f, indent=4, ensure_ascii=False)

def load_warns():
    global warns_data
    if os.path.exists(WARNS_FILE):
        with open(WARNS_FILE, 'r', encoding='utf-8') as f:
            warns_data = json.load(f)
    return warns_data

def save_warns():
    with open(WARNS_FILE, 'w', encoding='utf-8') as f:
        json.dump(warns_data, f, indent=4, ensure_ascii=False)

def load_mutes():
    global active_mutes
    if os.path.exists(MUTES_FILE):
        with open(MUTES_FILE, 'r', encoding='utf-8') as f:
            active_mutes = json.load(f)
    return active_mutes

def save_mutes():
    with open(MUTES_FILE, 'w', encoding='utf-8') as f:
        json.dump(active_mutes, f, indent=4, ensure_ascii=False)

# Загружаем все данные
user_data = load_data()
shop_data = load_shop()
load_boosts()
load_temp_roles()
load_replacement_config()
load_warns()
load_mutes()

# ============== ФУНКЦИИ УРОВНЕЙ ==============
def calculate_level(xp):
    level = 0
    xp_required = LEVEL_UP_BASE
    while xp >= xp_required:
        xp -= xp_required
        level += 1
        xp_required = int(LEVEL_UP_BASE * (LEVEL_UP_MULTIPLIER ** level))
    return level, xp, xp_required

def xp_to_next_level(level):
    return int(LEVEL_UP_BASE * (LEVEL_UP_MULTIPLIER ** level))

def create_progress_bar(current, maximum, length=15):
    if maximum == 0:
        return "⬛" * length
    progress = int((current / maximum) * length)
    bar = "🟥" * progress + "⬛" * (length - progress)
    percentage = (current / maximum) * 100
    return f"{bar} `{percentage:.1f}%`"

def create_separator(length=30):
    return f"```{'-' * length}```"

def get_level_reward(level):
    return COINS_PER_LEVEL_UP.get(level, 0)

def format_time(minutes):
    if minutes < 60:
        return f"{minutes} мин"
    elif minutes < 1440:
        hours = minutes // 60
        return f"{hours} ч"
    else:
        days = minutes // 1440
        return f"{days} дн"

# ============== ФУНКЦИИ ДЛЯ БУСТЕРОВ ==============
def get_user_boost(member):
    if not member:
        return 1.0
    
    user_id = str(member.id)
    current_time = datetime.now().timestamp()
    
    if user_id in user_boost_cache:
        cache = user_boost_cache[user_id]
        if current_time - cache['last_check'] < CACHE_TIME:
            return cache['multiplier']
    
    multiplier = 1.0
    for role in member.roles:
        if role.id in BOOST_ROLES:
            role_mult = BOOST_ROLES[role.id]
            if role_mult > multiplier:
                multiplier = role_mult
    
    user_boost_cache[user_id] = {
        'multiplier': multiplier,
        'last_check': current_time
    }
    
    return multiplier

# ============== ФУНКЦИИ ДЛЯ ВРЕМЕННЫХ РОЛЕЙ ==============
async def check_temp_roles():
    current_time = datetime.now().timestamp()
    removed_count = 0
    restored_count = 0
    
    for user_id, roles in list(temp_roles.items()):
        expired_roles = []
        
        for role_data in roles:
            if current_time > role_data['expires']:
                expired_roles.append(role_data)
        
        for role_data in expired_roles:
            for guild in bot.guilds:
                member = guild.get_member(int(user_id))
                if member:
                    temp_role = guild.get_role(role_data['role_id'])
                    if temp_role:
                        try:
                            await member.remove_roles(temp_role, reason="Время действия роли истекло")
                            removed_count += 1
                            
                            if 'saved_roles' in role_data and role_data['saved_roles']:
                                restored_roles_list = []
                                for saved_role_id in role_data['saved_roles']:
                                    saved_role = guild.get_role(saved_role_id)
                                    if saved_role:
                                        try:
                                            await member.add_roles(saved_role, reason="Возврат после временной роли")
                                            restored_roles_list.append(saved_role.name)
                                        except:
                                            pass
                                
                                if restored_roles_list:
                                    restored_count += len(restored_roles_list)
                                    
                                    try:
                                        embed = discord.Embed(
                                            title=f"🔄 **РОЛИ ВОЗВРАЩЕНЫ**",
                                            description=f"Вам возвращены роли после истечения временной роли **{temp_role.name}**",
                                            color=0x3498db
                                        )
                                        if restored_roles_list:
                                            embed.add_field(
                                                name="📋 Возвращённые роли",
                                                value="\n".join([f"• {role}" for role in restored_roles_list[:5]]) + 
                                                      ("..." if len(restored_roles_list) > 5 else ""),
                                                inline=False
                                            )
                                        await member.send(embed=embed)
                                    except:
                                        pass
                            
                            try:
                                log_channel = guild.system_channel or guild.text_channels[0]
                                if log_channel:
                                    embed = discord.Embed(
                                        title=f"⏰ **ВРЕМЕННАЯ РОЛЬ ИСТЕКЛА**",
                                        description=f"У {member.mention} истекла временная роль **{temp_role.name}**",
                                        color=0xffaa00
                                    )
                                    if 'saved_roles' in role_data and role_data['saved_roles']:
                                        embed.add_field(
                                            name="🔄 Роли возвращены",
                                            value=f"Возвращено {len(role_data['saved_roles'])} ролей",
                                            inline=False
                                        )
                                    await log_channel.send(embed=embed)
                            except:
                                pass
                            
                            print(f"⏰ Роль {temp_role.name} удалена у {member.name}, возвращено {len(role_data.get('saved_roles', []))} ролей")
                        except:
                            pass
            
            roles.remove(role_data)
        
        if not roles:
            del temp_roles[user_id]
    
    if removed_count > 0:
        save_temp_roles()
        print(f"⏰ Автоматически удалено {removed_count} временных ролей, возвращено {restored_count} ролей")
    
    return removed_count, restored_count

@tasks.loop(minutes=1)
async def temp_roles_check():
    removed, restored = await check_temp_roles()
    if removed > 0:
        print(f"⏰ Проверка завершена: удалено {removed}, возвращено {restored}")

# ============== ФУНКЦИИ ДЛЯ ПРЕДУПРЕЖДЕНИЙ ==============
def get_user_warns(user_id, guild_id):
    key = f"{guild_id}_{user_id}"
    return warns_data.get(key, [])

def add_warn(user_id, guild_id, moderator_id, reason):
    key = f"{guild_id}_{user_id}"
    
    if key not in warns_data:
        warns_data[key] = []
    
    warn = {
        'id': len(warns_data[key]) + 1,
        'moderator_id': moderator_id,
        'reason': reason,
        'date': datetime.now().isoformat(),
        'timestamp': datetime.now().timestamp()
    }
    
    warns_data[key].append(warn)
    save_warns()
    
    return warn, len(warns_data[key])

def remove_warn(user_id, guild_id, warn_id):
    key = f"{guild_id}_{user_id}"
    
    if key in warns_data:
        warns_data[key] = [w for w in warns_data[key] if w['id'] != warn_id]
        save_warns()
        return True
    return False

def clear_warns(user_id, guild_id):
    key = f"{guild_id}_{user_id}"
    
    if key in warns_data:
        del warns_data[key]
        save_warns()
        return True
    return False

# ============== ФУНКЦИИ ДЛЯ МУТОВ ==============
async def apply_mute(member, reason, duration_minutes, moderator):
    user_id = str(member.id)
    guild = member.guild
    
    for channel in guild.channels:
        try:
            if isinstance(channel, discord.TextChannel):
                await channel.set_permissions(
                    member,
                    send_messages=False,
                    add_reactions=False,
                    reason=f"Мут: {reason}"
                )
            elif isinstance(channel, discord.VoiceChannel):
                await channel.set_permissions(
                    member,
                    speak=False,
                    stream=False,
                    use_voice_activation=False,
                    reason=f"Мут: {reason}"
                )
        except:
            pass
    
    expires = datetime.now().timestamp() + (duration_minutes * 60)
    
    active_mutes[user_id] = {
        'user_id': user_id,
        'user_name': str(member),
        'guild_id': guild.id,
        'moderator_id': moderator.id,
        'moderator_name': str(moderator),
        'reason': reason,
        'duration_minutes': duration_minutes,
        'expires': expires,
        'started': datetime.now().timestamp()
    }
    
    save_mutes()
    return expires

async def remove_mute(member):
    user_id = str(member.id)
    guild = member.guild
    
    for channel in guild.channels:
        try:
            await channel.set_permissions(member, overwrite=None)
        except:
            pass
    
    if user_id in active_mutes:
        del active_mutes[user_id]
        save_mutes()
        return True
    return False

async def check_expired_mutes():
    current_time = datetime.now().timestamp()
    removed_count = 0
    
    for user_id, mute_data in list(active_mutes.items()):
        if current_time > mute_data['expires']:
            for guild in bot.guilds:
                if guild.id == mute_data['guild_id']:
                    member = guild.get_member(int(user_id))
                    if member:
                        await remove_mute(member)
                        
                        try:
                            embed = discord.Embed(
                                title=f"✅ **МУТ ИСТЕК**",
                                description=f"Ваш мут на сервере **{guild.name}** истёк",
                                color=0x00ff00
                            )
                            await member.send(embed=embed)
                        except:
                            pass
                        
                        try:
                            log_channel = guild.system_channel or guild.text_channels[0]
                            embed = discord.Embed(
                                title=f"✅ **МУТ ИСТЕК**",
                                description=f"У {member.mention} истёк мут",
                                color=0x00ff00
                            )
                            await log_channel.send(embed=embed)
                        except:
                            pass
                        
                        removed_count += 1
                        break
    
    return removed_count

@tasks.loop(minutes=1)
async def mutes_check():
    removed = await check_expired_mutes()
    if removed > 0:
        print(f"✅ Автоматически снято {removed} мутов")

async def auto_mute(ctx, member, reason):
    try:
        expires = await apply_mute(member, reason, 60, ctx.author)
        
        embed = discord.Embed(
            title=f"🔇 **АВТОМАТИЧЕСКИЙ МУТ**",
            description=f"{member.mention} получил мут (достигнут лимит предупреждений {MAX_WARNS})",
            color=0xff0000
        )
        embed.add_field(name="📝 Причина", value=f"```{reason}```", inline=False)
        embed.add_field(name="⏰ Длительность", value="1 час", inline=True)
        await ctx.send(embed=embed)
    except:
        pass

# ============== СОБЫТИЯ ==============
# ============== ИСПРАВЛЕННАЯ ФУНКЦИЯ on_ready ==============
@bot.event
async def on_ready():
    print(f'✅ Бот {bot.user} успешно запущен!')
    print(f'✅ Система уровней активна!')
    print(f'✅ Экономика и магазин активны!')
    print(f'✅ Отслеживание голосовых каналов активно!')
    print(f'✅ СИСТЕМА БУСТЕРОВ АКТИВНА! Настроено ролей: {len(BOOST_ROLES)}')
    print(f'✅ СИСТЕМА ВРЕМЕННЫХ РОЛЕЙ АКТИВНА! Активных: {sum(len(roles) for roles in temp_roles.values())}')
    print(f'✅ СИСТЕМА ПРЕДУПРЕЖДЕНИЙ АКТИВНА! Всего предупреждений: {sum(len(warns) for warns in warns_data.values())}')
    print(f'✅ СИСТЕМА МУТОВ АКТИВНА! Активных мутов: {len(active_mutes)}')
    
    # Подсчёт реального количества пользователей на сервере
    total_members = 0
    for guild in bot.guilds:
        total_members += guild.member_count
    
    # Подсчёт пользователей в системе уровней
    users_in_system = len(user_data)
    
    print(f'✅ Всего серверов: {len(bot.guilds)}')
    print(f'✅ Всего пользователей на серверах: {total_members}')
    print(f'✅ Пользователей в системе уровней: {users_in_system}')
    
    temp_roles_check.start()
    mutes_check.start()
    
    # Устанавливаем статус с реальным количеством
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
           name=f" !помощь - список команд"
        )
    )

@bot.event
async def on_message(message):
    if message.author.bot or not message.guild:
        return
    
    user_id = str(message.author.id)
    
    boost_multiplier = get_user_boost(message.author)
    base_xp = random.randint(10, 20)
    xp_gained = int(base_xp * boost_multiplier)
    
    if user_id not in user_data:
        user_data[user_id] = {
            'xp': 0, 'level': 0, 'total_xp': 0, 'voice_xp': 0, 'message_xp': 0,
            'username': str(message.author), 'messages': 0, 'voice_time': 0,
            'coins': 0, 'total_coins_earned': 0, 'items': [],
            'last_message_time': datetime.now().isoformat()
        }
    else:
        for field in ['message_xp', 'voice_xp', 'voice_time', 'coins', 'total_coins_earned', 'items']:
            if field not in user_data[user_id]:
                if field == 'items':
                    user_data[user_id][field] = []
                else:
                    user_data[user_id][field] = 0
    
    old_level = user_data[user_id]['level']
    
    user_data[user_id]['message_xp'] += xp_gained
    user_data[user_id]['total_xp'] += xp_gained
    user_data[user_id]['messages'] += 1
    user_data[user_id]['username'] = str(message.author)
    user_data[user_id]['last_message_time'] = datetime.now().isoformat()
    
    total_xp = user_data[user_id]['message_xp'] + user_data[user_id]['voice_xp']
    user_data[user_id]['total_xp'] = total_xp
    
    new_level, current_xp, xp_needed = calculate_level(total_xp)
    
    if new_level > old_level:
        user_data[user_id]['level'] = new_level
        user_data[user_id]['xp'] = current_xp
        
        coins_reward = get_level_reward(new_level)
        if coins_reward > 0:
            user_data[user_id]['coins'] += coins_reward
            user_data[user_id]['total_coins_earned'] += coins_reward
        
        embed = discord.Embed(title=f"🔴 **ПОВЫШЕНИЕ УРОВНЯ!** 🔴", color=0xff0000)
        embed.set_author(name=message.author.display_name, icon_url=message.author.avatar.url if message.author.avatar else message.author.default_avatar.url)
        
        level_text = f"📊 **Новый уровень:** `{old_level}` → `{new_level}` ⬆️"
        xp_text = f"✨ **Всего опыта:** `{total_xp:,}` XP"
        
        if boost_multiplier > 1.0:
            xp_text += f"\n⚡ **Бустер:** x{boost_multiplier}"
        
        embed.add_field(name="📊 Прогресс", value=level_text, inline=False)
        embed.add_field(name="✨ Достижение", value=xp_text, inline=True)
        
        if coins_reward > 0:
            embed.add_field(name="🎁 **НАГРАДА**", value=f"🪙 **+{coins_reward}** коинов!", inline=True)
        
        phrases = ["Так держать! 🚀", "Ты становишься легендой! ⭐", "Вперёд к новым вершинам! ⛰️", "Невероятный прогресс! 🌟", "Ты в огне! 🔥"]
        embed.set_footer(text=f"💫 {random.choice(phrases)}")
        embed.set_thumbnail(url=message.author.avatar.url if message.author.avatar else message.author.default_avatar.url)
        
        level_up_msg = await message.channel.send(embed=embed)
        await level_up_msg.delete(delay=10)
    
    save_data(user_data)
    await bot.process_commands(message)

# ============== ОБРАБОТЧИК ОШИБОК ==============
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    else:
        await ctx.send(f"❌ Произошла ошибка: {error}")

# ============== КОМАНДА !УР ==============
@bot.command(name='ур', aliases=['уровень', 'профиль', 'stat'])
async def rank_command(ctx, member: discord.Member = None):
    """Показывает статистику пользователя"""
    if member is None:
        member = ctx.author
    
    user_id = str(member.id)
    
    if user_id not in user_data:
        embed = discord.Embed(
            title=f"🔴 Нет данных",
            description=f"{member.mention} ещё не активен на сервере!",
            color=0xff0000
        )
        await ctx.send(embed=embed)
        return
    
    data = user_data[user_id]
    level = data['level']
    total_xp = data['total_xp']
    messages = data['messages']
    voice_time = data.get('voice_time', 0)
    message_xp = data.get('message_xp', 0)
    voice_xp = data.get('voice_xp', 0)
    coins = data.get('coins', 0)
    total_coins = data.get('total_coins_earned', 0)
    items = data.get('items', [])
    
    boost_multiplier = get_user_boost(member)
    
    current_xp = total_xp
    for i in range(level):
        current_xp -= xp_to_next_level(i)
    xp_needed = xp_to_next_level(level)
    
    embed = discord.Embed(title=f"🔴 **ПРОФИЛЬ ПОЛЬЗОВАТЕЛЯ** 🔴", color=0xff0000)
    embed.set_author(name=member.display_name, icon_url=member.avatar.url if member.avatar else member.default_avatar.url)
    embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
    
    stats_text = f"📊 **Уровень:** `{level}`\n"
    stats_text += f"🪙 **Баланс:** `{coins:,}` коинов\n"
    stats_text += f"✨ **Всего опыта:** `{total_xp:,}`\n"
    stats_text += f"💬 **Сообщений:** `{messages:,}`\n"
    stats_text += f"🎤 **Время в войсе:** `{voice_time} мин`"
    
    if boost_multiplier > 1.0:
        stats_text += f"\n⚡ **Активный бустер:** x{boost_multiplier}"
    
    if user_id in temp_roles and temp_roles[user_id]:
        temp_roles_text = ""
        current_time = datetime.now().timestamp()
        for role_data in temp_roles[user_id]:
            role = ctx.guild.get_role(role_data['role_id'])
            if role:
                time_left = role_data['expires'] - current_time
                if time_left > 0:
                    hours = int(time_left // 3600)
                    minutes = int((time_left % 3600) // 60)
                    
                    if hours > 0:
                        time_str = f"{hours} ч {minutes} мин"
                    else:
                        time_str = f"{minutes} мин"
                    
                    temp_roles_text += f"• {role.mention} — осталось {time_str}\n"
        
        if temp_roles_text:
            embed.add_field(name=f"⏰ **ВРЕМЕННЫЕ РОЛИ**", value=temp_roles_text, inline=False)
    
    embed.add_field(name="📊 **ОСНОВНАЯ СТАТИСТИКА**", value=stats_text, inline=False)
    embed.add_field(name=create_separator(30), value="", inline=False)
    
    progress_bar = create_progress_bar(current_xp, xp_needed, 20)
    progress_text = f"**{current_xp:,} / {xp_needed:,}** XP\n{progress_bar}"
    embed.add_field(name=f"📈 **ПРОГРЕСС ДО {level + 1} УРОВНЯ**", value=progress_text, inline=False)
    embed.add_field(name=create_separator(30), value="", inline=False)
    
    details = f"💬 **За сообщения:** `{message_xp:,}`\n"
    details += f"🎤 **За войс:** `{voice_xp:,}`\n"
    details += f"💰 **Всего заработано:** `{total_coins:,}` коинов"
    embed.add_field(name="✨ **ДЕТАЛИ**", value=details, inline=True)
    
    if items:
        items_text = ""
        for item_id in items[:5]:
            if item_id in shop_data:
                items_text += f"• {shop_data[item_id]['name']}\n"
        if len(items) > 5:
            items_text += f"... и ещё {len(items) - 5}"
        embed.add_field(name="📦 **ИНВЕНТАРЬ**", value=items_text, inline=True)
    else:
        embed.add_field(name="📦 **ИНВЕНТАРЬ**", value="Пусто", inline=True)
    
    embed.add_field(name=create_separator(30), value="", inline=False)
    
    user_info = f"🆔 **ID:** `{member.id}`\n"
    user_info += f"📅 **Присоединился:** {member.joined_at.strftime('%d.%m.%Y') if member.joined_at else 'Неизвестно'}"
    embed.add_field(name="👤 **ИНФОРМАЦИЯ**", value=user_info, inline=False)
    
    embed.set_footer(text=f"⚡ Запрошено: {ctx.author.display_name}", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
    embed.timestamp = datetime.now()
    
    await ctx.send(embed=embed)

# ============== КОМАНДА !БАЛ ==============
@bot.command(name='бал', aliases=['коины', 'баланс', 'balance', 'coins'])
async def balance_command(ctx, member: discord.Member = None):
    """Показывает баланс коинов"""
    if member is None:
        member = ctx.author
    
    user_id = str(member.id)
    
    if user_id not in user_data:
        user_data[user_id] = {'coins': 0, 'total_coins_earned': 0, 'username': str(member), 'items': [], 'level': 0}
    
    coins = user_data[user_id].get('coins', 0)
    total_earned = user_data[user_id].get('total_coins_earned', 0)
    
    embed = discord.Embed(title=f"💰 **БАЛАНС ПОЛЬЗОВАТЕЛЯ**", color=0xff0000)
    embed.set_author(name=member.display_name, icon_url=member.avatar.url if member.avatar else member.default_avatar.url)
    embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
    
    embed.add_field(name="🪙 **Текущий баланс**", value=f"**{coins:,}** коинов", inline=False)
    embed.add_field(name="📊 **Всего заработано**", value=f"**{total_earned:,}** коинов", inline=False)
    
    next_reward = None
    for lvl in sorted(COINS_PER_LEVEL_UP.keys()):
        if lvl > user_data[user_id].get('level', 0):
            next_reward = (lvl, COINS_PER_LEVEL_UP[lvl])
            break
    
    if next_reward:
        embed.add_field(
            name="🎯 **СЛЕДУЮЩАЯ НАГРАДА**", 
            value=f"На {next_reward[0]} уровне: **+{next_reward[1]}** коинов",
            inline=False
        )
    
    embed.set_footer(text=f"⚡ Чем выше уровень, тем больше награда!")
    await ctx.send(embed=embed)

# ============== КОМАНДА !МАГАЗИН ==============
@bot.command(name='магазин', aliases=['shop', 'store', 'market'])
async def shop_command(ctx, page: int = 1):
    """Показывает магазин предметов"""
    if not shop_data:
        embed = discord.Embed(
            title=f"🏪 **МАГАЗИН ПРЕДМЕТОВ**", 
            description=f"📦 В магазине пока нет товаров!", 
            color=0xff0000
        )
        await ctx.send(embed=embed)
        return
    
    sorted_items = sorted(shop_data.items(), key=lambda x: x[1]['price'])
    
    items_per_page = 5
    total_pages = math.ceil(len(sorted_items) / items_per_page)
    page = max(1, min(page, total_pages))
    
    start_idx = (page - 1) * items_per_page
    end_idx = start_idx + items_per_page
    page_items = sorted_items[start_idx:end_idx]
    
    embed = discord.Embed(
        title=f"🏪 **МАГАЗИН ПРЕДМЕТОВ**",
        description=f"Страница {page}/{total_pages} • Всего товаров: {len(shop_data)}",
        color=0xff0000
    )
    
    for idx, (item_id, item) in enumerate(page_items, 1):
        if 'duration' in item:
            category_emoji = "⏰"
        elif item.get('price', 0) > 1000:
            category_emoji = "✨"
        elif 'role_id' in item:
            category_emoji = "👑"
        else:
            category_emoji = "📦"
        
        item_text = f"**{category_emoji} {item['name']}**\n"
        item_text += f"└─ 🆔 `{item_id}`\n"
        item_text += f"└─ 📝 {item.get('description', 'Нет описания')}\n"
        
        if 'role_id' in item:
            role = ctx.guild.get_role(item['role_id'])
            if role:
                item_text += f"└─ 👑 Роль: {role.mention}\n"
                
                if role.id in BOOST_ROLES:
                    boost_mult = BOOST_ROLES[role.id]
                    item_text += f"└─ ⚡ Бустер: x{boost_mult}\n"
        
        if 'duration' in item:
            duration = item['duration']
            time_str = format_time(duration)
            item_text += f"└─ ⏰ Длительность: {time_str}\n"
        
        item_text += f"└─ 💰 Цена: {item['price']} 🪙\n"
        
        user_id = str(ctx.author.id)
        
        if 'duration' in item:
            is_active = False
            time_left = 0
            
            if user_id in temp_roles:
                for record in temp_roles[user_id]:
                    if 'role_id' in item and record.get('role_id') == item.get('role_id'):
                        is_active = True
                        current_time = datetime.now().timestamp()
                        time_left = record['expires'] - current_time
                        if time_left < 0:
                            is_active = False
                        break
            
            if is_active and time_left > 0:
                if time_left < 3600:
                    time_str = f"{int(time_left/60)} мин"
                elif time_left < 86400:
                    time_str = f"{int(time_left/3600)} ч"
                else:
                    time_str = f"{int(time_left/86400)} дн"
                item_text += f"└─ ⏳ **Действует:** осталось {time_str}\n"
            else:
                item_text += f"└─ ⏳ **Действует:** `0/∞`\n"
        else:
            has_item = user_id in user_data and item_id in user_data[user_id].get('items', [])
            if has_item:
                item_text += f"└─ ✅ **УЖЕ КУПЛЕНО**\n"
            else:
                item_text += f"└─ 🛒 Введите `!купить {item_id}`\n"
        
        embed.add_field(name=f"━━━━━━━━━━━━━━━━━━", value=item_text, inline=False)
    
    legend = (
        "⏰ - Временный товар\n"
        "👑 - Товар с ролью\n"
        "⚡ - Даёт бустер опыта\n"
        "✨ - Особый товар\n"
        "📦 - Обычный товар\n"
        "⏳ `0/∞` - Нет активной временной роли"
    )
    embed.add_field(name="📋 **ЛЕГЕНДА**", value=legend, inline=False)
    
    embed.set_footer(text=f"🛒 Используй !купить [ID] для покупки • Временные предметы можно покупать несколько раз")
    embed.timestamp = datetime.now()
    
    await ctx.send(embed=embed)

# ============== КОМАНДА !КУПИТЬ ==============
@bot.command(name='купить', aliases=['buy'])
async def buy_command(ctx, item_id: str):
    """Покупает предмет из магазина и выдаёт роль (возможно временную)"""
    if item_id not in shop_data:
        embed = discord.Embed(
            title=f"🔴 **ОШИБКА**",
            description=f"Товар с ID `{item_id}` не найден!",
            color=0xff0000
        )
        await ctx.send(embed=embed)
        return
    
    user_id = str(ctx.author.id)
    
    if user_id not in user_data:
        user_data[user_id] = {'coins': 0, 'total_coins_earned': 0, 'username': str(ctx.author), 'items': [], 'level': 0}
    
    item = shop_data[item_id]
    price = item['price']
    
    if user_data[user_id].get('coins', 0) < price:
        embed = discord.Embed(
            title=f"🔴 **ОШИБКА**", 
            description=f"Недостаточно коинов! Нужно: **{price}**, у тебя: **{user_data[user_id].get('coins', 0)}**", 
            color=0xff0000
        )
        await ctx.send(embed=embed)
        return
    
    role_given = None
    boost_info = ""
    duration_info = ""
    time_added = 0
    total_time = 0
    
    if 'role_id' in item:
        role = ctx.guild.get_role(item['role_id'])
        if role:
            try:
                role_already_had = role in ctx.author.roles
                
                await ctx.author.add_roles(role, reason=f"Покупка в магазине")
                role_given = role.name
                
                if role.id in BOOST_ROLES:
                    boost_mult = BOOST_ROLES[role.id]
                    boost_info = f"\n⚡ **Бустер:** x{boost_mult} к опыту"
                
                if 'duration' in item:
                    duration_minutes = item['duration']
                    current_time = datetime.now().timestamp()
                    
                    if user_id not in temp_roles:
                        temp_roles[user_id] = []
                    
                    existing_record = None
                    for record in temp_roles[user_id]:
                        if record.get('role_id') == role.id:
                            existing_record = record
                            break
                    
                    if existing_record:
                        old_expires = existing_record['expires']
                        time_left = old_expires - current_time
                        
                        if time_left > 0:
                            new_expires = current_time + time_left + (duration_minutes * 60)
                            time_added = duration_minutes
                            total_time = int((new_expires - current_time) / 60)
                        else:
                            new_expires = current_time + (duration_minutes * 60)
                            time_added = duration_minutes
                            total_time = duration_minutes
                        
                        existing_record['expires'] = new_expires
                    else:
                        new_expires = current_time + (duration_minutes * 60)
                        time_added = duration_minutes
                        total_time = duration_minutes
                        
                        temp_roles[user_id].append({
                            'role_id': role.id,
                            'expires': new_expires,
                            'item_id': item_id,
                            'saved_roles': []
                        })
                    
                    save_temp_roles()
                    
                    if time_added < 60:
                        added_str = f"{time_added} мин"
                    elif time_added < 1440:
                        added_str = f"{time_added//60} ч"
                    else:
                        added_str = f"{time_added//1440} дн"
                    
                    if total_time < 60:
                        total_str = f"{total_time} мин"
                    elif total_time < 1440:
                        total_str = f"{total_time//60} ч"
                    else:
                        total_str = f"{total_time//1440} дн"
                    
                    if existing_record and time_left > 0:
                        duration_info = f"\n⏰ **Добавлено:** +{added_str}\n⏳ **Теперь всего:** {total_str}"
                    else:
                        duration_info = f"\n⏰ **Длительность:** {added_str}"
                    
                    try:
                        expire_time = datetime.fromtimestamp(new_expires).strftime("%d.%m.%Y %H:%M")
                        dm_embed = discord.Embed(
                            title=f"⏰ **ВРЕМЕННАЯ РОЛЬ**",
                            description=f"Ты получил роль **{role.name}**",
                            color=0x3498db
                        )
                        if existing_record and time_left > 0:
                            dm_embed.add_field(name="⏳ Добавлено времени", value=added_str, inline=True)
                            dm_embed.add_field(name="⏰ Теперь до", value=expire_time, inline=True)
                        else:
                            dm_embed.add_field(name="⏰ Действует до", value=expire_time, inline=True)
                        
                        await ctx.author.send(embed=dm_embed)
                    except:
                        pass
                    
            except discord.Forbidden:
                role_given = "ОШИБКА: Нет прав на выдачу роли"
            except Exception as e:
                role_given = f"ОШИБКА: {e}"
        else:
            role_given = "ОШИБКА: Роль не найдена на сервере"
    
    if role_given and "ОШИБКА" not in role_given:
        user_data[user_id]['coins'] -= price
        if 'items' not in user_data[user_id]:
            user_data[user_id]['items'] = []
        
        if 'duration' not in item:
            user_data[user_id]['items'].append(item_id)
        
        save_data(user_data)
        
        if user_id in user_boost_cache:
            del user_boost_cache[user_id]
        
        embed = discord.Embed(
            title=f"✅ **ПОКУПКА УСПЕШНА**",
            color=0x00ff00
        )
        
        embed.add_field(name="🎁 Товар", value=f"**{item['name']}**", inline=True)
        embed.add_field(name="💰 Потрачено", value=f"**{price}** 🪙", inline=True)
        embed.add_field(name="🪙 Остаток", value=f"**{user_data[user_id]['coins']}** 🪙", inline=True)
        
        if role_given:
            embed.add_field(name=f"👑 Получена роль", value=f"**{role_given}**{boost_info}{duration_info}", inline=False)
        
        embed.set_footer(text=f"Спасибо за покупку! 🎉")
        embed.timestamp = datetime.now()
        
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(
            title=f"❌ **ОШИБКА ПРИ ВЫДАЧЕ**",
            description=f"Произошла ошибка: {role_given}\n\nКоины не списаны!",
            color=0xff0000
        )
        await ctx.send(embed=embed)

# ============== КОМАНДА !ИНВЕНТАРЬ ==============
@bot.command(name='инвентарь', aliases=['inv', 'items'])
async def inventory_command(ctx, member: discord.Member = None):
    """Показывает инвентарь пользователя"""
    if member is None:
        member = ctx.author
    
    user_id = str(member.id)
    current_time = datetime.now().timestamp()
    
    items_to_remove = []
    if user_id in user_data and 'items' in user_data[user_id]:
        for item_id in user_data[user_id]['items']:
            if item_id in shop_data and 'duration' in shop_data[item_id]:
                is_active = False
                if user_id in temp_roles:
                    for record in temp_roles[user_id]:
                        if 'role_id' in shop_data[item_id] and record.get('role_id') == shop_data[item_id].get('role_id'):
                            if record['expires'] > current_time:
                                is_active = True
                                break
                
                if not is_active:
                    items_to_remove.append(item_id)
        
        if items_to_remove:
            user_data[user_id]['items'] = [item for item in user_data[user_id]['items'] if item not in items_to_remove]
            save_data(user_data)
    
    items = user_data[user_id].get('items', []) if user_id in user_data else []
    
    if not items:
        embed = discord.Embed(
            title=f"📦 **ИНВЕНТАРЬ**",
            description=f"У {member.mention} пока нет предметов!",
            color=0xff0000
        )
        await ctx.send(embed=embed)
        return
    
    embed = discord.Embed(
        title=f"📦 **ИНВЕНТАРЬ {member.display_name}**",
        color=0xff0000
    )
    embed.set_author(name=member.display_name, icon_url=member.avatar.url if member.avatar else member.default_avatar.url)
    
    item_groups = {}
    
    for item_id in items:
        if item_id in shop_data:
            item = shop_data[item_id]
            if 'role_id' in item:
                role_id = item['role_id']
                if role_id not in item_groups:
                    item_groups[role_id] = {
                        'item_id': item_id,
                        'item_data': item,
                        'count': 0,
                        'active_count': 0
                    }
            else:
                if item_id not in item_groups:
                    item_groups[item_id] = {
                        'item_id': item_id,
                        'item_data': item,
                        'count': 1,
                        'active_count': 0,
                        'no_role': True
                    }
    
    if user_id in temp_roles:
        for record in temp_roles[user_id]:
            if record['expires'] > current_time:
                role_id = record.get('role_id')
                if role_id and role_id in item_groups:
                    item_groups[role_id]['active_count'] += 1
    
    items_text = ""
    active_count_total = 0
    
    for role_id, group in item_groups.items():
        item = group['item_data']
        
        if group.get('no_role'):
            items_text += f"• **{item['name']}** - {item.get('description', 'Нет описания')}\n"
        else:
            role = ctx.guild.get_role(role_id)
            if role:
                items_text += f"• **{item['name']}** - {item.get('description', 'Нет описания')}\n"
                items_text += f"  └─ 👑 Роль: {role.mention}"
                
                if role.id in BOOST_ROLES:
                    boost_mult = BOOST_ROLES[role.id]
                    items_text += f" ⚡ x{boost_mult}"
                
                if group['active_count'] > 0:
                    items_text += f" **(x{group['active_count']})**"
                    active_count_total += group['active_count']
                
                items_text += f"\n"
            else:
                items_text += f"• **{item['name']}** - {item.get('description', 'Нет описания')}\n"
                items_text += f"  └─ 👑 Роль: Не найдена\n"
    
    embed.description = items_text
    
    if user_id in temp_roles and temp_roles[user_id]:
        temp_roles_text = "\n**⏰ АКТИВНЫЕ ВРЕМЕННЫЕ РОЛИ:**\n"
        active_count_total = 0
        
        for record in temp_roles[user_id]:
            if record['expires'] > current_time:
                role = ctx.guild.get_role(record['role_id'])
                if role:
                    time_left = record['expires'] - current_time
                    if time_left < 3600:
                        time_str = f"{int(time_left/60)} мин"
                    elif time_left < 86400:
                        time_str = f"{int(time_left/3600)} ч"
                    else:
                        time_str = f"{int(time_left/86400)} дн"
                    
                    temp_roles_text += f"  • {role.mention} — осталось {time_str}\n"
                    active_count_total += 1
        
        if active_count_total > 0:
            embed.add_field(name="━━━━━━━━━━━━━━━━━━", value=temp_roles_text, inline=False)
    
    embed.set_footer(text=f"📊 Всего предметов: {len(items)} • Активных временных ролей: {active_count_total}")
    await ctx.send(embed=embed)

# ============== КОМАНДА !ТОПЫ ==============
@bot.command(name='топы', aliases=['топ', 'лидеры', 'leaderboard', 'top'])
async def leaderboard_command(ctx, page: int = 1):
    """Показывает таблицу лидеров"""
    sorted_users = sorted(user_data.items(), key=lambda x: (x[1].get('level', 0), x[1].get('total_xp', 0)), reverse=True)
    
    items_per_page = 10
    total_pages = math.ceil(len(sorted_users) / items_per_page)
    page = max(1, min(page, total_pages))
    
    start_idx = (page - 1) * items_per_page
    end_idx = start_idx + items_per_page
    page_users = sorted_users[start_idx:end_idx]
    
    embed = discord.Embed(
        title=f"🏆 **ТАБЛИЦА ЛИДЕРОВ**",
        description=f"Страница {page}/{total_pages}",
        color=0xff0000
    )
    
    top_text = ""
    for i, (user_id, data) in enumerate(page_users, start=start_idx + 1):
        member = ctx.guild.get_member(int(user_id))
        username = member.display_name if member else data.get('username', 'Неизвестный')
        
        if len(username) > 20:
            username = username[:17] + "..."
        
        if i == 1:
            medal = "🥇"
        elif i == 2:
            medal = "🥈"
        elif i == 3:
            medal = "🥉"
        else:
            medal = f"{i}."
        
        voice_time = data.get('voice_time', 0)
        messages = data.get('messages', 0)
        coins = data.get('coins', 0)
        level = data.get('level', 0)
        
        top_text += f"{medal} **{username}**\n"
        top_text += f"  └─ Ур.{level} | 🪙{coins} | 💬{messages} | 🎤{voice_time}мин\n\n"
    
    embed.description = top_text
    embed.set_footer(text=f"📊 Всего участников: {len(sorted_users)}")
    
    await ctx.send(embed=embed)

# ============== КОМАНДА !ВРЕМЕННЫЕ ==============
@bot.command(name='временные', aliases=['temp', 'время'])
async def temp_roles_command(ctx, member: discord.Member = None):
    """Показывает временные роли пользователя"""
    if member is None:
        member = ctx.author
    
    user_id = str(member.id)
    
    if user_id not in temp_roles or not temp_roles[user_id]:
        embed = discord.Embed(
            title=f"⏰ **ВРЕМЕННЫЕ РОЛИ**",
            description=f"У {member.mention} нет временных ролей",
            color=0xff0000
        )
        await ctx.send(embed=embed)
        return
    
    embed = discord.Embed(
        title=f"⏰ **ВРЕМЕННЫЕ РОЛИ {member.display_name}**",
        color=0x3498db
    )
    embed.set_author(name=member.display_name, icon_url=member.avatar.url if member.avatar else member.default_avatar.url)
    
    current_time = datetime.now().timestamp()
    roles_text = ""
    
    for role_data in temp_roles[user_id]:
        role = ctx.guild.get_role(role_data['role_id'])
        if role:
            time_left = role_data['expires'] - current_time
            if time_left > 0:
                hours = int(time_left // 3600)
                minutes = int((time_left % 3600) // 60)
                
                if hours > 0:
                    time_str = f"{hours} ч {minutes} мин"
                else:
                    time_str = f"{minutes} мин"
                
                expire_time = datetime.fromtimestamp(role_data['expires']).strftime("%d.%m.%Y %H:%M")
                roles_text += f"• {role.mention}\n  └─ Осталось: **{time_str}** (до {expire_time})\n"
                
                if 'saved_roles' in role_data and role_data['saved_roles']:
                    roles_text += f"  └─ 💾 Будет возвращено ролей: {len(role_data['saved_roles'])}\n"
            else:
                roles_text += f"• {role.mention}\n  └─ **Истекла** (будет удалена)\n"
    
    if roles_text:
        embed.description = roles_text
    else:
        embed.description = "Нет активных временных ролей"
    
    await ctx.send(embed=embed)

# ============== КОМАНДА !ВОЙС ==============
@bot.command(name='войс', aliases=['voice', 'вс'])
async def voice_stats_command(ctx, member: discord.Member = None):
    """Показывает статистику по голосовым каналам"""
    if member is None:
        member = ctx.author
    
    user_id = str(member.id)
    
    if user_id not in user_data:
        embed = discord.Embed(
            title=f"🔴 Нет данных", 
            description=f"{member.mention} ещё не был в голосовых каналах!", 
            color=0xff0000
        )
        await ctx.send(embed=embed)
        return
    
    data = user_data[user_id]
    voice_time = data.get('voice_time', 0)
    voice_xp = data.get('voice_xp', 0)
    
    in_voice = False
    current_session_time = 0
    if user_id in voice_tracking:
        in_voice = True
        join_time = voice_tracking[user_id]["join_time"]
        current_session_time = int((datetime.now() - join_time).total_seconds() / 60)
    
    embed = discord.Embed(
        title=f"🔴 **ГОЛОСОВАЯ СТАТИСТИКА** 🔴",
        color=0xff0000
    )
    embed.set_author(name=member.display_name, icon_url=member.avatar.url if member.avatar else member.default_avatar.url)
    
    stats_text = f"⏱️ **Всего в войсе:** `{voice_time}` минут\n"
    stats_text += f"✨ **Опыта за войс:** `{voice_xp:,}` XP\n"
    hours = voice_time // 60
    minutes = voice_time % 60
    stats_text += f"⏰ **Это:** `{hours}ч {minutes}м`\n"
    
    embed.add_field(name="📊 **СТАТИСТИКА**", value=stats_text, inline=False)
    embed.add_field(name=create_separator(30), value="", inline=False)
    
    if in_voice:
        session_text = f"🔊 **Текущая сессия:** `{current_session_time}` минут\n"
        if current_session_time > 0:
            session_bonus = current_session_time * XP_PER_VOICE_MINUTE
            session_text += f"└─ ⚡ Заработано сейчас: `+{session_bonus}` XP"
        embed.add_field(name="🎤 **ТЕКУЩАЯ СЕССИЯ**", value=session_text, inline=False)
        embed.add_field(name=create_separator(30), value="", inline=False)
    
    all_voice_times = [d.get('voice_time', 0) for d in user_data.values()]
    if all_voice_times:
        avg_voice = sum(all_voice_times) / len(all_voice_times)
        if voice_time > avg_voice:
            comparison = f"⬆️ **Выше среднего** на `{voice_time - avg_voice:.0f}` мин"
        else:
            comparison = f"⬇️ **Ниже среднего** на `{avg_voice - voice_time:.0f}` мин"
        embed.add_field(name="📈 **СРАВНЕНИЕ**", value=comparison, inline=False)
        embed.add_field(name=create_separator(30), value="", inline=False)
    
    next_goal = (voice_time // 60 + 1) * 60
    if next_goal > voice_time:
        goal_progress = create_progress_bar(voice_time, next_goal, 15)
        embed.add_field(
            name="🎯 **ЦЕЛЬ**", 
            value=f"До {next_goal} минут:\n{goal_progress}", 
            inline=False
        )
    
    embed.set_footer(text=f"⚡ {XP_PER_VOICE_MINUTE} XP за минуту в войсе")
    await ctx.send(embed=embed)

# ============== КОМАНДА !ПРЕД ==============
@bot.command(name='пред', aliases=['warn'])
@commands.has_permissions(administrator=True)
async def warn_command(ctx, member: discord.Member = None, *, reason: str = "Не указана"):
    """Выдать предупреждение пользователю"""
    if member is None and ctx.message.reference:
        referenced_msg = await ctx.channel.fetch_message(ctx.message.reference.message_id)
        member = referenced_msg.author
    
    if member is None:
        embed = discord.Embed(
            title=f"❌ **ОШИБКА**",
            description=f"Укажи пользователя: `!пред @пользователь причина`\nИли ответь на сообщение: `!пред причина`",
            color=0xff0000
        )
        await ctx.send(embed=embed)
        return
    
    if member == ctx.author:
        embed = discord.Embed(
            title=f"❌ **ОШИБКА**",
            description=f"Нельзя выдать предупреждение самому себе!",
            color=0xff0000
        )
        await ctx.send(embed=embed)
        return
    
    if member.bot:
        embed = discord.Embed(
            title=f"❌ **ОШИБКА**",
            description=f"Нельзя выдавать предупреждения ботам!",
            color=0xff0000
        )
        await ctx.send(embed=embed)
        return
    
    warn, total_warns = add_warn(member.id, ctx.guild.id, ctx.author.id, reason)
    
    embed = discord.Embed(
        title=f"⚠️ **ПРЕДУПРЕЖДЕНИЕ ВЫДАНО**",
        description=f"Пользователю {member.mention} выдано предупреждение",
        color=0xffaa00
    )
    
    embed.add_field(name="👤 Пользователь", value=member.mention, inline=True)
    embed.add_field(name="🔢 Предупреждение", value=f"**#{warn['id']}**", inline=True)
    embed.add_field(name="📊 Всего предупреждений", value=f"**{total_warns}/{MAX_WARNS}**", inline=True)
    embed.add_field(name="📝 Причина", value=f"```{reason}```", inline=False)
    embed.add_field(name="👑 Модератор", value=ctx.author.mention, inline=True)
    
    embed.set_footer(text=f"ID предупреждения: {warn['id']} • {datetime.now().strftime('%d.%m.%Y %H:%M')}")
    
    await ctx.send(embed=embed)
    
    try:
        dm_embed = discord.Embed(
            title=f"⚠️ **ПРЕДУПРЕЖДЕНИЕ**",
            description=f"Вы получили предупреждение на сервере **{ctx.guild.name}**",
            color=0xffaa00
        )
        dm_embed.add_field(name="🔢 Предупреждение", value=f"**#{warn['id']}**", inline=True)
        dm_embed.add_field(name="📊 Всего предупреждений", value=f"**{total_warns}/{MAX_WARNS}**", inline=True)
        dm_embed.add_field(name="📝 Причина", value=f"```{reason}```", inline=False)
        dm_embed.add_field(name="👑 Модератор", value=ctx.author.name, inline=True)
        
        await member.send(embed=dm_embed)
    except:
        pass
    
    if total_warns >= MAX_WARNS:
        if ACTION_ON_MAX_WARNS == "mute":
            await auto_mute(ctx, member, reason)

# ============== КОМАНДА !ПРЕДЫ ==============
@bot.command(name='преды', aliases=['warns', 'предупреждения'])
@commands.has_permissions(administrator=True)
async def warns_command(ctx, member: discord.Member = None):
    """Показать предупреждения пользователя"""
    if member is None:
        member = ctx.author
    
    user_warns = get_user_warns(member.id, ctx.guild.id)
    
    if not user_warns:
        embed = discord.Embed(
            title=f"📋 **ПРЕДУПРЕЖДЕНИЯ**",
            description=f"У {member.mention} нет предупреждений",
            color=0x00ff00
        )
        await ctx.send(embed=embed)
        return
    
    embed = discord.Embed(
        title=f"📋 **ПРЕДУПРЕЖДЕНИЯ {member.display_name}**",
        description=f"Всего: **{len(user_warns)}** / {MAX_WARNS}",
        color=0xffaa00
    )
    embed.set_author(name=member.display_name, icon_url=member.avatar.url if member.avatar else member.default_avatar.url)
    
    warns_text = ""
    for warn in user_warns[-5:]:
        moderator = ctx.guild.get_member(warn['moderator_id'])
        mod_name = moderator.name if moderator else "Неизвестно"
        
        date = datetime.fromisoformat(warn['date']).strftime("%d.%m.%Y %H:%M")
        warns_text += f"**#{warn['id']}** | {date}\n"
        warns_text += f"└─ Модератор: {mod_name}\n"
        warns_text += f"└─ Причина: {warn['reason']}\n\n"
    
    embed.description = warns_text
    
    if len(user_warns) > 5:
        embed.set_footer(text=f"Показано последние 5 из {len(user_warns)} предупреждений")
    
    await ctx.send(embed=embed)

# ============== КОМАНДА !СНЯТЬПРЕД ==============
@bot.command(name='снятьпред', aliases=['unwarn', 'removewarn'])
@commands.has_permissions(administrator=True)
async def unwarn_command(ctx, member: discord.Member, warn_id: int):
    """Снять предупреждение по ID"""
    if remove_warn(member.id, ctx.guild.id, warn_id):
        embed = discord.Embed(
            title=f"✅ **ПРЕДУПРЕЖДЕНИЕ СНЯТО**",
            description=f"У {member.mention} снято предупреждение #{warn_id}",
            color=0x00ff00
        )
        embed.add_field(name="👑 Модератор", value=ctx.author.mention, inline=True)
        await ctx.send(embed=embed)
        
        try:
            dm_embed = discord.Embed(
                title=f"✅ **ПРЕДУПРЕЖДЕНИЕ СНЯТО**",
                description=f"На сервере **{ctx.guild.name}** с вас снято предупреждение #{warn_id}",
                color=0x00ff00
            )
            await member.send(embed=dm_embed)
        except:
            pass
    else:
        embed = discord.Embed(
            title=f"❌ **ОШИБКА**",
            description=f"Предупреждение #{warn_id} не найдено у {member.mention}",
            color=0xff0000
        )
        await ctx.send(embed=embed)

# ============== КОМАНДА !ОЧИСТИТЬПРЕДЫ ==============
@bot.command(name='очиститьпреды', aliases=['clearwarns'])
@commands.has_permissions(administrator=True)
async def clear_warns_command(ctx, member: discord.Member):
    """Удалить все предупреждения пользователя"""
    if clear_warns(member.id, ctx.guild.id):
        embed = discord.Embed(
            title=f"✅ **ВСЕ ПРЕДУПРЕЖДЕНИЯ УДАЛЕНЫ**",
            description=f"У {member.mention} удалены все предупреждения",
            color=0x00ff00
        )
        embed.add_field(name="👑 Модератор", value=ctx.author.mention, inline=True)
        await ctx.send(embed=embed)
        
        try:
            dm_embed = discord.Embed(
                title=f"✅ **ПРЕДУПРЕЖДЕНИЯ УДАЛЕНЫ**",
                description=f"На сервере **{ctx.guild.name}** с вас удалены все предупреждения",
                color=0x00ff00
            )
            await member.send(embed=dm_embed)
        except:
            pass
    else:
        embed = discord.Embed(
            title=f"ℹ️ **НЕТ ПРЕДУПРЕЖДЕНИЙ**",
            description=f"У {member.mention} нет предупреждений",
            color=0xffaa00
        )
        await ctx.send(embed=embed)

# ============== КОМАНДА !МУТ ==============
@bot.command(name='мут', aliases=['mute'])
@commands.has_permissions(administrator=True)
async def mute_command(ctx, member: discord.Member = None, duration: str = None, *, reason: str = "Не указана"):
    """Замутить пользователя на время"""
    if member is None and ctx.message.reference:
        referenced_msg = await ctx.channel.fetch_message(ctx.message.reference.message_id)
        member = referenced_msg.author
        
        if duration is None and reason != "Не указана":
            parts = reason.split(' ', 1)
            if len(parts) > 1 and parts[0][-1] in ['м', 'ч', 'д']:
                duration = parts[0]
                reason = parts[1]
    
    if member is None:
        embed = discord.Embed(
            title=f"❌ **ОШИБКА**",
            description=f"Укажи пользователя: `!мут @пользователь время причина`\nПример: `!мут @User 1ч Спам`",
            color=0xff0000
        )
        await ctx.send(embed=embed)
        return
    
    if duration is None:
        embed = discord.Embed(
            title=f"❌ **ОШИБКА**",
            description=f"Укажи время мута! Пример: `30м`, `2ч`, `1д`",
            color=0xff0000
        )
        await ctx.send(embed=embed)
        return
    
    if member == ctx.author:
        embed = discord.Embed(
            title=f"❌ **ОШИБКА**",
            description=f"Нельзя замутить самого себя!",
            color=0xff0000
        )
        await ctx.send(embed=embed)
        return
    
    if member.bot:
        embed = discord.Embed(
            title=f"❌ **ОШИБКА**",
            description=f"Нельзя мутить ботов!",
            color=0xff0000
        )
        await ctx.send(embed=embed)
        return
    
    duration = duration.lower()
    minutes = 0
    
    try:
        if duration.endswith('м'):
            minutes = int(duration[:-1])
        elif duration.endswith('ч'):
            minutes = int(duration[:-1]) * 60
        elif duration.endswith('д'):
            minutes = int(duration[:-1]) * 1440
        else:
            minutes = int(duration)
    except:
        embed = discord.Embed(
            title=f"❌ **ОШИБКА**",
            description=f"Неправильный формат времени! Используй: `30м`, `2ч`, `1д`",
            color=0xff0000
        )
        await ctx.send(embed=embed)
        return
    
    if minutes <= 0:
        embed = discord.Embed(
            title=f"❌ **ОШИБКА**",
            description=f"Время должно быть положительным!",
            color=0xff0000
        )
        await ctx.send(embed=embed)
        return
    
    if minutes > 43200:
        embed = discord.Embed(
            title=f"❌ **ОШИБКА**",
            description=f"Максимальная длительность мута - 30 дней!",
            color=0xff0000
        )
        await ctx.send(embed=embed)
        return
    
    try:
        expires = await apply_mute(member, reason, minutes, ctx.author)
        
        if minutes < 60:
            time_str = f"{minutes} мин"
        elif minutes < 1440:
            time_str = f"{minutes//60} ч"
        else:
            time_str = f"{minutes//1440} дн"
        
        expire_time = datetime.fromtimestamp(expires).strftime("%d.%m.%Y %H:%M")
        
        embed = discord.Embed(
            title=f"🔇 **МУТ ВЫДАН**",
            description=f"Пользователю {member.mention} выдан мут",
            color=0xff0000
        )
        
        embed.add_field(name="👤 Пользователь", value=member.mention, inline=True)
        embed.add_field(name="⏰ Длительность", value=time_str, inline=True)
        embed.add_field(name="📅 Истекает", value=expire_time, inline=True)
        embed.add_field(name="📝 Причина", value=f"```{reason}```", inline=False)
        embed.add_field(name="👑 Модератор", value=ctx.author.mention, inline=True)
        
        embed.set_footer(text=f"Мут без роли • Все каналы заблокированы")
        embed.timestamp = datetime.now()
        
        await ctx.send(embed=embed)
        
        try:
            dm_embed = discord.Embed(
                title=f"🔇 **МУТ**",
                description=f"Вам выдан мут на сервере **{ctx.guild.name}**",
                color=0xff0000
            )
            dm_embed.add_field(name="⏰ Длительность", value=time_str, inline=True)
            dm_embed.add_field(name="📅 Истекает", value=expire_time, inline=True)
            dm_embed.add_field(name="📝 Причина", value=f"```{reason}```", inline=False)
            dm_embed.add_field(name="👑 Модератор", value=ctx.author.name, inline=True)
            dm_embed.set_footer(text="Вы не сможете писать в чатах и говорить в войсе")
            
            await member.send(embed=dm_embed)
        except:
            pass
        
    except discord.Forbidden:
        embed = discord.Embed(
            title=f"❌ **ОШИБКА**",
            description=f"У бота нет прав на изменение прав в каналах!\nПроверь, что у бота есть право 'Управлять каналами'",
            color=0xff0000
        )
        await ctx.send(embed=embed)
    except Exception as e:
        embed = discord.Embed(
            title=f"❌ **ОШИБКА**",
            description=f"Произошла ошибка: {e}",
            color=0xff0000
        )
        await ctx.send(embed=embed)

# ============== КОМАНДА !СНЯТЬМУТ ==============
@bot.command(name='снятьмут', aliases=['unmute'])
@commands.has_permissions(administrator=True)
async def unmute_command(ctx, member: discord.Member = None):
    """Снять мут с пользователя"""
    if member is None and ctx.message.reference:
        referenced_msg = await ctx.channel.fetch_message(ctx.message.reference.message_id)
        member = referenced_msg.author
    
    if member is None:
        embed = discord.Embed(
            title=f"❌ **ОШИБКА**",
            description=f"Укажи пользователя: `!снятьмут @пользователь`\nИли ответь на сообщение",
            color=0xff0000
        )
        await ctx.send(embed=embed)
        return
    
    try:
        if await remove_mute(member):
            embed = discord.Embed(
                title=f"✅ **МУТ СНЯТ**",
                description=f"У {member.mention} снят мут",
                color=0x00ff00
            )
            embed.add_field(name="👑 Модератор", value=ctx.author.mention, inline=True)
            await ctx.send(embed=embed)
            
            try:
                dm_embed = discord.Embed(
                    title=f"✅ **МУТ СНЯТ**",
                    description=f"На сервере **{ctx.guild.name}** с вас снят мут",
                    color=0x00ff00
                )
                await member.send(embed=dm_embed)
            except:
                pass
        else:
            embed = discord.Embed(
                title=f"ℹ️ **НЕТ МУТА**",
                description=f"У {member.mention} нет активного мута",
                color=0xffaa00
            )
            await ctx.send(embed=embed)
        
    except discord.Forbidden:
        embed = discord.Embed(
            title=f"❌ **ОШИБКА**",
            description=f"У бота нет прав на изменение прав!",
            color=0xff0000
        )
        await ctx.send(embed=embed)
    except Exception as e:
        embed = discord.Embed(
            title=f"❌ **ОШИБКА**",
            description=f"Произошла ошибка: {e}",
            color=0xff0000
        )
        await ctx.send(embed=embed)

# ============== КОМАНДА !МУТЫ ==============
@bot.command(name='муты', aliases=['mutelist', 'mutes'])
@commands.has_permissions(administrator=True)
async def mutelist_command(ctx):
    """Показать всех замученных пользователей"""
    if not active_mutes:
        embed = discord.Embed(
            title=f"🔇 **СПИСОК ЗАМУЧЕННЫХ**",
            description="Нет замученных пользователей",
            color=0x00ff00
        )
        await ctx.send(embed=embed)
        return
    
    embed = discord.Embed(
        title=f"🔇 **СПИСОК ЗАМУЧЕННЫХ**",
        description=f"Всего активных мутов: {len(active_mutes)}",
        color=0xff0000
    )
    
    muted_text = ""
    current_time = datetime.now().timestamp()
    
    for user_id, mute_data in list(active_mutes.items())[:10]:
        member = ctx.guild.get_member(int(user_id))
        if member:
            time_left = mute_data['expires'] - current_time
            if time_left > 0:
                minutes_left = int(time_left / 60)
                if minutes_left < 60:
                    time_str = f"{minutes_left} мин"
                elif minutes_left < 1440:
                    time_str = f"{minutes_left//60} ч"
                else:
                    time_str = f"{minutes_left//1440} дн"
                
                muted_text += f"• {member.mention}\n"
                muted_text += f"  └─ Осталось: {time_str}\n"
                muted_text += f"  └─ Причина: {mute_data['reason'][:50]}\n\n"
    
    if len(active_mutes) > 10:
        muted_text += f"\n... и ещё {len(active_mutes) - 10}"
    
    embed.description = muted_text
    await ctx.send(embed=embed)

# ============== КОМАНДА !БАН ==============
@bot.command(name='бан', aliases=['ban'])
@commands.has_permissions(administrator=True)
async def ban_command(ctx, member: discord.Member):
    """Выдать роль БАН и забрать все остальные роли"""
    BAN_ROLE_ID = 1475987838897098794
    
    ban_role = ctx.guild.get_role(BAN_ROLE_ID)
    
    if ban_role is None:
        embed = discord.Embed(
            title=f"❌ **ОШИБКА**",
            description=f"Роль БАН с ID `{BAN_ROLE_ID}` не найдена на сервере!",
            color=0xff0000
        )
        await ctx.send(embed=embed)
        return
    
    try:
        saved_roles = []
        removed_roles_names = []
        
        for role in member.roles:
            if role.id != ctx.guild.id and role.id != BAN_ROLE_ID:
                saved_roles.append(role.id)
                removed_roles_names.append(role.name)
        
        if saved_roles:
            roles_to_remove = [role for role in member.roles if role.id != ctx.guild.id and role.id != BAN_ROLE_ID]
            await member.remove_roles(*roles_to_remove, reason=f"Бан от {ctx.author}")
        
        await member.add_roles(ban_role, reason=f"Бан от {ctx.author}")
        
        user_id = str(member.id)
        
        if user_id not in temp_roles:
            temp_roles[user_id] = []
        
        temp_roles[user_id] = [r for r in temp_roles[user_id] if r.get('role_id') != BAN_ROLE_ID]
        
        ban_record = {
            'role_id': BAN_ROLE_ID,
            'expires': datetime.now().timestamp() + (365 * 24 * 60 * 60),
            'item_id': f"ban_{ctx.author.id}_{int(time.time())}",
            'saved_roles': saved_roles,
            'is_ban': True
        }
        
        temp_roles[user_id].append(ban_record)
        save_temp_roles()
        
        embed = discord.Embed(
            title=f"🔴 **БАН ВЫДАН**",
            description=f"Пользователю {member.mention} выдана роль {ban_role.mention}",
            color=0xff0000
        )
        
        embed.add_field(name="👤 Пользователь", value=member.mention, inline=True)
        embed.add_field(name="🔴 Роль", value=ban_role.mention, inline=True)
        embed.add_field(name="👑 Администратор", value=ctx.author.mention, inline=True)
        
        if removed_roles_names:
            embed.add_field(
                name="💾 **СОХРАНЁННЫЕ РОЛИ**", 
                value=f"Сохранено ролей: {len(removed_roles_names)}\n```{', '.join(removed_roles_names[:5])}{'...' if len(removed_roles_names) > 5 else ''}```\n✅ Роли будут возвращены при снятии бана", 
                inline=False
            )
        
        embed.set_footer(text=f"ID бана: {BAN_ROLE_ID}")
        embed.timestamp = datetime.now()
        
        await ctx.send(embed=embed)
        
        try:
            dm_embed = discord.Embed(
                title=f"🔴 **ВЫДАЧА РОЛИ БАН**",
                description=f"Вам выдана роль **БАН** на сервере **{ctx.guild.name}**",
                color=0xff0000
            )
            dm_embed.add_field(name="👑 Администратор", value=ctx.author.name, inline=True)
            if removed_roles_names:
                dm_embed.add_field(name="💾 Сохранённые роли", value=f"{len(removed_roles_names)} ролей будут возвращены при снятии бана", inline=False)
            
            await member.send(embed=dm_embed)
        except:
            pass
        
    except discord.Forbidden:
        embed = discord.Embed(
            title=f"❌ **ОШИБКА**",
            description=f"У бота нет прав на выдачу/удаление ролей!\nПроверь, что роль бота выше роли БАН",
            color=0xff0000
        )
        await ctx.send(embed=embed)
    except Exception as e:
        embed = discord.Embed(
            title=f"❌ **ОШИБКА**",
            description=f"Произошла ошибка: {e}",
            color=0xff0000
        )
        await ctx.send(embed=embed)

# ============== КОМАНДА !ЧСС ==============
@bot.command(name='чсс', aliases=['chss'])
@commands.has_permissions(administrator=True)
async def chss_command(ctx, member: discord.Member):
    """Выдать роль ЧСС и забрать все остальные роли"""
    CHSS_ROLE_ID = 1475987685985226873
    
    chss_role = ctx.guild.get_role(CHSS_ROLE_ID)
    
    if chss_role is None:
        embed = discord.Embed(
            title=f"❌ **ОШИБКА**",
            description=f"Роль ЧСС с ID `{CHSS_ROLE_ID}` не найдена на сервере!",
            color=0xff0000
        )
        await ctx.send(embed=embed)
        return
    
    try:
        saved_roles = []
        removed_roles_names = []
        
        for role in member.roles:
            if role.id != ctx.guild.id and role.id != CHSS_ROLE_ID:
                saved_roles.append(role.id)
                removed_roles_names.append(role.name)
        
        if saved_roles:
            roles_to_remove = [role for role in member.roles if role.id != ctx.guild.id and role.id != CHSS_ROLE_ID]
            await member.remove_roles(*roles_to_remove, reason=f"ЧСС от {ctx.author}")
        
        await member.add_roles(chss_role, reason=f"ЧСС от {ctx.author}")
        
        user_id = str(member.id)
        
        if user_id not in temp_roles:
            temp_roles[user_id] = []
        
        temp_roles[user_id] = [r for r in temp_roles[user_id] if r.get('role_id') != CHSS_ROLE_ID]
        
        chss_record = {
            'role_id': CHSS_ROLE_ID,
            'expires': datetime.now().timestamp() + (365 * 24 * 60 * 60),
            'item_id': f"chss_{ctx.author.id}_{int(time.time())}",
            'saved_roles': saved_roles,
            'is_chss': True
        }
        
        temp_roles[user_id].append(chss_record)
        save_temp_roles()
        
        embed = discord.Embed(
            title=f"🟢 **ЧСС ВЫДАНА**",
            description=f"Пользователю {member.mention} выдана роль {chss_role.mention}",
            color=0x00ff00
        )
        
        embed.add_field(name="👤 Пользователь", value=member.mention, inline=True)
        embed.add_field(name="🟢 Роль", value=chss_role.mention, inline=True)
        embed.add_field(name="👑 Администратор", value=ctx.author.mention, inline=True)
        
        if removed_roles_names:
            embed.add_field(
                name="💾 **СОХРАНЁННЫЕ РОЛИ**", 
                value=f"Сохранено ролей: {len(removed_roles_names)}\n```{', '.join(removed_roles_names[:5])}{'...' if len(removed_roles_names) > 5 else ''}```\n✅ Роли будут возвращены при снятии ЧСС", 
                inline=False
            )
        
        embed.set_footer(text=f"ID ЧСС: {CHSS_ROLE_ID}")
        embed.timestamp = datetime.now()
        
        await ctx.send(embed=embed)
        
        try:
            dm_embed = discord.Embed(
                title=f"🟢 **ВЫДАЧА РОЛИ ЧСС**",
                description=f"Вам выдана роль **ЧСС** на сервере **{ctx.guild.name}**",
                color=0x00ff00
            )
            dm_embed.add_field(name="👑 Администратор", value=ctx.author.name, inline=True)
            if removed_roles_names:
                dm_embed.add_field(name="💾 Сохранённые роли", value=f"{len(removed_roles_names)} ролей будут возвращены при снятии ЧСС", inline=False)
            
            await member.send(embed=dm_embed)
        except:
            pass
        
    except discord.Forbidden:
        embed = discord.Embed(
            title=f"❌ **ОШИБКА**",
            description=f"У бота нет прав на выдачу/удаление ролей!\nПроверь, что роль бота выше роли ЧСС",
            color=0xff0000
        )
        await ctx.send(embed=embed)
    except Exception as e:
        embed = discord.Embed(
            title=f"❌ **ОШИБКА**",
            description=f"Произошла ошибка: {e}",
            color=0xff0000
        )
        await ctx.send(embed=embed)

# ============== КОМАНДА !СНЯТЬ ==============
@bot.command(name='снять', aliases=['unban', 'unchss'])
@commands.has_permissions(administrator=True)
async def remove_ban_chss_command(ctx, member: discord.Member):
    """Снять роли БАН и ЧСС, вернуть сохранённые роли"""
    BAN_ROLE_ID = 1475987838897098794
    CHSS_ROLE_ID = 1475987685985226873
    
    ban_role = ctx.guild.get_role(BAN_ROLE_ID)
    chss_role = ctx.guild.get_role(CHSS_ROLE_ID)
    
    user_id = str(member.id)
    restored_roles = []
    removed_roles = []
    
    try:
        ban_record = None
        chss_record = None
        
        if user_id in temp_roles:
            for record in temp_roles[user_id]:
                if record.get('role_id') == BAN_ROLE_ID:
                    ban_record = record
                if record.get('role_id') == CHSS_ROLE_ID:
                    chss_record = record
        
        if ban_role and ban_role in member.roles:
            await member.remove_roles(ban_role, reason=f"Снятие бана от {ctx.author}")
            removed_roles.append(ban_role.name)
        
        if chss_role and chss_role in member.roles:
            await member.remove_roles(chss_role, reason=f"Снятие ЧСС от {ctx.author}")
            removed_roles.append(chss_role.name)
        
        if ban_record and ban_record.get('saved_roles'):
            for role_id in ban_record['saved_roles']:
                role = ctx.guild.get_role(role_id)
                if role:
                    try:
                        await member.add_roles(role, reason=f"Возврат после снятия бана")
                        restored_roles.append(role.name)
                    except:
                        pass
        
        if chss_record and chss_record.get('saved_roles'):
            for role_id in chss_record['saved_roles']:
                role = ctx.guild.get_role(role_id)
                if role and role.name not in restored_roles:
                    try:
                        await member.add_roles(role, reason=f"Возврат после снятия ЧСС")
                        restored_roles.append(role.name)
                    except:
                        pass
        
        if user_id in temp_roles:
            temp_roles[user_id] = [r for r in temp_roles[user_id] 
                                   if r.get('role_id') not in [BAN_ROLE_ID, CHSS_ROLE_ID]]
            save_temp_roles()
        
        if removed_roles or restored_roles:
            embed = discord.Embed(
                title=f"✅ **РОЛИ СНЯТЫ**",
                description=f"У {member.mention} выполнены следующие действия:",
                color=0x00ff00
            )
            
            if removed_roles:
                embed.add_field(
                    name="🗑️ **УДАЛЁННЫЕ РОЛИ**", 
                    value=f"```{', '.join(removed_roles)}```", 
                    inline=False
                )
            
            if restored_roles:
                embed.add_field(
                    name="🔄 **ВОЗВРАЩЁННЫЕ РОЛИ**", 
                    value=f"```{', '.join(restored_roles[:10])}{'...' if len(restored_roles) > 10 else ''}```\n✅ Возвращено ролей: {len(restored_roles)}", 
                    inline=False
                )
            
            embed.add_field(name="👑 Администратор", value=ctx.author.mention, inline=True)
            
            await ctx.send(embed=embed)
            
            try:
                dm_embed = discord.Embed(
                    title=f"✅ **РОЛИ СНЯТЫ**",
                    description=f"На сервере **{ctx.guild.name}** с вас сняты ограничения",
                    color=0x00ff00
                )
                if removed_roles:
                    dm_embed.add_field(name="🗑️ Удалённые роли", value=f"```{', '.join(removed_roles)}```", inline=False)
                if restored_roles:
                    dm_embed.add_field(name="🔄 Возвращённые роли", value=f"Возвращено {len(restored_roles)} ролей", inline=False)
                
                await member.send(embed=dm_embed)
            except:
                pass
        else:
            embed = discord.Embed(
                title=f"ℹ️ **НЕТ РОЛЕЙ**",
                description=f"У {member.mention} нет ролей БАН или ЧСС",
                color=0xffaa00
            )
            await ctx.send(embed=embed)
        
    except discord.Forbidden:
        embed = discord.Embed(
            title=f"❌ **ОШИБКА**",
            description=f"У бота нет прав на удаление/выдачу ролей!",
            color=0xff0000
        )
        await ctx.send(embed=embed)
    except Exception as e:
        embed = discord.Embed(
            title=f"❌ **ОШИБКА**",
            description=f"Произошла ошибка: {e}",
            color=0xff0000
        )
        await ctx.send(embed=embed)

# ============== КОМАНДА !БАНЛИСТ ==============
@bot.command(name='банлист', aliases=['banlist', 'ban_list'])
@commands.has_permissions(administrator=True)
async def ban_list_command(ctx):
    """Показать всех пользователей с баном/ЧСС"""
    BAN_ROLE_ID = 1475987838897098794
    CHSS_ROLE_ID = 1475987685985226873
    
    banned_users = []
    
    for user_id, records in temp_roles.items():
        for record in records:
            if record.get('role_id') in [BAN_ROLE_ID, CHSS_ROLE_ID]:
                member = ctx.guild.get_member(int(user_id))
                if member:
                    role_type = "🔴 БАН" if record.get('role_id') == BAN_ROLE_ID else "🟢 ЧСС"
                    saved_count = len(record.get('saved_roles', []))
                    banned_users.append(f"• {member.mention} — {role_type} (сохранено {saved_count} ролей)")
    
    if banned_users:
        embed = discord.Embed(
            title=f"📋 **СПИСОК ЗАБЛОКИРОВАННЫХ**",
            description="\n".join(banned_users[:20]),
            color=0x3498db
        )
        if len(banned_users) > 20:
            embed.set_footer(text=f"Показано 20 из {len(banned_users)}")
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(
            title=f"📋 **СПИСОК ЗАБЛОКИРОВАННЫХ**",
            description="Нет пользователей с баном или ЧСС",
            color=0xffaa00
        )
        await ctx.send(embed=embed)

# ============== КОМАНДЫ ДЛЯ УПРАВЛЕНИЯ ЗАМЕНЯЮЩИМИ РОЛЯМИ ==============
@bot.command(name='replacement_add')
@commands.has_permissions(administrator=True)
async def replacement_add_command(ctx, role: discord.Role):
    """Добавить роль в список заменяющих"""
    global REPLACEMENT_ROLES
    
    if role.id not in REPLACEMENT_ROLES:
        REPLACEMENT_ROLES.append(role.id)
        save_replacement_config()
        
        embed = discord.Embed(
            title=f"✅ **РОЛЬ ДОБАВЛЕНА В ЗАМЕНЯЮЩИЕ**",
            description=f"При выдаче роли {role.mention} будут удаляться все остальные роли (кроме белого списка)\n\n💾 Настройка сохранена!",
            color=0x00ff00
        )
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(
            title=f"ℹ️ **РОЛЬ УЖЕ В ЗАМЕНЯЮЩИХ**",
            description=f"Роль {role.mention} уже находится в списке заменяющих",
            color=0xffaa00
        )
        await ctx.send(embed=embed)

@bot.command(name='replacement_remove')
@commands.has_permissions(administrator=True)
async def replacement_remove_command(ctx, role: discord.Role):
    """Убрать роль из списка заменяющих"""
    global REPLACEMENT_ROLES
    
    if role.id in REPLACEMENT_ROLES:
        REPLACEMENT_ROLES.remove(role.id)
        save_replacement_config()
        
        embed = discord.Embed(
            title=f"✅ **РОЛЬ УБРАНА ИЗ ЗАМЕНЯЮЩИХ**",
            description=f"Роль {role.mention} больше не будет удалять другие роли при выдаче\n\n💾 Настройка сохранена!",
            color=0x00ff00
        )
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(
            title=f"ℹ️ **РОЛЬ НЕ В ЗАМЕНЯЮЩИХ**",
            description=f"Роль {role.mention} не находится в списке заменяющих",
            color=0xffaa00
        )
        await ctx.send(embed=embed)

@bot.command(name='whitelist_add')
@commands.has_permissions(administrator=True)
async def whitelist_add_command(ctx, role: discord.Role):
    """Добавить роль в белый список"""
    global WHITELISTED_ROLES
    
    if role.id not in WHITELISTED_ROLES:
        WHITELISTED_ROLES.append(role.id)
        save_replacement_config()
        
        embed = discord.Embed(
            title=f"✅ **РОЛЬ ДОБАВЛЕНА В БЕЛЫЙ СПИСОК**",
            description=f"Роль {role.mention} теперь не будет удаляться при замене\n\n💾 Настройка сохранена!",
            color=0x00ff00
        )
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(
            title=f"ℹ️ **РОЛЬ УЖЕ В БЕЛОМ СПИСКЕ**",
            description=f"Роль {role.mention} уже находится в белом списке",
            color=0xffaa00
        )
        await ctx.send(embed=embed)

@bot.command(name='whitelist_remove')
@commands.has_permissions(administrator=True)
async def whitelist_remove_command(ctx, role: discord.Role):
    """Убрать роль из белого списка"""
    global WHITELISTED_ROLES
    
    if role.id in WHITELISTED_ROLES:
        WHITELISTED_ROLES.remove(role.id)
        save_replacement_config()
        
        embed = discord.Embed(
            title=f"✅ **РОЛЬ УБРАНА ИЗ БЕЛОГО СПИСКА**",
            description=f"Роль {role.mention} теперь может удаляться при замене\n\n💾 Настройка сохранена!",
            color=0x00ff00
        )
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(
            title=f"ℹ️ **РОЛЬ НЕ В БЕЛОМ СПИСКЕ**",
            description=f"Роль {role.mention} не находится в белом списке",
            color=0xffaa00
        )
        await ctx.send(embed=embed)

@bot.command(name='list_protected')
@commands.has_permissions(administrator=True)
async def list_protected_command(ctx):
    """Показать все защищённые и заменяющие роли"""
    embed = discord.Embed(
        title=f"📋 **СПИСОК ЗАЩИЩЁННЫХ РОЛЕЙ**",
        color=0x3498db
    )
    
    whitelist_text = ""
    if WHITELISTED_ROLES:
        for role_id in WHITELISTED_ROLES:
            role = ctx.guild.get_role(role_id)
            if role:
                whitelist_text += f"• {role.mention}\n"
            else:
                whitelist_text += f"• Роль ID: `{role_id}` (удалена)\n"
    else:
        whitelist_text = "Нет ролей в белом списке"
    
    embed.add_field(name="🛡️ **БЕЛЫЙ СПИСОК**", value=whitelist_text, inline=False)
    
    replacement_text = ""
    if REPLACEMENT_ROLES:
        for role_id in REPLACEMENT_ROLES:
            role = ctx.guild.get_role(role_id)
            if role:
                replacement_text += f"• {role.mention}\n"
            else:
                replacement_text += f"• Роль ID: `{role_id}` (удалена)\n"
    else:
        replacement_text = "Нет заменяющих ролей"
    
    embed.add_field(name="🔄 **ЗАМЕНЯЮЩИЕ РОЛИ**", value=replacement_text, inline=False)
    
    embed.set_footer(text=f"💾 Настройки сохраняются в файл {REPLACEMENT_FILE}")
    
    await ctx.send(embed=embed)

# ============== КОМАНДА !ОЧИСТИТЬИНВЕНТАРЬ ==============
@bot.command(name='очиститьинвентарь', aliases=['clearinv', 'очистить_инвентарь'])
@commands.has_permissions(administrator=True)
async def clear_inventory_command(ctx, member: discord.Member = None, item_id: str = None):
    """Очистить инвентарь пользователя"""
    if member is None and item_id is None and ctx.message.content.endswith('all'):
        confirm_msg = await ctx.send("⚠️ **ВНИМАНИЕ!** Вы уверены, что хотите очистить инвентарь **ВСЕХ** пользователей? Это действие нельзя отменить!\n\nНапишите `да` в течение 30 секунд для подтверждения.")
        
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel and m.content.lower() == 'да'
        
        try:
            await bot.wait_for('message', timeout=30.0, check=check)
        except asyncio.TimeoutError:
            await ctx.send("❌ Операция отменена (таймаут).")
            return
        
        cleared_count = 0
        for user_id in user_data:
            if 'items' in user_data[user_id]:
                if user_data[user_id]['items']:
                    cleared_count += len(user_data[user_id]['items'])
                user_data[user_id]['items'] = []
        
        save_data(user_data)
        
        embed = discord.Embed(
            title=f"🧹 **МАССОВАЯ ОЧИСТКА**",
            description=f"Инвентарь **ВСЕХ** пользователей очищен!\nУдалено предметов: **{cleared_count}**",
            color=0x00ff00
        )
        embed.add_field(name="👑 Администратор", value=ctx.author.mention, inline=True)
        await ctx.send(embed=embed)
        return
    
    if member is None:
        embed = discord.Embed(
            title=f"❌ **ОШИБКА**",
            description=f"Укажи пользователя: `!очиститьинвентарь @пользователь`\nИли для удаления конкретного предмета: `!очиститьинвентарь @пользователь ID`\nИли для массовой очистки: `!очиститьинвентарь all`",
            color=0xff0000
        )
        await ctx.send(embed=embed)
        return
    
    user_id = str(member.id)
    
    if user_id not in user_data:
        embed = discord.Embed(
            title=f"ℹ️ **НЕТ ДАННЫХ**",
            description=f"У {member.mention} нет данных в системе",
            color=0xffaa00
        )
        await ctx.send(embed=embed)
        return
    
    if item_id:
        if 'items' not in user_data[user_id] or item_id not in user_data[user_id]['items']:
            embed = discord.Embed(
                title=f"❌ **ОШИБКА**",
                description=f"У {member.mention} нет предмета с ID `{item_id}` в инвентаре",
                color=0xff0000
            )
            await ctx.send(embed=embed)
            return
        
        item_name = item_id
        if item_id in shop_data:
            item_name = shop_data[item_id]['name']
        
        user_data[user_id]['items'].remove(item_id)
        save_data(user_data)
        
        embed = discord.Embed(
            title=f"🧹 **ПРЕДМЕТ УДАЛЁН**",
            description=f"Из инвентаря {member.mention} удалён предмет: **{item_name}**",
            color=0x00ff00
        )
        embed.add_field(name="🆔 ID предмета", value=f"`{item_id}`", inline=True)
        embed.add_field(name="👑 Администратор", value=ctx.author.mention, inline=True)
        embed.add_field(name="📦 Осталось предметов", value=f"**{len(user_data[user_id].get('items', []))}**", inline=True)
        
        await ctx.send(embed=embed)
        
        try:
            dm_embed = discord.Embed(
                title=f"🧹 **ПРЕДМЕТ УДАЛЁН**",
                description=f"На сервере **{ctx.guild.name}** из вашего инвентаря удалён предмет: **{item_name}**",
                color=0xffaa00
            )
            dm_embed.add_field(name="👑 Администратор", value=ctx.author.name, inline=True)
            await member.send(embed=dm_embed)
        except:
            pass
        
        return
    
    if 'items' not in user_data[user_id] or not user_data[user_id]['items']:
        embed = discord.Embed(
            title=f"ℹ️ **ПУСТОЙ ИНВЕНТАРЬ**",
            description=f"У {member.mention} и так пустой инвентарь",
            color=0xffaa00
        )
        await ctx.send(embed=embed)
        return
    
    removed_items = user_data[user_id]['items'].copy()
    removed_count = len(removed_items)
    
    user_data[user_id]['items'] = []
    save_data(user_data)
    
    embed = discord.Embed(
        title=f"🧹 **ИНВЕНТАРЬ ОЧИЩЕН**",
        description=f"Инвентарь {member.mention} полностью очищен",
        color=0x00ff00
    )
    
    embed.add_field(name="👤 Пользователь", value=member.mention, inline=True)
    embed.add_field(name="📦 Удалено предметов", value=f"**{removed_count}**", inline=True)
    embed.add_field(name="👑 Администратор", value=ctx.author.mention, inline=True)
    
    if removed_items:
        items_sample = []
        for item_id in removed_items[:5]:
            if item_id in shop_data:
                items_sample.append(shop_data[item_id]['name'])
            else:
                items_sample.append(f"Неизвестный ({item_id})")
        
        embed.add_field(
            name="📋 **Удалённые предметы**",
            value=f"```{', '.join(items_sample)}{'...' if len(removed_items) > 5 else ''}```",
            inline=False
        )
    
    await ctx.send(embed=embed)
    
    try:
        dm_embed = discord.Embed(
            title=f"🧹 **ИНВЕНТАРЬ ОЧИЩЕН**",
            description=f"На сервере **{ctx.guild.name}** ваш инвентарь был очищен администратором",
            color=0xffaa00
        )
        dm_embed.add_field(name="👑 Администратор", value=ctx.author.name, inline=True)
        dm_embed.add_field(name="📦 Удалено предметов", value=removed_count, inline=True)
        
        await member.send(embed=dm_embed)
    except:
        pass

# ============== КОМАНДА !ИНВЕНТАРЬАДМИН ==============
@bot.command(name='инвентарьадмин', aliases=['invadmin', 'посмотретьинвентарь'])
@commands.has_permissions(administrator=True)
async def admin_inventory_command(ctx, member: discord.Member):
    """Посмотреть инвентарь пользователя (админская версия)"""
    user_id = str(member.id)
    
    if user_id not in user_data:
        embed = discord.Embed(
            title=f"📦 **ИНВЕНТАРЬ {member.display_name}**",
            description=f"У пользователя нет данных в системе",
            color=0xffaa00
        )
        await ctx.send(embed=embed)
        return
    
    items = user_data[user_id].get('items', [])
    
    embed = discord.Embed(
        title=f"📦 **ИНВЕНТАРЬ {member.display_name} (АДМИН)**",
        color=0x3498db
    )
    embed.set_author(name=member.display_name, icon_url=member.avatar.url if member.avatar else member.default_avatar.url)
    
    if not items:
        embed.description = "Инвентарь пуст"
    else:
        items_text = ""
        for item_id in items:
            if item_id in shop_data:
                item = shop_data[item_id]
                items_text += f"• **{item['name']}** - ID: `{item_id}`\n"
            else:
                items_text += f"• Неизвестный предмет - ID: `{item_id}`\n"
        
        embed.description = items_text
        embed.set_footer(text=f"📊 Всего предметов: {len(items)}")
    
    await ctx.send(embed=embed)

# ============== ОБНОВЛЁННАЯ КОМАНДА !ПОМОЩЬ ==============
@bot.command(name='помощь', aliases=['хелп', 'команды'])
async def help_command(ctx):
    """Показывает список всех доступных команд"""
    
    # Подсчёт статистики
    users_in_system = len(user_data)
    total_shop_items = len(shop_data)
    
    # Считаем реальных пользователей на сервере
    real_users = 0
    for guild in bot.guilds:
        for member in guild.members:
            if not member.bot:
                real_users += 1
    
    embed = discord.Embed(
        title=f"📚 **СПРАВКА ПО КОМАНДАМ**",
        description=f"Привет, {ctx.author.mention}! Вот список всех команд:",
        color=0x3498db
    )
    
    embed.set_footer(text="Discord Bot v2.0 • Разработано с ❤️")
    embed.timestamp = datetime.now()
    
    if bot.user.avatar:
        embed.set_thumbnail(url=bot.user.avatar.url)
        
    invites_commands = (
        "`!приг` / `!приглашения` - твои приглашения\n"
        "`!приг @пользователь` - приглашения другого\n"
        "`!пригтоп` / `!топприг` - топ по приглашениям"
    )
    embed.add_field(name="🎟️ **ПРИГЛАШЕНИЯ**", value=invites_commands, inline=False)
    # ===== ПРОФИЛЬ И СТАТИСТИКА =====
    profile_commands = (
        "`!ур` / `!уровень` - твой профиль\n"
        "`!ур @пользователь` - профиль другого\n"
        "`!бал` / `!баланс` - баланс коинов\n"
        "`!топы` / `!лидеры` - таблица лидеров\n"
        "`!войс` / `!вс` - статистика войса\n"
        "`!временные` / `!temp` - временные роли"
    )
    embed.add_field(name="👤 **ПРОФИЛЬ**", value=profile_commands, inline=False)
    
    # ===== МАГАЗИН И ЭКОНОМИКА =====
    shop_commands = (
        "`!магазин` / `!shop` - открыть магазин\n"
        "`!купить [ID]` - купить предмет\n"
        "`!инвентарь` / `!inv` - инвентарь\n"
        "`!сохранённые` / `!saved` - роли на возврат"
    )
    embed.add_field(name="🛒 **МАГАЗИН**", value=shop_commands, inline=False)
    
    # ===== КАЗИНО =====
    casino_commands = (
        "`!казино` - список игр казино\n"
        "`!орёл [ставка]` / `!решка [ставка]` - орлянка\n"
        "`!кость [ставка] [число]` - угадай число\n"
        "`!слоты [ставка]` - игровые слоты\n"
        "`!рулетка [цвет] [ставка]` - рулетка\n"
        "`!бонус` - ежедневный бонус"
    )
    embed.add_field(name="🎰 **КАЗИНО**", value=casino_commands, inline=False)
    
    # ===== ОБЩЕЕ =====
    general_commands = (
        "`!помощь` / `!хелп` - это меню\n"
        "`!падмин` - команды для админов"
    )
    embed.add_field(name="📋 **ОБЩЕЕ**", value=general_commands, inline=False)
    
    # ===== СТАТИСТИКА СЕРВЕРА =====
    stats = (
        f"👥 **Пользователей на сервере:** {real_users}\n"
        f"📊 **В системе уровней:** {users_in_system}\n"
        f"🛍️ **Товаров в магазине:** {total_shop_items}\n"
        f"💰 **Всего коинов в обороте:** {sum(u.get('coins', 0) for u in user_data.values()):,}"
    )
    embed.add_field(name="📊 **СТАТИСТИКА**", value=stats, inline=False)
    
    await ctx.send(embed=embed)

# ============== КОМАНДА !ПАДМИН ==============
@bot.command(name='падмин', aliases=['админпомощь', 'adminhelp', 'помощадмина'])
@commands.has_permissions(administrator=True)
async def admin_help_command(ctx):
    """Показывает список административных команд"""
    
    embed = discord.Embed(
        title=f"👑 **АДМИНИСТРАТИВНЫЕ КОМАНДЫ**",
        description="Команды, доступные только администраторам:",
        color=0xff0000
    )
    
    embed.set_footer(text="⚠️ Будьте осторожны с этими командами!")
    embed.timestamp = datetime.now()
    
    if bot.user.avatar:
        embed.set_thumbnail(url=bot.user.avatar.url)
    
    role_commands = (
        "`!выдатьроль @пользователь @роль время` - временная роль\n"
        "`!выдатьроль @пользователь ID_роли время` - по ID роли\n"
        "`!бан @пользователь` - выдать роль БАН\n"
        "`!чсс @пользователь` - выдать роль ЧСС\n"
        "`!снять @пользователь` - снять БАН/ЧСС"
    )
    embed.add_field(name="🎭 **УПРАВЛЕНИЕ РОЛЯМИ**", value=role_commands, inline=False)
    
    punish_commands = (
        "`!пред @пользователь причина` - предупреждение\n"
        "`!преды @пользователь` - список предупреждений\n"
        "`!снятьпред @пользователь ID` - снять предупреждение\n"
        "`!очиститьпреды @пользователь` - удалить все предупреждения\n"
        "`!мут @пользователь время причина` - замутить\n"
        "`!снятьмут @пользователь` - снять мут\n"
        "`!муты` - список замученных"
    )
    embed.add_field(name="⚠️ **НАКАЗАНИЯ**", value=punish_commands, inline=False)
    
    shop_admin = (
        "`!add_item ID цена название` - добавить товар\n"
        "`!add_temp_item ID цена минуты название` - временный товар\n"
        "`!remove_item ID` - удалить товар\n"
        "`!edit_item ID поле значение` - изменить товар\n"
        "`!set_role ID @роль` - привязать роль\n"
        "`!remove_role ID` - убрать привязку роли"
    )
    embed.add_field(name="🛒 **УПРАВЛЕНИЕ МАГАЗИНОМ**", value=shop_admin, inline=False)
    
    boost_admin = (
        "`!set_boost @роль множитель` - настроить бустер\n"
        "`!remove_boost @роль` - убрать бустер\n"
        "`!list_boosts` - список бустеров"
    )
    embed.add_field(name="⚡ **НАСТРОЙКА БУСТЕРОВ**", value=boost_admin, inline=False)
    
    replacement_admin = (
        "`!replacement_add @роль` - роль будет заменять другие\n"
        "`!replacement_remove @роль` - убрать из заменяющих\n"
        "`!whitelist_add @роль` - роль не будет удаляться\n"
        "`!whitelist_remove @роль` - убрать из белого списка\n"
        "`!list_protected` - показать настройки"
    )
    embed.add_field(name="🔄 **ЗАМЕНА РОЛЕЙ**", value=replacement_admin, inline=False)
    
    inventory_admin = (
        "`!очиститьинвентарь @пользователь` - очистить инвентарь\n"
        "`!очиститьинвентарь @пользователь ID` - удалить предмет\n"
        "`!очиститьинвентарь all` - очистить ВСЕ инвентари\n"
        "`!инвентарьадмин @пользователь` - посмотреть инвентарь"
    )
    embed.add_field(name="📦 **УПРАВЛЕНИЕ ИНВЕНТАРЁМ**", value=inventory_admin, inline=False)
    
    economy_admin = (
        "`!give_coins @пользователь количество` - выдать коины\n"
        "`!set_voice_xp количество` - изменить XP за войс\n"
        "`!reset_levels` - СБРОСИТЬ ВСЕ УРОВНИ"
    )
    embed.add_field(name="💰 **ЭКОНОМИКА**", value=economy_admin, inline=False)
    
    warning = "⚠️ **ВНИМАНИЕ:** Некоторые команды могут быть опасными! Будьте внимательны."
    embed.add_field(name="━━━━━━━━━━━━━━━━━━", value=warning, inline=False)
    
    await ctx.send(embed=embed)

@admin_help_command.error
async def admin_help_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(
            title=f"❌ **ОШИБКА ДОСТУПА**",
            description="Эта команда доступна только администраторам сервера!",
            color=0xff0000
        )
        await ctx.send(embed=embed)

# ============== СИСТЕМА КАЗИНО ==============
import random
import time

# Настройки казино
CASINO_SETTINGS = {
    'min_bet': 10,           # Минимальная ставка
    'max_bet': 10000,        # Максимальная ставка
    'coin_flip_mult': 1.8,    # Множитель выигрыша (x1.8, т.е. +80%)
    'dice_mult': 5,           # Множитель для угадывания числа (x5)
    'slot_mult': {            # Множители для слотов
        '🍒': 2,              # Вишня - x2
        '🍋': 3,              # Лимон - x3
        '🍊': 4,              # Апельсин - x4
        '🍇': 5,              # Виноград - x5
        '💎': 10,             # Алмаз - x10
        '7⃣': 20              # Джекпот - x20
    }
}

# ============== КОМАНДА !КАЗИНО ==============
@bot.command(name='казино', aliases=['casino', 'игры'])
async def casino_command(ctx):
    """Показывает список доступных игр в казино"""
    
    embed = discord.Embed(
        title=f"🎰 **КАЗИНО**",
        description="Добро пожаловать в казино! Выбери игру:",
        color=0xffd700  # Золотой цвет
    )
    
    embed.add_field(
        name="🪙 **!орёл** / **!решка**", 
        value=f"Ставка на орла или решку\nМножитель: x{CASINO_SETTINGS['coin_flip_mult']} (возврат +80%)\nМин: {CASINO_SETTINGS['min_bet']} 🪙",
        inline=False
    )
    
    embed.add_field(
        name="🎲 **!кость** / **!кубик**", 
        value=f"Бросок кубика (1-6). Угадай число!\nМножитель: x{CASINO_SETTINGS['dice_mult']}\nМин: {CASINO_SETTINGS['min_bet']} 🪙",
        inline=False
    )
    
    embed.add_field(
        name="🎰 **!слоты** / **!слот**", 
        value=f"Крути слоты! Три одинаковых символа = выигрыш\n"
               f"🍒 x2 | 🍋 x3 | 🍊 x4 | 🍇 x5 | 💎 x10 | 7⃣ x20\n"
               f"Мин: {CASINO_SETTINGS['min_bet']} 🪙",
        inline=False
    )
    
    embed.add_field(
        name="📊 **!рулетка [цвет] [ставка]**", 
        value=f"Ставка на красное/черное\nМножитель: x2\nМин: {CASINO_SETTINGS['min_bet']} 🪙",
        inline=False
    )
    
    embed.add_field(
        name="ℹ️ **ПРАВИЛА**",
        value=f"Минимальная ставка: {CASINO_SETTINGS['min_bet']} 🪙\n"
              f"Максимальная ставка: {CASINO_SETTINGS['max_bet']} 🪙\n"
              f"Удачи! 🍀",
        inline=False
    )
    
    await ctx.send(embed=embed)

# ============== КОМАНДА !ОРЁЛ / !РЕШКА ==============
@bot.command(name='орёл', aliases=['орел', 'решка', 'coin'])
async def coin_flip_command(ctx, bet: int = None):
    """!орёл [ставка] - сыграть в орлянку"""
    
    if bet is None:
        embed = discord.Embed(
            title=f"❌ **ОШИБКА**",
            description=f"Укажи ставку! Пример: `!орёл 100`",
            color=0xff0000
        )
        await ctx.send(embed=embed)
        return
    
    user_id = str(ctx.author.id)
    
    # Проверяем наличие пользователя в базе
    if user_id not in user_data:
        user_data[user_id] = {'coins': 0, 'total_coins_earned': 0, 'username': str(ctx.author), 'items': []}
    
    coins = user_data[user_id].get('coins', 0)
    
    # Проверка минимальной ставки
    if bet < CASINO_SETTINGS['min_bet']:
        embed = discord.Embed(
            title=f"❌ **ОШИБКА**",
            description=f"Минимальная ставка: {CASINO_SETTINGS['min_bet']} 🪙",
            color=0xff0000
        )
        await ctx.send(embed=embed)
        return
    
    # Проверка максимальной ставки
    if bet > CASINO_SETTINGS['max_bet']:
        embed = discord.Embed(
            title=f"❌ **ОШИБКА**",
            description=f"Максимальная ставка: {CASINO_SETTINGS['max_bet']} 🪙",
            color=0xff0000
        )
        await ctx.send(embed=embed)
        return
    
    # Проверка баланса
    if coins < bet:
        embed = discord.Embed(
            title=f"❌ **ОШИБКА**",
            description=f"Недостаточно коинов! У тебя: {coins} 🪙",
            color=0xff0000
        )
        await ctx.send(embed=embed)
        return
    
    # Определяем, на что поставил игрок
    bet_on = ctx.invoked_with.lower()
    if bet_on in ['орёл', 'орел']:
        bet_on = 'орёл'
    else:
        bet_on = 'решка'
    
    # Бросаем монету
    result = random.choice(['орёл', 'решка'])
    
    # Проверяем выигрыш
    win = (bet_on == result)
    
    if win:
        winnings = int(bet * CASINO_SETTINGS['coin_flip_mult'])
        user_data[user_id]['coins'] += winnings - bet  # Добавляем только выигрыш (без ставки)
        result_text = f"🎉 **ВЫИГРЫШ!** +{winnings - bet} 🪙"
        color = 0x00ff00
    else:
        user_data[user_id]['coins'] -= bet
        result_text = f"😢 **ПРОИГРЫШ** -{bet} 🪙"
        color = 0xff0000
    
    save_data(user_data)
    
    # Создаём красивый embed
    embed = discord.Embed(
        title=f"🪙 **ОРЛЯНКА**",
        color=color
    )
    
    embed.add_field(name="👤 Игрок", value=ctx.author.mention, inline=True)
    embed.add_field(name="🎯 Ставка", value=f"{bet_on}", inline=True)
    embed.add_field(name="📊 Результат", value=f"**{result}**", inline=True)
    embed.add_field(name="💰 Итог", value=result_text, inline=False)
    embed.add_field(name="🪙 Новый баланс", value=f"{user_data[user_id]['coins']} 🪙", inline=False)
    
    await ctx.send(embed=embed)

# ============== КОМАНДА !КОСТЬ ==============
@bot.command(name='кость', aliases=['кубик', 'dice'])
async def dice_command(ctx, bet: int = None, guess: int = None):
    """!кость [ставка] [число] - угадай число на кубике (1-6)"""
    
    if bet is None or guess is None:
        embed = discord.Embed(
            title=f"❌ **ОШИБКА**",
            description=f"Укажи ставку и число! Пример: `!кость 100 3`",
            color=0xff0000
        )
        await ctx.send(embed=embed)
        return
    
    if guess < 1 or guess > 6:
        embed = discord.Embed(
            title=f"❌ **ОШИБКА**",
            description=f"Число должно быть от 1 до 6!",
            color=0xff0000
        )
        await ctx.send(embed=embed)
        return
    
    user_id = str(ctx.author.id)
    
    if user_id not in user_data:
        user_data[user_id] = {'coins': 0, 'total_coins_earned': 0, 'username': str(ctx.author), 'items': []}
    
    coins = user_data[user_id].get('coins', 0)
    
    if bet < CASINO_SETTINGS['min_bet']:
        embed = discord.Embed(
            title=f"❌ **ОШИБКА**",
            description=f"Минимальная ставка: {CASINO_SETTINGS['min_bet']} 🪙",
            color=0xff0000
        )
        await ctx.send(embed=embed)
        return
    
    if bet > CASINO_SETTINGS['max_bet']:
        embed = discord.Embed(
            title=f"❌ **ОШИБКА**",
            description=f"Максимальная ставка: {CASINO_SETTINGS['max_bet']} 🪙",
            color=0xff0000
        )
        await ctx.send(embed=embed)
        return
    
    if coins < bet:
        embed = discord.Embed(
            title=f"❌ **ОШИБКА**",
            description=f"Недостаточно коинов! У тебя: {coins} 🪙",
            color=0xff0000
        )
        await ctx.send(embed=embed)
        return
    
    # Бросаем кубик
    result = random.randint(1, 6)
    
    win = (guess == result)
    
    if win:
        winnings = bet * CASINO_SETTINGS['dice_mult']
        user_data[user_id]['coins'] += winnings - bet
        result_text = f"🎉 **ДЖЕКПОТ!** +{winnings - bet} 🪙 (x{CASINO_SETTINGS['dice_mult']})"
        color = 0x00ff00
    else:
        user_data[user_id]['coins'] -= bet
        result_text = f"😢 **ПРОИГРЫШ** -{bet} 🪙"
        color = 0xff0000
    
    save_data(user_data)
    
    embed = discord.Embed(
        title=f"🎲 **КУБИК**",
        color=color
    )
    
    embed.add_field(name="👤 Игрок", value=ctx.author.mention, inline=True)
    embed.add_field(name="🎯 Ставка", value=f"на {guess}", inline=True)
    embed.add_field(name="📊 Результат", value=f"**{result}**", inline=True)
    embed.add_field(name="💰 Итог", value=result_text, inline=False)
    embed.add_field(name="🪙 Новый баланс", value=f"{user_data[user_id]['coins']} 🪙", inline=False)
    
    await ctx.send(embed=embed)

# ============== КОМАНДА !СЛОТЫ ==============
@bot.command(name='слоты', aliases=['слот', 'slots', 'slot'])
async def slots_command(ctx, bet: int = None):
    """!слоты [ставка] - крути слоты"""
    
    if bet is None:
        embed = discord.Embed(
            title=f"❌ **ОШИБКА**",
            description=f"Укажи ставку! Пример: `!слоты 100`",
            color=0xff0000
        )
        await ctx.send(embed=embed)
        return
    
    user_id = str(ctx.author.id)
    
    if user_id not in user_data:
        user_data[user_id] = {'coins': 0, 'total_coins_earned': 0, 'username': str(ctx.author), 'items': []}
    
    coins = user_data[user_id].get('coins', 0)
    
    if bet < CASINO_SETTINGS['min_bet']:
        embed = discord.Embed(
            title=f"❌ **ОШИБКА**",
            description=f"Минимальная ставка: {CASINO_SETTINGS['min_bet']} 🪙",
            color=0xff0000
        )
        await ctx.send(embed=embed)
        return
    
    if bet > CASINO_SETTINGS['max_bet']:
        embed = discord.Embed(
            title=f"❌ **ОШИБКА**",
            description=f"Максимальная ставка: {CASINO_SETTINGS['max_bet']} 🪙",
            color=0xff0000
        )
        await ctx.send(embed=embed)
        return
    
    if coins < bet:
        embed = discord.Embed(
            title=f"❌ **ОШИБКА**",
            description=f"Недостаточно коинов! У тебя: {coins} 🪙",
            color=0xff0000
        )
        await ctx.send(embed=embed)
        return
    
    # Символы для слотов
    symbols = ['🍒', '🍋', '🍊', '🍇', '💎', '7⃣']
    weights = [50, 30, 15, 7, 3, 1]  # Вероятности выпадения
    
    # Крутим слоты
    slot1 = random.choices(symbols, weights=weights)[0]
    slot2 = random.choices(symbols, weights=weights)[0]
    slot3 = random.choices(symbols, weights=weights)[0]
    
    # Проверяем выигрыш
    multiplier = 0
    if slot1 == slot2 == slot3:
        multiplier = CASINO_SETTINGS['slot_mult'].get(slot1, 1)
    
    if multiplier > 0:
        winnings = bet * multiplier
        user_data[user_id]['coins'] += winnings - bet
        result_text = f"🎉 **ДЖЕКПОТ!** +{winnings - bet} 🪙 (x{multiplier})"
        color = 0x00ff00
    else:
        user_data[user_id]['coins'] -= bet
        result_text = f"😢 **ПРОИГРЫШ** -{bet} 🪙"
        color = 0xff0000
    
    save_data(user_data)
    
    embed = discord.Embed(
        title=f"🎰 **СЛОТЫ**",
        color=color
    )
    
    embed.add_field(name="👤 Игрок", value=ctx.author.mention, inline=True)
    embed.add_field(name="🎰 Результат", value=f"`{slot1}` `{slot2}` `{slot3}`", inline=False)
    embed.add_field(name="💰 Итог", value=result_text, inline=False)
    embed.add_field(name="🪙 Новый баланс", value=f"{user_data[user_id]['coins']} 🪙", inline=False)
    
    await ctx.send(embed=embed)

# ============== КОМАНДА !РУЛЕТКА ==============
@bot.command(name='рулетка', aliases=['roulette'])
async def roulette_command(ctx, color: str = None, bet: int = None):
    """!рулетка [цвет] [ставка] - ставка на красное/черное"""
    
    if color is None or bet is None:
        embed = discord.Embed(
            title=f"❌ **ОШИБКА**",
            description=f"Укажи цвет и ставку! Пример: `!рулетка красное 100`",
            color=0xff0000
        )
        await ctx.send(embed=embed)
        return
    
    color = color.lower()
    if color not in ['красное', 'черное', 'красный', 'черный', 'red', 'black']:
        embed = discord.Embed(
            title=f"❌ **ОШИБКА**",
            description=f"Цвет должен быть 'красное' или 'черное'",
            color=0xff0000
        )
        await ctx.send(embed=embed)
        return
    
    # Нормализуем цвет
    if color in ['красное', 'красный', 'red']:
        bet_color = 'красное'
    else:
        bet_color = 'черное'
    
    user_id = str(ctx.author.id)
    
    if user_id not in user_data:
        user_data[user_id] = {'coins': 0, 'total_coins_earned': 0, 'username': str(ctx.author), 'items': []}
    
    coins = user_data[user_id].get('coins', 0)
    
    if bet < CASINO_SETTINGS['min_bet']:
        embed = discord.Embed(
            title=f"❌ **ОШИБКА**",
            description=f"Минимальная ставка: {CASINO_SETTINGS['min_bet']} 🪙",
            color=0xff0000
        )
        await ctx.send(embed=embed)
        return
    
    if bet > CASINO_SETTINGS['max_bet']:
        embed = discord.Embed(
            title=f"❌ **ОШИБКА**",
            description=f"Максимальная ставка: {CASINO_SETTINGS['max_bet']} 🪙",
            color=0xff0000
        )
        await ctx.send(embed=embed)
        return
    
    if coins < bet:
        embed = discord.Embed(
            title=f"❌ **ОШИБКА**",
            description=f"Недостаточно коинов! У тебя: {coins} 🪙",
            color=0xff0000
        )
        await ctx.send(embed=embed)
        return
    
    # Крутим рулетку (0 - зеленый, 1-7 - красные, 8-14 - черные)
    number = random.randint(0, 14)
    
    if number == 0:
        result_color = 'зеленое'
        win = False
    elif 1 <= number <= 7:
        result_color = 'красное'
        win = (bet_color == 'красное')
    else:
        result_color = 'черное'
        win = (bet_color == 'черное')
    
    if win:
        winnings = bet * 2
        user_data[user_id]['coins'] += winnings - bet
        result_text = f"🎉 **ВЫИГРЫШ!** +{winnings - bet} 🪙 (x2)"
        color_embed = 0x00ff00
    else:
        user_data[user_id]['coins'] -= bet
        if result_color == 'зеленое':
            result_text = f"💚 **ЗЕЛЕНОЕ!** -{bet} 🪙 (проигрыш)"
        else:
            result_text = f"😢 **ПРОИГРЫШ** -{bet} 🪙"
        color_embed = 0xff0000
    
    save_data(user_data)
    
    embed = discord.Embed(
        title=f"🎡 **РУЛЕТКА**",
        color=color_embed
    )
    
    embed.add_field(name="👤 Игрок", value=ctx.author.mention, inline=True)
    embed.add_field(name="🎯 Ставка", value=f"{bet_color}", inline=True)
    embed.add_field(name="📊 Результат", value=f"**{result_color}** (число {number})", inline=True)
    embed.add_field(name="💰 Итог", value=result_text, inline=False)
    embed.add_field(name="🪙 Новый баланс", value=f"{user_data[user_id]['coins']} 🪙", inline=False)
    
    await ctx.send(embed=embed)

# ============== КОМАНДА !БОНУС ==============
@bot.command(name='бонус', aliases=['bonus', 'daily'])
async def bonus_command(ctx):
    """!бонус - получить ежедневный бонус (раз в 24 часа)"""
    
    user_id = str(ctx.author.id)
    
    if user_id not in user_data:
        user_data[user_id] = {'coins': 0, 'total_coins_earned': 0, 'username': str(ctx.author), 'items': [], 'last_bonus': 0}
    
    current_time = time.time()
    last_bonus = user_data[user_id].get('last_bonus', 0)
    
    # Проверяем, прошло ли 24 часа
    if current_time - last_bonus < 86400:  # 24 часа в секундах
        time_left = 86400 - (current_time - last_bonus)
        hours = int(time_left // 3600)
        minutes = int((time_left % 3600) // 60)
        
        embed = discord.Embed(
            title=f"⏰ **БОНУС НЕДОСТУПЕН**",
            description=f"Следующий бонус через {hours} ч {minutes} мин",
            color=0xffaa00
        )
        await ctx.send(embed=embed)
        return
    
    # Рассчитываем бонус (случайный)
    bonus = random.randint(30, 50)
    
    user_data[user_id]['coins'] += bonus
    user_data[user_id]['total_coins_earned'] += bonus
    user_data[user_id]['last_bonus'] = current_time
    save_data(user_data)
    
    embed = discord.Embed(
        title=f"🎁 **ЕЖЕДНЕВНЫЙ БОНУС**",
        description=f"{ctx.author.mention}, ты получил **{bonus}** 🪙!",
        color=0x00ff00
    )
    embed.add_field(name="💰 Текущий баланс", value=f"{user_data[user_id]['coins']} 🪙", inline=False)
    embed.add_field(name="⏰ Следующий бонус", value="через 24 часа", inline=False)
    
    await ctx.send(embed=embed)

# ============== КОМАНДА !ВЫДАТЬРОЛЬ ==============
@bot.command(name='выдатьроль', aliases=['giverole', 'temprole'])
@commands.has_permissions(administrator=True)
async def give_temp_role_command(ctx, member: discord.Member, role_input: str, duration: str):
    """Выдать временную роль пользователю"""
    role = None
    
    try:
        role_id = int(role_input.strip('<>@&'))
        role = ctx.guild.get_role(role_id)
    except:
        role = discord.utils.get(ctx.guild.roles, name=role_input.strip('<>@&'))
    
    if role is None:
        embed = discord.Embed(
            title=f"❌ **ОШИБКА**",
            description=f"Роль `{role_input}` не найдена!\nИспользуй @роль или ID роли",
            color=0xff0000
        )
        await ctx.send(embed=embed)
        return
    
    duration = duration.lower()
    minutes = 0
    
    try:
        if duration.endswith('м'):
            minutes = int(duration[:-1])
        elif duration.endswith('ч'):
            minutes = int(duration[:-1]) * 60
        elif duration.endswith('д'):
            minutes = int(duration[:-1]) * 1440
        else:
            minutes = int(duration)
    except:
        embed = discord.Embed(
            title=f"❌ **ОШИБКА**",
            description=f"Неправильный формат времени! Используй: 30м, 2ч, 1д",
            color=0xff0000
        )
        await ctx.send(embed=embed)
        return
    
    if minutes <= 0:
        embed = discord.Embed(
            title=f"❌ **ОШИБКА**",
            description=f"Время должно быть положительным!",
            color=0xff0000
        )
        await ctx.send(embed=embed)
        return
    
    if minutes > 43200:
        embed = discord.Embed(
            title=f"❌ **ОШИБКА**",
            description=f"Максимальная длительность - 30 дней!",
            color=0xff0000
        )
        await ctx.send(embed=embed)
        return
    
    try:
        saved_roles = []
        removed_roles = []
        
        if role.id in REPLACEMENT_ROLES:
            roles_to_remove = []
            
            for member_role in member.roles:
                if (member_role.id not in WHITELISTED_ROLES and 
                    member_role.id != role.id and 
                    member_role.id != ctx.guild.id):
                    roles_to_remove.append(member_role)
                    saved_roles.append(member_role.id)
            
            if roles_to_remove:
                for remove_role in roles_to_remove:
                    try:
                        await member.remove_roles(remove_role, reason=f"Замена ролями от {ctx.author}")
                        removed_roles.append(remove_role.name)
                    except:
                        if remove_role.id in saved_roles:
                            saved_roles.remove(remove_role.id)
        
        await member.add_roles(role, reason=f"Временная роль от {ctx.author}")
        
        user_id = str(member.id)
        expires = datetime.now().timestamp() + (minutes * 60)
        
        if user_id not in temp_roles:
            temp_roles[user_id] = []
        
        temp_role_data = {
            'role_id': role.id,
            'expires': expires,
            'item_id': f"admin_{ctx.author.id}_{int(time.time())}",
            'saved_roles': saved_roles
        }
        
        role_exists = False
        for existing_role in temp_roles[user_id]:
            if existing_role['role_id'] == role.id:
                existing_role['expires'] = expires
                existing_role['saved_roles'] = saved_roles
                role_exists = True
                save_temp_roles()
                break
        
        if not role_exists:
            temp_roles[user_id].append(temp_role_data)
            save_temp_roles()
        
        if minutes < 60:
            time_str = f"{minutes} мин"
        elif minutes < 1440:
            time_str = f"{minutes//60} ч"
        else:
            time_str = f"{minutes//1440} дн"
        
        expire_time = datetime.fromtimestamp(expires).strftime("%d.%m.%Y %H:%M")
        
        embed = discord.Embed(
            title=f"✅ **ВРЕМЕННАЯ РОЛЬ ВЫДАНА**",
            color=0x00ff00
        )
        
        embed.add_field(name="👤 Пользователь", value=member.mention, inline=True)
        embed.add_field(name="🎭 Роль", value=role.mention, inline=True)
        embed.add_field(name="⏰ Длительность", value=time_str, inline=True)
        
        if saved_roles:
            saved_roles_names = []
            for role_id in saved_roles[:5]:
                saved_role = ctx.guild.get_role(role_id)
                if saved_role:
                    saved_roles_names.append(saved_role.name)
            
            embed.add_field(
                name="💾 **СОХРАНЁННЫЕ РОЛИ**", 
                value=f"Будут возвращены через {time_str}\n```{', '.join(saved_roles_names)}{'...' if len(saved_roles) > 5 else ''}```", 
                inline=False
            )
        
        if removed_roles:
            embed.add_field(
                name="🗑️ **ВРЕМЕННО УДАЛЁННЫЕ РОЛИ**", 
                value=f"Удалено ролей: {len(removed_roles)}\n```{', '.join(removed_roles[:5])}{'...' if len(removed_roles) > 5 else ''}```", 
                inline=False
            )
        
        embed.add_field(name="📅 Истекает", value=expire_time, inline=False)
        embed.add_field(name="👑 Администратор", value=ctx.author.mention, inline=True)
        embed.add_field(name="🆔 ID роли", value=f"`{role.id}`", inline=True)
        
        embed.set_footer(text=f"По истечении времени роли вернутся автоматически")
        embed.timestamp = datetime.now()
        
        await ctx.send(embed=embed)
        
        try:
            dm_embed = discord.Embed(
                title=f"⏰ **ВРЕМЕННАЯ РОЛЬ**",
                description=f"Вам выдана временная роль на сервере **{ctx.guild.name}**",
                color=0x3498db
            )
            dm_embed.add_field(name="🎭 Роль", value=role.name, inline=True)
            dm_embed.add_field(name="⏰ Длительность", value=time_str, inline=True)
            
            if saved_roles:
                dm_embed.add_field(
                    name="💾 Сохранённые роли", 
                    value=f"{len(saved_roles)} ролей будут возвращены после истечения", 
                    inline=False
                )
            
            dm_embed.add_field(name="📅 Истекает", value=expire_time, inline=False)
            dm_embed.add_field(name="👑 Администратор", value=ctx.author.name, inline=True)
            dm_embed.set_footer(text="✅ Ваши старые роли будут возвращены автоматически")
            
            await member.send(embed=dm_embed)
        except:
            pass
        
    except discord.Forbidden:
        embed = discord.Embed(
            title=f"❌ **ОШИБКА**",
            description=f"У бота нет прав на выдачу/удаление ролей!\nПроверь, что роль бота выше всех изменяемых ролей",
            color=0xff0000
        )
        await ctx.send(embed=embed)
    except Exception as e:
        embed = discord.Embed(
            title=f"❌ **ОШИБКА**",
            description=f"Произошла ошибка: {e}",
            color=0xff0000
        )
        await ctx.send(embed=embed)

# ============== КОМАНДА !СОХРАНЁННЫЕ ==============
@bot.command(name='сохранённые', aliases=['saved', 'хранимые'])
async def saved_roles_command(ctx, member: discord.Member = None):
    """Показывает какие роли сохранены для возврата"""
    if member is None:
        member = ctx.author
    
    user_id = str(member.id)
    
    if user_id not in temp_roles or not temp_roles[user_id]:
        embed = discord.Embed(
            title=f"💾 **СОХРАНЁННЫЕ РОЛИ**",
            description=f"У {member.mention} нет ролей, ожидающих возврата",
            color=0xff0000
        )
        await ctx.send(embed=embed)
        return
    
    embed = discord.Embed(
        title=f"💾 **СОХРАНЁННЫЕ РОЛИ {member.display_name}**",
        color=0x3498db
    )
    embed.set_author(name=member.display_name, icon_url=member.avatar.url if member.avatar else member.default_avatar.url)
    
    current_time = datetime.now().timestamp()
    saved_text = ""
    
    for role_data in temp_roles[user_id]:
        if 'saved_roles' in role_data and role_data['saved_roles']:
            temp_role = ctx.guild.get_role(role_data['role_id'])
            temp_role_name = temp_role.name if temp_role else "Неизвестная роль"
            
            time_left = role_data['expires'] - current_time
            if time_left > 0:
                hours = int(time_left // 3600)
                minutes = int((time_left % 3600) // 60)
                
                if hours > 0:
                    time_str = f"{hours} ч {minutes} мин"
                else:
                    time_str = f"{minutes} мин"
                
                saved_text += f"**Временная роль:** {temp_role_name}\n"
                saved_text += f"⏰ Осталось: {time_str}\n"
                saved_text += f"📋 Роли к возврату:\n"
                
                for saved_role_id in role_data['saved_roles'][:5]:
                    saved_role = ctx.guild.get_role(saved_role_id)
                    if saved_role:
                        saved_text += f"  • {saved_role.name}\n"
                
                if len(role_data['saved_roles']) > 5:
                    saved_text += f"  • ... и ещё {len(role_data['saved_roles']) - 5}\n"
                
                saved_text += "\n"
    
    if saved_text:
        embed.description = saved_text
    else:
        embed.description = "Нет ролей, ожидающих возврата"
    
    await ctx.send(embed=embed)

# ============== КОМАНДА !СБРОСИТЬУРОВНИ ==============
@bot.command(name='reset_levels', aliases=['сброситьуровни', 'resetlevels'])
@commands.has_permissions(administrator=True)
async def reset_levels_command(ctx):
    """Сбрасывает все уровни и статистику (только для админов)"""
    
    confirm_msg = await ctx.send("⚠️ **ВНИМАНИЕ!** Вы уверены, что хотите сбросить **ВСЕ УРОВНИ** всех пользователей? Это действие нельзя отменить!\n\nНапишите `да` в течение 30 секунд для подтверждения.")
    
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel and m.content.lower() == 'да'
    
    try:
        await bot.wait_for('message', timeout=30.0, check=check)
    except asyncio.TimeoutError:
        await ctx.send("❌ Операция отменена (таймаут).")
        return
    
    global user_data
    user_data.clear()
    
    save_data(user_data)
    
    global warns_data
    warns_data.clear()
    save_warns()
    
    embed = discord.Embed(
        title=f"✅ **ДАННЫЕ СБРОШЕНЫ**", 
        description=f"Все уровни, статистика и предупреждения были очищены!\n📊 Всего пользователей в системе: {len(user_data)}", 
        color=0x00ff00
    )
    embed.add_field(name="👑 Администратор", value=ctx.author.mention, inline=True)
    embed.set_footer(text="Система готова к новой статистике!")
    
    await ctx.send(embed=embed)

# ============== АДМИН-КОМАНДЫ ЭКОНОМИКИ ==============

# ============== КОМАНДА !SET_BOOST ==============
@bot.command(name='set_boost')
@commands.has_permissions(administrator=True)
async def set_boost_command(ctx, role: discord.Role, multiplier: float):
    """
    !set_boost @роль множитель - настроить бустер для роли
    Пример: !set_boost @Бустер 25% 1.25
    """
    global BOOST_ROLES
    
    if multiplier < 1.0:
        embed = discord.Embed(
            title=f"🔴 Ошибка",
            description=f"Множитель должен быть больше или равен 1.0",
            color=0xff0000
        )
        await ctx.send(embed=embed)
        return
    
    # Сохраняем настройку
    BOOST_ROLES[role.id] = multiplier
    
    # Сохраняем в файл
    save_boosts()
    
    # Очищаем кеш пользователей
    global user_boost_cache
    user_boost_cache.clear()
    
    bonus_percent = (multiplier - 1) * 100
    
    embed = discord.Embed(
        title=f"⚡ **БУСТЕР НАСТРОЕН**",
        description=f"Роль {role.mention} теперь даёт множитель опыта **x{multiplier}**",
        color=0x00ff00
    )
    embed.add_field(name="📊 Бонус к опыту", value=f"+{bonus_percent:.0f}%", inline=True)
    embed.add_field(name="💾 Сохранение", value="Автоматически сохранено", inline=True)
    
    await ctx.send(embed=embed)


# ============== КОМАНДА !REMOVE_BOOST ==============
@bot.command(name='remove_boost')
@commands.has_permissions(administrator=True)
async def remove_boost_command(ctx, role: discord.Role):
    """
    !remove_boost @роль - убрать бустер у роли
    """
    global BOOST_ROLES
    
    if role.id in BOOST_ROLES:
        old_mult = BOOST_ROLES[role.id]
        del BOOST_ROLES[role.id]
        
        # Сохраняем изменения
        save_boosts()
        
        # Очищаем кеш
        global user_boost_cache
        user_boost_cache.clear()
        
        embed = discord.Embed(
            title=f"✅ **БУСТЕР УБРАН**",
            description=f"Роль {role.mention} больше не даёт бустер (было x{old_mult})",
            color=0x00ff00
        )
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(
            title=f"🔴 Ошибка",
            description=f"У роли {role.mention} нет настроенного бустера",
            color=0xff0000
        )
        await ctx.send(embed=embed)


# ============== КОМАНДА !LIST_BOOSTS ==============
@bot.command(name='list_boosts')
@commands.has_permissions(administrator=True)
async def list_boosts_command(ctx):
    """
    !list_boosts - показать все настроенные бустеры
    """
    if not BOOST_ROLES:
        embed = discord.Embed(
            title=f"📋 **СПИСОК БУСТЕРОВ**",
            description="Пока нет настроенных бустеров",
            color=0xffaa00
        )
        await ctx.send(embed=embed)
        return
    
    embed = discord.Embed(
        title=f"⚡ **СПИСОК БУСТЕРОВ**",
        description=f"Настроено ролей: {len(BOOST_ROLES)}",
        color=0x3498db
    )
    
    boost_text = ""
    for role_id, multiplier in BOOST_ROLES.items():
        role = ctx.guild.get_role(role_id)
        if role:
            bonus = (multiplier - 1) * 100
            boost_text += f"• {role.mention} → **x{multiplier}** (+{bonus:.0f}%)\n"
        else:
            boost_text += f"• Роль ID: `{role_id}` (удалена) → x{multiplier}\n"
    
    embed.add_field(name="📊 **АКТИВНЫЕ БУСТЕРЫ**", value=boost_text, inline=False)
    
    await ctx.send(embed=embed)

@bot.command(name='give_coins')
@commands.has_permissions(administrator=True)
async def give_coins_command(ctx, member: discord.Member, amount: int):
    """!give_coins @пользователь [количество] - выдать коины"""
    user_id = str(member.id)
    
    if user_id not in user_data:
        user_data[user_id] = {'coins': 0, 'total_coins_earned': 0, 'username': str(member), 'items': []}
    
    user_data[user_id]['coins'] += amount
    user_data[user_id]['total_coins_earned'] += amount
    save_data(user_data)
    
    embed = discord.Embed(
        title=f"✅ **КОИНЫ ВЫДАНЫ**", 
        description=f"{member.mention} получил **{amount}** 🪙!", 
        color=0x00ff00
    )
    embed.add_field(name="💰 Новый баланс", value=f"**{user_data[user_id]['coins']}** 🪙", inline=False)
    await ctx.send(embed=embed)


@bot.command(name='set_voice_xp')
@commands.has_permissions(administrator=True)
async def set_voice_xp_command(ctx, xp_per_minute: int):
    """!set_voice_xp [количество] - изменить XP за минуту в войсе"""
    global XP_PER_VOICE_MINUTE
    XP_PER_VOICE_MINUTE = xp_per_minute
    
    embed = discord.Embed(
        title=f"⚡ **НАСТРОЙКИ ИЗМЕНЕНЫ**", 
        description=f"Опыт за минуту в войсе установлен: **{xp_per_minute} XP**", 
        color=0x00ff00
    )
    await ctx.send(embed=embed)

@bot.command(name='сброситьоборот', aliases=['resetcoins', 'сброситькоины'])
@commands.has_permissions(administrator=True)
async def reset_coins_command(ctx, member: discord.Member = None):
    """
    !сброситьоборот @пользователь - сбросить оборот коинов пользователя
    !сброситьоборот all - сбросить оборот ВСЕХ пользователей
    """
    
    # Сброс всех пользователей
    if member is None and ctx.message.content.endswith('all'):
        # Запрашиваем подтверждение
        confirm_msg = await ctx.send("⚠️ **ВНИМАНИЕ!** Вы уверены, что хотите сбросить **ОБОРОТ КОИНОВ** всех пользователей? Это действие нельзя отменить!\n\nНапишите `да` в течение 30 секунд для подтверждения.")
        
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel and m.content.lower() == 'да'
        
        try:
            await bot.wait_for('message', timeout=30.0, check=check)
        except asyncio.TimeoutError:
            await ctx.send("❌ Операция отменена (таймаут).")
            return
        
        total_reset = 0
        for user_id in user_data:
            if 'total_coins_earned' in user_data[user_id]:
                total_reset += user_data[user_id]['total_coins_earned']
                user_data[user_id]['total_coins_earned'] = 0
        
        save_data(user_data)
        
        embed = discord.Embed(
            title=f"💰 **ОБОРОТ СБРОШЕН**",
            description=f"Оборот коинов **ВСЕХ** пользователей сброшен!\nВсего сброшено: **{total_reset}** 🪙",
            color=0x00ff00
        )
        embed.add_field(name="👑 Администратор", value=ctx.author.mention, inline=True)
        await ctx.send(embed=embed)
        return
    
    # Сброс конкретного пользователя
    if member is None:
        embed = discord.Embed(
            title=f"❌ **ОШИБКА**",
            description=f"Укажи пользователя: `!сброситьоборот @пользователь`\nИли для всех: `!сброситьоборот all`",
            color=0xff0000
        )
        await ctx.send(embed=embed)
        return
    
    user_id = str(member.id)
    
    if user_id not in user_data:
        embed = discord.Embed(
            title=f"ℹ️ **НЕТ ДАННЫХ**",
            description=f"У {member.mention} нет данных в системе",
            color=0xffaa00
        )
        await ctx.send(embed=embed)
        return
    
    old_oborot = user_data[user_id].get('total_coins_earned', 0)
    user_data[user_id]['total_coins_earned'] = 0
    save_data(user_data)
    
    embed = discord.Embed(
        title=f"💰 **ОБОРОТ СБРОШЕН**",
        description=f"У {member.mention} сброшен оборот коинов",
        color=0x00ff00
    )
    embed.add_field(name="📊 Было сброшено", value=f"**{old_oborot}** 🪙", inline=True)
    embed.add_field(name="👑 Администратор", value=ctx.author.mention, inline=True)
    await ctx.send(embed=embed)

# ============== АДМИН-КОМАНДЫ ДЛЯ МАГАЗИНА ==============

@bot.command(name='add_item')
@commands.has_permissions(administrator=True)
async def add_item_command(ctx, item_id: str, price: int, *, name: str):
    """!add_item [ID] [цена] [название] - добавить обычный товар"""
    if item_id in shop_data:
        embed = discord.Embed(
            title=f"🔴 Ошибка",
            description=f"Товар с ID `{item_id}` уже существует!",
            color=0xff0000
        )
        await ctx.send(embed=embed)
        return
    
    shop_data[item_id] = {
        'name': name, 
        'price': price, 
        'description': 'Нет описания'
    }
    save_shop(shop_data)
    
    embed = discord.Embed(
        title=f"✅ **ТОВАР ДОБАВЛЕН**", 
        description=f"ID: `{item_id}`\nНазвание: **{name}**\nЦена: **{price}** 🪙", 
        color=0x00ff00
    )
    await ctx.send(embed=embed)


@bot.command(name='add_temp_item')
@commands.has_permissions(administrator=True)
async def add_temp_item_command(ctx, item_id: str, price: int, duration: int, *, name: str):
    """!add_temp_item [ID] [цена] [минуты] [название] - добавить временный товар"""
    if item_id in shop_data:
        embed = discord.Embed(
            title=f"🔴 Ошибка",
            description=f"Товар с ID `{item_id}` уже существует!",
            color=0xff0000
        )
        await ctx.send(embed=embed)
        return
    
    # Форматируем время для красивого отображения
    if duration < 60:
        time_str = f"{duration} мин"
    elif duration < 1440:
        time_str = f"{duration//60} ч"
    else:
        time_str = f"{duration//1440} дн"
    
    shop_data[item_id] = {
        'name': name,
        'price': price,
        'description': f'Временный товар на {time_str}',
        'duration': duration
    }
    save_shop(shop_data)
    
    embed = discord.Embed(
        title=f"✅ **ВРЕМЕННЫЙ ТОВАР ДОБАВЛЕН**",
        description=f"ID: `{item_id}`\nНазвание: **{name}**\nЦена: **{price}** 🪙\nДлительность: **{time_str}**",
        color=0x00ff00
    )
    await ctx.send(embed=embed)


@bot.command(name='remove_item')
@commands.has_permissions(administrator=True)
async def remove_item_command(ctx, item_id: str):
    """!remove_item [ID] - удалить товар"""
    if item_id not in shop_data:
        embed = discord.Embed(
            title=f"🔴 Ошибка",
            description=f"Товар с ID `{item_id}` не найден!",
            color=0xff0000
        )
        await ctx.send(embed=embed)
        return
    
    item_name = shop_data[item_id]['name']
    del shop_data[item_id]
    save_shop(shop_data)
    
    embed = discord.Embed(
        title=f"✅ **ТОВАР УДАЛЁН**", 
        description=f"Товар **{item_name}** (ID: `{item_id}`) удалён из магазина", 
        color=0x00ff00
    )
    await ctx.send(embed=embed)


@bot.command(name='edit_item')
@commands.has_permissions(administrator=True)
async def edit_item_command(ctx, item_id: str, field: str, *, value):
    """!edit_item [ID] [field] [value] - изменить товар (field: name, price, description, duration)"""
    if item_id not in shop_data:
        embed = discord.Embed(
            title=f"🔴 Ошибка",
            description=f"Товар с ID `{item_id}` не найден!",
            color=0xff0000
        )
        await ctx.send(embed=embed)
        return
    
    if field.lower() == 'name':
        old = shop_data[item_id]['name']
        shop_data[item_id]['name'] = value
        field_name = "Название"
    elif field.lower() == 'price':
        try:
            value = int(value)
            old = shop_data[item_id]['price']
            shop_data[item_id]['price'] = value
            field_name = "Цена"
        except:
            embed = discord.Embed(
                title=f"🔴 Ошибка",
                description=f"Цена должна быть числом!",
                color=0xff0000
            )
            await ctx.send(embed=embed)
            return
    elif field.lower() == 'description':
        old = shop_data[item_id].get('description', 'Нет описания')
        shop_data[item_id]['description'] = value
        field_name = "Описание"
    elif field.lower() == 'duration':
        try:
            value = int(value)
            old = shop_data[item_id].get('duration', 0)
            shop_data[item_id]['duration'] = value
            field_name = "Длительность"
        except:
            embed = discord.Embed(
                title=f"🔴 Ошибка",
                description=f"Длительность должна быть числом (в минутах)!",
                color=0xff0000
            )
            await ctx.send(embed=embed)
            return
    else:
        embed = discord.Embed(
            title=f"🔴 Ошибка", 
            description=f"Поле должно быть: name, price, description или duration", 
            color=0xff0000
        )
        await ctx.send(embed=embed)
        return
    
    save_shop(shop_data)
    
    # Красивое отображение времени для duration
    if field.lower() == 'duration':
        if value < 60:
            display_value = f"{value} мин"
        elif value < 1440:
            display_value = f"{value//60} ч"
        else:
            display_value = f"{value//1440} дн"
        
        if old < 60:
            old_display = f"{old} мин"
        elif old < 1440:
            old_display = f"{old//60} ч"
        else:
            old_display = f"{old//1440} дн"
        
        embed = discord.Embed(
            title=f"✅ **ТОВАР ИЗМЕНЁН**", 
            description=f"ID: `{item_id}`\n{field_name}: `{old_display}` → `{display_value}`", 
            color=0x00ff00
        )
    else:
        embed = discord.Embed(
            title=f"✅ **ТОВАР ИЗМЕНЁН**", 
            description=f"ID: `{item_id}`\n{field_name}: `{old}` → `{value}`", 
            color=0x00ff00
        )
    
    await ctx.send(embed=embed)


@bot.command(name='set_role')
@commands.has_permissions(administrator=True)
async def set_role_command(ctx, item_id: str, role: discord.Role):
    """!set_role [ID товара] @роль - привязать роль к товару"""
    if item_id not in shop_data:
        embed = discord.Embed(
            title=f"🔴 Ошибка",
            description=f"Товар с ID `{item_id}` не найден!",
            color=0xff0000
        )
        await ctx.send(embed=embed)
        return
    
    shop_data[item_id]['role_id'] = role.id
    save_shop(shop_data)
    
    boost_info = ""
    if role.id in BOOST_ROLES:
        boost_mult = BOOST_ROLES[role.id]
        boost_info = f"\n⚡ У этой роли есть бустер x{boost_mult}!"
    
    duration_info = ""
    if 'duration' in shop_data[item_id]:
        duration = shop_data[item_id]['duration']
        if duration < 60:
            time_str = f"{duration} мин"
        elif duration < 1440:
            time_str = f"{duration//60} ч"
        else:
            time_str = f"{duration//1440} дн"
        duration_info = f"\n⏰ Временная роль на {time_str}"
    
    embed = discord.Embed(
        title=f"✅ **РОЛЬ ПРИВЯЗАНА**", 
        description=f"К товару **{shop_data[item_id]['name']}** привязана роль {role.mention}{boost_info}{duration_info}", 
        color=0x00ff00
    )
    await ctx.send(embed=embed)


@bot.command(name='remove_role')
@commands.has_permissions(administrator=True)
async def remove_role_command(ctx, item_id: str):
    """!remove_role [ID товара] - убрать привязку роли у товара"""
    if item_id not in shop_data:
        embed = discord.Embed(
            title=f"🔴 Ошибка",
            description=f"Товар с ID `{item_id}` не найден!",
            color=0xff0000
        )
        await ctx.send(embed=embed)
        return
    
    if 'role_id' in shop_data[item_id]:
        del shop_data[item_id]['role_id']
        save_shop(shop_data)
        
        embed = discord.Embed(
            title=f"✅ **РОЛЬ УДАЛЕНА**", 
            description=f"У товара **{shop_data[item_id]['name']}** больше нет привязанной роли", 
            color=0x00ff00
        )
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(
            title=f"🔴 Ошибка", 
            description=f"У товара **{shop_data[item_id]['name']}** нет привязанной роли!", 
            color=0xff0000
        )
        await ctx.send(embed=embed)

@bot.event
async def on_voice_state_update(member, before, after):
    """Отслеживает вход/выход из голосовых каналов"""
    if member.bot:
        return
    
    user_id = str(member.id)
    current_time = datetime.now()
    
    # Пользователь зашёл в голосовой канал
    if before.channel is None and after.channel is not None:
        voice_tracking[user_id] = {
            "channel_id": after.channel.id,
            "join_time": current_time,
            "total_earned": 0
        }
        print(f"🔊 {member.display_name} зашёл в {after.channel.name}")
    
    # Пользователь вышел из голосового канала
    elif before.channel is not None and after.channel is None:
        if user_id in voice_tracking:
            join_time = voice_tracking[user_id]["join_time"]
            leave_time = current_time
            minutes_voice = (leave_time - join_time).total_seconds() / 60
            
            if minutes_voice >= 1:
                # Получаем бустер пользователя
                boost_multiplier = get_user_boost(member)
                xp_earned = int(minutes_voice * XP_PER_VOICE_MINUTE * boost_multiplier)
                
                # Инициализируем данные пользователя если нужно
                if user_id not in user_data:
                    user_data[user_id] = {
                        'xp': 0, 'level': 0, 'total_xp': 0, 'voice_xp': 0, 'message_xp': 0,
                        'username': str(member), 'messages': 0, 'voice_time': 0,
                        'coins': 0, 'total_coins_earned': 0, 'items': [],
                        'last_message_time': datetime.now().isoformat()
                    }
                
                # Запоминаем старый уровень
                old_level = user_data[user_id]['level']
                
                # Начисляем опыт
                user_data[user_id]['voice_xp'] += xp_earned
                user_data[user_id]['voice_time'] += int(minutes_voice)
                
                # Пересчитываем общий опыт
                total_xp = user_data[user_id]['message_xp'] + user_data[user_id]['voice_xp']
                user_data[user_id]['total_xp'] = total_xp
                
                # Проверяем повышение уровня
                new_level, current_xp, xp_needed = calculate_level(total_xp)
                
                if new_level > old_level:
                    user_data[user_id]['level'] = new_level
                    user_data[user_id]['xp'] = current_xp
                    
                    # Уведомление о повышении уровня
                    try:
                        channel = member.guild.system_channel or member.guild.text_channels[0]
                        embed = discord.Embed(
                            title=f"🔴 **ПОВЫШЕНИЕ УРОВНЯ В ВОЙСЕ!**", 
                            description=f"{member.mention} достиг **{new_level}** уровня!\nПолучено **{xp_earned}** XP",
                            color=0xff0000
                        )
                        await channel.send(embed=embed)
                    except:
                        pass
                
                print(f"🔊 {member.display_name} получил {xp_earned} XP за {int(minutes_voice)} минут в войсе (бустер x{boost_multiplier})")
                save_data(user_data)
            
            # Удаляем из отслеживания
            del voice_tracking[user_id]
    
    # Пользователь переключил канал
    elif before.channel is not None and after.channel is not None and before.channel != after.channel:
        if user_id in voice_tracking:
            voice_tracking[user_id]["channel_id"] = after.channel.id
            print(f"🔊 {member.display_name} перешёл в {after.channel.name}")
async def voice_xp_loop():
    """Начисляет опыт каждую минуту за нахождение в войсе"""
    await bot.wait_until_ready()
    
    while not bot.is_closed():
        try:
            current_time = datetime.now()
            
            for user_id, data in list(voice_tracking.items()):
                join_time = data["join_time"]
                minutes_passed = int((current_time - join_time).total_seconds() / 60)
                
                # Начисляем опыт за каждую полную минуту
                if minutes_passed > data["total_earned"]:
                    # Находим пользователя на сервере
                    member = None
                    for guild in bot.guilds:
                        member = guild.get_member(int(user_id))
                        if member:
                            break
                    
                    if member:
                        # Получаем бустер
                        boost_multiplier = get_user_boost(member)
                        xp_gained = int(XP_PER_VOICE_MINUTE * boost_multiplier)
                        
                        # Инициализируем данные
                        if user_id not in user_data:
                            try:
                                username = str(member) if member else "Unknown"
                            except:
                                username = "Unknown"
                            
                            user_data[user_id] = {
                                'xp': 0, 'level': 0, 'total_xp': 0, 'voice_xp': 0, 'message_xp': 0,
                                'username': username, 'messages': 0, 'voice_time': 0,
                                'coins': 0, 'total_coins_earned': 0, 'items': [],
                                'last_message_time': datetime.now().isoformat()
                            }
                        
                        old_level = user_data[user_id]['level']
                        
                        # Начисляем опыт
                        user_data[user_id]['voice_xp'] += xp_gained
                        user_data[user_id]['voice_time'] += 1
                        
                        # Пересчитываем общий опыт
                        total_xp = user_data[user_id]['message_xp'] + user_data[user_id]['voice_xp']
                        user_data[user_id]['total_xp'] = total_xp
                        
                        # Проверяем уровень
                        new_level, current_xp, xp_needed = calculate_level(total_xp)
                        
                        if new_level > old_level:
                            user_data[user_id]['level'] = new_level
                            user_data[user_id]['xp'] = current_xp
                        
                        # Обновляем счётчик начислений
                        voice_tracking[user_id]["total_earned"] = minutes_passed
                        save_data(user_data)
                        
                        print(f"⏱️ {member.name} +{xp_gained} XP за минуту в войсе")
            
        except Exception as e:
            print(f"❌ Ошибка в voice_xp_loop: {e}")
        
        await asyncio.sleep(60)
        
@bot.event
async def setup_hook():
    bot.loop.create_task(voice_xp_loop())
    print("✅ Фоновая задача для войса запущена!")

# ============== СИСТЕМА ПРИГЛАШЕНИЙ ==============
import datetime

# ID ролей вербовщика
INVITE_ROLES = {
    3: 1476307246597148883,   # Вербовщик I - 3 приглашения
    5: 1476307365945938035,   # Вербовщик II - 5 приглашений
    10: None                   # Вербовщик III - ID нужно будет добавить
}

# Файл для хранения данных приглашений
INVITES_FILE = 'invites_data.json'

def load_invites():
    """Загружает данные о приглашениях"""
    if os.path.exists(INVITES_FILE):
        with open(INVITES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_invites(invites):
    """Сохраняет данные о приглашениях"""
    with open(INVITES_FILE, 'w', encoding='utf-8') as f:
        json.dump(invites, f, indent=4, ensure_ascii=False)

# Загружаем данные о приглашениях
invites_data = load_invites()

@bot.event
async def on_member_join(member):
    """Срабатывает, когда новый пользователь заходит на сервер"""
    guild = member.guild
    
    # Получаем приглашения до и после
    invites_before = await guild.invites()
    
    # Нужно подождать немного, чтобы обновились приглашения
    await asyncio.sleep(1)
    
    invites_after = await guild.invites()
    
    # Ищем, какое приглашение было использовано
    for invite in invites_before:
        for new_invite in invites_after:
            if invite.code == new_invite.code:
                if new_invite.uses > invite.uses:
                    # Нашли того, кто пригласил
                    inviter = new_invite.inviter
                    
                    if inviter:
                        inviter_id = str(inviter.id)
                        
                        # Инициализируем данные если нужно
                        if inviter_id not in invites_data:
                            invites_data[inviter_id] = {
                                'username': str(inviter),
                                'invites': 0,
                                'joined_users': []
                            }
                        
                        # Добавляем приглашение
                        invites_data[inviter_id]['invites'] += 1
                        invites_data[inviter_id]['joined_users'].append({
                            'user_id': member.id,
                            'username': str(member),
                            'joined_at': datetime.now().isoformat()
                        })
                        
                        # Сохраняем
                        save_invites(invites_data)
                        
                        # Проверяем и выдаём роли
                        await check_invite_roles(member.guild, inviter)
                        
                        print(f"✅ {inviter.name} пригласил {member.name}")
                        
                        # Уведомление в ЛС
                        try:
                            embed = discord.Embed(
                                title=f"🎉 **НОВОЕ ПРИГЛАШЕНИЕ**",
                                description=f"Пользователь **{member.name}** присоединился по вашему приглашению!",
                                color=0x00ff00
                            )
                            embed.add_field(name="📊 Всего приглашений", value=f"**{invites_data[inviter_id]['invites']}**", inline=True)
                            await inviter.send(embed=embed)
                        except:
                            pass
                        
                        break

async def check_invite_roles(guild, member):
    """Проверяет и выдаёт роли за приглашения"""
    inviter_id = str(member.id)
    
    if inviter_id not in invites_data:
        return
    
    invites_count = invites_data[inviter_id]['invites']
    
    # Проверяем каждую роль
    for required_invites, role_id in INVITE_ROLES.items():
        if role_id and invites_count >= required_invites:
            role = guild.get_role(role_id)
            if role and role not in member.roles:
                try:
                    await member.add_roles(role, reason=f"Достигнуто {required_invites} приглашений")
                    
                    # Уведомление о новой роли
                    try:
                        embed = discord.Embed(
                            title=f"🎖️ **НОВАЯ РОЛЬ!**",
                            description=f"Вы получили роль **{role.name}** за {required_invites} приглашений!",
                            color=0xffd700
                        )
                        await member.send(embed=embed)
                    except:
                        pass
                    
                    # Уведомление в общий чат
                    try:
                        channel = guild.system_channel or guild.text_channels[0]
                        embed = discord.Embed(
                            title=f"🎉 **НОВАЯ РОЛЬ ВЕРБОВЩИКА**",
                            description=f"{member.mention} получил роль **{role.name}** за {required_invites} приглашений!",
                            color=0xffd700
                        )
                        await channel.send(embed=embed)
                    except:
                        pass
                    
                except:
                    pass

# ============== КОМАНДА !ПРИГ ==============
@bot.command(name='приг', aliases=['invites', 'приглашения'])
async def invites_command(ctx, member: discord.Member = None):
    """!приг - показать количество приглашений"""
    
    if member is None:
        member = ctx.author
    
    user_id = str(member.id)
    
    if user_id not in invites_data:
        embed = discord.Embed(
            title=f"📊 **ПРИГЛАШЕНИЯ**",
            description=f"У {member.mention} пока нет приглашений",
            color=0xffaa00
        )
        await ctx.send(embed=embed)
        return
    
    data = invites_data[user_id]
    invites_count = data['invites']
    joined_users = data.get('joined_users', [])
    
    # Определяем текущую роль
    current_role = "Нет роли"
    for req_invites, role_id in sorted(INVITE_ROLES.items()):
        if role_id and invites_count >= req_invites:
            role = ctx.guild.get_role(role_id)
            if role:
                current_role = role.mention
    
    # Следующая цель
    next_goal = None
    for req_invites, role_id in sorted(INVITE_ROLES.items()):
        if role_id and invites_count < req_invites:
            next_goal = req_invites
            break
    
    embed = discord.Embed(
        title=f"📊 **ПРИГЛАШЕНИЯ {member.display_name}**",
        color=0x3498db
    )
    embed.set_author(name=member.display_name, icon_url=member.avatar.url if member.avatar else member.default_avatar.url)
    
    embed.add_field(name="👥 Приглашений", value=f"**{invites_count}**", inline=True)
    embed.add_field(name="🎖️ Текущая роль", value=current_role, inline=True)
    
    if next_goal:
        embed.add_field(name="🎯 Следующая цель", value=f"**{next_goal}** приглашений", inline=True)
        
        # Прогресс-бар
        progress = int((invites_count / next_goal) * 10)
        bar = "🟩" * progress + "⬜" * (10 - progress)
        embed.add_field(name="📈 Прогресс", value=f"{bar} {invites_count}/{next_goal}", inline=False)
    
    # Последние приглашённые
    if joined_users:
        recent = joined_users[-5:]  # Последние 5
        recent_text = ""
        for user in recent:
            date = datetime.fromisoformat(user['joined_at']).strftime("%d.%m")
            recent_text += f"• {user['username']} ({date})\n"
        embed.add_field(name="📋 Последние приглашённые", value=recent_text, inline=False)
    
    await ctx.send(embed=embed)

# ============== КОМАНДА !ПРИГТОП ==============
@bot.command(name='пригтоп', aliases=['topinvites', 'топприг'])
async def top_invites_command(ctx, page: int = 1):
    """!пригтоп - топ пользователей по приглашениям"""
    
    if not invites_data:
        embed = discord.Embed(
            title=f"🏆 **ТОП ПРИГЛАШЕНИЙ**",
            description="Пока нет данных о приглашениях",
            color=0xffaa00
        )
        await ctx.send(embed=embed)
        return
    
    # Сортируем по количеству приглашений
    sorted_users = sorted(invites_data.items(), key=lambda x: x[1]['invites'], reverse=True)
    
    items_per_page = 10
    total_pages = math.ceil(len(sorted_users) / items_per_page)
    page = max(1, min(page, total_pages))
    
    start_idx = (page - 1) * items_per_page
    end_idx = start_idx + items_per_page
    page_users = sorted_users[start_idx:end_idx]
    
    embed = discord.Embed(
        title=f"🏆 **ТОП ПРИГЛАШЕНИЙ**",
        description=f"Страница {page}/{total_pages}",
        color=0xffd700
    )
    
    top_text = ""
    for i, (user_id, data) in enumerate(page_users, start=start_idx + 1):
        member = ctx.guild.get_member(int(user_id))
        username = member.display_name if member else data.get('username', 'Неизвестный')
        
        if len(username) > 20:
            username = username[:17] + "..."
        
        if i == 1:
            medal = "🥇"
        elif i == 2:
            medal = "🥈"
        elif i == 3:
            medal = "🥉"
        else:
            medal = f"{i}."
        
        invites = data['invites']
        
        # Определяем роль
        role_emoji = ""
        for req_invites, role_id in sorted(INVITE_ROLES.items()):
            if role_id and invites >= req_invites:
                role = ctx.guild.get_role(role_id)
                if role:
                    role_emoji = " 👑"
        
        top_text += f"{medal} **{username}**{role_emoji} — **{invites}** приг.\n"
    
    embed.description = top_text
    embed.set_footer(text=f"📊 Всего участников: {len(sorted_users)}")
    
    await ctx.send(embed=embed)

# ============== КОМАНДА ДЛЯ ОЧИСТКИ ПРИГЛАШЕНИЙ (АДМИН) ==============
@bot.command(name='сброситьприг', aliases=['resetinvites'])
@commands.has_permissions(administrator=True)
async def reset_invites_command(ctx, member: discord.Member = None):
    """
    !сброситьприг @пользователь - сбросить приглашения пользователя
    !сброситьприг all - сбросить приглашения всех пользователей
    """
    
    # Сброс всех
    if member is None and ctx.message.content.endswith('all'):
        confirm_msg = await ctx.send("⚠️ **ВНИМАНИЕ!** Вы уверены, что хотите сбросить **ВСЕ** приглашения? Это действие нельзя отменить!\n\nНапишите `да` в течение 30 секунд для подтверждения.")
        
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel and m.content.lower() == 'да'
        
        try:
            await bot.wait_for('message', timeout=30.0, check=check)
        except asyncio.TimeoutError:
            await ctx.send("❌ Операция отменена (таймаут).")
            return
        
        global invites_data
        invites_data = {}
        save_invites(invites_data)
        
        embed = discord.Embed(
            title=f"✅ **ПРИГЛАШЕНИЯ СБРОШЕНЫ**",
            description=f"Все приглашения всех пользователей сброшены!",
            color=0x00ff00
        )
        embed.add_field(name="👑 Администратор", value=ctx.author.mention, inline=True)
        await ctx.send(embed=embed)
        return
    
    if member is None:
        embed = discord.Embed(
            title=f"❌ **ОШИБКА**",
            description=f"Укажи пользователя: `!сброситьприг @пользователь`\nИли `!сброситьприг all`",
            color=0xff0000
        )
        await ctx.send(embed=embed)
        return
    
    user_id = str(member.id)
    
    if user_id in invites_data:
        old_count = invites_data[user_id]['invites']
        del invites_data[user_id]
        save_invites(invites_data)
        
        # Снимаем роли вербовщика
        for role_id in INVITE_ROLES.values():
            if role_id:
                role = ctx.guild.get_role(role_id)
                if role and role in member.roles:
                    try:
                        await member.remove_roles(role, reason="Сброс приглашений")
                    except:
                        pass
        
        embed = discord.Embed(
            title=f"✅ **ПРИГЛАШЕНИЯ СБРОШЕНЫ**",
            description=f"У {member.mention} сброшено {old_count} приглашений",
            color=0x00ff00
        )
        embed.add_field(name="👑 Администратор", value=ctx.author.mention, inline=True)
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(
            title=f"ℹ️ **НЕТ ДАННЫХ**",
            description=f"У {member.mention} нет приглашений",
            color=0xffaa00
        )
        await ctx.send(embed=embed)

# ============== ЗАПУСК ==============
if __name__ == "__main__":
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        print("❌ ОШИБКА: Токен не найден! Добавь DISCORD_TOKEN в переменные окружения Railway")
    else:
        print(f"✅ Бот запускается...")
        keep_alive()  # Запускаем веб-сервер для поддержания активности
        bot.run(token)














