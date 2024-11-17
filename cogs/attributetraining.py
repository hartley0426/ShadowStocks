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
from jobutilities import attributes

class AttributeTraining(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"AttributeTraining is ready.")    

    @app_commands.command(name="workout", description="Increase your strength")
    @app_commands.checks.cooldown(3, 3600, key=lambda i: (i.guild_id, i.user.id))
    async def workout(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        user_id = str(interaction.user.id)
        async with aiosqlite.connect('profiles.db') as db:
            async with db.execute('''SELECT attributes FROM profiles WHERE guild_id = ? AND user_id = ?''', (guild_id, user_id)) as cursor:
                profile = await cursor.fetchone()
                if not profile:
                    await interaction.response.send_message(embed=basicEmbeds["SelfNoProfile"], ephemeral=True)
                    return

                attributes_json = profile[0]
                attributes_data = json.loads(attributes_json) if attributes_json else {}

                strength_attribute = attributes.Attribute.from_dict(attributes_data.get("strength", {}))
                if not strength_attribute.IsMaxLevel():
                    strength_attribute.IncrLevel(.25)

                    attributes_data["strength"] = strength_attribute.to_dict()

                    updated_attributes_json = json.dumps(attributes_data)

                    await db.execute('''UPDATE profiles SET attributes = ? WHERE guild_id = ? AND user_id = ?''',(updated_attributes_json, guild_id, user_id))
                    await db.commit()
                    await logs.send_player_log(self.bot, 'Workout', f"Worked out", utils.get_config(interaction.guild.id, 'log_channel_id'), interaction.user)
                    await interaction.response.send_message(embed=discord.Embed(description=f"`You did a workout and gained .25 strength | Total: {strength_attribute.GetLevel()}%`", colour=constants.colorHexes["LightBlue"]))
                else:
                    await interaction.response.send_message(embed=discord.Embed(description=f"`Your strength is already at the maximum level!`", colour=constants.colorHexes["LightBlue"]))

    @app_commands.command(name="study", description="Increase your intelligence")
    @app_commands.checks.cooldown(3, 3600, key=lambda i: (i.guild_id, i.user.id))
    async def study(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        user_id = str(interaction.user.id)
        async with aiosqlite.connect('profiles.db') as db:
            async with db.execute('''SELECT attributes FROM profiles WHERE guild_id = ? AND user_id = ?''', (guild_id, user_id)) as cursor:
                profile = await cursor.fetchone()
                if not profile:
                    await interaction.response.send_message(embed=basicEmbeds["SelfNoProfile"], ephemeral=True)
                    return

                attributes_json = profile[0]
                attributes_data = json.loads(attributes_json) if attributes_json else {}

                intelligence_attribute = attributes.Attribute.from_dict(attributes_data.get("intelligence", {}))
                if not intelligence_attribute.IsMaxLevel():
                    intelligence_attribute.IncrLevel(.25)

                    attributes_data["intelligence"] = intelligence_attribute.to_dict()

                    updated_attributes_json = json.dumps(attributes_data)

                    await db.execute('''UPDATE profiles SET attributes = ? WHERE guild_id = ? AND user_id = ?''',(updated_attributes_json, guild_id, user_id))
                    await db.commit()
                    await logs.send_player_log(self.bot, 'Studied', f"Studied", utils.get_config(interaction.guild.id, 'log_channel_id'), interaction.user)
                    await interaction.response.send_message(embed=discord.Embed(description=f"`You did a study session and gained .25 intelligence | Total: {intelligence_attribute.GetLevel()}%`", colour=constants.colorHexes["LightBlue"]))
                else:
                    await interaction.response.send_message(embed=discord.Embed(description=f"`Your intelligence is already at the maximum level!`", colour=constants.colorHexes["LightBlue"]))

    @app_commands.command(name="paint", description="Increase your dexterity")
    @app_commands.checks.cooldown(3, 3600, key=lambda i: (i.guild_id, i.user.id))
    async def paint(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        user_id = str(interaction.user.id)
        async with aiosqlite.connect('profiles.db') as db:
            async with db.execute('''SELECT attributes FROM profiles WHERE guild_id = ? AND user_id = ?''', (guild_id, user_id)) as cursor:
                profile = await cursor.fetchone()
                if not profile:
                    await interaction.response.send_message(embed=basicEmbeds["SelfNoProfile"], ephemeral=True)
                    return

                attributes_json = profile[0]
                attributes_data = json.loads(attributes_json) if attributes_json else {}

                dexterity_attribute = attributes.Attribute.from_dict(attributes_data.get("dexterity", {}))
                if not dexterity_attribute.IsMaxLevel():
                    dexterity_attribute.IncrLevel(.25)

                    attributes_data["dexterity"] = dexterity_attribute.to_dict()

                    updated_attributes_json = json.dumps(attributes_data)

                    await db.execute('''UPDATE profiles SET attributes = ? WHERE guild_id = ? AND user_id = ?''',(updated_attributes_json, guild_id, user_id))
                    await db.commit()
                    await interaction.response.send_message(embed=discord.Embed(description=f"`You painted a work of art and gained .25 dexterity | Total: {dexterity_attribute.GetLevel()}%`", colour=constants.colorHexes["LightBlue"]))
                    await logs.send_player_log(self.bot, 'Paint', f"Painted", utils.get_config(interaction.guild.id, 'log_channel_id'), interaction.user)
                else:
                    await interaction.response.send_message(embed=discord.Embed(description=f"`Your dexterity is already at the maximum level!`", colour=constants.colorHexes["LightBlue"]))

    @app_commands.command(name="socialize", description="Increase your charisma")
    @app_commands.checks.cooldown(3, 3600, key=lambda i: (i.guild_id, i.user.id))
    async def socialize(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        user_id = str(interaction.user.id)
        async with aiosqlite.connect('profiles.db') as db:
            async with db.execute('''SELECT attributes FROM profiles WHERE guild_id = ? AND user_id = ?''', (guild_id, user_id)) as cursor:
                profile = await cursor.fetchone()
                if not profile:
                    await interaction.response.send_message(embed=basicEmbeds["SelfNoProfile"], ephemeral=True)
                    return

                attributes_json = profile[0]
                attributes_data = json.loads(attributes_json) if attributes_json else {}

                charisma_attribute = attributes.Attribute.from_dict(attributes_data.get("charisma", {}))
                if not charisma_attribute.IsMaxLevel():
                    charisma_attribute.IncrLevel(.25)

                    attributes_data["charisma"] = charisma_attribute.to_dict()

                    updated_attributes_json = json.dumps(attributes_data)

                    await db.execute('''UPDATE profiles SET attributes = ? WHERE guild_id = ? AND user_id = ?''',(updated_attributes_json, guild_id, user_id))
                    await db.commit()
                    await interaction.response.send_message(embed=discord.Embed(description=f"`You spoke and gained .25 charisma | Total: {charisma_attribute.GetLevel()}%`", colour=constants.colorHexes["LightBlue"]))
                    await logs.send_player_log(self.bot, 'Socialize', f"Socialized", utils.get_config(interaction.guild.id, 'log_channel_id'), interaction.user)
                else:
                    await interaction.response.send_message(embed=discord.Embed(description=f"`Your charisma is already at the maximum level!`", colour=constants.colorHexes["LightBlue"]))

    @app_commands.command(name="meditate", description="Increase your wisdom")
    @app_commands.checks.cooldown(3, 3600, key=lambda i: (i.guild_id, i.user.id))
    async def meditate(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        user_id = str(interaction.user.id)
        async with aiosqlite.connect('profiles.db') as db:
            async with db.execute('''SELECT attributes FROM profiles WHERE guild_id = ? AND user_id = ?''', (guild_id, user_id)) as cursor:
                profile = await cursor.fetchone()
                if not profile:
                    await interaction.response.send_message(embed=basicEmbeds["SelfNoProfile"], ephemeral=True)
                    return

                attributes_json = profile[0]
                attributes_data = json.loads(attributes_json) if attributes_json else {}

                wisdom_attribute = attributes.Attribute.from_dict(attributes_data.get("wisdom", {}))
                if not wisdom_attribute.IsMaxLevel():
                    wisdom_attribute.IncrLevel(.25)

                    attributes_data["wisdom"] = wisdom_attribute.to_dict()

                    updated_attributes_json = json.dumps(attributes_data)

                    await db.execute('''UPDATE profiles SET attributes = ? WHERE guild_id = ? AND user_id = ?''',(updated_attributes_json, guild_id, user_id))
                    await db.commit()
                    await logs.send_player_log(self.bot, 'Meditate', f"Meditated", utils.get_config(interaction.guild.id, 'log_channel_id'), interaction.user)
                    await interaction.response.send_message(embed=discord.Embed(description=f"`You meditated and gained .25 wisdom | Total: {wisdom_attribute.GetLevel()}%`", colour=constants.colorHexes["LightBlue"]))
                else:
                    await interaction.response.send_message(embed=discord.Embed(description=f"`Your wisdom is already at the maximum level!`", colour=constants.colorHexes["LightBlue"]))

    async def handle_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CommandOnCooldown):
            retry_after = round(error.retry_after, 2)
            embed = discord.Embed(
                description=f"❌ You are on cooldown! Try again in {utils.convert_seconds(round(retry_after))}.",
                colour=constants.colorHexes["DarkBlue"]
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed = discord.Embed(
                description="❌ An unexpected error occurred. Please try again later.",
                colour=constants.colorHexes["Danger"]
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

    # Register error handlers for each command
    workout.error = study.error = paint.error = socialize.error = meditate.error = handle_error
            
async def setup(bot):
    AttributeTraining_cog = AttributeTraining(bot)
    await bot.add_cog(AttributeTraining_cog)