import discord
from discord.ext import commands, tasks
from discord import app_commands
import json
import os
import random
from datetime import datetime, timedelta 
import aiosqlite
import constants
from utilities import utils, logs
from utilities.embeds import basicEmbeds
from utilities.outcomes import OUTCOMES_WORK

COOLDOWNS = {}

class PartTimeJobs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"PartTimeJobs is ready.")

    
        
    @app_commands.command(name="work", description="Works a random part-time job.")
    @app_commands.checks.cooldown(1, 25200, key=lambda i: (i.guild_id, i.user.id))
    async def work(self, interaction: discord.Interaction):
        guild_id = interaction.guild.id
        user_id = interaction.user.id
        cooldown_duration = timedelta(hours=7)

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

                difficulty_multiplier = 2.5 if difficulty == "Rich" else (2.0 if difficulty == "Middle Class" else(1.5 if difficulty == "Poor" else 1))
                hours_worked = random.randint(14, 56)
                base_income = random.randint(6, 12)
                job_income = hours_worked * base_income
                final_income = round(job_income * difficulty_multiplier)
                
                new_cash = cash+final_income

                job_message = random.choice(OUTCOMES_WORK)

                work_embed = discord.Embed(
                    title="Part-Time Job Completed!",
                    colour=constants.colorHexes["LightBlue"],
                    description=f"{job_message}"
                                f"**Hourly Pay:** `{utils.to_money(base_income)}`\n"
                                f"**Hours Worked:** `{hours_worked}`\n\n"
                                f"**Difficulty:** `{difficulty}`\n"
                                f"**Difficulty Multiplier:** `{difficulty_multiplier}x`\n\n"
                                f"**Final Total:** `{utils.to_money(final_income)}`"
                )
                await logs.send_player_log(self.bot, 'Collection', f"Worked Part-time Job. Received {utils.to_money(final_income)} ", utils.get_config(interaction.guild.id, 'log_channel_id'), interaction.user)
                await db.execute('''UPDATE profiles SET cash = ? WHERE guild_id = ? AND user_id = ?''', (new_cash, guild_id, user_id))
                await db.commit()

                await interaction.response.send_message(embed=work_embed)

    @work.error
    async def handle_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CommandOnCooldown):
            try:
                retry_after = round(error.retry_after, 2)
                embed = discord.Embed(
                    description=f"❌ You are on cooldown! Try again in {utils.convert_seconds(round(retry_after))}.",
                    colour=constants.colorHexes['Danger']
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
            except Exception as e:
                print(e)
        else:
            embed = discord.Embed(
                description="❌ An unexpected error occurred. Please try again later.",
                colour=constants.colorHexes['Danger']
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)


    
                
async def setup(bot):
    PartTimeJobs_cog = PartTimeJobs(bot)
    await bot.add_cog(PartTimeJobs_cog)