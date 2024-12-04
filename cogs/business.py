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
from business_utils import businesses

class Business(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Business is ready.")    

    @app_commands.command(name="buybusiness", description="Buy a business to own.")
    async def buybusiness(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        guild_id = interaction.guild.id
        
        async with aiosqlite.connect('profiles.db') as db:
            async with db.execute('''SELECT cash, businesses FROM profiles WHERE guild_id = ? AND user_id = ?''', (guild_id, user_id)) as cursor:
                profile = await cursor.fetchone()

                if not profile:
                    await interaction.response.send_message(embed=basicEmbeds["SelfNoProfile"], ephemeral=True)
                    return
                
                cash, businesses_json = profile

                embed = discord.Embed(
                    title="Business Store",
                    description="Select a business to buy from the dropdown below!",
                    colour=constants.colorHexes["MediumBlue"]
                )

                for business_key in businesses.Businesses:
                    business = businesses.Businesses[business_key]
                    embed.add_field(name=f"{business.get_name()} - {utils.to_money(business.get_cost())}", value=f"**Pay:** `{utils.to_money(business.get_pay())}`", inline=False)

                view = BusinessBuyDropdownView(interaction.user.id, interaction.guild.id)
                await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @app_commands.command(name="collectbusinesses", description="Collect money from your business profits")
    async def collectbusinesses(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        guild_id = interaction.guild.id

        async with aiosqlite.connect('profiles.db') as db:
            async with db.execute('''SELECT cash, businesses, businesseslastcollected FROM profiles WHERE guild_id = ? AND user_id = ?''', (guild_id, user_id)) as cursor:
                profile = await cursor.fetchone()

                if not profile:
                    await interaction.response.send_message(embed=basicEmbeds["SelfNoProfile"], ephemeral=True)
                    return
                
                cash, businesses_json, businesseslastcollected_json = profile

                user_businesses = json.loads(businesses_json) if businesses_json else []

                if not user_businesses:
                    embed = discord.Embed(
                            title="Busineses",
                            description="You don't have any businesses.",
                            colour=constants.colorHexes["DarkBlue"]
                        )
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                    return
                
                embed = discord.Embed(
                        title="Busineses",
                        description="Here are your businesses. Select one to collect.",
                        colour=constants.colorHexes["DarkBlue"]
                    )
                
                for business_key in user_businesses:
                    if business_key in businesses.Businesses:
                        business = businesses.Businesses[business_key]
                        embed.add_field(name=f"{business.get_name()} | {utils.to_money(business.get_cost())}", value=f"{utils.to_money(business.get_pay())}/Day", inline=False)

                view = BusinessCollectDropdownView(user_businesses)
                await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

class BusinessCollectDropdownView(discord.ui.View):
    def __init__(self, user_businesses):
        super().__init__(timeout=60)
        self.user_businesses = user_businesses

        self.add_item(BusinessCollectDropdown(user_businesses))

class BusinessCollectDropdown(discord.ui.Select):
    def __init__(self, user_businesses):
        options = [
            discord.SelectOption(label=businesses.Businesses[business_key].get_name(), description=f"{utils.to_money(businesses.Businesses[business_key].get_pay())}", value=business_key)
            for business_key in user_businesses if business_key in businesses.Businesses]
        super().__init__(placeholder="Select a property to collect from", min_values=1, max_values=1, options=options)

        self.user_businesses = user_businesses

    async def callback(self, interaction: discord.Interaction):
        business_key = self.values[0]
        business = businesses.Businesses[business_key]

        try:

            async with aiosqlite.connect('profiles.db') as db:
                async with db.execute('''SELECT cash, businesses, businesseslastcollected FROM profiles WHERE guild_id = ? AND user_id = ?''', (interaction.guild.id, interaction.user.id)) as cursor:
                    profile = await cursor.fetchone()

                    if not profile:
                        await interaction.response.send_message(embed=basicEmbeds["SelfNoProfile"], ephemeral=True)
                        return
                    
                    cash, businesses_json, businesseslastcollected_json = profile

                    business_pay = business.get_pay()

                    if not businesseslastcollected_json:
                        businesseslastcollected_json = {}

                    else:
                        try:
                            businesseslastcollected_json = json.loads(businesseslastcollected_json)
                        except (json.JSONDecodeError, TypeError):
                            businesseslastcollected_json = {}

                    business_last_collected = businesseslastcollected_json.get(business_key)

                    if not business_last_collected:
                        businesseslastcollected_json[business_key] = datetime.now().isoformat()

                        updated_collecton = json.dumps(businesseslastcollected_json)

                        new_cash = cash + business_pay

                        await db.execute('''UPDATE profiles SET cash = ?, businesseslastcollected = ? WHERE guild_id = ? AND user_id = ?''', (new_cash, updated_collecton, interaction.guild.id, interaction.user.id))
                        await db.commit()

                        embed = discord.Embed(
                                title="Business Collected",
                                description=f"You have collected `{utils.to_money(business_pay)}` from **{business.get_name()}**",
                                colour=constants.colorHexes["SkyBlue"]
                            )
                        await interaction.response.send_message(embed=embed)

                    else:
                        businesslastcollected = datetime.fromisoformat(business_last_collected)
                        time_since_collect = utils.get_time_delta(initial_time=businesslastcollected)

                        if time_since_collect["days"] < 1:
                            embed = discord.Embed(
                                    description=f"`You've already collected your profits for today. Come back in {utils.convert_seconds(24-time_since_collect['total_game_minutes'])} to redeem again.`",
                                    colour=constants.colorHexes["Danger"]
                                )
                            await interaction.response.send_message(embed=embed, ephemeral=True)
                            return
                        
                        else:
                            paycheck = int(business_pay * (time_since_collect["days"]))
                            new_cash = cash+paycheck

                            businesseslastcollected_json[business_key] = datetime.now().isoformat()

                            updated_collecton = json.dumps(businesseslastcollected_json)

                            await db.execute('''UPDATE profiles SET cash = ?, businesseslastcollected = ? WHERE guild_id = ? AND user_id = ?''', (new_cash, updated_collecton, interaction.guild.id, interaction.user.id))
                            await db.commit()

                            embed = discord.Embed(
                                title="Business Collected",
                                description=f"You have collected `{utils.to_money(paycheck)}` from **{business.get_name()}**",
                                colour=constants.colorHexes["SkyBlue"]
                            )
                            await interaction.response.send_message(embed=embed)

        except Exception as e:
            print(e)


                

class BusinessBuyDropdownView(discord.ui.View):
    def __init__(self, user_id, guild_id):
        super().__init__(timeout=60)

        self.user_id = user_id
        self.guild_id = guild_id

        self.add_item(BusinessBuyDropdown())

class BusinessBuyDropdown(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label=business.get_name(), description=f"{utils.to_money(business.get_cost())}", value=business_key)
            for business_key, business in businesses.Businesses.items()
        ]
        super().__init__(placeholder="Select a business to buy", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):

        business_key = self.values[0]
        business = businesses.Businesses[business_key]

        async with aiosqlite.connect('profiles.db') as db:
            async with db.execute('''SELECT cash, businesses FROM profiles WHERE guild_id = ? AND user_id = ?''', (interaction.guild.id, interaction.user.id)) as cursor:
                profile = await cursor.fetchone()

                if not profile:
                    await interaction.response.send_message(embed=basicEmbeds["SelfNoProfile"], ephemeral=True)
                    return
                
                cash, businesses_json = profile

                if cash < business.get_cost():
                    await interaction.response.send_message("You don't have enough cash to buy this business.", ephemeral=True)
                    return
                
                if businesses_json:
                    try:
                        existing_businesses = json.loads(businesses_json)

                        if not isinstance(existing_businesses, list):
                            existing_businesses = []

                    except json.JSONDecodeError:
                        existing_businesses = []
                else:
                    existing_businesses = []

                if business_key in existing_businesses:
                    await interaction.response.send_message(embed=discord.Embed(description="`You already own this business`", colour=constants.colorHexes["Danger"]))
                    return
                
                existing_businesses.append(business_key)

                updated_businesses = json.dumps(existing_businesses)

                new_cash = cash - business.get_cost()

                await db.execute('''UPDATE profiles SET cash = ?, businesses = ? WHERE guild_id = ? AND user_id = ?''', (new_cash, updated_businesses, interaction.guild.id, interaction.user.id))
                await db.commit()

                embed = discord.Embed(
                            title="Purchase Complete",
                            description=f"You bought **{business.get_name()}** for `{utils.to_money(business.get_cost())}`.\n\nYou Now get paid `{utils.to_money(business.get_pay())}` per day.",
                            color=constants.colorHexes["MediumBlue"]
                        )
            
        
                await interaction.response.send_message(embed=embed, ephemeral=True)
            
async def setup(bot):
    Business_cog = Business(bot)
    await bot.add_cog(Business_cog)