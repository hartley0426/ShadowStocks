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

SIDES = ['Heads', 'Tails']

class SmallGambling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"SmallGambling is ready.")    

    @app_commands.command(name="coinflip", description="Flip a coin to win money")
    @app_commands.describe(bet="The amount of money to bet on the coinflip", side="The side of coin to bet on")
    @app_commands.choices(side=[
        discord.app_commands.Choice(name="Heads", value=1),
        discord.app_commands.Choice(name="Tails", value=2),
    ])
    async def coinflip(self, interaction: discord.Interaction, bet: int, side: discord.app_commands.Choice[int]):
        guild_id = interaction.guild.id
        user_id = interaction.user.id

        if bet < 100:
            embed = discord.Embed(
                description="`You must bet more than $100`",
                colour=constants.colorHexes["Danger"]
                )
            await interaction.response.send_message(embed=embed, ephemeral=True)

        async with aiosqlite.connect('profiles.db') as db:
            async with db.execute('''SELECT charactername, cash FROM profiles WHERE guild_id = ? AND user_id = ?''', (guild_id, user_id)) as cursor:
                profile = await cursor.fetchone()

                if not profile:
                    await interaction.response.send_message(embed=basicEmbeds["SelfNoProfiles"], ephemeral=True)
                    return
                
                charactername, cash = profile

                if bet > cash:
                    embed = discord.Embed(
                        description="`You don't have enough money!`",
                        colour=0x191A53
                        )
                    await interaction.response.send_message(embed=embed, ephemeral=True)

                new_cash = cash - bet

                await db.execute('''UPDATE profiles SET cash = ? WHERE guild_id = ? AND user_id = ?''', (new_cash, guild_id, user_id))
                await db.commit()

                winning_side = random.choice(SIDES)
                
                if interaction.user.avatar:
                    avatar_url = interaction.user.avatar.url

                if side.name == winning_side:
                    new_cash = cash + (2 * bet)

                    await db.execute('''UPDATE profiles SET cash = ? WHERE guild_id = ? AND user_id = ?''', (new_cash, guild_id, user_id))
                    await db.commit()

                    win_embed = discord.Embed(
                        title="Coinflip won!",
                        description=f"{charactername} has won the coinflip for `{utils.to_money(2*bet)}`",
                        colour=constants.colorHexes["SkyBlue"]
                    )
                    await logs.send_player_log(self.bot, 'Coinflip', f"Won {bet}", utils.get_config(interaction.guild.id, 'log_channel_id'), interaction.user)
                    win_embed.set_thumbnail(url=avatar_url)

                    await interaction.response.send_message(embed=win_embed)

                else:
                    lose_embed = discord.Embed(
                        title="Coinflip Lost!",
                        description=f"{charactername} has lost the coinflip for `{utils.to_money(bet)}`",
                        colour=constants.colorHexes["DarkBlue"]
                    )
                    await logs.send_player_log(self.bot, 'Coinflip', f"Lost", utils.get_config(interaction.guild.id, 'log_channel_id'), interaction.user)
                    lose_embed.set_thumbnail(url=avatar_url)

                    await interaction.response.send_message(embed=lose_embed)



                
            
async def setup(bot):
    SmallGambling_cog = SmallGambling(bot)
    await bot.add_cog(SmallGambling_cog)