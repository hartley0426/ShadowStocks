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

class Rob(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Rob is ready.")    

    @app_commands.command(name="rob", description="Robs any other user of a portion of their cash.")
    @app_commands.describe(member="The member you are wishing to rob.")
    async def rob(self, interaction: discord.Interaction, member: discord.Member):
        guild_id = interaction.guild.id
        robber_id = interaction.user.id
        member_id = member.id
        cooldown_duration = timedelta(hours=1)

        if guild_id not in COOLDOWNS:
            COOLDOWNS[guild_id] = {}

        if robber_id in COOLDOWNS[guild_id]:
            last_used = COOLDOWNS[guild_id][robber_id]
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
            async with db.execute('''SELECT charactername, cash, difficulty FROM profiles WHERE guild_id = ? and user_id = ?''', (guild_id, robber_id)) as cursor:
                robber_profile = await cursor.fetchone()

            async with db.execute('''SELECT charactername, cash, difficulty FROM profiles WHERE guild_id = ? and user_id = ?''', (guild_id, member_id)) as cursor:
                member_profile = await cursor.fetchone()

            if not robber_profile:
                await interaction.response.send_message(embed=basicEmbeds["SelfNoProfile"], ephemeral=True)

            if not member_profile:
                await interaction.response.send_message(embed=basicEmbeds["OtherNoProfile"], ephemeral=True)

            COOLDOWNS[guild_id][robber_id] = datetime.now()

            if robber_id == member_id:
                await interaction.response.send_message(embed = discord.Embed(description="`You tried to rob yourself and gained nothing.`", colour=constants.colorHexes["Danger"]), ephemeral=True)

            robber_name, robber_cash, robber_difficulty = robber_profile
            member_name, member_cash, member_difficulty = member_profile

            if member_cash <= 0:
                await interaction.response.send_message(embed=discord.Embed(description=f"You tried to rob `{member_name}` but they had no cash on them.", colour=constants.colorHexes["DarkBlue"]))

            robber_difficulty_multiplier = 1.6 if robber_difficulty == "Rich" else (1.4 if robber_difficulty == "Middle Class" else(1.2 if robber_difficulty == "Poor" else 1))
            member_difficulty_multiplier = 1.6 if member_difficulty == "Rich" else (1.4 if member_difficulty == "Middle Class" else(1.2 if member_difficulty == "Poor" else 1))

            success_chance = (random.randint(0, 100))/100
            weighted_success_chance = round(success_chance * robber_difficulty_multiplier, 2)

            if weighted_success_chance < .5: # Robbery Failed
                robber_balance_multiplier = 1.0 if robber_difficulty_multiplier == "Rich" else (1.2 if robber_difficulty_multiplier == "Middle Class" else(1.4 if robber_difficulty_multiplier == "Poor" else 1.6))
                member_balance_multiplier = 1.6 if robber_difficulty_multiplier == "Rich" else (1.4 if robber_difficulty_multiplier == "Middle Class" else(1.2 if robber_difficulty_multiplier == "Poor" else 1.0))

                full_balance_multipier = round(robber_balance_multiplier * member_balance_multiplier, 2)

                fine_percentage = round((random.randint(5,50)/100) * full_balance_multipier, 2)
                fine = round(member_cash * fine_percentage)

                final_robber_cash = robber_cash - fine
                final_member_cash = member_cash + fine

                await db.execute('''UPDATE profiles SET cash = ? WHERE guild_id = ? AND user_id = ?''', (final_robber_cash, guild_id, robber_id))
                await db.execute('''UPDATE profiles SET cash = ? WHERE guild_id = ? AND user_id = ?''', (final_member_cash, guild_id, member_id))

                await db.commit()

                fail_embed = discord.Embed(
                    title="Robbery Failed!",
                    description=f"You have been caught by the police! You must pay the fine `{member_name}`\n\n"
                                f"**Your Difficulty:** `{robber_difficulty}`\n"
                                f"**Their Difficulty:** `{member_difficulty}`\n\n"
                                f"**Fine:** `{utils.to_money(fine)}`\n"
                                f"**Your Final Cash:** `{utils.to_money(final_robber_cash)}`",
                    colour=constants.colorHexes["DarkBlue"]
                )

                await interaction.response.send_message(embed=fail_embed)

            else: # Robbery Success
                robber_balance_multiplier = 1.6 if robber_difficulty_multiplier == "Rich" else (1.4 if robber_difficulty_multiplier == "Middle Class" else(1.2 if robber_difficulty_multiplier == "Poor" else 1.0))
                member_balance_multiplier = 1.6 if robber_difficulty_multiplier == "Rich" else (1.4 if robber_difficulty_multiplier == "Middle Class" else(1.2 if robber_difficulty_multiplier == "Poor" else 1.0))

                full_balance_multipier = round(robber_balance_multiplier * member_balance_multiplier, 2)

                stolen_percentage = round((random.randint(5,50)/100) * full_balance_multipier, 2)
                stolen = round(member_cash * stolen_percentage)

                final_robber_cash = robber_cash - stolen
                final_member_cash = member_cash + stolen

                await db.execute('''UPDATE profiles SET cash = ? WHERE guild_id = ? AND user_id = ?''', (final_robber_cash, guild_id, robber_id))
                await db.execute('''UPDATE profiles SET cash = ? WHERE guild_id = ? AND user_id = ?''', (final_member_cash, guild_id, member_id))

                await db.commit()

                success_embed = discord.Embed(
                    title="Robbery Success!",
                    description=f"`{robber_name}` succesfully stole money from `{member_name}`\n\n"
                                f"**Your Difficulty:** `{robber_difficulty}`\n"
                                f"**Their Difficulty:** `{member_difficulty}`\n\n"
                                f"**Stolen:** `{utils.to_money(stolen)}`\n"
                                f"**Your Final Cash:** `{utils.to_money(final_robber_cash)}`",
                    colour=constants.colorHexes["MediumBlue"]
                )

                await interaction.response.send_message(embed=success_embed)

            

            
async def setup(bot):
    Rob_cog = Rob(bot)
    await bot.add_cog(Rob_cog)