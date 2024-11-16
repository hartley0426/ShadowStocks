import discord
from discord.ext import commands, tasks
from discord import app_commands
import os
import random
from datetime import datetime, timedelta 
import aiosqlite
import constants
from utilities import utils
from utilities.embeds import basicEmbeds
import asyncio

SUITS = ['♥', '♦', '♣', '♠']
RANKS = [('2', 2),
         ('3', 3),
         ('4', 4),
         ('5', 5),
         ('6', 6),
         ('7', 7),
         ('8', 8),
         ('9', 9),
         ('10', 10),
         ('J', 10),
         ('Q', 10),
         ('K', 10),
         ('A', 11)]

games = {}

def create_deck():
        deck = []
        for suit in SUITS:
            for rank in RANKS:
                deck.append((f"{rank[0]}{suit}", rank[1]))
            
        return deck
    
def deal(deck):
    return random.choice(deck)

def get_total(hand):
    total = sum(card[1] for card in hand)

    aces = sum(1 for card in hand if card[0].startswith('A'))
    while total > 21 and aces:
        total -= 10
        ace -= 1

    return total

class BlackjackView(discord.ui.View):
    def __init__(self, user_id, game_message, deck, bet, db, cursor, cash):
        super().__init__()
        self.user_id = user_id
        self.game_message = game_message
        self.deck = deck
        self.bet = bet
        self.db = db
        self.cursor = cursor
        self.cash = cash

    @discord.ui.button(label="Hit", style=discord.ButtonStyle.primary)
    async def hit(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != str(self.user_id):
            await interaction.response.send_message(embed=discord.Embed(description="This is not your game!", colour=constants.colorHexes["Danger"]), ephemeral=True)
            return
        
        db = self.db

        player_hand = games[self.user_id]['player']
        player_hand.append(deal(self.deck))
        total = get_total(player_hand)

        if total > 21:
            embed = discord.Embed(
                title="Blackjack Game",
                description=f"**Your Hand:** `{', '.join(card[0] for card in player_hand)}` | **Total:** `{total}`\n"
                            f"**Dealer Hand:** {games[self.user_id]['dealer'][0][0]}\n",
                colour=constants.colorHexes['DarkBlue']
            )

            embed.add_field(name="Result", value="Busted! You Lose", inline=False)

            del games[self.user_id]
            await interaction.response.edit_message(embed=embed)

        elif total == 21: 
            new_cash = self.cash + (2*self.bet)
            await db.execute('''UPDATE profiles SET cash = ? WHERE guild_id = ? AND user_id = ?''', (new_cash, interaction.guild.id, self.user_id))
            await db.commit()

            embed = discord.Embed(
                title="Blackjack Game",
                description=f"**Your Hand:** `{', '.join(card[0] for card in player_hand)}` | **Total:** `{total}`\n",
                colour=constants.colorHexes["SkyBlue"]
            )
            embed.add_field(name="Result", value=f"You got 21! you win {utils.to_money(2*self.bet)}", inline=False)

            await interaction.response.edit_message(embed=embed)

        else:
            embed = discord.Embed(
                title="Blackjack Game",
                description=f"**Your Hand:** `{', '.join(card[0] for card in player_hand)}` | **Total:** `{total}`\n"
                            f"**Dealer Hand:** `{games[self.user_id]['dealer'][0][0]}`",
                colour=constants.colorHexes["MediumBlue"]
            )
            await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Stand", style=discord.ButtonStyle.primary)
    async def stand(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != str(self.user_id):
            await interaction.response.send_message(embed=discord.Embed(description="`This is not your game!`", colour=constants.colorHexes["Danger"]), ephemeral=True)
            return
        
        db = self.db

        player_hand = games[self.user_id]['player']
        dealer_hand = games[self.user_id]['dealer']

        embed = discord.Embed(
            title="Blackjack Game",
            description=f"**Your final hand:** `{', '.join(card[0] for card in player_hand)}` | **Total:** `{get_total(player_hand)}`\n"
                        f"`Dealer's turn...`",
            colour=constants.colorHexes["MediumBlue"]
        )
        await interaction.response.edit_message(embed=embed, view=None)

        # Dealer Logic

        while get_total(dealer_hand) <= 17:
            dealer_hand.append(deal(self.deck))
            await asyncio.sleep(0.5)

        dealer_total = get_total(dealer_hand)
        player_total = get_total(player_hand)

        result_embed = discord.Embed(
            title="Blackjack Game",
            description=f"**Your Final Hand:** `{', '.join(card[0] for card in player_hand)}` | **Total:** `{player_total}`\n"
                        f"**Dealer Final Hand:** `{games[self.user_id]['dealer'][0][0]}` | **Total:** `{dealer_total}`",
            colour=constants.colorHexes["MediumBlue"]
        )

        if dealer_total > 21:
            new_cash = self.cash + (2*self.bet)
            await db.execute('''UPDATE profiles SET cash = ? WHERE guild_id = ? AND user_id = ?''', (new_cash, interaction.guild.id, self.user_id))
            await db.commit()

            result_embed.add_field(name="Result", value=f"Dealer Busts! You win {utils.to_money(2*self.bet)}", inline=False)

            del games[self.user_id]

        elif dealer_total == player_total:
            new_cash = self.cash + (self.bet)
            await db.execute('''UPDATE profiles SET cash = ? WHERE guild_id = ? AND user_id = ?''', (new_cash, interaction.guild.id, self.user_id))
            await db.commit()

            result_embed.add_field(name="Result", value=f"Dealer Tie! You win {utils.to_money(self.bet)}", inline=False)

            del games[self.user_id]

        elif dealer_total > player_total:
            result_embed.add_field(name="Result", value=f"Dealer Wins!", inline=False)

            del games[self.user_id]

        else:
            new_cash = self.cash + (2*self.bet)
            await db.execute('''UPDATE profiles SET cash = ? WHERE guild_id = ? AND user_id = ?''', (new_cash, interaction.guild.id, self.user_id))
            await db.commit()

            result_embed.add_field(name="Result", value=f"You Won! You win {utils.to_money(2 * self.bet)}", inline=False)

            del games[self.user_id]

        await interaction.edit_original_response(embed=result_embed)


        
class Blackjack(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.game_message = None

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Blackjack is ready.")

    

    @app_commands.command(name="blackjack", description="Play a game of blackjack!")
    @app_commands.describe(bet="The amount of money to bet")
    async def blackjack(self, interaction: discord.Interaction, bet: int):
        guild_id = interaction.guild.id
        user_id = interaction.user.id

        if user_id in games:
            await interaction.response.send_message(embed=discord.Embed(description="`You already have an open game.`", colour=constants.colorHexes["Danger"]), ephemeral=True)
            return

        async with aiosqlite.connect('profiles.db') as db:
            async with db.execute('''SELECT cash FROM profiles WHERE guild_id = ? AND user_id = ?''', (guild_id, user_id)) as cursor:
                profile = await cursor.fetchone()

                if not profile:
                    await interaction.response.send_message(embed=basicEmbeds["SelfNoProfile"], ephemeral=True)

                cash = profile[0]

                if bet < 100:
                    await interaction.response.send_message(embed=discord.Embed(description="`You must bet more than $100`", colour=constants.colorHexes["Danger"]), ephemeral=True)
                    return
                
                if bet > cash:
                    await interaction.response.send_message(embed=discord.Embed(description="`You cannot bet more than you have!`", colour=constants.colorHexes["Danger"]), ephemeral=True)
                    return
                
                removed_bet = cash - bet
                
                await db.execute('''UPDATE profiles SET cash = ? WHERE guild_id = ? AND user_id = ?''', (removed_bet, guild_id, user_id))
                await db.commit()

                deck = create_deck()

                player_hand = [deal(deck), deal(deck)]
                dealer_hand = [deal(deck), deal(deck)]

                games[user_id] = {
                    'player': player_hand,
                    'dealer': dealer_hand
                }

                self.game_message = discord.Embed(
                    title="Blackjack Game", 
                    description=f"**Your Hand:** `{player_hand[0][0]}, {player_hand[1][0]}` | **Total:** `{get_total(player_hand)}`\n"
                                f"**Dealer Hand:** `{dealer_hand[0][0]}`",
                    colour=constants.colorHexes["MediumBlue"]
                )

                game_message = self.game_message

                view = BlackjackView(user_id, game_message, deck, bet, db, cursor, cash)

                await interaction.response.send_message(embed=game_message, view=view)


async def setup(bot):
    Blackjack_cog = Blackjack(bot)
    await bot.add_cog(Blackjack_cog)