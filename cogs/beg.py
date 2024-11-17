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
from utilities.outcomes import OUTCOMES_BEG

COOLDOWNS = {}

class Beg(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Beg is ready.")

    @app_commands.command(name="beg", description="Beg strangers on the street for money. Very Inefficent")
    async def beg(self, interaction: discord.Interaction):
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

                cash, difficulty = profile

                difficulty_multiplier = 1.6 if difficulty == "Rich" else (1.4 if difficulty == "Middle Class" else(1.2 if difficulty == "Poor" else 1))

                payment = round(random.randint(5, 20) * difficulty_multiplier)

                final_cash = cash + payment

                payment_embed = discord.Embed(
                    title="Begging Success",
                    description=f"{random.choice(OUTCOMES_BEG)} `{utils.to_money(payment)}`\n\n"
                                f"**You now have:** `{utils.to_money(final_cash)}`",
                    colour=constants.colorHexes["LightBlue"]
                )

                await db.execute('''UPDATE profiles SET cash = ? WHERE guild_id = ? AND user_id = ?''', (final_cash, guild_id, user_id))
                await db.commit()
                await logs.send_player_log(self.bot, 'Begged', f"Begged and recieved {utils.to_money(payment)}", utils.get_config(interaction.guild.id, 'log_channel_id'), interaction.user)

                COOLDOWNS[guild_id][user_id] = datetime.now()

                await interaction.response.send_message(embed=payment_embed)
   
            
async def setup(bot):
    Beg_cog = Beg(bot)
    await bot.add_cog(Beg_cog)