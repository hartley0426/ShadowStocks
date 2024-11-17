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

CONFIG_FILE_PATH = 'json\settings.json'

class ChannelView(discord.ui.View):
    def __init__(self, guild_id):
        super().__init__()
        self.add_item(ChannelDropdown(guild_id))

class ChannelDropdown(discord.ui.Select):
    def __init__(self, guild_id):
            options = [
                discord.SelectOption(label="Set Log Channel ID", value="log_channel_id")
            ]
            super().__init__(placeholder = "Select an Option", min_values = 1, max_values = 1, options=options)
            self.guild_id = guild_id

    async def callback(self, interaction: discord.Interaction):
        selected_value = self.values[0] if self.values else None
        if self.values[0] == 'log_channel_id':
            await interaction.response.send_modal(ChannelModal(self.guild_id, selected_value))
            

class ChannelModal(discord.ui.Modal, title="Channel Configuration"):
    channel_id = discord.ui.TextInput(label="ID", placeholder="The ID you'd like to enter", required=True)

    def __init__(self, guild_id, values):
        super().__init__()
        self.guild_id =  guild_id
        self.values = values

    async def on_submit(self, interaction: discord.Interaction) :
        with open(CONFIG_FILE_PATH, mode="r") as config_file:
            data = json.load(config_file)

        if str(self.guild_id) not in data:
            data[str(self.guild_id)] = {}

        selected = self.values

        data[str(self.guild_id)][selected] = int(self.channel_id.value)

        with open(CONFIG_FILE_PATH, mode="w") as config_file:
            json.dump(data, config_file, indent=4)

        await interaction.response.send_message(embed=discord.Embed(description=f"Channel ID set to `{self.channel_id}`", colour=constants.colorHexes["SkyBlue"]), ephemeral=True)

class ConfigDropdown(discord.ui.Select):
    def __init__(self, guild_id):
        options = [
            discord.SelectOption(label="Channel ID Configuration", value="channelidconfig")
        ]
        super().__init__(placeholder = "Select an Option", min_values = 1, max_values = 1, options=options)
        self.guild_id = guild_id

    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == 'channelidconfig':
            view = ChannelView(self.guild_id)
            embed = discord.Embed(
                title='Channel Configuration Menu',
                description='Please select an option to configure!',
                colour=constants.colorHexes["SkyBlue"]
            )
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
            return


class ConfigView(discord.ui.View):
    def __init__(self, guild_id):
        super().__init__()
        self.add_item(ConfigDropdown(guild_id))

class Config(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Config is ready.") 

    @app_commands.command(name="config", description="Configure which ticket options are enabled")
    async def config(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("You don't have permission to configure this.", ephemeral=True)
            return
        
        guild_id = str(interaction.guild.id)

        with open(CONFIG_FILE_PATH, mode="r") as config_file:
            data = json.load(config_file)   

        if guild_id not in data: # Defaults
            data[guild_id] = {
                'log_channel_id': None
            }

        with open(CONFIG_FILE_PATH, mode="w") as config_file:
                json.dump(data, config_file, indent=4)

        embed = discord.Embed(
            title="Configuration Menu",
            description="Please select an option to continue:",
            colour=constants.colorHexes["SkyBlue"]
        )

        await interaction.response.send_message(embed=embed, view=ConfigView(guild_id))
            
async def setup(bot):
    Config_cog = Config(bot)
    await bot.add_cog(Config_cog)