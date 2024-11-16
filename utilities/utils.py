import os
import datetime
import aiosqlite


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

async def set_cash(db, amount, guild_id, user_id):
    await db.execute('''UPDATE profiles SET cash = ? WHERE guild_id = ? AND user_id = ?''', (amount, guild_id, user_id))
    await db.commit()
