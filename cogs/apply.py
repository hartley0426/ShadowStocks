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
from jobutilities import jobs, attributes, educationutils

class ConfirmButton(discord.ui.View):
    def __init__(self, bot, user_id, listing, attributes_json, occupation, education_json):
        super().__init__(timeout=100)
        self.bot = bot
        self.user_id = user_id
        self.listing = listing
        self.attributes_json = attributes_json
        self.occupation = occupation
        self.education_json = education_json

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.danger)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
       
            if interaction.user.id != self.user_id:
                embed = discord.Embed(
                    description="This is not your button!",
                    colour=constants.colorHexes["Danger"]
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            attributes_data = json.loads(self.attributes_json) if self.attributes_json else {}
            education_data = json.loads(self.education_json) if self.education_json else {}

            job_object = jobs.Jobs.get(self.listing, jobs.Jobs["unemployed"])
        
            job_name = job_object.GetName()
            job_pay = job_object.GetPay()
            job_requirements = job_object.GetRequirements()
            job_education = job_object.GetEducation()



            attribute_objects = {k: attributes.Attribute.from_dict(v) for k, v in attributes_data.items()}
            education_objects = {key: educationutils.Degrees[key] for key in education_data}
    
            
            missing_requirements = [
                f"{attribute.capitalize()} | **Required:** {required_value} | **You have:** {attribute_objects[attribute].GetLevel()}"
                for attribute, required_value in job_requirements.items()
                if attribute_objects.get(attribute, attributes.Attribute()).GetLevel() < required_value
            ]
            
            missing_education = [
                f"**Required:** `{educationutils.Degrees[education].get_name()}`"  
                for education in job_education
                if education not in education_objects
            ]

            if missing_education:
                embed = discord.Embed(
                    title="Application Failed",
                    description=f"You do not meet the requirements for the job `{job_name}`.\n\n***Missing degrees:***\n\n" + "\n".join(missing_education),
                    colour=constants.colorHexes["DarkBlue"]
                )
                embed.set_footer(text="Do /college to get degrees")
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
    
             
            if missing_requirements:
                embed = discord.Embed(
                    title="Application Failed",
                    description=f"You do not meet the requirements for the job `{job_name}`.\n\n***Missing requirements:***\n\n" + "\n".join(missing_requirements),
                    colour=constants.colorHexes["DarkBlue"]
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            async with aiosqlite.connect('profiles.db') as db:
                await db.execute(
                    '''UPDATE profiles SET occupation = ? WHERE guild_id = ? AND user_id = ?''',
                    (self.listing, interaction.guild.id, self.user_id)
                )
                await db.commit()
                embed = discord.Embed(
                    title="Application Successful",
                    description=f"Successfully applied for `{job_name}`. You are now paid `{utils.to_money(job_pay)}` per hour.",
                    colour=constants.colorHexes["DarkBlue"]
                )
                await logs.send_player_log(self.bot, 'Application', f"Successfully applied for {job_name}", utils.get_config(interaction.guild.id, 'log_channel_id'), interaction.user)
                await interaction.response.send_message(embed=embed)
    

        
            

class Apply(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Apply is ready.")  

    @app_commands.command(name="forcelisting", description="Forces the current listing.")
    @app_commands.describe(listing="The listing you'd like to force the current listing to be.")
    async def forcelisting(self, interaction: discord.Interaction, listing: str):
        moderator_id = utils.get_config(interaction.guild.id, "moderator_role_id")
        if not interaction.user.get_role(moderator_id):
            await interaction.response.send_message(embed=basicEmbeds["SelfNoPermission"], ephemeral=True)
            return
        if listing not in jobs.Jobs:
            embed = discord.Embed(description="`This listing doesn't exist`", color=discord.Color.red())
            await interaction.response.send_message(embed=embed)
        else:
            job_key = listing
            logs.send_player_log(self.bot, "Force Listing", f"Forced listing to: {listing}", utils.get_config(interaction.guild.id, 'log_channel_id'), interaction.user)
            jobs.listings[interaction.guild.id] = listing

            job_object = jobs.Jobs.get(listing, jobs.Jobs["unemployed"])

            jobs.last_updated[interaction.guild.id] = datetime.now()
    
            job_name = job_object.GetName()

            embed = discord.Embed(
                description=f"Listing set to `{job_name}`",
                color=constants.colorHexes["Success"],
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="checklisting", description="Checks the current job listing")
    async def checklisting(self, interaction: discord.Interaction):
        guild_id = interaction.guild_id

        listing_instance = jobs.Listing()

        if listing_instance.CheckUpdate(guild_id):
            listing_instance.GenerateListings(guild_id)

        listing = jobs.listings.get(guild_id)

        job_object = jobs.Jobs.get(listing, jobs.Jobs["unemployed"])
        
        job_name = job_object.GetName()
        job_desc = job_object.GetDesc()
        job_pay = job_object.GetPay()

        if not listing:
            embed = discord.Embed(
                description=f"`No jobs available right now. Please try again later.`",
                colour=constants.colorHexes["DarkBlue"])
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        try:
            job_descriptions = "\n".join([f"**{job_name}**: {job_desc} \n\n**Pay:** `{utils.to_money(job_pay)}/hour)`"])
        except Exception:
            job_descriptions = "`An error occurred while generating job descriptions.`"

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
            async with db.execute('''SELECT attributes, occupation, education FROM profiles WHERE guild_id = ? AND user_id = ?''', (guild_id, user_id)) as cursor:
                profile = await cursor.fetchone()

                if not profile:
                    await interaction.response.send_message(embed=basicEmbeds["SelfNoProfile"], ephemeral=True)
                    return

                attributes_json, occupation, education_json = profile

                listing_instance = jobs.Listing()

                if listing_instance.CheckUpdate(guild_id):
                    listing_instance.GenerateListings(guild_id)

                listing = jobs.listings.get(guild_id)

                job_object = jobs.Jobs.get(listing, jobs.Jobs["unemployed"])
                
                job_name = job_object.GetName()
                job_desc = job_object.GetDesc()
                job_pay = job_object.GetPay()

                if not listing:
                    embed = discord.Embed(
                        description=f"`No jobs available right now. Please try again later.`",
                        colour=constants.colorHexes["DarkBlue"])
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                    return

                try:
                    job_descriptions = "\n".join([f"**{job_name}**: {job_desc} \n\n**Pay:** `{utils.to_money(job_pay)}/hour)`"])
                except Exception:
                    job_descriptions = "`An error occurred while generating job descriptions.`"

                view = ConfirmButton(self.bot, user_id, listing, attributes_json, occupation, education_json)

                embed = discord.Embed(
                    title="Current Job Listing",
                    description=f"{job_descriptions}\n\nAre you sure you'd like to apply?",
                    colour=constants.colorHexes["LightBlue"]
                )
                await interaction.response.send_message(embed=embed, view=view)
                

async def setup(bot):
    Apply_cog = Apply(bot)
    await bot.add_cog(Apply_cog)