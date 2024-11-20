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
from realestate_utils import properties

class Property(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Property is ready.")  

    @app_commands.command(name="buyproperty", description="buyproperty")
    async def buyproperty(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        guild_id = interaction.guild.id

        try:
            async with aiosqlite.connect('profiles.db') as db:
                async with db.execute('''SELECT cash, property FROM profiles WHERE guild_id = ? AND user_id = ?''', (guild_id, user_id)) as cursor:
                    profile = await cursor.fetchone()

                    if not profile:
                        await interaction.response.send_message(embed=basicEmbeds["SelfNoProfile"], ephemeral=True)
                        return
                    
                    cash, property = profile

                    embed = discord.Embed(
                        title="Store", 
                        description="Select an item to purchase from the dropdown below!",
                        colour=constants.colorHexes["MediumBlue"]
                    )

                    for property_key, property in properties.Properties.items():
                        embed.add_field(name=f"{property.GetLocation()} - {utils.to_money(property.GetCost())}", value=property.GetShortDesc(), inline=False)
                    
                    view = PropertyDropdownView(user_id=user_id, guild_id=guild_id, cash=cash)
                    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        except Exception as e:
            print(e)  

    @app_commands.command(name="properties", description="View your properties.")
    async def properties(self, interaction: discord.Interaction):
        try:
            user_id = interaction.user.id
            guild_id = interaction.guild.id

            async with aiosqlite.connect('profiles.db') as db:
                async with db.execute('SELECT property FROM profiles WHERE guild_id = ? AND user_id = ?', (guild_id, user_id)) as cursor:
                    profile = await cursor.fetchone()

                    if not profile:
                        await interaction.response.send_message(embed=basicEmbeds["SelfNoProfile"], ephemeral=True)
                        return
                    
                    property_json = profile[0]
                    user_property = json.loads(property_json) if property_json else []

                    # Check if inventory is empty
                    if not user_property:
                        embed = discord.Embed(
                            title="Properties",
                            description="You have no properties/buy.",
                            colour=constants.colorHexes["DarkBlue"]
                        )
                        await interaction.response.send_message(embed=embed, ephemeral=True)
                        return

                    # Create embed to show inventory
                    embed = discord.Embed(
                        title="Properties",
                        description="Here are the properties that you own. Select an property from the dropdown below to see details.",
                        colour=constants.colorHexes["SkyBlue"]
                    )

                    # Add each item name to the embed
                    for property_key in user_property:
                        if property_key in properties.Properties:
                            property = properties.Properties[property_key]
                            embed.add_field(name=property.GetLocation(), value=f"{utils.to_money(property.GetCost())}", inline=False)

                    # Create the dropdown for item details
                    view = PropertiesDropdownView(user_property)
                    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        
        except Exception as e:
            print(e)

class PropertiesDropdownView(discord.ui.View):
    def __init__(self, user_property):
        super().__init__(timeout=60)
        self.user_property = user_property

        # Create dropdown for inventory items
        self.add_item(PropertiesDropdown(self.user_property))

class PropertiesDropdown(discord.ui.Select):
    def __init__(self, user_property):
        # Define options based on user's inventory
        options = [
            discord.SelectOption(
                label=properties.Properties[property_key].GetLocation(),
                description=properties.Properties[property_key].GetDesc(),
                value=property_key
            )
            for property_key in user_property if property_key in properties.Properties
        ]
        super().__init__(placeholder="Select an item to view details...", min_values=1, max_values=1, options=options)
    try:
        async def callback(self, interaction: discord.Interaction):
            selected_value = self.values[0]
            property_key = selected_value
            property = properties.Properties[property_key]
            
            # Show item details in an embed
            embed = discord.Embed(
                title=f"{property.GetLocation()}",
                description=property.GetDesc(),
                colour=constants.colorHexes["LightBlue"]
            )
            embed.add_field(name="Cost", value=f"{utils.to_money(property.GetCost())}", inline=False)

            try:
                embed.set_image(url=property.GetImage())
            except Exception as e:
                print(e)

            await interaction.response.send_message(embed=embed, view=SellButton(interaction.user.id, property, property_key), ephemeral=True)
    except Exception as e:
            print(e)

class SellButton(discord.ui.View):
    def __init__(self, user_id, property, property_key):
        super().__init__()
        self.user_id = user_id
        self.property = property
        self.property_key = property_key

    @discord.ui.button(label="Sell", style=discord.ButtonStyle.danger)
    async def sell(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(
                embed=discord.Embed(
                    description="This is not your inventory!", 
                    color=constants.colorHexes["Danger"]
                ),
                ephemeral=True
            )
            return

        try:
            async with aiosqlite.connect('profiles.db') as db:
                async with db.execute(
                    '''SELECT cash, property FROM profiles WHERE guild_id = ? AND user_id = ?''', 
                    (interaction.guild.id, self.user_id)
                ) as cursor:
                    profile = await cursor.fetchone()

                    if not profile:
                        await interaction.response.send_message(
                            embed=basicEmbeds["SelfNoProfile"],
                            ephemeral=True
                        )
                        return

                    cash, property_json = profile
                    property_list = json.loads(property_json) if property_json else []

                    if self.property_key not in property_list:
                        await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You do not own this item!",
                                color=constants.colorHexes["Danger"]
                            ),
                            ephemeral=True
                        )
                        return

                    # Remove the item from inventory
                    property_list.remove(self.property_key)
                    updated_property_json = json.dumps(property_list)

                    # Calculate refund amount
                    refund = self.property.GetCost() // 2  # Adjust refund logic if necessary
                    new_cash = cash + refund

                    # Update the database
                    await db.execute(
                        '''UPDATE profiles SET cash = ?, property = ? WHERE guild_id = ? AND user_id = ?''',
                        (new_cash, updated_property_json, interaction.guild.id, self.user_id)
                    )
                    await db.commit()

                    # Confirmation message
                    embed = discord.Embed(
                        title="Item Sold",
                        description=f"You sold your **{self.property.GetLocation()}** for `{utils.to_money(refund)}`.",
                        color=constants.colorHexes["MediumBlue"]
                    )
                    await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            print(e)
            await interaction.response.send_message(
                "An error occurred while processing your request.",
                ephemeral=True
            )


class PropertyDropdownView(discord.ui.View):
    def __init__(self, user_id, guild_id, cash):
        super().__init__(timeout=60)
        self.user_id = user_id
        self.guild_id = guild_id
        self.cash = cash

        self.add_item(PropertyDropdown())

class PropertyDropdown(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label=property.GetLocation(), description=property.GetShortDesc(), value=property_key)
            for property_key, property in properties.Properties.items()
        ]
        super().__init__(placeholder="Select an item to buy", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        property_key = self.values[0]
        property = properties.Properties[property_key]

        # Check if user has enough cash
        if self.view.cash < property.GetCost():
            await interaction.response.send_message("You don't have enough cash to buy this property.", ephemeral=True)
            return

        try:
            async with aiosqlite.connect('profiles.db') as db:
                async with db.execute(
                    '''SELECT cash, property FROM profiles WHERE guild_id = ? AND user_id = ?''', 
                    (self.view.guild_id, self.view.user_id)
                ) as cursor:
                    profile = await cursor.fetchone()

                    if not profile:
                        await interaction.response.send_message(embed=basicEmbeds["SelfNoProfile"], ephemeral=True)
                        return

                    cash, property_json = profile
                    # Ensure items_json is a list
                    if isinstance(property_json, str):
                        property_json = json.loads(property_json)

                    # Initialize as an empty list if items_json is None or not a list
                    existing_property = property_json if isinstance(property_json, list) else []
                    print(existing_property)
                    if property_key in existing_property:
                        embed = discord.Embed(
                            title="Purchase Failed",
                            description=f"You already have **{property.GetLocation()}** .",
                            color=constants.colorHexes["Danger"]
                        )

                        await interaction.response.send_message(embed=embed, ephemeral=True)
                        return
                    existing_property.append(property_key)
                    updated_property = json.dumps(existing_property)

                    print(updated_property)

                    new_cash = cash - property.GetCost()

                    # Update cash and items in the database
                    await db.execute(
                        '''UPDATE profiles SET cash = ?, property = ? WHERE guild_id = ? AND user_id = ?''',
                        (new_cash, updated_property, interaction.guild.id, interaction.user.id)
                    )
                    await db.commit()

                    # Confirmation message
                    embed = discord.Embed(
                        title="Purchase Complete",
                        description=f"You bought  **{property.GetLocation()}** for `{utils.to_money(property.GetCost())}`.",
                        color=constants.colorHexes["MediumBlue"]
                    )

                    await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            print(e)
            
async def setup(bot):
    Property_cog = Property(bot)
    await bot.add_cog(Property_cog)