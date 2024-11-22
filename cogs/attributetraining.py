import discord
from discord.ext import commands, tasks
from discord import app_commands
import os
import json
import aiosqlite
import constants
from utilities import utils, logs
from utilities.embeds import basicEmbeds
from jobutilities import attributes

class AttributeTraining(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"AttributeTraining is ready.")

    async def handle_training(self, interaction: discord.Interaction, attribute_name: str, action: str, gain: float, description: str):
        guild_id = str(interaction.guild.id)
        user_id = str(interaction.user.id)

        async with aiosqlite.connect('profiles.db') as db:
            async with db.execute(
                '''SELECT attributes FROM profiles WHERE guild_id = ? AND user_id = ?''',
                (guild_id, user_id)
            ) as cursor:
                profile = await cursor.fetchone()

                if not profile:
                    await interaction.response.send_message(
                        embed=basicEmbeds["SelfNoProfile"], ephemeral=True
                    )
                    return

                attributes_json = profile[0]
                attributes_data = json.loads(attributes_json) if attributes_json else {}

                # Get or initialize attribute
                attribute = attributes.Attribute.from_dict(
                    attributes_data.get(attribute_name, {})
                )
                if not attribute.IsMaxLevel():
                    attribute.IncrLevel(gain)
                    attributes_data[attribute_name] = attribute.to_dict()
                    updated_attributes_json = json.dumps(attributes_data)

                    # Update database
                    await db.execute(
                        '''UPDATE profiles SET attributes = ? WHERE guild_id = ? AND user_id = ?''',
                        (updated_attributes_json, guild_id, user_id)
                    )
                    await db.commit()

                    # Log and respond
                    await logs.send_player_log(
                        self.bot, action, description,
                        utils.get_config(interaction.guild.id, 'log_channel_id'),
                        interaction.user
                    )
                    await interaction.response.send_message(
                        embed=discord.Embed(
                            description=f"`{description} | Total: {attribute.GetLevel()}%`",
                            colour=constants.colorHexes["LightBlue"]
                        )
                    )
                else:
                    await interaction.response.send_message(
                        embed=discord.Embed(
                            description=f"`Your {attribute_name} is already at the maximum level!`",
                            colour=constants.colorHexes["LightBlue"]
                        )
                    )

    @app_commands.command(name="workout", description="Increase your strength")
    @app_commands.checks.cooldown(3, 3600, key=lambda i: (i.guild_id, i.user.id))
    async def workout(self, interaction: discord.Interaction):
        await self.handle_training(
            interaction, "strength", "Workout", 0.25,
            "You did a workout and gained 0.25 strength"
        )

    @app_commands.command(name="study", description="Increase your intelligence")
    @app_commands.checks.cooldown(3, 3600, key=lambda i: (i.guild_id, i.user.id))
    async def study(self, interaction: discord.Interaction):
        await self.handle_training(
            interaction, "intelligence", "Studied", 0.25,
            "You did a study session and gained 0.25 intelligence"
        )

    @app_commands.command(name="paint", description="Increase your dexterity")
    @app_commands.checks.cooldown(3, 3600, key=lambda i: (i.guild_id, i.user.id))
    async def paint(self, interaction: discord.Interaction):
        await self.handle_training(
            interaction, "dexterity", "Paint", 0.25,
            "You painted a work of art and gained 0.25 dexterity"
        )

    @app_commands.command(name="socialize", description="Increase your charisma")
    @app_commands.checks.cooldown(3, 3600, key=lambda i: (i.guild_id, i.user.id))
    async def socialize(self, interaction: discord.Interaction):
        await self.handle_training(
            interaction, "charisma", "Socialize", 0.25,
            "You socialized and gained 0.25 charisma"
        )

    @app_commands.command(name="meditate", description="Increase your wisdom")
    @app_commands.checks.cooldown(3, 3600, key=lambda i: (i.guild_id, i.user.id))
    async def meditate(self, interaction: discord.Interaction):
        await self.handle_training(
            interaction, "wisdom", "Meditate", 0.25,
            "You meditated and gained 0.25 wisdom"
        )

    @workout.error
    async def workout_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CommandOnCooldown):
                retry_after = round(error.retry_after, 2)
                embed = discord.Embed(
                    description=f"❌ You are on cooldown! Try again in {utils.convert_seconds(round(retry_after))}.",
                    colour=constants.colorHexes["DarkBlue"]
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed = discord.Embed(
                description="❌ An unexpected error occurred. Please try again later.",
                colour=constants.colorHexes["Danger"]
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @study.error
    async def study_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CommandOnCooldown):
                retry_after = round(error.retry_after, 2)
                embed = discord.Embed(
                    description=f"❌ You are on cooldown! Try again in {utils.convert_seconds(round(retry_after))}.",
                    colour=constants.colorHexes["DarkBlue"]
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed = discord.Embed(
                description="❌ An unexpected error occurred. Please try again later.",
                colour=constants.colorHexes["Danger"]
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @meditate.error
    async def meditate_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CommandOnCooldown):
                retry_after = round(error.retry_after, 2)
                embed = discord.Embed(
                    description=f"❌ You are on cooldown! Try again in {utils.convert_seconds(round(retry_after))}.",
                    colour=constants.colorHexes["DarkBlue"]
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed = discord.Embed(
                description="❌ An unexpected error occurred. Please try again later.",
                colour=constants.colorHexes["Danger"]
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @paint.error
    async def paint_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CommandOnCooldown):
                retry_after = round(error.retry_after, 2)
                embed = discord.Embed(
                    description=f"❌ You are on cooldown! Try again in {utils.convert_seconds(round(retry_after))}.",
                    colour=constants.colorHexes["DarkBlue"]
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed = discord.Embed(
                description="❌ An unexpected error occurred. Please try again later.",
                colour=constants.colorHexes["Danger"]
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @socialize.error
    async def socialize_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CommandOnCooldown):
                retry_after = round(error.retry_after, 2)
                embed = discord.Embed(
                    description=f"❌ You are on cooldown! Try again in {utils.convert_seconds(round(retry_after))}.",
                    colour=constants.colorHexes["DarkBlue"]
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed = discord.Embed(
                description="❌ An unexpected error occurred. Please try again later.",
                colour=constants.colorHexes["Danger"]
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(AttributeTraining(bot))
