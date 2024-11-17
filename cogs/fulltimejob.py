import discord
from discord.ext import commands, tasks
from discord import app_commands
import os
import json
import random
from datetime import datetime, timedelta 
import aiosqlite
import constants
from utilities import utils, logs
from utilities.embeds import basicEmbeds
from jobutilities import jobs

class cogname(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"cogname is ready.") 

    @app_commands.command(name="collect", description="Gets your hourly pay.")
    async def collect(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        guild_id = interaction.guild.id

        async with aiosqlite.connect('profiles.db') as db:
            async with db.execute('''SELECT bank, charactername, occupation, moneylastcollected FROM profiles WHERE guild_id = ? AND user_id = ?''', (guild_id, user_id)) as cursor:
                profile = await cursor.fetchone()

                if not profile:
                    await interaction.response.send_message(embed=basicEmbeds["SelfNoProfile"], ephemeral=True)
                    return
                
                bank, charactername, occupation, moneylastcollected = profile

                job_object = jobs.Jobs.get(occupation, jobs.Jobs["unemployed"])
                job_pay = job_object.GetPay()

                if moneylastcollected == "never":
                    try:
                        new_moneylastcollected = datetime.now().isoformat()
                        new_bank = int(bank + job_pay)
                        await db.execute('''UPDATE profiles SET bank = ?, moneylastcollected = ? WHERE guild_id = ? AND user_id = ?''', (new_bank, new_moneylastcollected, guild_id, user_id))
                        await db.commit()
                        embed = discord.Embed(
                            colour=constants.colorHexes["LightBlue"],
                            title="Paycheck Collected",
                            description=f"{charactername} has collected `{utils.to_money(job_pay)}`."
                        )
                        await interaction.response.send_message(embed=embed)
                        await logs.send_player_log(self.bot, 'Collection', f"Collected hourly pay for first time. Received {utils.to_money(job_pay)} ", utils.get_config(interaction.guild.id, 'log_channel_id'), interaction.user)
                    except Exception as e:
                        print(e)

                else:
                    moneylastcollected_datetime = datetime.fromisoformat(moneylastcollected)
                    time_since_collect = utils.get_time_delta(initial_time=moneylastcollected_datetime)
                    if time_since_collect["hours"] < 24:
                        embed = discord.Embed(
                            description=f"`You've already collected your paycheck. Come back in {24 - time_since_collect['hours']} minutes to redeem again.`",
                            colour=constants.colorHexes["Danger"]
                        )
                        await interaction.response.send_message(embed=embed, ephemeral=True)
                        return
                    else:
                        try:
                            paycheck = int(job_pay * time_since_collect["hours"])
                            new_bank = bank + paycheck
                            new_moneylastcollected = datetime.now().isoformat()
                            await db.execute('''UPDATE profiles SET bank = ?, moneylastcollected = ? WHERE guild_id = ? AND user_id = ?''', (new_bank, new_moneylastcollected, guild_id, user_id))
                            await db.commit()
                            await logs.send_player_log(self.bot, 'Collection', f"Collected hourly pay after {time_since_collect['hours']}. Received {utils.to_money(paycheck)} ", utils.get_config(interaction.guild.id, 'log_channel_id'), interaction.user)
                        except Exception as e:
                            print(e)

                        embed = discord.Embed(
                            colour=constants.colorHexes["SkyBlue"],
                            title="Paycheck Collected",
                            description=f"{charactername} has collected `{utils.to_money(paycheck)}`."
                        )
                        await interaction.response.send_message(embed=embed)


            
async def setup(bot):
    cogname_cog = cogname(bot)
    await bot.add_cog(cogname_cog)