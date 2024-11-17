import discord
from discord.ext import commands, tasks
from discord import app_commands
import os
import json
import random
from datetime import datetime, timedelta 
import aiosqlite
import constants
import itemsutilities.items
from utilities import utils, logs
from utilities.embeds import basicEmbeds
from discord.ui import View, Button, Modal, TextInput
from discord import Interaction, Embed
import itemsutilities


class Inventory(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Inventory is ready.")

    @app_commands.command(name="inventory", description="View your inventory.")
    async def inventory(self, interaction: discord.Interaction):
        try:
            user_id = interaction.user.id
            guild_id = interaction.guild.id

            async with aiosqlite.connect('profiles.db') as db:
                async with db.execute('SELECT items FROM profiles WHERE guild_id = ? AND user_id = ?', (guild_id, user_id)) as cursor:
                    profile = await cursor.fetchone()

                    if not profile:
                        await interaction.response.send_message(embed=basicEmbeds["SelfNoProfile"], ephemeral=True)
                        return
                    
                    items_json = profile[0]
                    user_items = json.loads(items_json) if items_json else []

                    # Check if inventory is empty
                    if not user_items:
                        embed = discord.Embed(
                            title="Inventory",
                            description="Your inventory is empty.",
                            colour=constants.colorHexes["DarkBlue"]
                        )
                        await interaction.response.send_message(embed=embed, ephemeral=True)
                        return

                    # Create embed to show inventory
                    embed = discord.Embed(
                        title="Inventory",
                        description="Here are the items in your inventory. Select an item from the dropdown below to see details.",
                        colour=constants.colorHexes["SkyBlue"]
                    )

                    # Add each item name to the embed
                    for item_name in user_items:
                        if item_name in itemsutilities.items.Items:
                            item = itemsutilities.items.Items[item_name]
                            embed.add_field(name=item.GetName(), value=f"{utils.to_money(item.GetCost())}", inline=False)

                    # Create the dropdown for item details
                    view = InventoryDropdownView(user_items)
                    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        
        except Exception as e:
            print(e)

class InventoryDropdownView(discord.ui.View):
    def __init__(self, user_items):
        super().__init__(timeout=60)
        self.user_items = user_items

        # Create dropdown for inventory items
        self.add_item(InventoryDropdown(self.user_items))


class InventoryDropdown(discord.ui.Select):
    def __init__(self, user_items):
        # Define options based on user's inventory
        options = [
            discord.SelectOption(label=itemsutilities.items.Items[item].GetName(), description=itemsutilities.items.Items[item].GetShortDesc(), value=f"{item}_{i}")
            for i, item in enumerate(user_items) if item in itemsutilities.items.Items
        ]
        super().__init__(placeholder="Select an item to view details...", min_values=1, max_values=1, options=options)
    try:
        async def callback(self, interaction: discord.Interaction):
            selected_value = self.values[0]
            item_name, index = selected_value.rsplit('_', 1)
            item = itemsutilities.items.Items[item_name]
            
            # Show item details in an embed
            embed = discord.Embed(
                title=f"{item.GetName()}",
                description=item.GetDesc(),
                colour=constants.colorHexes["LightBlue"]
            )
            embed.add_field(name="Cost", value=f"{utils.to_money(item.GetCost())}", inline=False)

            try:
                embed.set_thumbnail(url=item.GetImage())
            except Exception as e:
                print(e)

            await interaction.response.send_message(embed=embed, view=SellButton(interaction.user.id, item, item_name), ephemeral=True)
    except Exception as e:
            print(e)

class SellButton(discord.ui.View):
    def __init__(self, user_id, item, item_name):
        super().__init__()
        self.user_id = user_id
        self.item = item
        self.item_name = item_name

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
                    '''SELECT cash, items FROM profiles WHERE guild_id = ? AND user_id = ?''', 
                    (interaction.guild.id, self.user_id)
                ) as cursor:
                    profile = await cursor.fetchone()

                    if not profile:
                        await interaction.response.send_message(
                            embed=basicEmbeds["SelfNoProfile"],
                            ephemeral=True
                        )
                        return

                    cash, items_json = profile
                    items_list = json.loads(items_json) if items_json else []

                    if self.item_name not in items_list:
                        await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You do not own this item!",
                                color=constants.colorHexes["Danger"]
                            ),
                            ephemeral=True
                        )
                        return

                    # Remove the item from inventory
                    items_list.remove(self.item_name)
                    updated_items_json = json.dumps(items_list)

                    # Calculate refund amount
                    refund = self.item.GetCost() // 2  # Adjust refund logic if necessary
                    new_cash = cash + refund

                    # Update the database
                    await db.execute(
                        '''UPDATE profiles SET cash = ?, items = ? WHERE guild_id = ? AND user_id = ?''',
                        (new_cash, updated_items_json, interaction.guild.id, self.user_id)
                    )
                    await db.commit()

                    # Confirmation message
                    embed = discord.Embed(
                        title="Item Sold",
                        description=f"You sold your **{self.item.GetName()}** for `{utils.to_money(refund)}`.",
                        color=constants.colorHexes["MediumBlue"]
                    )
                    await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            print(e)
            await interaction.response.send_message(
                "An error occurred while processing your request.",
                ephemeral=True
            )
        


async def setup(bot):
    Inventory_cog = Inventory(bot)
    await bot.add_cog(Inventory_cog)