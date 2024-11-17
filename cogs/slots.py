import discord
from discord.ext import commands, tasks
from discord import app_commands
import os
import random
from datetime import datetime, timedelta 
import aiosqlite
import constants
from utilities import utils, logs
from utilities.embeds import basicEmbeds

SYMBOL_LIST = [
    ":apple:", 
    ":green_apple:", 
    ":tangerine: ", 
    ":banana:", 
    ":eggplant: "
]

class Slots(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Slots is ready.")    

    @app_commands.command(name="slots", description="Play a game on a slot machine")
    @app_commands.describe(bet="The ammount of money to bet")
    async def slots(self, interaction: discord.Interaction, bet: int):
        user_id = interaction.user.id
        guild_id = interaction.guild.id
        
        async with aiosqlite.connect('profiles.db') as db:
            async with db.execute('''SELECT cash FROM profiles WHERE guild_id = ? AND user_id = ?''', (guild_id, user_id)) as cursor:
                profile = await cursor.fetchone()

                if not profile:
                    await interaction.response.send_message(embed=basicEmbeds["SelfNoProfile"], ephemeral=True)
                    return

                if bet < 100:
                    embed = discord.Embed(
                        description="`You must bet more than $100`",
                        colour=constants.colorHexes["Danger"]
                        )
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                    return
                        
                cash = profile[0]

                if bet > cash:
                    await interaction.response.send_message(embed=discord.Embed(description="`You don't have enough money!`", colour=constants.colorHexes["Danger"]), ephemeral=True)
                    return

                removed_bet_cash = cash - bet

                await utils.set_cash(db, removed_bet_cash, guild_id, user_id)

                slot = [[0,0,0],[0,0,0],[0,0,0]]

                for i in range(3):
                    for j in range(3):
                        slot[i][j] = random.choice(SYMBOL_LIST)

                win = slot[1][0] == slot[1][1] == slot[1][2]

                if win:
                    winnings = bet * 2
                    await utils.set_cash(db, winnings, guild_id, user_id)
                    embed = discord.Embed(
                        title="Slots Won!",
                        description=f"You won `{utils.to_money(winnings)}`",
                        colour=constants.colorHexes["LightBlue"]
                    )
                    await logs.send_player_log(self.bot, 'Slots', f"Won {bet}", utils.get_config(interaction.guild.id, 'log_channel_id'), interaction.user)


                if not win:
                    losings = bet
                    embed = discord.Embed(
                        title="Slots Won!",
                        description=f"You lost `{utils.to_money(losings)}`",
                        colour=constants.colorHexes["LightBlue"]
                    )
                    await logs.send_player_log(self.bot, 'Slots', f"Lost", utils.get_config(interaction.guild.id, 'log_channel_id'), interaction.user)


                try:
                    embed.add_field(name=f"{slot[0][0]} | {slot[0][1]} | {slot[0][2]}", value="", inline=False)
                    embed.add_field(name=f"{slot[1][0]} | {slot[1][1]} | {slot[1][2]}    **<**", value="", inline=False)
                    embed.add_field(name=f"{slot[2][0]} | {slot[2][1]} | {slot[2][2]}", value="", inline=False)
                except Exception as e:
                    print(e)

                await interaction.response.send_message(embed=embed)


async def setup(bot):
    Slots_cog = Slots(bot)
    await bot.add_cog(Slots_cog)