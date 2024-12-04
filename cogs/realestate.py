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
from realestate_utils import realestateutils

class Realestate(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Realestate is ready.")

    @app_commands.command(name="getrealestate", description="Buy some more realestate to make you money.")
    async def getrealestate(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        guild_id = interaction.guild.id
        
        async with aiosqlite.connect('profiles.db') as db:
            async with db.execute('''SELECT cash, realestate FROM profiles WHERE guild_id = ? AND user_id = ?''', (guild_id, user_id)) as cursor:
                profile = await cursor.fetchone()

                if not profile:
                    await interaction.response.send_message(embed=basicEmbeds["SelfNoProfile"], ephemeral=True)
                    return
                
                cash, realestate_json = profile
                
                embed = discord.Embed(
                    title="Realestate Store",
                    description="Select a property to buy from the dropdown below!",
                    colour=constants.colorHexes["MediumBlue"]
                )
                try:
                    for property_key in realestateutils.Properties:
                        property = realestateutils.Properties[property_key]
                        embed.add_field(name=f"{property.GetLocation()} - {utils.to_money(property.GetCost())}", value=f"**Pay:** `{utils.to_money(property.GetPay())}`")
                    
                    view = RealestateDropdownView(user_id, guild_id)
                    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
                except Exception as e:
                                print(e)
        

    @app_commands.command(name="collectrealestate", description="Collect any of your realestates")
    async def collectrealestate(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        guild_id = interaction.guild.id

        try:

            async with aiosqlite.connect('profiles.db') as db:
                async with db.execute('''SELECT cash, realestate, realestatelastcollected FROM profiles WHERE guild_id = ? AND user_id = ?''', (guild_id, user_id)) as cursor:
                    profile = await cursor.fetchone()

                    if not profile:
                        await interaction.response.send_message(embed=basicEmbeds["SelfNoProfile"], ephemeral=True)
                        return
                    
                    cash, realestate_json, realestatelastcollected_json = profile

                    user_realestates = json.loads(realestate_json) if realestate_json else []

                    if not user_realestates:
                        embed = discord.Embed(
                                title="Realestate",
                                description="You don't have any realestate.",
                                colour=constants.colorHexes["DarkBlue"]
                            )
                        await interaction.response.send_message(embed=embed, ephemeral=True)
                        return
                    
                    embed = discord.Embed(
                        title="Realestate",
                        description="Here are your realestate properties. Select one below to collect.",
                        colour=constants.colorHexes["MediumBlue"]
                    )

                    for property_key in user_realestates:
                        if property_key in realestateutils.Properties:
                            property = realestateutils.Properties[property_key]
                            embed.add_field(name=f"{property.GetLocation()} | {utils.to_money(property.GetCost())}", value=f"{utils.to_money(property.GetPay())}/Month", inline=False)

                    view = RealestateCollectDropdownView(user_realestates)
                    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        
        except Exception as e:
            print(f"{e}")

class RealestateCollectDropdownView(discord.ui.View):
    def __init__(self, user_realestates):
        super().__init__(timeout=60)
        self.user_realestates = user_realestates

        self.add_item(RealestateCollectDropdown(user_realestates))

class RealestateCollectDropdown(discord.ui.Select):
    def __init__(self, user_realestates):
        options = [
            discord.SelectOption(label=realestateutils.Properties[property_key].GetLocation(), description=f"{utils.to_money(realestateutils.Properties[property_key].GetPay())}", value=property_key)
            for property_key in user_realestates if property_key in realestateutils.Properties]
        super().__init__(placeholder="Select a property to collect from", min_values=1, max_values=1, options=options)

        self.user_realestates = user_realestates


    async def callback(self, interaction: discord.Interaction):
        property_key = self.values[0]
        property = realestateutils.Properties[property_key]
        try:

            async with aiosqlite.connect('profiles.db') as db:
                async with db.execute('''SELECT cash, realestate, realestatelastcollected FROM profiles WHERE guild_id = ? AND user_id = ?''', (interaction.guild.id, interaction.user.id)) as cursor:
                    profile = await cursor.fetchone()

                    if not profile:
                        await interaction.response.send_message(embed=basicEmbeds["SelfNoProfile"], ephemeral=True)
                        return
                    
                    cash, realestate_json, realestatelastcollected_json = profile

                    realestate_pay = property.GetPay()
                    

                    if not realestatelastcollected_json:
                        realestatelastcollected_json = {}

                    else:
                        try:
                            realestatelastcollected_json = json.loads(realestatelastcollected_json)
                        except (json.JSONDecodeError, TypeError):
                            realestatelastcollected_json = {}

                    propertylastcollected = realestatelastcollected_json.get(property_key)

                    if not propertylastcollected:
                        realestatelastcollected_json[property_key] = datetime.now().isoformat()

                        updated_collection = json.dumps(realestatelastcollected_json)

                        new_cash = cash + realestate_pay
                        await db.execute('''UPDATE profiles SET cash = ?, realestatelastcollected = ? WHERE guild_id = ? AND user_id = ?''', (new_cash, updated_collection, interaction.guild.id, interaction.user.id))
                        await db.commit()

                        embed = discord.Embed(
                            title="Realestate Collected",
                            description=f"You have collected `{utils.to_money(realestate_pay)}` from **{property.GetLocation()}**",
                            colour=constants.colorHexes["SkyBlue"]
                        )
                        await interaction.response.send_message(embed=embed)

                    else:
                        realestatelastcollected = datetime.fromisoformat(propertylastcollected)
                        time_since_collect = utils.get_time_delta(initial_time=realestatelastcollected)

                        if time_since_collect["months"] < 1:
                            embed = discord.Embed(
                                description=f"`You've already collected your rent for this month. Come back in {utils.convert_seconds(43200-time_since_collect['total_game_minutes'])} to redeem again.`",
                                colour=constants.colorHexes["Danger"]
                            )
                            await interaction.response.send_message(embed=embed, ephemeral=True)
                            return
                        
                        else:
                            paycheck = int(realestate_pay * (time_since_collect["months"]))
                            new_cash = cash+paycheck
                            realestatelastcollected_json[property_key] = datetime.now().isoformat()

                            updated_collection = json.dumps(realestatelastcollected_json)

                            
                            await db.execute('''UPDATE profiles SET cash = ?, realestatelastcollected = ? WHERE guild_id = ? AND user_id = ?''', (new_cash, updated_collection, interaction.guild.id, interaction.user.id))
                            await db.commit()

                            embed = discord.Embed(
                                title="Realestate Collected",
                                description=f"You have collected `{utils.to_money(paycheck)}` from **{property.GetLocation()}**",
                                colour=constants.colorHexes["SkyBlue"]
                            )
                            await interaction.response.send_message(embed=embed)

        except Exception as e:
            print(e)




class RealestateDropdownView(discord.ui.View):
    def __init__(self, user_id, guild_id):
        super().__init__(timeout=60)

        self.user_id = user_id
        self.guild_id = guild_id

        self.add_item(RealestateDropdown())


class RealestateDropdown(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label=property.GetLocation(), description=f"{utils.to_money(property.GetPay())}", value = property_key)
            for property_key, property in realestateutils.Properties.items()
        ]
        super().__init__(placeholder="Select a property to buy", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        property_key = self.values[0]
        property = realestateutils.Properties[property_key]

        
        try:
            async with aiosqlite.connect('profiles.db') as db:
                async with db.execute('''SELECT cash, realestate FROM profiles WHERE guild_id = ? AND user_id = ?''', (interaction.guild.id, interaction.user.id)) as cursor:
                    profile = await cursor.fetchone()

                    if not profile:
                        await interaction.response.send_message(embed=basicEmbeds["SelfNoProfile"], ephemeral=True)
                        return
                    
                    cash, realestate_json = profile

                    if cash < property.GetCost():
                        await interaction.response.send_message("You don't have enough cash to buy this property.", ephemeral=True)
                        return
                    
                    if realestate_json:
                        try:
                            existing_properties = json.loads(realestate_json)

                            if not isinstance(existing_properties, list):
                                existing_properties = []  
                        except json.JSONDecodeError:
                            existing_properties = []  
                    else:
                        existing_properties = [] 

                    if property_key in existing_properties:
                        await interaction.response.send_message(embed=discord.Embed(description="`You already own this building`", colour=constants.colorHexes["Danger"]))
                        return


                    existing_properties.append(property_key)


                    updated_realestate = json.dumps(existing_properties)

                    new_cash = cash - property.GetCost()
                    await db.execute(
                        '''UPDATE profiles SET cash = ?, realestate = ? WHERE guild_id = ? AND user_id = ?''',
                        (new_cash, updated_realestate, interaction.guild.id, interaction.user.id)
                    )
                    await db.commit()


                    embed = discord.Embed(
                            title="Purchase Complete",
                            description=f"You bought **{property.GetLocation()}** for `{utils.to_money(property.GetCost())}`.\n\nYou Now get paid `{utils.to_money(property.GetPay())}` per month.",
                            color=constants.colorHexes["MediumBlue"]
                        )

                    await interaction.response.send_message(embed=embed, ephemeral=True)

        except Exception as e:
            print(e)
                
        


            
async def setup(bot):
    Realestate_cog = Realestate(bot)
    await bot.add_cog(Realestate_cog)
