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
from bank_utils import account_utils

class TypeView(discord.ui.View):
    def __init__(self, bot, user_id, guild_id):
        super().__init__()
        self.add_item(TypeDropdown(bot, user_id, guild_id))

class TypeDropdown(discord.ui.Select):
    def __init__(self, bot, user_id, guild_id):
        options = [
            discord.SelectOption(label="Savings Account", value="savings"),
            discord.SelectOption(label="Checking Account", value="checking")
        ]
        super().__init__(placeholder="Select a type", min_values=1, max_values=1, options=options)
        self.user_id = user_id
        self.guild_id = guild_id
        self.bot = bot
        
    async def callback(self, interaction: discord.Interaction):
        selected_value = self.values[0] if self.values else None

        async with aiosqlite.connect('profiles.db') as db:
            async with db.execute('''SELECT accounts, cash, difficulty FROM profiles WHERE guild_id = ? AND user_id = ?''', (self.guild_id, self.user_id)) as cursor:
                profile = await cursor.fetchone()
                if not profile:
                    await interaction.response.send_message(embed=basicEmbeds["SelfNoProfile"], ephemeral=True)
                    return

                accounts_json, cash, difficulty = profile
        
                if not accounts_json:
                    accounts_json = {}
                else:
                    try:
                        accounts_json = json.loads(accounts_json)
                    except (json.JSONDecodeError, TypeError):
                        accounts_json = {}

                if len(accounts_json) > 10:
                    await interaction.response.send_message(
                        embed=discord.Embed(
                            description="`You cannot have more than 10 accounts!`",
                            colour=constants.colorHexes["Danger"]
                        ),
                        ephemeral=True
                    )
                    return

                if selected_value == "savings":
                    if any(acc['type'] == 'savings' for acc in accounts_json.values()):
                        await interaction.response.send_message(
                            embed=discord.Embed(
                                description="`You can only have one savings account!`",
                                colour=constants.colorHexes["Danger"]
                            ),
                            ephemeral=True
                        )
                        return
                
            
                    
                await interaction.response.send_modal(NameModal(self.bot, self.user_id, self.guild_id, selected_value))
            
class NameModal(discord.ui.Modal, title="Name Creation"):
    name_input = discord.ui.TextInput(label="Name", placeholder="The name of your account", required=True)

    def __init__(self, bot, user_id, guild_id, selected_value):
        super().__init__()
        self.user_id = user_id
        self.guild_id = guild_id
        self.selected_value = selected_value
        self.bot = bot

    async def on_submit(self, interaction: discord.Interaction):
        async with aiosqlite.connect('profiles.db') as db:
            async with db.execute(
                '''SELECT accounts, cash, difficulty FROM profiles WHERE guild_id = ? AND user_id = ?''',
                (self.guild_id, self.user_id)
            ) as cursor:
                profile = await cursor.fetchone()

                if not profile:
                    await interaction.response.send_message(embed=basicEmbeds["SelfNoProfile"], ephemeral=True)
                    return

                try:
                    accounts_json, cash, difficulty = profile

                    if not accounts_json:
                        accounts_json = {}
                    else:
                        try:
                            accounts_json = json.loads(accounts_json)
                        except (json.JSONDecodeError, TypeError):
                            accounts_json = {}

                    account_key = str(self.selected_value)
                    account_name = str(self.name_input)

                    # Check for any duplicate name in all accounts
                    if any(acc['name'].lower() == account_name.lower() for acc in accounts_json.values()):
                        await interaction.response.send_message(
                            embed=discord.Embed(
                                description="`You already have an account with that name!`",
                                colour=constants.colorHexes["Danger"]
                            ),
                            ephemeral=True
                        )
                        return
                    
                    last_action = datetime.now()

                    # Create a new account
                    new_account = account_utils.Account(
                        name=account_name,
                        balance=0,  # Balance should be a number, not a string
                        type=account_key,
                        last_action=last_action  # Ensure it's always a valid ISO 8601 string
                    )

                    # Add new account to the accounts dictionary
                    account_id = str(len(accounts_json))  # Generate a new unique ID
                    accounts_json[account_id] = new_account.to_dict()

                    print(accounts_json[account_id])

                    # Save updated accounts to the database
                    updated_accounts_json = json.dumps(accounts_json)



                    new_cash = cash - 100

                    await db.execute(
                        '''UPDATE profiles SET accounts = ?, cash = ? WHERE guild_id = ? AND user_id = ?''',
                        (updated_accounts_json, new_cash, self.guild_id, self.user_id)
                    )
                    await db.commit()

                    await logs.send_player_log(
                        self.bot, 
                        "Bank Account Created", 
                        "Created a bank account.", 
                        utils.get_config(interaction.guild.id, 'log_channel_id'), 
                        interaction.user
                    )
                    await interaction.response.send_message(
                        embed=discord.Embed(
                            title="Bank Account Created",
                            description=f"**Successfully Created Bank Account:** `{account_name} | {account_key.capitalize()}`",
                            colour=constants.colorHexes["SkyBlue"]
                        )
                    )
                except Exception as e:
                    print(f"Error creating account: {e}")


class AccountsView(discord.ui.View):
    def __init__(self, bot, user_id, guild_id, accounts_json):
        super().__init__()
        self.add_item(AccountsDropdown(bot, user_id, guild_id, accounts_json))

class AccountsDropdown(discord.ui.Select):
    def __init__(self, bot, user_id, guild_id, accounts_json):
        options = [
            discord.SelectOption(
                label=f"{acc['name']} | {utils.to_money(int(acc['balance']))}",
                description=f"Account Type: `{acc['type'].capitalize()}`",
                value=acc['name']
            ) for acc in accounts_json.values()
        ]
        super().__init__(placeholder="Select an account to continue", min_values=1, max_values=1, options=options)
        self.bot = bot
        self.user_id = user_id
        self.guild_id = guild_id
        self.accounts_json = accounts_json

    async def callback(self, interaction: discord.Interaction):
        async with aiosqlite.connect('profiles.db') as db:
            async with db.execute('''SELECT accounts, cash, difficulty FROM profiles WHERE guild_id = ? AND user_id = ?''', (self.guild_id, self.user_id)) as cursor:
                profile = await cursor.fetchone()

                if not profile:
                    await interaction.response.send_message(embed=basicEmbeds["SelfNoProfile"], ephemeral=True)
                    return

                accounts_json, cash, difficulty = profile
                try:
                    accounts_json = json.loads(accounts_json) if accounts_json else {}
                except (json.JSONDecodeError, TypeError):
                    accounts_json = {}

                selected_account_name = self.values[0]
                # Locate account by its name
                account_info = next(
                    (acc for acc in accounts_json.values() if acc['name'] == selected_account_name), None
                )

                if not account_info:
                    await interaction.response.send_message(
                        embed=discord.Embed(description="`Account not found!`", colour=constants.colorHexes["Danger"]),
                        ephemeral=True
                    )
                    return

                embed = discord.Embed(
                    title="Account Details",
                    description=f"**Name:** `{account_info['name']}`\n"
                                f"**Type:** `{account_info['type'].capitalize()}`\n"
                                f"**Balance:** `{utils.to_money(int(account_info['balance']))}`",
                    colour=constants.colorHexes["SkyBlue"]
                )
                await interaction.response.send_message(embed=embed, view=AccountsInfoView(self.bot, self.user_id, self.guild_id, accounts_json, account_info['name']))

class AccountsInfoView(discord.ui.View):
    def __init__(self, bot, user_id, guild_id, accounts_json, account_name):
        super().__init__()
        self.bot = bot
        self.user_id = user_id
        self.guild_id = guild_id
        self.accounts_json = accounts_json
        self.account_name = account_name

    @discord.ui.button(label="Deposit", style=discord.ButtonStyle.primary)
    async def deposit(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != str(self.user_id):
            await interaction.response.send_message(
                embed=discord.Embed(description="This is not your account!", colour=constants.colorHexes["Danger"]),
                ephemeral=True
            )
            return

        async with aiosqlite.connect('profiles.db') as db:
            async with db.execute('''SELECT accounts, cash FROM profiles WHERE guild_id = ? AND user_id = ?''', (self.guild_id, self.user_id)) as cursor:
                profile = await cursor.fetchone()

                if not profile:
                    await interaction.response.send_message(embed=basicEmbeds["SelfNoProfile"], ephemeral=True)
                    return
                
                accounts_json, cash = profile

                await interaction.response.send_modal(DepositModal(self.bot, self.user_id, self.guild_id, self.accounts_json, self.account_name, cash))
    
    @discord.ui.button(label="Withdraw", style=discord.ButtonStyle.secondary)
    async def withdraw(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != str(self.user_id):
            await interaction.response.send_message(
                embed=discord.Embed(description="This is not your account!", colour=constants.colorHexes["Danger"]),
                ephemeral=True
            )
            return

        async with aiosqlite.connect('profiles.db') as db:
            async with db.execute('''SELECT accounts, cash FROM profiles WHERE guild_id = ? AND user_id = ?''', (self.guild_id, self.user_id)) as cursor:
                profile = await cursor.fetchone()

                if not profile:
                    await interaction.response.send_message(embed=basicEmbeds["SelfNoProfile"], ephemeral=True)
                    return
                
                accounts_json, cash = profile

                await interaction.response.send_modal(WithdrawModal(self.bot, self.user_id, self.guild_id, self.accounts_json, self.account_name, cash))
    
    @discord.ui.button(label="Close", style=discord.ButtonStyle.danger)
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != str(self.user_id):
            await interaction.response.send_message(
                embed=discord.Embed(description="This is not your account!", colour=constants.colorHexes["Danger"]),
                ephemeral=True
            )
            return
        
        if str(interaction.user.id) != str(self.user_id):
            await interaction.response.send_message(
                embed=discord.Embed(description="This is not your account!", colour=constants.colorHexes["Danger"]),
                ephemeral=True
            )
            return

        async with aiosqlite.connect('profiles.db') as db:
            async with db.execute('''SELECT accounts, cash FROM profiles WHERE guild_id = ? AND user_id = ?''', (self.guild_id, self.user_id)) as cursor:
                profile = await cursor.fetchone()

                if not profile:
                    await interaction.response.send_message(embed=basicEmbeds["SelfNoProfile"], ephemeral=True)
                    return
                
                accounts_json, cash = profile

                embed = discord.Embed(
                    title="Delete Account",
                    description="Are you sure you'd like to delete your account?\n\n**You will lose all funds stored in it**",
                    colour=constants.colorHexes["Danger"])
                

                await interaction.response.send_message(embed=embed, view=DeleteAccount(self.bot, self.user_id, self.guild_id, self.accounts_json, self.account_name))

class DeleteAccount(discord.ui.View):
    def __init__(self, bot, user_id, guild_id, accounts_json, account_name):
        super().__init__()
        self.bot = bot
        self.user_id = user_id
        self.guild_id = guild_id
        self.accounts_json = accounts_json
        self.account_name = account_name

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.danger)
    async def confirm_delete(self, interaction: discord.Interaction, button: discord.ui.Button):
        async with aiosqlite.connect('profiles.db') as db:
            async with db.execute('''SELECT accounts FROM profiles WHERE guild_id = ? AND user_id = ?''', (self.guild_id, self.user_id)) as cursor:
                profile = await cursor.fetchone()

                if not profile:
                    await interaction.response.send_message(embed=basicEmbeds["SelfNoProfile"], ephemeral=True)
                    return

                accounts_json = profile[0]

                # Parse accounts JSON
                try:
                    accounts_json = json.loads(accounts_json) if accounts_json else {}
                except (json.JSONDecodeError, TypeError):
                    accounts_json = {}

                # Find and delete the account
                account_id = None
                for key, account_data in accounts_json.items():
                    if account_data["name"] == self.account_name:
                        account_id = key
                        break

                if not account_id:
                    await interaction.response.send_message(
                        embed=discord.Embed(description="`Account not found!`", colour=constants.colorHexes["Danger"]),
                        ephemeral=True
                    )
                    return

                # Remove the account and update the database
                del accounts_json[account_id]
                updated_accounts_json = json.dumps(accounts_json)

                await db.execute(
                    '''UPDATE profiles SET accounts = ? WHERE guild_id = ? AND user_id = ?''',
                    (updated_accounts_json, self.guild_id, self.user_id)
                )
                await db.commit()

                await interaction.response.send_message(
                    embed=discord.Embed(
                        description=f"`Successfully deleted the account: {self.account_name}`",
                        colour=constants.colorHexes["Success"]
                    ),
                    ephemeral=True
                )

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary)
    async def cancel_delete(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            embed=discord.Embed(description="`Account deletion canceled.`", colour=constants.colorHexes["Neutral"]),
            ephemeral=True
        )

class ConfirmFeeDeposit(discord.ui.View):
    def __init__(self, bot, user_id, guild_id, accounts_json, account_name, account_obj, cash, account_id, deposit_amount):
        super().__init__()
        self.bot = bot
        self.user_id = user_id
        self.guild_id = guild_id
        self.accounts_json = accounts_json
        self.account_name = account_name
        self.account_obj = account_obj
        self.cash = cash
        self.account_id = account_id
        self.deposit_amount = deposit_amount

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.danger)
    async def confirm_deposit(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            async with aiosqlite.connect('profiles.db') as db:
                charge_fee_percent = 0.05
                fee = int(self.deposit_amount) * charge_fee_percent
                new_balance = self.account_obj.get_balance() + int(self.deposit_amount) - fee
                self.account_obj.set_balance(new_balance)
                self.account_obj.set_last_action(datetime.now())

                self.accounts_json[self.account_id] = self.account_obj.to_dict()
                new_cash = self.cash - int(self.deposit_amount)

                updated_accounts_json = json.dumps(self.accounts_json)
                await db.execute(
                    '''UPDATE profiles SET cash = ?, accounts = ? WHERE guild_id = ? AND user_id = ?''',
                    (new_cash, updated_accounts_json, self.guild_id, self.user_id)
                )
                await db.commit()

                await logs.send_player_log(
                    self.bot, 
                    "Deposit Processed", 
                    f"Deposited {utils.to_money(self.deposit_amount)}", 
                    utils.get_config(interaction.guild.id, 'log_channel_id'), 
                    interaction.user
                )

                await interaction.response.send_message(
                    embed=discord.Embed(
                        description=f"`Successfully deposited {utils.to_money(int(self.deposit_amount) - fee)} into {self.account_name}`",
                        colour=constants.colorHexes["SkyBlue"]
                    ),
                    ephemeral=True
                )
        except Exception as e:
            await interaction.response.send_message(
                embed=discord.Embed(description=f"`Error during deposit: {e}`", colour=constants.colorHexes["Danger"]),
                ephemeral=True
            )

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary)
    async def cancel_deposit(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            embed=discord.Embed(description="`Deposit canceled.`", colour=constants.colorHexes["Neutral"]),
            ephemeral=True
        )

        


class DepositModal(discord.ui.Modal, title="Deposit Cash"):
    deposit_input = discord.ui.TextInput(label="Amount", placeholder="Enter the amount to deposit", required=True)

    def __init__(self, bot, user_id, guild_id, accounts_json, account_name, cash):
        super().__init__()
        self.bot = bot
        self.user_id = user_id
        self.guild_id = guild_id
        self.accounts_json = accounts_json
        self.account_name = account_name
        self.cash = cash

    async def on_submit(self, interaction: discord.Interaction):
        try:
            async with aiosqlite.connect('profiles.db') as db:
                cursor = await db.execute('''SELECT accounts, cash FROM profiles WHERE guild_id = ? AND user_id = ?''', (self.guild_id, self.user_id))
                profile = await cursor.fetchone()
                if not profile:
                    await interaction.response.send_message(embed=basicEmbeds["SelfNoProfile"], ephemeral=True)
                    return
                
                accounts_json, cash = profile
                accounts_json = json.loads(accounts_json) if accounts_json else {}

                try:
                    deposit_amount = int(self.deposit_input.value)
                except ValueError:
                    await interaction.response.send_message(
                        embed=discord.Embed(description="`Please enter a valid integer amount!`", colour=constants.colorHexes["Danger"]),
                        ephemeral=True
                    )
                    return

                if deposit_amount < 1:
                    await interaction.response.send_message(
                        embed=discord.Embed(description="`You must deposit at least $1!`", colour=constants.colorHexes["Danger"]),
                        ephemeral=True
                    )
                    return

                if self.cash < deposit_amount:
                    await interaction.response.send_message(
                        embed=discord.Embed(description="`You can't deposit more money than you have!`", colour=constants.colorHexes["Danger"]),
                        ephemeral=True
                    )
                    return

                account_id, account_data = next(((k, v) for k, v in accounts_json.items() if v["name"] == self.account_name), (None, None))
                if not account_id:
                    await interaction.response.send_message(
                        embed=discord.Embed(description="`Account not found!`", colour=constants.colorHexes["Danger"]),
                        ephemeral=True
                    )
                    return

                account_obj = account_utils.Account.from_dict(account_data)
                time_since_action = utils.get_time_delta(account_obj.get_action())

                charge_fee_percent = 0.05 if account_obj.get_type() == "checking" and time_since_action["hours"] < 6 else 0

                if charge_fee_percent > 0:
                    fee = deposit_amount * charge_fee_percent
                    embed = discord.Embed(
                        title="Confirm Deposit",
                        description=f"Confirming will apply a 5% fee: `{utils.to_money(fee)}`\n**Available in:** `{utils.convert_seconds(360 - time_since_action['total_game_minutes'])}`",
                        colour=constants.colorHexes["Danger"]
                    )
                    view = ConfirmFeeDeposit(self.bot, self.user_id, self.guild_id, accounts_json, self.account_name, account_obj, cash, account_id, deposit_amount)
                    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
                else:
                    fee = 0
                    await self.process_deposit(db, interaction, accounts_json, account_obj, account_id, deposit_amount, fee)
        except Exception as e:
            await interaction.response.send_message(embed=discord.Embed(description=f"`Error: {e}`", colour=constants.colorHexes["Danger"]), ephemeral=True)

    async def process_deposit(self, db, interaction, accounts_json, account_obj, account_id, deposit_amount, fee):
        account_obj.set_balance(account_obj.get_balance() + deposit_amount - fee)
        account_obj.set_last_action(datetime.now())
        accounts_json[account_id] = account_obj.to_dict()

        new_cash = self.cash - deposit_amount
        updated_accounts_json = json.dumps(accounts_json)

        await db.execute('''UPDATE profiles SET cash = ?, accounts = ? WHERE guild_id = ? AND user_id = ?''', (new_cash, updated_accounts_json, self.guild_id, self.user_id))
        await db.commit()

        await logs.send_player_log(
            self.bot, 
            "Deposit Processed", 
            f"Deposited {utils.to_money(deposit_amount)}", 
            utils.get_config(interaction.guild.id, 'log_channel_id'), 
            interaction.user
        )

        await interaction.response.send_message(
            embed=discord.Embed(description=f"`Successfully deposited {utils.to_money(deposit_amount)} into {self.account_name}. Fee: {utils.to_money(fee)}`", colour=constants.colorHexes["SkyBlue"]),
            ephemeral=True
        )

class ConfirmFeeWithdraw(discord.ui.View):
    def __init__(self, bot, user_id, guild_id, accounts_json, account_name, account_obj, cash, account_id, withdraw_amount):
        super().__init__()
        self.bot = bot
        self.user_id = user_id
        self.guild_id = guild_id
        self.accounts_json = accounts_json
        self.account_name = account_name
        self.account_obj = account_obj
        self.cash = cash
        self.account_id = account_id
        self.withdraw_amount = withdraw_amount

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.danger)
    async def confirm_withdraw(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            async with aiosqlite.connect('profiles.db') as db:
                charge_fee_percent = 0.05
                fee = int(self.withdraw_amount) * charge_fee_percent
                new_balance = self.account_obj.get_balance() - int(self.withdraw_amount)
                self.account_obj.set_balance(new_balance)
                self.account_obj.set_last_action(datetime.now())

                self.accounts_json[self.account_id] = self.account_obj.to_dict()
                new_cash = self.cash - int(self.withdraw_amount) - fee

                updated_accounts_json = json.dumps(self.accounts_json)
                await db.execute(
                    '''UPDATE profiles SET cash = ?, accounts = ? WHERE guild_id = ? AND user_id = ?''',
                    (new_cash, updated_accounts_json, self.guild_id, self.user_id)
                )
                await db.commit()

                await logs.send_player_log(
                    self.bot, 
                    "Withdraw Processed", 
                    f"Withdrew {utils.to_money(self.withdraw_amount)}", 
                    utils.get_config(interaction.guild.id, 'log_channel_id'),
                    interaction.user
                )

                await interaction.response.send_message(
                    embed=discord.Embed(
                        description=f"`Successfully withdrew {utils.to_money(int(self.withdraw_amount) - fee)} from {self.account_name}`",
                        colour=constants.colorHexes["SkyBlue"]
                    ),
                    ephemeral=True
                )
        except Exception as e:
            await interaction.response.send_message(
                embed=discord.Embed(description=f"`Error during withdraw: {e}`", colour=constants.colorHexes["Danger"]),
                ephemeral=True
            )

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary)
    async def cancel_withdraw(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            embed=discord.Embed(description="`Withdraw canceled.`", colour=constants.colorHexes["Neutral"]),
            ephemeral=True
        )

        


class WithdrawModal(discord.ui.Modal, title="Withdraw Cash"):
    withdraw_input = discord.ui.TextInput(label="Amount", placeholder="Enter the amount to withdraw", required=True)

    def __init__(self, bot, user_id, guild_id, accounts_json, account_name, cash):
        super().__init__()
        self.bot = bot
        self.user_id = user_id
        self.guild_id = guild_id
        self.accounts_json = accounts_json
        self.account_name = account_name
        self.cash = cash

    async def on_submit(self, interaction: discord.Interaction):
        try:
            async with aiosqlite.connect('profiles.db') as db:
                cursor = await db.execute('''SELECT accounts, cash FROM profiles WHERE guild_id = ? AND user_id = ?''', (self.guild_id, self.user_id))
                profile = await cursor.fetchone()
                if not profile:
                    await interaction.response.send_message(embed=basicEmbeds["SelfNoProfile"], ephemeral=True)
                    return
                
                accounts_json, cash = profile
                accounts_json = json.loads(accounts_json) if accounts_json else {}

                try:
                    withdraw_amount = int(self.withdraw_input.value)
                except ValueError:
                    await interaction.response.send_message(
                        embed=discord.Embed(description="`Please enter a valid integer amount!`", colour=constants.colorHexes["Danger"]),
                        ephemeral=True
                    )
                    return

                if withdraw_amount < 1:
                    await interaction.response.send_message(
                        embed=discord.Embed(description="`You must withdraw at least $1!`", colour=constants.colorHexes["Danger"]),
                        ephemeral=True
                    )
                    return
                
                account_id, account_data = next(((k, v) for k, v in accounts_json.items() if v["name"] == self.account_name), (None, None))
                account_obj = account_utils.Account.from_dict(account_data)
                if not account_id:
                    await interaction.response.send_message(
                        embed=discord.Embed(description="`Account not found!`", colour=constants.colorHexes["Danger"]),
                        ephemeral=True
                    )
                    return
                
                if account_obj.get_balance() < withdraw_amount:
                    await interaction.response.send_message(
                        embed=discord.Embed(description="`You can't withdraw more money than you have!`", colour=constants.colorHexes["Danger"]),
                        ephemeral=True
                    )
                    return

                
                time_since_action = utils.get_time_delta(account_obj.get_action())

                charge_fee_percent = 0.05 if account_obj.get_type() == "checking" and time_since_action["hours"] < 6 else 0

                if account_obj.get_type() == "checking":
                    if time_since_action["hours"] < 6: 
                        charge_fee_percent = 0.05
                        fee = withdraw_amount * charge_fee_percent
                        embed = discord.Embed(
                            title="Confirm withdraw",
                            description=f"Confirming will apply a 5% fee: `{utils.to_money(fee)}`\n**Available in:** `{utils.convert_seconds(360 - time_since_action['total_game_minutes'])}`",
                            colour=constants.colorHexes["Danger"]
                        )
                        view = ConfirmFeeWithdraw(self.bot, self.user_id, self.guild_id, accounts_json, self.account_name, account_obj, cash, account_id, withdraw_amount)
                        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
                    else:
                        fee = 0
                        await self.process_withdraw(db, interaction, accounts_json, account_obj, account_id, withdraw_amount, fee)

                else:
                    if time_since_action["months"] < 1: 
                            charge_fee_percent = 0.05
                            fee = withdraw_amount * charge_fee_percent
                            embed = discord.Embed(
                                title="Confirm withdraw",
                                description=f"Confirming will apply a 5% fee: `{utils.to_money(fee)}`\n**Available in:** `{utils.convert_seconds(43200 - time_since_action['total_game_minutes'])}`",
                                colour=constants.colorHexes["Danger"]
                            )
                            view = ConfirmFeeWithdraw(self.bot, self.user_id, self.guild_id, accounts_json, self.account_name, account_obj, cash, account_id, withdraw_amount)
                            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
                    else:
                        fee = 0
                        await self.process_withdraw(db, interaction, accounts_json, account_obj, account_id, withdraw_amount, fee, time_since_action)
        except Exception as e:
            await interaction.response.send_message(embed=discord.Embed(description=f"`Error: {e}`", colour=constants.colorHexes["Danger"]), ephemeral=True)

    async def process_withdraw(self, db, interaction, accounts_json, account_obj, account_id, withdraw_amount, fee, time_since_action):

        interest_percentage = 0.04

        calculated_interest = int(time_since_action["months"]) * (int(account_obj.get_balance()) * interest_percentage)
        account_obj.set_balance(account_obj.get_balance() - withdraw_amount + calculated_interest)
        account_obj.set_last_action(datetime.now())
        accounts_json[account_id] = account_obj.to_dict()

        

        new_cash = self.cash - withdraw_amount - fee
        updated_accounts_json = json.dumps(accounts_json)

        await db.execute('''UPDATE profiles SET cash = ?, accounts = ? WHERE guild_id = ? AND user_id = ?''', (new_cash, updated_accounts_json, self.guild_id, self.user_id))
        await db.commit()

        await logs.send_player_log(
            self.bot, 
            "Withdraw Processed", 
            f"Withdrew {utils.to_money(self.withdraw_amount)}", 
            utils.get_config(interaction.guild.id, 'log_channel_id'), 
            interaction.user
        )

        await interaction.response.send_message(
            embed=discord.Embed(description=f"`Successfully withdrew {utils.to_money(withdraw_amount)} from {self.account_name}. Fee: {utils.to_money(fee)}`", colour=constants.colorHexes["SkyBlue"]),
            ephemeral=True
        )


class Bank(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Bank is ready.")    

    @app_commands.command(name="createaccount", description="Creates you a new bank account")
    async def createaccount(self, interaction: discord.Interaction):
        guild_id = interaction.guild.id
        user_id = interaction.user.id

        async with aiosqlite.connect('profiles.db') as db:
            async with db.execute('''SELECT accounts, cash FROM profiles WHERE guild_id = ? AND user_id = ?''', (guild_id, user_id)) as cursor:
                profile = await cursor.fetchone()

                if not profile:
                    await interaction.response.send_message(embed=basicEmbeds["SelfNoProfile"], ephemeral=True)
                    return

                accounts_json, cash = profile

                if cash < 100:
                    await interaction.response.send_message(embed=discord.Embed(description="`You don't have enough money to open a bank account. You need $100!`", colour=constants.colorHexes["Danger"]))
                    return

                embed = discord.Embed(
                    title="Bank",
                    description=f"**Account Creation Menu**\n\nChoose a type from below to continue",
                    colour=constants.colorHexes["MediumBlue"]
                )

                await interaction.response.send_message(embed=embed, view=TypeView(self.bot, user_id, guild_id))
        
    @app_commands.command(name="accounts", description="Displays all of your accounts, allows you to deposit & withdraw.")
    async def accounts(self, interaction: discord.Interaction):
        guild_id = interaction.guild.id
        user_id = interaction.user.id

        try:

            async with aiosqlite.connect('profiles.db') as db:
                async with db.execute('''SELECT accounts, cash FROM profiles WHERE guild_id = ? AND user_id = ?''', (guild_id, user_id)) as cursor:
                    profile = await cursor.fetchone()

                    if not profile:
                        await interaction.response.send_message(embed=basicEmbeds["SelfNoProfile"], ephemeral=True)
                        return

                    accounts_json, cash = profile

                    # Validate and parse accounts JSON
                    try:
                        accounts_json = json.loads(accounts_json) if accounts_json else {}
                    except (json.JSONDecodeError, TypeError):
                        accounts_json = {}
                        await interaction.response.send_message(
                            embed=discord.Embed(
                                description="`There was an issue loading your accounts.`",
                                colour=constants.colorHexes["Danger"]
                            ),
                            ephemeral=True
                        )
                        return

                    if not accounts_json:
                        await interaction.response.send_message(
                            embed=discord.Embed(description="`You don't have any accounts!`", colour=constants.colorHexes["Danger"]),
                            ephemeral=True
                        )
                        return

                    # Construct Embed Message
                    embed = discord.Embed(
                        title="Bank Accounts",
                        description="**Select an account from below to continue**",
                        colour=constants.colorHexes["SkyBlue"]
                    )

                    for acc_name, acc_details in accounts_json.items():
                        account = account_utils.Account.from_dict(acc_details)
                        embed.add_field(
                            name=f"{account.name} | {utils.to_money(int(account.balance))}",
                            value=f"**Account Type:** `{account.type.capitalize()}`",
                            inline=False
                        )

                    await interaction.response.send_message(embed=embed, view=AccountsView(self.bot, user_id, guild_id, accounts_json))

        except Exception as e:
            print(e)


                
                







async def setup(bot):
    Bank_cog = Bank(bot)
    await bot.add_cog(Bank_cog)