import discord
from discord.ext import commands, tasks
from discord import app_commands
import os
import json
import random
from datetime import datetime, timedelta 
import aiosqlite
import constants
from utilities import utils
from utilities.embeds import basicEmbeds
from jobutilities import jobs, attributes

class ConfirmButton(discord.ui.View):
    def __init__(self, user_id, listing, attributes_json, occupation):
        super().__init__(timeout=100)
        self.user_id = user_id
        self.listing = listing
        self.attributes_json = attributes_json
        self.occupation = occupation

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.danger)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            if interaction.user.id != self.user_id:
                embed = discord.Embed(
                    description="This is not your button!",
                    colour=constants.colorHexes["Danger"]
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            applied_job = self.listing
            attributes_data = json.loads(self.attributes_json) if self.attributes_json else {}

            # Deserialize attributes
            attribute_objects = {k: attributes.Attribute.from_dict(v) for k, v in attributes_data.items()}

            # Check for missing requirements
            missing_requirements = [
                f"{attribute.capitalize()} | **Required:** {required_value} | **You have:** {attribute_objects[attribute].GetLevel()}"
                for attribute, required_value in applied_job.requirements.items()
                if attribute_objects.get(attribute, attributes.Attribute()).GetLevel() < required_value
            ]

            if missing_requirements:
                embed = discord.Embed(
                    title="Application Failed",
                    description=f"You do not meet the requirements for the job {applied_job.name}.\n\n***Missing requirements:***\n" + "\n".join(missing_requirements),
                    colour=constants.colorHexes["DarkBlue"]
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return

            job_key = next(key for key, job in jobs.Jobs.items() if job == applied_job)

            # Open a new database connection here
            async with aiosqlite.connect('profiles.db') as db:
                await db.execute(
                    '''UPDATE profiles SET occupation = ? WHERE guild_id = ? AND user_id = ?''',
                    (job_key, interaction.guild.id, self.user_id)
                )
                await db.commit()

            embed = discord.Embed(
                title="Application Successful",
                description=f"Successfully applied for `{applied_job.name}`. You are now paid `{utils.to_money(applied_job.pay)}` per hour.",
                colour=constants.colorHexes["DarkBlue"]
            )
            await interaction.response.send_message(embed=embed)

        except Exception as e:
            print(e)

class Apply(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Apply is ready.")    

    @app_commands.command(name="checklisting", description="Checks the current job listing")
    async def checklisting(self, interaction: discord.Interaction):
        guild_id = interaction.guild_id

        listing_instance = jobs.Listing()

        try:
            if listing_instance.CheckUpdate(guild_id):
                listing_instance.GenerateListings(guild_id)
        except Exception as e:
            print(e)

        listing = listing_instance.GetListing(guild_id)

        if not listing:
            embed = discord.Embed(
                description=f"`No jobs available right now. Please try again later.`",
                colour=constants.colorHexes["DarkBlue"])
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        try:
            job_descriptions = "\n".join([f"**{listing.GetName()}**: {listing.GetDesc()} | **Pay:** `${listing.GetPay()}/hour)`"])
        except Exception as e:
            print(e)
            job_descriptions = "`An error occurred while generating job descriptions.`"
        except Exception as e:
            print(e)

        embed = discord.Embed(
            title="Current Job Listing",
            description=job_descriptions,
            colour=constants.colorHexes["LightBlue"]
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="apply", description="Apply for the current listing.")
    async def apply(self, interaction: discord.Interaction):
        guild_id = interaction.guild.id
        user_id = interaction.user.id

        async with aiosqlite.connect('profiles.db') as db:
            async with db.execute('''SELECT attributes, occupation FROM profiles WHERE guild_id = ? AND user_id = ?''', (guild_id, user_id)) as cursor:
                profile = await cursor.fetchone()

                if not profile:
                    await interaction.response.send_message(embed=basicEmbeds["SelfNoProfile"], ephemeral=True)
                    return

                attributes_json, occupation = profile

                listing_instance = jobs.Listing()

                try:
                    if listing_instance.CheckUpdate(guild_id):
                        listing_instance.GenerateListings(guild_id)
                except Exception as e:
                    print(e)

                listing = listing_instance.GetListing(guild_id)

                if not listing:
                    embed = discord.Embed(
                        description=f"`No jobs available right now. Please try again later.`",
                        colour=constants.colorHexes["DarkBlue"])
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                    return

                try:
                    job_descriptions = "\n".join([f"**{listing.GetName()}**: {listing.GetDesc()} | **Pay:** `${listing.GetPay()}/hour)`"])
                except Exception as e:
                    print(e)
                    job_descriptions = "`An error occurred while generating job descriptions.`"
                except Exception as e:
                    print(e)

                view = ConfirmButton(user_id, listing, attributes_json, occupation)

                embed = discord.Embed(
                    title="Current Job Listing",
                    description=f"{job_descriptions} | Are you sure you'd like to apply?",
                    colour=constants.colorHexes["LightBlue"]
                )
                await interaction.response.send_message(embed=embed, view=view)
                

async def setup(bot):
    Apply_cog = Apply(bot)
    await bot.add_cog(Apply_cog)