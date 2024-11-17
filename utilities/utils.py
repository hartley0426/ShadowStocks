import os
import datetime
import aiosqlite
import json

CONFIG_FILE_PATH = 'json\settings.json'


def to_money(amount: float) -> str:
    return f"${amount:,.2f}"

def convert_seconds(seconds: int) -> str:
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    remaining_seconds = seconds % 60

    result = []

    if hours > 0:
        if hours > 1:
            result.append(f"{hours} hours")
        else:
            result.append(f"{hours} hour")

    if minutes > 0:
        if minutes > 1:
            result.append(f"{minutes} minutes")
        else:
            result.append(f"{minutes} minute")

    if remaining_seconds > 0:
        if remaining_seconds > 1:
            result.append(f"{remaining_seconds} seconds")
        else:
            result.append(f"{remaining_seconds} second")

    return ", ".join(result)

def to_height(inches: int) -> str:
    feet = inches // 12
    remaining = inches % 12

    result = []

    if feet > 0:
        if feet > 1:
            result.append(f"{feet} feet")
        else:
            result.append(f"{feet} foot")

    if remaining > 0:
        if remaining > 1:
            result.append(f"{remaining} inches")
        else:
            result.append(f"{remaining} inch")

    return ", ".join(result)

def get_time_delta(initial_time : datetime.datetime):
    """Returns the time delta between the current time and the given time in game time."""
    time_delta = datetime.datetime.now() - initial_time

    hours, remainder = divmod(time_delta.seconds, 3600) 
    minutes, seconds = divmod(remainder, 60)
    

    return {
        "days": hours,
        "hours": minutes,
        "minutes": seconds}

async def set_cash(db, amount, guild_id, user_id):
    await db.execute('''UPDATE profiles SET cash = ? WHERE guild_id = ? AND user_id = ?''', (amount, guild_id, user_id))
    await db.commit()

def get_config(guild_id, key):
    with open(CONFIG_FILE_PATH, 'r') as f:
        data = json.load(f)
    return data.get(str(guild_id), {}).get(key, None)
