import datetime
import discord
from discord.ext import commands
import constants

async def send_action_log(bot, log_type: str, action: str, channel_id: str): 
    timestamp = int(datetime.datetime.now().timestamp())
    discord_timestamp = f"<t:{timestamp}:f>"

    embed = discord.Embed(
        title=log_type,
        description=f"`{action}` | {discord_timestamp}",
        colour=constants.colorHexes["DarkBlue"]
    )
    
    channel = bot.get_channel(int(channel_id)) 
    
    if channel: 
        await channel.send(embed=embed)
    else:
        print(f"Channel with ID {channel_id} not found.")

async def send_player_log(bot, log_type: str, action: str, channel_id: str, user: discord.Member, user_2: discord.Member = None): 
    timestamp = int(datetime.datetime.now().timestamp())
    discord_timestamp = f"<t:{timestamp}:f>"

    if user.avatar:
        user_avatar_url = user.avatar.url
    else:
        user_avatar_url = "https://cdn.discordapp.com/avatars/1306443031163179039/2086b84499e71a303ed1fd51a1e02c8b.webp?size=1024&width=768&height=768"
    if user_2 == None:
        embed = discord.Embed(
            title=log_type,
            description=f"`{user}` | `{action}` | {discord_timestamp}",
            colour=constants.colorHexes["DarkBlue"]
        )
    else:
        embed = discord.Embed(
            title=log_type,
            description=f"`{user}` | `{action}` | `{user_2}` | {discord_timestamp}",
            colour=constants.colorHexes["DarkBlue"]
        )

    embed.set_thumbnail(url=user_avatar_url)
    
    channel = bot.get_channel(int(channel_id)) 
    
    if channel: 
        await channel.send(embed=embed)
    else:
        print(f"Channel with ID {channel_id} not found.")