import discord
from discord.ext import commands
from discord import app_commands
import aiosqlite
import json
from itemsutilities.items import Items
from utilities.embeds import basicEmbeds
import constants
from utilities import utils

class Store(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Store is ready.")

    @app_commands.command(name="store", description="Buy items from the store.")
    async def store(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        guild_id = interaction.guild.id

        try:
            async with aiosqlite.connect('profiles.db') as db:
                async with db.execute('''SELECT cash, items FROM profiles WHERE guild_id = ? AND user_id = ?''', (guild_id, user_id)) as cursor:
                    profile = await cursor.fetchone()

                    if not profile:
                        await interaction.response.send_message(embed=basicEmbeds["SelfNoProfile"], ephemeral=True)
                        return
                    
                    cash, items = profile

                    embed = discord.Embed(
                        title="Store", 
                        description="Select an item to purchase from the dropdown below!",
                        colour=constants.colorHexes["MediumBlue"]
                    )

                    for item_key, item in Items.items():
                        embed.add_field(name=f"{item.GetName()} - {utils.to_money(item.GetCost())}", value=item.GetShortDesc(), inline=False)
                    
                    view = StoreDropdownView(user_id=user_id, guild_id=guild_id, cash=cash)
                    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        except Exception as e:
            print(e)

class StoreDropdownView(discord.ui.View):
    def __init__(self, user_id, guild_id, cash):
        super().__init__(timeout=60)
        self.user_id = user_id
        self.guild_id = guild_id
        self.cash = cash

        self.add_item(StoreDropdown())

class StoreDropdown(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label=item.GetName(), description=item.GetShortDesc(), value=item_name)
            for item_name, item in Items.items()
        ]
        super().__init__(placeholder="Select an item to buy", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        item_name = self.values[0]
        item = Items[item_name]

        # Check if user has enough cash
        if self.view.cash < item.GetCost():
            await interaction.response.send_message("You don't have enough cash to buy this item.", ephemeral=True)
            return

        try:
            async with aiosqlite.connect('profiles.db') as db:
                async with db.execute(
                    '''SELECT cash, items FROM profiles WHERE guild_id = ? AND user_id = ?''', 
                    (self.view.guild_id, self.view.user_id)
                ) as cursor:
                    profile = await cursor.fetchone()

                    if not profile:
                        await interaction.response.send_message(embed=basicEmbeds["SelfNoProfile"], ephemeral=True)
                        return

                    cash, items_json = profile
                    # Ensure items_json is a list
                    if isinstance(items_json, str):
                        items_json = json.loads(items_json)

                    # Initialize as an empty list if items_json is None or not a list
                    existing_items = items_json if isinstance(items_json, list) else []
                    existing_items.append(item_name)
                    updated_items = json.dumps(existing_items)

                    new_cash = cash - item.GetCost()

                    # Update cash and items in the database
                    await db.execute(
                        '''UPDATE profiles SET cash = ?, items = ? WHERE guild_id = ? AND user_id = ?''',
                        (new_cash, updated_items, self.view.guild_id, self.view.user_id)
                    )
                    await db.commit()

                    # Confirmation message
                    embed = discord.Embed(
                        title="Purchase Complete",
                        description=f"You bought a **{item.GetName()}** for `{utils.to_money(item.GetCost())}`.",
                        color=constants.colorHexes["MediumBlue"]
                    )

                    await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            print(e)


async def setup(bot):
    Store_cog = Store(bot)
    await bot.add_cog(Store_cog)
