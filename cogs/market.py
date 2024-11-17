import discord
from discord.ext import commands
from discord import app_commands
import json
import aiosqlite
from utilities import utils
from utilities.embeds import basicEmbeds
import constants

ASSETS_FOR_PURCHASE = "json/assetsforpurchase.json"
ASSETS = "json/assets.json"

class MarketCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Market is ready.")

    @app_commands.command(name="addmarket", description="Adds an asset to the market (no duplicates).")
    async def addmarket(self, interaction: discord.Interaction, name: str, cost: int, description: str):
        guild_id = str(interaction.guild.id)

        with open(ASSETS_FOR_PURCHASE, "r") as f:
            market_data = json.load(f)

        if guild_id not in market_data:
            market_data[guild_id] = {}

        if name in market_data[guild_id]:
            await interaction.response.send_message(embed=discord.Embed(description=f"`{name} already exists in the market.`", colour=constants.colorHexes["Danger"]), ephemeral=True)
            return

        market_data[guild_id][name] = {"description": description, "cost": cost}

        with open(ASSETS_FOR_PURCHASE, "w") as f:
            json.dump(market_data, f, indent=4)

        await interaction.response.send_message(
            embed=discord.Embed(description=f"`{name} successfully added to the market.`", colour=constants.colorHexes["Success"]), ephemeral=True
        )

    @app_commands.command(name="removemarket", description="Removes an asset from the market.")
    async def removemarket(self, interaction: discord.Interaction, name: str):
        guild_id = str(interaction.guild.id)

        with open(ASSETS_FOR_PURCHASE, "r") as f:
            market_data = json.load(f)

        if guild_id not in market_data or name not in market_data[guild_id]:
            await interaction.response.send_message(
                discord.Embed(description=f"`{name} doesn't exist in the market.`", colour=constants.colorHexes["Danger"]), ephemeral=True
            )
            return

        del market_data[guild_id][name]

        with open(ASSETS_FOR_PURCHASE, "w") as f:
            json.dump(market_data, f, indent=4)

        await interaction.response.send_message(
            embed=discord.Embed(description=f"`{name} successfully removed from the market.`", colour=constants.colorHexes["Success"]), ephemeral=True
        )

    @app_commands.command(name="market", description="Displays items available for purchase.")
    async def market(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        user_id = interaction.user.id

        with open(ASSETS_FOR_PURCHASE, "r") as f:
            market_data = json.load(f)

        if guild_id not in market_data or not market_data[guild_id]:
            await interaction.response.send_message(embed=discord.Embed(description=f"`There are no items on the market`", colour=constants.colorHexes["DarkBlue"]), ephemeral=True)
            return

        async with aiosqlite.connect("profiles.db") as db:
            async with db.execute(
                "SELECT cash FROM profiles WHERE guild_id = ? AND user_id = ?", (guild_id, user_id)
            ) as cursor:
                profile = await cursor.fetchone()

        if not profile:
            await interaction.response.send_message(embed=basicEmbeds["SelfNoProfile"], ephemeral=True)
            return

        cash = profile[0]
        market_items = market_data[guild_id]

        embed = discord.Embed(
            title="Market",
            description="Select an item to purchase from the dropdown below.",
            colour=constants.colorHexes["LightBlue"]
        )
        for item, details in market_items.items():
            embed.add_field(name=f"`{item}` - `{details['cost']}`", value=details['description'], inline=False)

        view = MarketDropdownView(user_id, guild_id, cash, market_items)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @app_commands.command(name="assets", description="Shows your owned assets.")
    async def assets(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        user_id = str(interaction.user.id)

        with open(ASSETS, "r") as f:
            assets_data = json.load(f)

        if guild_id not in assets_data or user_id not in assets_data[guild_id]:
            await interaction.response.send_message(embed=discord.Embed(description=f"`You don't own any assets`", colour=constants.colorHexes["DarkBlue"]), ephemeral=True)
            return

        user_assets = assets_data[guild_id][user_id]

        if not user_assets:  # Check if the user's assets are empty
            await interaction.response.send_message(embed=discord.Embed(description=f"`You don't own any assets`", colour=constants.colorHexes["DarkBlue"]), ephemeral=True)
            return

        embed = discord.Embed(
            title="Your Assets",
            description="Select an asset to view its details.",
            colour=constants.colorHexes["LightBlue"]
        )

        for asset, details in user_assets.items():
            embed.add_field(name=asset, value=f"{details['description']} - `{utils.to_money(details['cost'])}`", inline=False)

        view = AssetDropdownView(user_id, guild_id, user_assets)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


class MarketDropdownView(discord.ui.View):
    def __init__(self, user_id, guild_id, cash, market_items):
        super().__init__(timeout=60)
        self.add_item(MarketDropdown(user_id, guild_id, cash, market_items))


class MarketDropdown(discord.ui.Select):
    def __init__(self, user_id, guild_id, cash, market_items):
        options = [
            discord.SelectOption(label=name, description=details['description'], value=name)
            for name, details in market_items.items()
        ]
        super().__init__(placeholder="Select an item to buy", options=options)
        self.user_id = user_id
        self.guild_id = guild_id
        self.cash = cash
        self.market_items = market_items

    async def callback(self, interaction: discord.Interaction):
        item_name = self.values[0]
        item_details = self.market_items[item_name]

        if self.cash < item_details["cost"]:
            await interaction.response.send_message(embed=discord.Embed(description=f"`You don't have enough money to buy this item`", colour=constants.colorHexes["Danger"]), ephemeral=True)
            return

        async with aiosqlite.connect("profiles.db") as db:
            async with db.execute(
                "SELECT cash FROM profiles WHERE guild_id = ? AND user_id = ?", (self.guild_id, self.user_id)
            ) as cursor:
                profile = await cursor.fetchone()

        if not profile:
            await interaction.response.send_message(embed=basicEmbeds["SelfNoProfile"], ephemeral=True)
            return

        current_cash = profile[0]

        # Read existing data
        with open(ASSETS, "r") as f:
            assets_data = json.load(f)

        # Ensure guild and user exist in the JSON structure
        guild_assets = assets_data.setdefault(str(self.guild_id), {})
        user_assets = guild_assets.setdefault(str(self.user_id), {})

        # Prevent duplicate asset names
        if item_name in user_assets:
            await interaction.response.send_message(embed=discord.Embed(description=f"`You already own {item_name}`", colour=constants.colorHexes["DarkBlue"]), ephemeral=True)
            return

        # Add new asset
        user_assets[item_name] = item_details

        # Deduct cash
        new_cash = current_cash - item_details["cost"]

        # Write updated data back to the file
        with open(ASSETS, "w") as f:
            json.dump(assets_data, f, indent=4)

        # Update database
        async with aiosqlite.connect("profiles.db") as db:
            await db.execute(
                "UPDATE profiles SET cash = ? WHERE guild_id = ? AND user_id = ?",
                (new_cash, self.guild_id, self.user_id)
            )
            await db.commit()

        await interaction.response.send_message(embed=discord.Embed(description=f"`You bought {item_name}` for `{utils.to_money(item_details['cost'])}`", colour=constants.colorHexes["DarkBlue"]), ephemeral=True)


class AssetDropdownView(discord.ui.View):
    def __init__(self, user_id, guild_id, user_assets):
        super().__init__(timeout=60)
        self.add_item(AssetDropdown(user_id, guild_id, user_assets))


class AssetDropdown(discord.ui.Select):
    def __init__(self, user_id, guild_id, user_assets):
        options = [
            discord.SelectOption(label=name, description=details["description"], value=name)
            for name, details in user_assets.items()
        ]
        super().__init__(placeholder="Select an asset to view details", options=options)
        self.user_id = user_id
        self.guild_id = guild_id
        self.user_assets = user_assets

    async def callback(self, interaction: discord.Interaction):
        asset_name = self.values[0]
        asset_details = self.user_assets[asset_name]

        embed = discord.Embed(
            title="Asset Details",
            description=f"{asset_name}\n\n{asset_details['description']}\nValue: `{utils.to_money(asset_details['cost'])}`",
            colour=constants.colorHexes["LightBlue"]
        )
        view = AssetSellButtonView(self.user_id, self.guild_id, asset_name, asset_details)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


class AssetSellButtonView(discord.ui.View):
    def __init__(self, user_id, guild_id, asset_name, asset_details):
        super().__init__()
        self.add_item(SellButton(user_id, guild_id, asset_name, asset_details))


class SellButton(discord.ui.Button):
    def __init__(self, user_id, guild_id, asset_name, asset_details):
        super().__init__(label="Sell Asset", style=discord.ButtonStyle.danger)
        self.user_id = user_id
        self.guild_id = guild_id
        self.asset_name = asset_name
        self.asset_details = asset_details

    async def callback(self, interaction: discord.Interaction):
        async with aiosqlite.connect("profiles.db") as db:
            async with db.execute(
                "SELECT cash FROM profiles WHERE guild_id = ? AND user_id = ?", (self.guild_id, self.user_id)
            ) as cursor:
                profile = await cursor.fetchone()

        if not profile:
            await interaction.response.send_message(embed=basicEmbeds["SelfNoProfile"], ephemeral=True)
            return

        current_cash = profile[0]
        new_cash = current_cash + self.asset_details["cost"]

        with open(ASSETS, "r") as f:
            assets_data = json.load(f)

        user_assets = assets_data[self.guild_id][self.user_id]
        del user_assets[self.asset_name]

        with open(ASSETS, "w") as f:
            json.dump(assets_data, f, indent=4)

        async with aiosqlite.connect("profiles.db") as db:
            await db.execute(
                "UPDATE profiles SET cash = ? WHERE guild_id = ? AND user_id = ?",
                (new_cash, self.guild_id, self.user_id)
            )
            await db.commit()

        await interaction.response.send_message(embed=discord.Embed(description=f"You sold `{self.asset_name}` for `{utils.to_money(self.asset_details['cost'])}`", colour=constants.colorHexes["DarkBlue"]), ephemeral=True)


async def setup(bot):
    await bot.add_cog(MarketCog(bot))
