import discord
from discord.ext import commands, tasks
from discord import app_commands
import json
import os
import random
from datetime import datetime, timedelta 
import aiosqlite
import constants
from utilities import utils
from utilities.embeds import basicEmbeds

COOLDOWNS = {}

class Crime(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Crime is ready.")    

    @app_commands.command(name="crime", description="Commit a crime. High Risk --> High Reward")
    async def crime(self, interaction: discord.Interaction):
        guild_id = interaction.guild.id
        user_id = interaction.user.id
        cooldown_duration = timedelta(hours=1)

        if guild_id not in COOLDOWNS:
            COOLDOWNS[guild_id] = {}

        if user_id in COOLDOWNS[guild_id]:
            last_used = COOLDOWNS[guild_id][user_id]
            if datetime.now() < last_used + cooldown_duration:
                remaining_time = (last_used + cooldown_duration) - datetime.now()
                seconds = remaining_time.seconds

                wait_embed = discord.Embed(
                    description=f"`You are on cooldown! You must wait {utils.convert_seconds(seconds)}`",
                    colour=constants.colorHexes["Danger"]
                )
                await interaction.response.send_message(embed=wait_embed, ephemeral=True)
                return

        async with aiosqlite.connect('profiles.db') as db:
            async with db.execute('''SELECT cash, difficulty FROM profiles WHERE guild_id = ? AND user_id = ?''', (guild_id, user_id)) as cursor:
                profile = await cursor.fetchone()

                if not profile:
                    await interaction.response.send_message(embed=basicEmbeds["SelfNoProfile"], ephemeral=True)
                    return
                
                COOLDOWNS[guild_id][user_id] = datetime.now()
                
                cash, difficulty = profile

                difficulty_multiplier = 1.6 if difficulty == "Rich" else (1.4 if difficulty == "Middle Class" else(1.2 if difficulty == "Poor" else 1))

                success_chance = (random.randint(0, 100))/100
                weighted_success_chance = round(success_chance * difficulty_multiplier, 2)

                if weighted_success_chance <= .5: # Fail Chance
                    balance_multiplier = 1.0 if difficulty == "Rich" else (1.2 if difficulty == "Middle Class" else(1.4 if difficulty == "Poor" else 1.6))

                    fine_percentage = round((random.randint(5,50)/100) * balance_multiplier, 2)

                    fine = round(cash * fine_percentage)

                    new_cash = cash - fine

                    await db.execute('''UPDATE profiles SET cash = ? WHERE guild_id = ? AND user_id = ?''', (new_cash, guild_id, user_id))
                    await db.commit()

                    failed_embed = discord.Embed(
                        title="Crime Failed!",
                        description=f"You have been caught by the police!\n\n"
                                    f"**Difficulty:** `{difficulty}`\n"
                                    f"**Difficulty Multiplier:** `{difficulty_multiplier}x`\n\n"
                                    f"**Fine:** `{utils.to_money(fine)}`\n\n"
                                    f"**Cash Total:** `{utils.to_money(new_cash)}`",
                        colour=constants.colorHexes["DarkBlue"]
                    )

                    await interaction.response.send_message(embed=failed_embed)
                
                if success_chance == 1: # Heist Check (Natural 100)
                    balance_multiplier = 1.0 if difficulty == "Rich" else (1.2 if difficulty == "Middle Class" else(1.4 if difficulty == "Poor" else 1.6))

                    pay_percentage = round((random.randint(50,200)/100) * balance_multiplier, 2)

                    payment = round(cash * pay_percentage)

                    new_cash = cash + payment

                    await db.execute('''UPDATE profiles SET cash = ? WHERE guild_id = ? AND user_id = ?''', (new_cash, guild_id, user_id))
                    await db.commit()

                    payment_embed = discord.Embed(
                        title="Heist Completed!",
                        description=f"You have made it out succesfully!\n\n"
                                    f"**Difficulty:** `{difficulty}`\n"
                                    f"**Difficulty Multiplier:** `{difficulty_multiplier}x`\n\n"
                                    f"**Payment:** `{utils.to_money(payment)}`\n\n"
                                    f"**Cash Total:** `{utils.to_money(new_cash)}`",
                        colour=constants.colorHexes["SkyBlue"]
                    )

                    await interaction.response.send_message(embed=payment_embed)

                if weighted_success_chance >= 0.51: # Regular Win
                    balance_multiplier = 1.0 if difficulty == "Rich" else (1.2 if difficulty == "Middle Class" else(1.4 if difficulty == "Poor" else 1.6))

                    pay_percentage = round((random.randint(5,50)/100) * balance_multiplier, 2)

                    payment = round(cash * pay_percentage)

                    new_cash = cash + payment

                    await db.execute('''UPDATE profiles SET cash = ? WHERE guild_id = ? AND user_id = ?''', (new_cash, guild_id, user_id))
                    await db.commit()

                    payment_embed = discord.Embed(
                        title="Heist Completed!",
                        description=f"You have made it out succesfully!\n\n"
                                    f"**Difficulty:** `{difficulty}`\n"
                                    f"**Difficulty Multiplier:** `{difficulty_multiplier}x`\n\n"
                                    f"**Payment:** `{utils.to_money(payment)}`\n\n"
                                    f"**Cash Total:** `{utils.to_money(new_cash)}`",
                        colour=constants.colorHexes["LightBlue"]
                    )

                    await interaction.response.send_message(embed=payment_embed)
                    
    
async def setup(bot):
    Crime_cog = Crime(bot)
    await bot.add_cog(Crime_cog)