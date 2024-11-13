import discord
from discord.ext import commands, tasks
from discord import app_commands
import json
import os
import random
from datetime import datetime 
import aiosqlite
import constants
from utilities import utils

class ProfileAdmin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"ProfileAdmin is ready.")

    @app_commands.command(name="createprofile", description="Creates a profile for your character")
    @app_commands.choices(gender=[
        discord.app_commands.Choice(name="Male", value=1),
        discord.app_commands.Choice(name="Female", value=2),
        discord.app_commands.Choice(name="Other", value=3),
    ],
    difficulty=[
        discord.app_commands.Choice(name='Rich', value=1),
        discord.app_commands.Choice(name='Middle Class', value=2),
        discord.app_commands.Choice(name='Poor', value=3),
        discord.app_commands.Choice(name='Homeless', value=4)
    ])
    async def createprofile(self, interaction: discord.Interaction, charactername: str, gender: discord.app_commands.Choice[int], difficulty: discord.app_commands.Choice[int]):
        user_id = interaction.user.id
        user = interaction.user
        guild_id = interaction.guild.id

        async with aiosqlite.connect('profiles.db') as db:
            try:
                async with db.execute('''
                    SELECT charactername FROM profiles
                    WHERE guild_id = ? AND user_id = ?
                    ''', (guild_id, user_id)) as cursor:
                    profile = await cursor.fetchone()
                    if profile:
                        await interaction.response.send_message(
                            embed=discord.Embed(description="`You already have a profile created!`", colour=constants.colorHexes["Danger"]),
                            ephemeral=True
                        )
                        return
                    else:
                        try:
                            age = random.randint(16,60)
                            height = utils.to_height(random.randint(40,80)) 
                            cash = 1500 if difficulty.value == 1 else (1000 if difficulty.value == 2 else (500 if difficulty.value == 3 else 0))
                            bank = 0 
                        except Exception as e:
                            print(e)
                        try: 
                            await db.execute('''
                                INSERT INTO profiles (guild_id, user_id, charactername, age, gender, difficulty, height, cash, bank)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                                ON CONFLICT(guild_id, user_id) DO UPDATE SET
                                    charactername = excluded.charactername,
                                    age = excluded.age,
                                    gender = excluded.gender,
                                    difficulty = excluded.difficulty,
                                    height = excluded.height,
                                    cash = excluded.cash,
                                    bank = excluded.bank
                            ''', (guild_id, user_id, charactername, age, gender.name, difficulty.name, height, cash, bank)) 
                            await db.commit()
                            await interaction.response.send_message(
                                embed=discord.Embed(description=f"`Successfully created: {charactername}`", colour=constants.colorHexes["Success"]),
                                ephemeral=True
                            )
                        except Exception as e:
                            print(f"Unexpected error during profile creation: {e}")
            except Exception as e:
                        print(e)
            
    @app_commands.command(name="profile", description="Gets the profile of a user.")
    async def profile(self, interaction: discord.Interaction, user: discord.Member):
        user_id = user.id
        guild_id = interaction.guild.id
        async with aiosqlite.connect('profiles.db') as db:
            async with db.execute('''SELECT charactername, age, gender, difficulty, height, cash, bank FROM profiles WHERE guild_id = ? AND user_id = ?''', (guild_id, user_id)) as cursor:
                profile = await cursor.fetchone()
                if not profile:
                    await interaction.response.send_message(embed=discord.Embed(description="`This user doesn't have a profile`", colour=constants.colorHexes["Danger"]), ephemeral=True)
                    return
                else:
                    charactername, age, gender, difficulty, height, cash, bank = profile
                    embed = discord.Embed(
                        title=f"{user.display_name}'s Profile",
                        description=f"**Roleplay Information**\n\n"
                                    f"**Character Name:** `{charactername}`\n"
                                    f"**Age:** `{age}`\n"
                                    f"**Gender:** `{gender}`\n"
                                    f"**Height:** `{height}`\n"
                                    f"**Difficulty:** `{difficulty}`\n\n"
                                    f"**Easy Banking**\n\n"
                                    f"**Cash:** `{utils.to_money(cash)}`\n"
                                    f"**Bank:** `{utils.to_money(bank)}`",
                        colour=constants.colorHexes['MediumBlue']
                    )
                    await interaction.response.send_message(embed=embed)

                    
    @app_commands.command(name="deleteprofile", description="Deletes your profile.")
    async def deleteprofile(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        guild_id = interaction.guild.id
        async with aiosqlite.connect('profiles.db') as db:
            async with db.execute('''SELECT charactername FROM profiles WHERE guild_id = ? AND user_id = ?''', (guild_id, user_id)) as cursor:
                profile = await cursor.fetchone()
                if not profile:
                    await interaction.response.send_message(embed=discord.Embed(description="`You don't have a profile to delete!`", colour=constants.colorHexes["Danger"]), ephemeral=True)
                    return
                else:
                    await db.execute('''DELETE FROM profiles WHERE guild_id = ? AND user_id = ?''', (guild_id, user_id))
                    await db.commit()
                    await interaction.response.send_message(embed=discord.Embed(description="`Profile deleted successfully.`", colour=constants.colorHexes["Success"]), ephemeral=True)
        
    @app_commands.command(name="addmoney", description="Adds money to a profile.")
    async def addmoney(self, interaction: discord.Interaction, user: discord.Member, amount: int):
        user_id = user.id
        guild_id = interaction.guild.id
        
        # Ensure the amount is positive
        if amount < 0:
            await interaction.response.send_message(embed=discord.Embed(description="`Amount must be positive.`", colour=constants.colorHexes["Danger"]), ephemeral=True)
            return

        async with aiosqlite.connect('profiles.db') as db:
            # Fetch the current cash balance for the user
            async with db.execute('''SELECT cash FROM profiles WHERE guild_id = ? AND user_id = ?''', (guild_id, user_id)) as cursor:
                profile = await cursor.fetchone()

                if not profile:
                    # Send a response if no profile exists
                    await interaction.response.send_message(embed=discord.Embed(description="`This user doesn't have a profile.`", colour=constants.colorHexes["Danger"]), ephemeral=True)
                    return

                # Get the current cash balance
                cash = profile[0]

                # Add the specified amount to the current cash
                new_cash = cash + amount

                # Update the user's cash balance in the database
                await db.execute('''UPDATE profiles SET cash = ? WHERE guild_id = ? AND user_id = ?''', (new_cash, guild_id, user_id))
                await db.commit()

                # Send a confirmation response
                await interaction.response.send_message(embed=discord.Embed(description=f"`{utils.to_money(amount)} has been added to {user.display_name}'s balance. New balance: {utils.to_money(new_cash)}`", colour=constants.colorHexes["Success"]), ephemeral=True)
                
    
    @app_commands.command(name="removemoney", description="Removes money from a profile.")
    async def removemoney(self, interaction: discord.Interaction, user: discord.Member, amount: int):
        user_id = user.id
        guild_id = interaction.guild.id
        
        # Ensure the amount is positive
        if amount < 0:
            await interaction.response.send_message(embed=discord.Embed(description="`Amount must be positive.`", colour=constants.colorHexes["Danger"]), ephemeral=True)
            return

        async with aiosqlite.connect('profiles.db') as db:
            # Fetch the current cash balance for the user
            async with db.execute('''SELECT cash FROM profiles WHERE guild_id = ? AND user_id = ?''', (guild_id, user_id)) as cursor:
                profile = await cursor.fetchone()

                if not profile:
                    # Send a response if no profile exists
                    await interaction.response.send_message(embed=discord.Embed(description="`This user doesn't have a profile.`", colour=constants.colorHexes["Danger"]), ephemeral=True)
                    return

                # Get the current cash balance
                cash = profile[0]

                # Add the specified amount to the current cash
                new_cash = cash - amount

                # Update the user's cash balance in the database
                await db.execute('''UPDATE profiles SET cash = ? WHERE guild_id = ? AND user_id = ?''', (new_cash, guild_id, user_id))
                await db.commit()

                # Send a confirmation response
                await interaction.response.send_message(embed=discord.Embed(description=f"`{utils.to_money(amount)} has been removed {user.display_name}'s balance. New balance: {utils.to_money(new_cash)}`", colour=constants.colorHexes["Success"]), ephemeral=True)


    
            
async def setup(bot):
    ProfileAdmin_cog = ProfileAdmin(bot)
    await bot.add_cog(ProfileAdmin_cog)