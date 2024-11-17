import discord
from discord.ext import commands, tasks
from discord import app_commands
import os
import random
from datetime import datetime, timedelta 
import aiosqlite
import constants
from utilities import utils, logs
from utilities.embeds import basicEmbeds

RED_NUMBERS = {1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36}
GREEN_NUMBERS = {0}
BLACK_NUMBERS = {2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35}
EVEN_NUMBERS = {2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36}
ODD_NUMBERS = {1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31, 33, 35}
ROULETTE_MIN = 0
ROULETTE_MAX = 36

def get_color(number: int) -> str:
    if number in RED_NUMBERS:
        return "red"
    elif number in BLACK_NUMBERS:
        return "black"
    elif number in GREEN_NUMBERS:
        return "green"
    
def get_parity(number: int) -> str:
    if number in EVEN_NUMBERS:
            return "even"
    elif number in ODD_NUMBERS:
        return "odd"
    elif number in GREEN_NUMBERS:
        return "zero"

class Roulette(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Roulette is ready.")    

    @app_commands.command(name="roulette", description="Plays a game of roulette")
    @app_commands.describe(choice="The space you are placing your bet on", bet="The amount of money you are betting.")
    @app_commands.choices(choice=[
        discord.app_commands.Choice(name="0", value=0),
        discord.app_commands.Choice(name="1-18", value=1),
        discord.app_commands.Choice(name="19-36", value=2),
        discord.app_commands.Choice(name="1-12", value=3),
        discord.app_commands.Choice(name="13-24", value=4),
        discord.app_commands.Choice(name="25-36", value=5),
        discord.app_commands.Choice(name="1-9", value=6),
        discord.app_commands.Choice(name="10-18", value=7),
        discord.app_commands.Choice(name="19-27", value=8),
        discord.app_commands.Choice(name="28-36", value=9),
        discord.app_commands.Choice(name="Even", value=37),
        discord.app_commands.Choice(name="Odd", value=38),
        discord.app_commands.Choice(name="Red", value=39),
        discord.app_commands.Choice(name="Black", value=40)])
    async def roulette(self, interaction: discord.Interaction, choice: discord.app_commands.Choice[int], bet: int):
        guild_id = interaction.guild.id
        user_id = interaction.user.id
        if bet < 100:
                    embed = discord.Embed(
                        description="`You must bet more than $100`",
                        colour=constants.colorHexes["Danger"]
                        )
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                    return
        
        async with aiosqlite.connect('profiles.db') as db:
            async with db.execute('''SELECT cash, charactername FROM profiles WHERE guild_id = ? AND user_id = ?''', (guild_id, user_id)) as cursor:
                profile = await cursor.fetchone() 
                
                if not profile:
                    await interaction.response.send_message(embed=basicEmbeds["SelfNoProfile"], ephemeral=True)
                    return
                
                cash, charactername = profile

                if bet > cash:
                    embed = discord.Embed(
                        description="`You don't have enough money!`",
                        colour=constants.colorHexes["Danger"]
                        )
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                    return
                
                removed_bet_cash = cash-bet

                await utils.set_cash(db, removed_bet_cash, guild_id, user_id)

                rolled_number = random.randint(ROULETTE_MIN, ROULETTE_MAX)
                number_color = get_color(rolled_number)
                number_parity = get_parity(rolled_number)

                if choice.value in (0, 1, 2):
                    if choice.value == 0:
                        if choice.value == rolled_number:
                            payout = 71 * bet
                            new_cash = removed_bet_cash + payout
                            await utils.set_cash(db, new_cash, guild_id, user_id)

                            embed = discord.Embed(
                                colour=constants.colorHexes["MediumBlue"],
                                title="Roulette won!",
                                description=f"`{charactername}` has won **${payout}**\n\n"
                                            f"**Bet:** `${bet}\n`"
                                            f"**Choice Picked:** `{choice.name}\n`"
                                            f"**Number Rolled:** `{number_color.capitalize()} {rolled_number} | {number_parity.capitalize()}`"
                                )
                            await logs.send_player_log(self.bot, 'Roulette', f"Won {payout}", utils.get_config(interaction.guild.id, 'log_channel_id'), interaction.user)
                            embed.set_footer(text=f"{interaction.user} has won ${payout}")
                            await interaction.response.send_message(embed=embed)

                        else: 
                            embed = discord.Embed(
                                colour=constants.colorHexes["MediumBlue"],
                                title="Roulette Lost!",
                                description=f"`{charactername}` has lost.\n\n"
                                            f"**Bet:** `${bet}\n`"
                                            f"**Choice Picked:** `{choice.name}\n`"
                                            f"**Number Rolled:** `{number_color.capitalize()} {rolled_number} | {number_parity.capitalize()}`"
                            )
                            await logs.send_player_log(self.bot, 'Roulette', f"Lost", utils.get_config(interaction.guild.id, 'log_channel_id'), interaction.user)
                            embed.set_footer(text=f"{interaction.user} lost.")
                            await interaction.response.send_message(embed=embed)

                    else:
                        if choice.value == rolled_number:
                            payout = 2 * bet
                            new_cash = removed_bet_cash + payout
                            await utils.set_cash(db, new_cash, guild_id, user_id)
                            embed = discord.Embed(
                                colour=constants.colorHexes["MediumBlue"],
                                title="Roulette won!",
                                description=f"`{charactername}` has won **${payout}**\n\n"
                                            f"**Bet:** `${bet}\n`"
                                            f"**Choice Picked:** `{choice.name}\n`"
                                            f"**Number Rolled:** `{number_color.capitalize()} {rolled_number} | {number_parity.capitalize()}`"
                            )
                            await logs.send_player_log(self.bot, 'Roulette', f"Won {payout}", utils.get_config(interaction.guild.id, 'log_channel_id'), interaction.user)
                            embed.set_footer(text=f"{interaction.user} has won ${payout}")
                            await interaction.response.send_message(embed=embed)
                        else:
                            embed = discord.Embed(
                                colour=constants.colorHexes["MediumBlue"],
                                title="Roulette Lost!",
                                description=f"`{charactername}` has lost.\n\n"
                                            f"**Bet:** `${bet}\n`"
                                            f"**Choice Picked:** `{choice.name}\n`"
                                            f"**Number Rolled:** `{number_color.capitalize()} {rolled_number} | {number_parity.capitalize()}`"
                            )
                            await logs.send_player_log(self.bot, 'Roulette', f"Lost", utils.get_config(interaction.guild.id, 'log_channel_id'), interaction.user)
                            embed.set_footer(text=f"{interaction.user} lost.")
                            await interaction.response.send_message(embed=embed)

                elif int(choice.value) in (6, 7, 8, 9):
                    if choice.value == rolled_number:
                        payout = 6 * bet
                        new_cash = removed_bet_cash + payout
                        await utils.set_cash(db, new_cash, guild_id, user_id)
                        embed = discord.Embed(
                            colour=constants.colorHexes["MediumBlue"],
                            title="Roulette won!",
                            description=f"`{charactername}` has won **${payout}**\n\n"
                                        f"**Bet:** `${bet}\n`"
                                        f"**Choice Picked:** `{choice.name}\n`"
                                        f"**Number Rolled:** `{number_color.capitalize()} {rolled_number} | {number_parity.capitalize()}`"
                        )
                        await logs.send_player_log(self.bot, 'Roulette', f"Won {payout}", utils.get_config(interaction.guild.id, 'log_channel_id'), interaction.user)
                        embed.set_footer(text=f"{interaction.user} has won ${payout}")
                        await interaction.response.send_message(embed=embed)
                    else:
                        embed = discord.Embed(
                            colour=constants.colorHexes["MediumBlue"],
                            title="Roulette Lost!",
                            description=f"`{charactername}` has lost.\n\n"
                                        f"**Bet:** `${bet}\n`"
                                        f"**Choice Picked:** `{choice.name}\n`"
                                        f"**Number Rolled:** `{number_color.capitalize()} {rolled_number} | {number_parity.capitalize()}`"
                        )
                        await logs.send_player_log(self.bot, 'Roulette', f"Lost", utils.get_config(interaction.guild.id, 'log_channel_id'), interaction.user)
                        embed.set_footer(text=f"{interaction.user} lost.")
                        await interaction.response.send_message(embed=embed)

                elif int(choice.value) in (3, 4, 5):
                    if choice.value == rolled_number:
                        payout = 4 * bet 
                        new_cash = removed_bet_cash + payout
                        await utils.set_cash(db, new_cash, guild_id, user_id)
                        embed = discord.Embed(
                            colour=constants.colorHexes["MediumBlue"],
                            title="Roulette won!",
                            description=f"`{charactername}` has won **${payout}**\n\n"
                                        f"**Bet:** `${bet}\n`"
                                        f"**Choice Picked:** `{choice.name}\n`"
                                        f"**Number Rolled:** `{number_color.capitalize()} {rolled_number} | {number_parity.capitalize()}`"
                        )
                        await logs.send_player_log(self.bot, 'Roulette', f"Won {payout}", utils.get_config(interaction.guild.id, 'log_channel_id'), interaction.user)
                        embed.set_footer(text=f"{interaction.user} has won ${payout}")
                        await interaction.response.send_message(embed=embed)
                    else:
                        embed = discord.Embed(
                            colour=constants.colorHexes["MediumBlue"],
                            title="Roulette Lost!",
                            description=f"`{charactername}` has lost.\n\n"
                                        f"**Bet:** `${bet}\n`"
                                        f"**Choice Picked:** `{choice.name}\n`"
                                        f"**Number Rolled:** `{number_color.capitalize()} {rolled_number} | {number_parity.capitalize()}`"
                        )
                        await logs.send_player_log(self.bot, 'Roulette', f"Lost", utils.get_config(interaction.guild.id, 'log_channel_id'), interaction.user)
                        embed.set_footer(text=f"{interaction.user} lost.")
                        await interaction.response.send_message(embed=embed)

                elif int(choice.value) in (37, 38):
                    if int(choice.value) == 37:
                        choicestr = "even"
                    elif int(choice.value) == 38:
                        choicestr = "odd"


                    if choicestr == number_parity:
                        payout = 3 * bet 
                        new_cash = removed_bet_cash + payout
                        await utils.set_cash(db, new_cash, guild_id, user_id)
                        embed = discord.Embed(
                            colour=constants.colorHexes["MediumBlue"],
                            title="Roulette won!",
                            description=f"`{charactername}` has won **${payout}**\n\n"
                                        f"**Bet:** `${bet}\n`"
                                        f"**Choice Picked:** `{choice.name}\n`"
                                        f"**Number Rolled:** `{number_color.capitalize()} {rolled_number} | {number_parity.capitalize()}`"
                        )
                        await logs.send_player_log(self.bot, 'Roulette', f"Won {payout}", utils.get_config(interaction.guild.id, 'log_channel_id'), interaction.user)
                        embed.set_footer(text=f"{interaction.user} has won ${payout}")
                        await interaction.response.send_message(embed=embed)
                    else:
                        embed = discord.Embed(
                            colour=constants.colorHexes["MediumBlue"],
                            title="Roulette Lost!",
                            description=f"`{charactername}` has lost.\n\n"
                                        f"**Bet:** `${bet}\n`"
                                        f"**Choice Picked:** `{choice.name}\n`"
                                        f"**Number Rolled:** `{number_color.capitalize()} {rolled_number} | {number_parity.capitalize()}`"
                        )
                        await logs.send_player_log(self.bot, 'Roulette', f"Lost", utils.get_config(interaction.guild.id, 'log_channel_id'), interaction.user)
                        embed.set_footer(text=f"{interaction.user} lost.")
                        await interaction.response.send_message(embed=embed)

                elif int(choice.value) in (39, 40):
                    if int(choice.value) == 39:
                        choicestr = "red"
                    elif int(choice.value) == 40:
                        choicestr = "black"


                    if choicestr == number_color:
                        payout = 3 * bet 
                        new_cash = removed_bet_cash + payout
                        await utils.set_cash(db, new_cash, guild_id, user_id)
                        embed = discord.Embed(
                            colour=constants.colorHexes["MediumBlue"],
                            title="Roulette won!",
                            description=f"`{charactername}` has won **${payout}**\n\n"
                                        f"**Bet:** `${bet}\n`"
                                        f"**Choice Picked:** `{choice.name}\n`"
                                        f"**Number Rolled:** `{number_color.capitalize()} {rolled_number} | {number_parity.capitalize()}`"
                        )
                        await logs.send_player_log(self.bot, 'Roulette', f"Won {payout}", utils.get_config(interaction.guild.id, 'log_channel_id'), interaction.user)
                        embed.set_footer(text=f"{interaction.user} has won ${payout}")
                        await interaction.response.send_message(embed=embed)
                    else:
                        embed = discord.Embed(
                            colour=constants.colorHexes["MediumBlue"],
                            title="Roulette Lost!",
                            description=f"`{charactername}` has lost.\n\n"
                                        f"**Bet:** `${bet}\n`"
                                        f"**Choice Picked:** `{choice.name}\n`"
                                        f"**Number Rolled:** `{number_color.capitalize()} {rolled_number} | {number_parity.capitalize()}`"
                        )
                        await logs.send_player_log(self.bot, 'Roulette', f"Lost", utils.get_config(interaction.guild.id, 'log_channel_id'), interaction.user)
                        embed.set_footer(text=f"{interaction.user} lost.")
                        await interaction.response.send_message(embed=embed)


            
async def setup(bot):
    Roulette_cog = Roulette(bot)
    await bot.add_cog(Roulette_cog)
