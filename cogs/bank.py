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

class Bank(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Bank is ready.")    

    @app_commands.command(name="balance", description="Checks the balance of any user.")
    async def balance(self, interaction: discord.Interaction, member: discord.Member):
        guild_id = interaction.guild.id
        member_id = member.id

        async with aiosqlite.connect('profiles.db') as db:
            async with db.execute('''SELECT charactername, cash, bank FROM profiles WHERE guild_id = ? AND user_id = ?''', (guild_id, member_id)) as cursor:
                profile = await cursor.fetchone()

                if not profile:
                    await interaction.response.send_message(embed=discord.Embed(description="`This user doesn't have a profile!`", colour=constants.colorHexes["Danger"]), ephemeral=True)
                    return
                
                charactername, cash, bank = profile

                balance_embed = discord.Embed(
                    colour=constants.colorHexes["SkyBlue"], 
                    title=f"{charactername}'s Balance",
                    description=f"**Cash:** `{utils.to_money(cash)}`\n"
                                f"**Bank:** `{utils.to_money(bank)}`\n\n"
                                f"**Total:** `{utils.to_money(cash+bank)}`"
                )

                balance_embed.set_author(name=f"{member.display_name}'s Profile")
                if member.avatar:
                    balance_embed.set_thumbnail(url=member.avatar.url)

                await interaction.response.send_message(embed=balance_embed)

    @app_commands.command(name="deposit", description="Deposit your cash into a bank account")
    @app_commands.describe(amount="The amount of money to deposit")
    async def deposit(self, interaction: discord.Interaction, amount: int):
        guild_id = interaction.guild.id
        user_id = interaction.user.id

        async with aiosqlite.connect('profiles.db') as db:
            async with db.execute('''SELECT charactername, cash, bank FROM profiles WHERE guild_id = ? AND user_id = ?''', (guild_id, user_id)) as cursor:
                profile = await cursor.fetchone()

                if not profile:
                    await interaction.response.send_message(embed=discord.Embed(description="`You do not have a profile! Do /createprofile to begin!`", colour=constants.colorHexes["Danger"]), ephemeral=True)
                    return
                
                charactername, cash, bank = profile

                final_cash = cash - amount
                final_bank = bank + amount

                if amount <= 0:
                    embed = discord.Embed(
                        description="`The amount must be greater than 0!`",
                        colour=constants.colorHexes["Danger"]
                        )
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                    return
                
                if final_cash < 0:
                    embed = discord.Embed(
                        description="`You can't deposit more than you have on hand!`",
                        colour=constants.colorHexes["Danger"]
                        )
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                    return
                
                deposit_embed = discord.Embed(
                    title=f"Deposit Transaction Completed",
                    description=f"Deposit for `{charactername}`\n\n"
                                f"**Deposit Amount:** `{utils.to_money(amount)}`\n"
                                f"**Cash:** `{utils.to_money(final_cash)}`\n"
                                f"**Bank:** `{utils.to_money(final_bank)}`\n",
                    colour=constants.colorHexes["SkyBlue"]
                )

                await db.execute('''UPDATE profiles SET cash = ?, bank = ? WHERE guild_id = ? AND user_id = ?''', (final_cash, final_bank, guild_id, user_id))
                await db.commit()

                await interaction.response.send_message(embed=deposit_embed)


    @app_commands.command(name="withdraw", description="Withdraws money from your bank account")
    @app_commands.describe(amount="The amount of money to withdraw")
    async def withdraw(self, interaction: discord.Interaction, amount: int):
        guild_id = interaction.guild.id
        user_id = interaction.user.id

        async with aiosqlite.connect('profiles.db') as db:
            async with db.execute('''SELECT charactername, cash, bank FROM profiles WHERE guild_id = ? AND user_id = ?''', (guild_id, user_id)) as cursor:
                profile = await cursor.fetchone()

                if not profile:
                    await interaction.response.send_message(embed=discord.Embed(description="`You do not have a profile! Do /createprofile to begin!`", colour=constants.colorHexes["Danger"]), ephemeral=True)
                    return
                
                charactername, cash, bank = profile

                final_cash = cash + amount
                final_bank = bank - amount

                if amount <= 0:
                    embed = discord.Embed(
                        description="`The amount must be greater than 0!`",
                        colour=constants.colorHexes["Danger"]
                        )
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                    return
                
                if final_bank < 0:
                    embed = discord.Embed(
                        description="`You can't withdraw more than you have in your account!`",
                        colour=constants.colorHexes["Danger"]
                        )
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                    return
                
                deposit_embed = discord.Embed(
                    title=f"Withdraw Transaction Completed",
                    description=f"Withdraw for `{charactername}`\n\n"
                                f"**Withdraw Amount:** `{utils.to_money(amount)}`\n"
                                f"**Cash:** `{utils.to_money(final_cash)}`\n"
                                f"**Bank:** `{utils.to_money(final_bank)}`\n",
                    colour=constants.colorHexes["SkyBlue"]
                )

                await db.execute('''UPDATE profiles SET cash = ?, bank = ? WHERE guild_id = ? AND user_id = ?''', (final_cash, final_bank, guild_id, user_id))
                await db.commit()

                await interaction.response.send_message(embed=deposit_embed)

    @app_commands.command(name="pay", description="Pays another member cash")
    @app_commands.describe(member="The member to pay", amount="The amount of cash to pay")
    async def pay(self, interaction: discord.Interaction, member: discord.Member, amount: int):
        guild_id = interaction.guild.id
        payer_id = interaction.user.id
        recipient_id = member.id

        if payer_id == recipient_id:
            embed = discord.Embed(
                description="`You cannot pay yourself!`",
                colour=constants.colorHexes["Danger"]
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        async with aiosqlite.connect('profiles.db') as db:
            async with db.execute('''SELECT charactername, cash FROM profiles WHERE guild_id = ? AND user_id = ?''', (guild_id, payer_id)) as cursor:
                payer_profile = await cursor.fetchone()

            if not payer_profile:
                await interaction.response.send_message(embed=discord.Embed(description="`You do not have a profile! Do /createprofile to begin!`", colour=constants.colorHexes["Danger"]), ephemeral=True)
                return

            payer_name, payer_cash = payer_profile

            async with db.execute('''SELECT charactername, cash FROM profiles WHERE guild_id = ? AND user_id = ?''', (guild_id, recipient_id)) as cursor:
                recipient_profile = await cursor.fetchone()

            if not recipient_profile:
                await interaction.response.send_message(embed=discord.Embed(description=f"`{member.display_name} does not have a profile!`", colour=constants.colorHexes["Danger"]), ephemeral=True)
                return

            recipient_name, recipient_cash = recipient_profile

            if amount <= 0:
                embed = discord.Embed(
                    description="`The amount must be greater than 0!`",
                    colour=constants.colorHexes["Danger"]
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return

            if payer_cash < amount:
                embed = discord.Embed(
                    description="`You don't have enough cash to pay!`",
                    colour=constants.colorHexes["Danger"]
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return

            final_payer_cash = payer_cash - amount
            final_recipient_cash = recipient_cash + amount

            await db.execute('''UPDATE profiles SET cash = ? WHERE guild_id = ? AND user_id = ?''', (final_payer_cash, guild_id, payer_id))
            await db.execute('''UPDATE profiles SET cash = ? WHERE guild_id = ? AND user_id = ?''', (final_recipient_cash, guild_id, recipient_id))
            await db.commit()

            pay_embed = discord.Embed(
                title="Pay Transaction Completed",
                description=f"Payment from `{payer_name}` to `{recipient_name}`\n\n"
                            f"**Amount Paid:** `{utils.to_money(amount)}`\n"
                            f"**Your Remaining Cash:** `{utils.to_money(final_payer_cash)}`\n"
                            f"**{recipient_name}'s New Cash:** `{utils.to_money(final_recipient_cash)}`\n",
                colour=constants.colorHexes["SkyBlue"]
            )

            await interaction.response.send_message(embed=pay_embed)


    @app_commands.command(name="transfer", description="Transfers bank funds to another member")
    @app_commands.describe(member="The member to pay", amount="The amount of cash to pay")
    async def transfer(self, interaction: discord.Interaction, member: discord.Member, amount: int):
        guild_id = interaction.guild.id
        payer_id = interaction.user.id
        recipient_id = member.id

        if payer_id == recipient_id:
            embed = discord.Embed(
                description="`You cannot pay yourself!`",
                colour=constants.colorHexes["Danger"]
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        async with aiosqlite.connect('profiles.db') as db:
            async with db.execute('''SELECT charactername, bank FROM profiles WHERE guild_id = ? AND user_id = ?''', (guild_id, payer_id)) as cursor:
                payer_profile = await cursor.fetchone()

            if not payer_profile:
                await interaction.response.send_message(embed=discord.Embed(description="`You do not have a profile! Do /createprofile to begin!`", colour=constants.colorHexes["Danger"]), ephemeral=True)
                return

            payer_name, payer_bank = payer_profile

            async with db.execute('''SELECT charactername, bank FROM profiles WHERE guild_id = ? AND user_id = ?''', (guild_id, recipient_id)) as cursor:
                recipient_profile = await cursor.fetchone()

            if not recipient_profile:
                await interaction.response.send_message(embed=discord.Embed(description=f"`{member.display_name} does not have a profile!`", colour=constants.colorHexes["Danger"]), ephemeral=True)
                return

            recipient_name, recipient_bank = recipient_profile

            if amount <= 0:
                embed = discord.Embed(
                    description="`The amount must be greater than 0!`",
                    colour=constants.colorHexes["Danger"]
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return

            if payer_bank < amount:
                embed = discord.Embed(
                    description="`You don't have enough bank funds to transfer!`",
                    colour=constants.colorHexes["Danger"]
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return

            final_payer_bank = payer_bank - amount
            final_recipient_bank = recipient_bank + amount

            await db.execute('''UPDATE profiles SET bank = ? WHERE guild_id = ? AND user_id = ?''', (final_payer_bank, guild_id, payer_id))
            await db.execute('''UPDATE profiles SET bank = ? WHERE guild_id = ? AND user_id = ?''', (final_recipient_bank, guild_id, recipient_id))
            await db.commit()

            pay_embed = discord.Embed(
                title="Pay Transaction Completed",
                description=f"Payment from `{payer_name}` to `{recipient_name}`\n\n"
                            f"**Amount Paid:** `{utils.to_money(amount)}`\n"
                            f"**Your Remaining Bank:** `{utils.to_money(final_payer_bank)}`\n"
                            f"**{recipient_name}'s New Bank:** `{utils.to_money(final_recipient_bank)}`\n",
                colour=constants.colorHexes["SkyBlue"]
            )

            await interaction.response.send_message(embed=pay_embed)
        
async def setup(bot):
    Bank_cog = Bank(bot)
    await bot.add_cog(Bank_cog)