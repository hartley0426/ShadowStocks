import discord
from discord.ext import commands, tasks
from discord import app_commands
import json
import os
import random
from datetime import datetime 
import aiosqlite
import constants
from utilities import utils, logs
from utilities.embeds import basicEmbeds
from jobutilities import attributes, jobs


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
    @app_commands.describe(charactername="The name of your character", gender="The gender of your character", difficulty="The mode you are playing on. Rich = Easy, Homeless = Hard")
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

                            occupation = "unemployed"
                            moneylastcollected = "never"

                            strength_level = 20.0 if difficulty.value == 1 else (15.0 if difficulty.value == 2 else (10.0 if difficulty.value == 3 else 5.0))
                            dexterity_level  = 20.0 if difficulty.value == 1 else (15.0 if difficulty.value == 2 else (10.0 if difficulty.value == 3 else 5.0))
                            intelligence_level  = 20.0 if difficulty.value == 1 else (15.0 if difficulty.value == 2 else (10.0 if difficulty.value == 3 else 5.0))
                            charisma_level  = 20.0 if difficulty.value == 1 else (15.0 if difficulty.value == 2 else (10.0 if difficulty.value == 3 else 5.0))
                            wisdom_level  = 20.0 if difficulty.value == 1 else (15.0 if difficulty.value == 2 else (10.0 if difficulty.value == 3 else 5.0))

                            basic_attributes = {
                                "strength": attributes.Attribute(level=strength_level, minimum=0.0, maximum=100.0).to_dict(),
                                "dexterity": attributes.Attribute(level=dexterity_level, minimum=0.0, maximum=100.0).to_dict(),
                                "intelligence": attributes.Attribute(level=intelligence_level, minimum=0.0, maximum=100.0).to_dict(),
                                "charisma": attributes.Attribute(level=charisma_level, minimum=0.0, maximum=100.0).to_dict(),
                                "wisdom": attributes.Attribute(level=wisdom_level, minimum=0.0, maximum=100.0).to_dict()
                            }
                            
                            items = {}
                            education = {}
                            property = {}

                        except Exception as e:
                            print(e)
                        try: 
                            attributes_json = json.dumps(basic_attributes)
                            items_json = json.dumps(items)
                            education_json = json.dumps(education)
                            property_json = json.dumps(property)
                            await db.execute('''
                                INSERT INTO profiles (guild_id, user_id, charactername, age, gender, difficulty, height, cash, bank, attributes, occupation, moneylastcollected, items, education, property)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                ON CONFLICT(guild_id, user_id) DO UPDATE SET
                                    charactername = excluded.charactername,
                                    age = excluded.age,
                                    gender = excluded.gender,
                                    difficulty = excluded.difficulty,
                                    height = excluded.height,
                                    cash = excluded.cash,
                                    bank = excluded.bank,
                                    attributes = excluded.attributes,
                                    occupation = excluded.occupation,
                                    moneylastcollected = excluded.moneylastcollected,
                                    items = excluded.items,
                                    education = excluded.education,
                                    property = excluded.property
                            ''', (guild_id, user_id, charactername, age, gender.name, difficulty.name, height, cash, bank, attributes_json, occupation, moneylastcollected, items_json, education_json, property_json)) 
                            await db.commit()
                            await interaction.response.send_message(
                                embed=discord.Embed(description=f"`Successfully created: {charactername}`", colour=constants.colorHexes["Success"]),
                                ephemeral=True
                            )

                            await logs.send_player_log(self.bot, 'Profile Creation', f"Created Profile with name of {charactername} | Difficulty: {difficulty.name} ", utils.get_config(interaction.guild.id, 'log_channel_id'), interaction.user)

                        except Exception as e:
                            print(f"Unexpected error during profile creation: {e}")
            except Exception as e:
                        print(e)

    @app_commands.command(name="setlevel", description="Set all of your attribute levels")
    async def setlevel(self, interaction: discord.Interaction, member: discord.Member, strength: float, intelligence: float, dexterity: float, charisma: float, wisdom: float):
        guild_id = str(interaction.guild.id)
        user_id = str(member.id)
        async with aiosqlite.connect('profiles.db') as db:
            async with db.execute('''SELECT attributes FROM profiles WHERE guild_id = ? AND user_id = ?''', (guild_id, user_id)) as cursor:
                profile = await cursor.fetchone()
                if not profile:
                    await interaction.response.send_message(embed=basicEmbeds["OtherNoProfile"], ephemeral=True)
                    return
                

                attributes_json = profile[0]
                attributes_data = json.loads(attributes_json) if attributes_json else {}

                strength_attribute = attributes.Attribute.from_dict(attributes_data.get("strength", {}))
                dexterity_attribute = attributes.Attribute.from_dict(attributes_data.get("dexterity", {}))
                intelligence_attribute = attributes.Attribute.from_dict(attributes_data.get("intelligence", {}))
                charisma_attribute = attributes.Attribute.from_dict(attributes_data.get("charisma", {}))
                wisdom_attribute = attributes.Attribute.from_dict(attributes_data.get("wisdom", {})) 


                if strength > 100:
                    await interaction.response.send_message(embed=discord.Embed(description="Must be below 100", colour=constants.colorHexes["Danger"]))
                else:
                    strength_attribute.SetLevel(strength)
                    attributes_data["strength"] = strength_attribute.to_dict()

                if intelligence > 100:
                    await interaction.response.send_message(embed=discord.Embed(description="Must be below 100", colour=constants.colorHexes["Danger"]))
                else:
                    intelligence_attribute.SetLevel(intelligence)
                    attributes_data["intelligence"] = intelligence_attribute.to_dict()

                if dexterity > 100:
                    await interaction.response.send_message(embed=discord.Embed(description="Must be below 100", colour=constants.colorHexes["Danger"]))
                else:
                    dexterity_attribute.SetLevel(dexterity)
                    attributes_data["dexterity"] = dexterity_attribute.to_dict()

                if charisma > 100:
                    await interaction.response.send_message(embed=discord.Embed(description="Must be below 100", colour=constants.colorHexes["Danger"]))
                else:
                    charisma_attribute.SetLevel(charisma)
                    attributes_data["charisma"] = charisma_attribute.to_dict()

                if wisdom > 100:
                    await interaction.response.send_message(embed=discord.Embed(description="Must be below 100", colour=constants.colorHexes["Danger"]))
                else:
                    wisdom_attribute.SetLevel(wisdom)
                    attributes_data["wisdom"] = wisdom_attribute.to_dict()

                updated_attributes_json = json.dumps(attributes_data)

                await db.execute('''UPDATE profiles SET attributes = ? WHERE guild_id = ? AND user_id = ?''',(updated_attributes_json, guild_id, user_id))
                await db.commit()
                await logs.send_player_log(self.bot, 'Set Level', f"Changed Level", utils.get_config(interaction.guild.id, 'log_channel_id'), interaction.user, member)

                await interaction.response.send_message(embed=discord.Embed(description="`Levels set`"))
            
    @app_commands.command(name="profile", description="Gets the profile of a user.")
    async def profile(self, interaction: discord.Interaction, user: discord.Member):
        user_id = user.id
        guild_id = interaction.guild.id
        async with aiosqlite.connect('profiles.db') as db:
            async with db.execute('''SELECT charactername, age, gender, difficulty, height, cash, bank, attributes, occupation FROM profiles WHERE guild_id = ? AND user_id = ?''', (guild_id, user_id)) as cursor:
                profile = await cursor.fetchone()
                if not profile:
                    await interaction.response.send_message(embed=discord.Embed(description="`This user doesn't have a profile`", colour=constants.colorHexes["Danger"]), ephemeral=True)
                    return
                else:
                    charactername, age, gender, difficulty, height, cash, bank, attributes_json, occupation = profile
                    attributes_data = json.loads(attributes_json) if attributes_json else {}

                    strength_attribute = attributes.Attribute.from_dict(attributes_data.get("strength", {}))
                    strength_percentage = strength_attribute.GetLevelPercentage()

                    dexterity_attribute = attributes.Attribute.from_dict(attributes_data.get("dexterity", {}))
                    dexterity_percentage = dexterity_attribute.GetLevelPercentage()

                    intelligence_attribute = attributes.Attribute.from_dict(attributes_data.get("intelligence", {}))
                    intelligence_percentage = intelligence_attribute.GetLevelPercentage()

                    charisma_attribute = attributes.Attribute.from_dict(attributes_data.get("charisma", {}))
                    charisma_percentage = charisma_attribute.GetLevelPercentage()

                    wisdom_attribute = attributes.Attribute.from_dict(attributes_data.get("wisdom", {}))
                    wisdom_percentage = wisdom_attribute.GetLevelPercentage()

                    job_key = occupation
                    job_object = jobs.Jobs.get(job_key, jobs.Jobs["unemployed"])
                    job_name = job_object.GetName()
                    job_desc = job_object.GetDesc()
                    job_pay = job_object.GetPay()
                                                                        
                    profile_embed = discord.Embed(
                        title=f"{user.display_name}'s Profile",
                        description=f"**Roleplay Information**\n\n"
                                    f"**Character Name:** `{charactername}`\n"
                                    f"**Age:** `{age}`\n"
                                    f"**Gender:** `{gender}`\n"
                                    f"**Height:** `{height}`\n"
                                    f"**Difficulty:** `{difficulty}`\n\n"
                                    f"**Easy Banking**\n\n"
                                    f"**Cash:** `{utils.to_money(cash)}`\n"
                                    f"**Bank:** `{utils.to_money(bank)}`\n\n"
                                    f"**Attributes**\n\n"
                                    f"**Strength:** `{strength_percentage}%`\n"
                                    f"**Dexterity:** `{dexterity_percentage}%`\n"
                                    f"**Intelligence:** `{intelligence_percentage}%`\n"
                                    f"**Charisma:** `{charisma_percentage}%`\n"
                                    f"**Wisdom:** `{wisdom_percentage}%`\n\n"
                                    f"**Full Time Job**\n\n"
                                    f"**Job:** `{job_name}`\n"
                                    f"**Description:** `{job_desc}`\n"
                                    f"**Pay:** `{utils.to_money(job_pay)}`\n",
                                    
                        colour=constants.colorHexes['MediumBlue']
                    )

                    if user.avatar:
                        profile_embed.set_thumbnail(url=user.avatar.url)

                    await interaction.response.send_message(embed=profile_embed)
                    
    @app_commands.command(name="deleteprofile", description="Deletes your profile.")
    async def deleteprofile(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        guild_id = interaction.guild.id
        async with aiosqlite.connect('profiles.db') as db:
            async with db.execute('''SELECT charactername FROM profiles WHERE guild_id = ? AND user_id = ?''', (guild_id, user_id)) as cursor:
                profile = await cursor.fetchone()
                if not profile:
                    await interaction.response.send_message(embed=basicEmbeds["SelfNoProfile"], ephemeral=True)
                    return
                else:
                    await db.execute('''DELETE FROM profiles WHERE guild_id = ? AND user_id = ?''', (guild_id, user_id))
                    await db.commit()
                    await logs.send_player_log(self.bot, 'Profile Creation', f"Deleted their profile", utils.get_config(interaction.guild.id, 'log_channel_id'), interaction.user)
                    await interaction.response.send_message(embed=discord.Embed(description="`Profile deleted successfully.`", colour=constants.colorHexes["Success"]), ephemeral=True)
        
    @app_commands.command(name="addmoney", description="Adds money to a profile.")
    @app_commands.describe(user="The user to give money to", amount="The amount of money")
    async def addmoney(self, interaction: discord.Interaction, user: discord.Member, amount: int):
        user_id = user.id
        guild_id = interaction.guild.id

        moderator_id = utils.get_config(guild_id, "moderator_role_id")
        if not user.get_role(moderator_id):
            await interaction.response.send_message(embed=basicEmbeds["SelfNoPermission"], ephemeral=True)
            return
        
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
                    await interaction.response.send_message(embed=basicEmbeds["OtherNoProfile"], ephemeral=True)
                    return

                # Get the current cash balance
                cash = profile[0]

                # Add the specified amount to the current cash
                new_cash = cash + amount

                # Update the user's cash balance in the database
                await db.execute('''UPDATE profiles SET cash = ? WHERE guild_id = ? AND user_id = ?''', (new_cash, guild_id, user_id))
                await db.commit()
                await logs.send_player_log(self.bot, 'Money Addition', f"Gave ${amount}", utils.get_config(interaction.guild.id, 'log_channel_id'), interaction.user, user)
                # Send a confirmation response
                await interaction.response.send_message(embed=discord.Embed(description=f"`{utils.to_money(amount)} has been added to {user.display_name}'s balance.`\n\n **New balance:** `{utils.to_money(new_cash)}`", colour=constants.colorHexes["Success"]), ephemeral=True)
                
    
    @app_commands.command(name="removemoney", description="Removes money from a profile.")
    @app_commands.describe(user="The user to take money from", amount="The amount of money")
    async def removemoney(self, interaction: discord.Interaction, user: discord.Member, amount: int):
        user_id = user.id
        guild_id = interaction.guild.id

        moderator_id = utils.get_config(guild_id, "moderator_role_id")
        if not user.get_role(moderator_id):
            await interaction.response.send_message(embed=basicEmbeds["SelfNoPermission"], ephemeral=True)
            return
        
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
                    await interaction.response.send_message(embed=basicEmbeds["OtherNoProfile"], ephemeral=True)
                    return

                # Get the current cash balance
                cash = profile[0]

                # Add the specified amount to the current cash
                new_cash = cash - amount

                # Update the user's cash balance in the database
                await db.execute('''UPDATE profiles SET cash = ? WHERE guild_id = ? AND user_id = ?''', (new_cash, guild_id, user_id))
                await db.commit()
                await logs.send_player_log(self.bot, 'Money Removal', f"Removed ${amount}", utils.get_config(interaction.guild.id, 'log_channel_id'), interaction.user, user)
                # Send a confirmation response
                await interaction.response.send_message(embed=discord.Embed(description=f"`{utils.to_money(amount)} has been removed {user.display_name}'s balance.`\n\n **New balance:** `{utils.to_money(new_cash)}`", colour=constants.colorHexes["Success"]), ephemeral=True)


    
            
async def setup(bot):
    ProfileAdmin_cog = ProfileAdmin(bot)
    await bot.add_cog(ProfileAdmin_cog)