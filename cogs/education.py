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
from jobutilities import educationutils, attributes
from utilities.embeds import basicEmbeds

class Education(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Education is ready.") 

    @app_commands.command(name="education", description="Check what degrees and education you have")
    async def education(self, interaction: discord.Interaction):
        guild_id = interaction.guild.id
        user_id = interaction.user.id

        async with aiosqlite.connect('profiles.db') as db:
            async with db.execute('''SELECT charactername, education FROM profiles WHERE guild_id = ? AND user_id =?''', (guild_id, user_id)) as cursor:
                profile = await cursor.fetchone()

                if not profile:
                    await interaction.response.send_message(embed=basicEmbeds["SelfNoProfile"])
                    return
                
                charactername, education_json = profile

                

                degrees = json.loads(education_json) if education_json else []

                if not degrees:
                    embed = discord.Embed(
                        title="Education",
                        description="Your education is empty.",
                        colour=constants.colorHexes["DarkBlue"]
                    )
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                    return

                embed = discord.Embed(
                    title=f"{charactername}'s Education History",
                    description=f"Listed below are all of {charactername}'s degrees:",
                    colour=constants.colorHexes["LightBlue"]
                )
                embed.set_footer(text="Do /college to get degrees")

                for degree_key in degrees:
                    if degree_key in educationutils.Degrees:
                        degree_object = educationutils.Degrees[degree_key]
                        embed.add_field(name=f"{degree_object.get_name()} - {degree_object.get_type()}", value=degree_object.get_description(), inline=False)

                await interaction.response.send_message(embed = embed)


    
    @app_commands.command(name="college", description="Go to college and get an degree.")
    async def college(self, interaction: discord.Interaction):
        guild_id = interaction.guild.id
        user_id = interaction.user.id

        try:

            async with aiosqlite.connect('profiles.db') as db:
                async with db.execute('''SELECT cash, attributes, education FROM profiles WHERE guild_id = ? AND user_id =?''', (guild_id, user_id)) as cursor:
                    profile = await cursor.fetchone()

                    if not profile:
                        await interaction.response.send_message(embed=basicEmbeds["SelfNoProfile"])
                        return
                    
                    cash, attributes_json, education_json = profile

                    embed = discord.Embed(
                            title="College", 
                            description="Select a degree below to attempt to get it!",
                            colour=constants.colorHexes["MediumBlue"]
                        )
                    
                    for degree_key, degree_object in educationutils.Degrees.items():
                        embed.add_field(name=f"{degree_object.get_name()} - {utils.to_money(degree_object.get_cost())} - {degree_object.get_type()}", value=degree_object.get_description(), inline=False)

                    await interaction.response.send_message(embed=embed, view=CollegeDropdownView(user_id, guild_id, cash), ephemeral=True)

        except Exception as e:
            print(e)

class CollegeDropdownView(discord.ui.View):
    def __init__(self, user_id, guild_id, cash):
        super().__init__()
        self.user_id = user_id
        self.guild_id = guild_id
        self.cash = cash

        self.add_item(CollegeDropdown())

class CollegeDropdown(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label=degree_object.get_name(), description=degree_object.get_description(), value=degree_key)
            for degree_key, degree_object in educationutils.Degrees.items()
        ]
        super().__init__(placeholder="Select a degree to go to college for", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        try:
            degree_key = self.values[0]
            degree_object = educationutils.Degrees[degree_key]

            if self.view.cash < degree_object.get_cost():
                await interaction.response.send_message(embed=discord.Embed(description="`You don't have enough cash to study this.`", colour=constants.colorHexes["Danger"]), ephemeral=True)
                return
            
            async with aiosqlite.connect('profiles.db') as db:
                async with db.execute('''SELECT cash, attributes, education FROM profiles WHERE guild_id = ? AND user_id =?''', (self.view.guild_id, self.view.user_id)) as cursor:
                    profile = await cursor.fetchone()

                    if not profile:
                        await interaction.response.send_message(embed=basicEmbeds["SelfNoProfile"])
                        return
                    
                    cash, attributes_json, education_json = profile

                    attributes_data = json.loads(attributes_json) if attributes_json else {}

                    attributes_objects = {k: attributes.Attribute.from_dict(v) for k, v in attributes_data.items()}

                    degree_name = degree_object.get_name()
                    degree_description = degree_object.get_description()
                    degree_type = degree_object.get_type()
                    degree_requirements = degree_object.get_requirements()

                    missing_requirements = [
                            f"{attribute.capitalize()} | **Required:** {required_value} | **You have:** {attributes_objects[attribute].GetLevel()}"
                            for attribute, required_value in degree_requirements.items()
                            if attributes_objects.get(attribute, attributes.Attribute()).GetLevel() < required_value
                        ]
                    
                    if missing_requirements:
                        embed = discord.Embed(
                            title="Application Failed",
                            description=f"You do not meet the requirements for the degree {degree_name}.\n\n***Missing requirements:***\n" + "\n".join(missing_requirements),
                            colour=constants.colorHexes["DarkBlue"]
                        )
                        await interaction.response.send_message(embed=embed, ephemeral=True)
                        return
                    
                    else:
                        if isinstance(education_json, str):
                            education_json = json.loads(education_json)

                        existing_degrees = education_json if isinstance(education_json, list) else []
                        if degree_key not in existing_degrees:
                            existing_degrees.append(degree_key)
                        else:
                            await interaction.response.send_message(embed=discord.Embed(description="You already have this degree!", colour=constants.colorHexes["DarkBlue"]), ephemeral=True)
                            return
                        
                        updated_degrees = json.dumps(existing_degrees)
                        new_cash = cash - degree_object.get_cost()

                        await db.execute(
                            '''UPDATE profiles SET cash = ?, education = ? WHERE guild_id = ? AND user_id = ?''',
                                (new_cash, updated_degrees, self.view.guild_id, self.view.user_id)
                            )
                        await db.commit()

                        embed = discord.Embed(
                            title="Application Passed",
                            description=f"You now have the `{degree_name}`.\n\nYou paid `{utils.to_money(degree_object.get_cost())}`\n\n**Type:** `{degree_type}`\n\n**Description:** `{degree_description}`",
                            colour=constants.colorHexes["SkyBlue"]
                        )

                        await interaction.response.send_message(embed=embed)
        except Exception as e:
            print(e)


            
async def setup(bot):
    Education_cog = Education(bot)
    await bot.add_cog(Education_cog)