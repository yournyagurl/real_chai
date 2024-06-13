import os
import random
import discord
from discord.ext import commands
from dotenv import load_dotenv
from eliDb import add_cash, get_cash, remove_cash

# Load environment variables from .env file
load_dotenv()

# Retrieve the token from environment variables
TOKEN = os.getenv('DISCORD_TOKEN_CHAI')

# Create an instance of a Client with the appropriate intents
intents = discord.Intents.default()
intents.guilds = True
intents.messages = True
intents.voice_states = True
intents.message_content = True
intents.members = True

# Initialize the Discord bot
bot = commands.Bot(command_prefix='!', intents=intents)

# Define card ranks, suits, and values
ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
suits = ['♠', '♣', '♦', '♥']
values = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10, 'J': 10, 'Q': 10, 'K': 10, 'A': 11}

# Card class to represent each playing card
class Card:
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit

    def __str__(self):
        return f'{self.rank}{self.suit}'

# Deck class to represent a deck of cards
class Deck:
    def __init__(self):
        self.cards = [Card(rank, suit) for rank in ranks for suit in suits]
        random.shuffle(self.cards)

    def deal_card(self):
        return self.cards.pop()

# Hand class to represent a player's or dealer's hand
class Hand:
    def __init__(self):
        self.cards = []
        self.value = 0
        self.aces = 0

    def add_card(self, card):
        self.cards.append(card)
        self.value += values[card.rank]
        if card.rank == 'A':
            self.aces += 1

    def adjust_for_ace(self):
        while self.value > 21 and self.aces:
            self.value -= 10
            self.aces -= 1

# Function to show some of the cards (hide one of the dealer's cards)
def show_some(player, dealer):
    embed = discord.Embed(title="Blackjack", color=0x00ff00)
    dealer_hand = f"🎴 <card hidden>\n🎴 {dealer.cards[1]}\nTotal Value: ??"
    embed.add_field(name="Dealer's Hand", value=dealer_hand, inline=False)

    # Player's Hand
    player_hand = '\n'.join([f"🎴 {card}" for card in player.cards]) + f"\nTotal Value: {player.value}"
    embed.add_field(name="Player's Hand", value=player_hand, inline=False)

    return embed

# Function to show all cards
def show_all(player, dealer):
    embed = discord.Embed(title="Blackjack", color=0x00ff00)

    # Dealer's Hand
    dealer_hand = '\n'.join([f"🎴 {card}" for card in dealer.cards]) + f"\nTotal Value: {dealer.value}"
    embed.add_field(name="Dealer's Hand", value=dealer_hand, inline=False)

    # Player's Hand
    player_hand = '\n'.join([f"🎴 {card}" for card in player.cards]) + f"\nTotal Value: {player.value}"
    embed.add_field(name="Player's Hand", value=player_hand, inline=False)

    return embed

# Function for when player busts
def player_busts(member_id, bet):
    # Remove cash from the database
    remove_cash(member_id, bet)
    return "Player busts!\n"

# Function for when player wins
def player_wins(member_id, bet):
    # Add cash to the database
    add_cash(member_id, bet)
    return "Player wins!\n"

# Function for when dealer busts
def dealer_busts(member_id, bet):
    # Add cash to the database
    add_cash(member_id, bet)
    return "Dealer busts!\n"

# Function for when dealer wins
def dealer_wins(member_id, bet):
    # Remove cash from the database
    remove_cash(member_id, bet)
    return "Dealer wins!\n"

# Function for when there's a tie
def push():
    return "Dealer and Player tie! It's a push.\n"

# Class to manage player's chips
class Chips:
    def __init__(self, member_id, total=100):
        self.member_id = member_id
        self.total = total
        self.bet = 0

    def win_bet(self):
        self.total += self.bet

    def lose_bet(self):
        self.total -= self.bet

# Discord command for Blackjack game
@bot.command(name='blackjack', help='Starts a game of Blackjack.')
async def blackjack_game_discord(ctx):
    member_id = ctx.author.id  # Assuming ctx.author.id gives you the member's ID

    while True:
        await ctx.send('Welcome to Blackjack!')

        deck = Deck()
        player_hand = Hand()
        dealer_hand = Hand()
        player_chips = Chips(member_id)

        # Prompt player for their bet
        await ctx.send(f'You have {player_chips.total} chips. Enter your bet amount:')
        def check_bet(message):
            return message.author == ctx.author and message.channel == ctx.channel and message.content.isdigit() and int(message.content) <= player_chips.total

        msg = await bot.wait_for('message', check=check_bet)
        bet_amount = int(msg.content)
        player_chips.bet = bet_amount

        # Deal initial cards
        player_hand.add_card(deck.deal_card())
        dealer_hand.add_card(deck.deal_card())
        player_hand.add_card(deck.deal_card())
        dealer_hand.add_card(deck.deal_card())

        # Check for player Blackjack
        if player_hand.value == 21:
            await ctx.send("Blackjack! Player wins!")
            player_wins(member_id, player_chips.bet)
            await ctx.send(f'Player\'s total chips: {get_cash(member_id)}')
            await ctx.send('Do you want to play again? Enter yes or no:')
            def check(message):
                return message.author == ctx.author and message.channel == ctx.channel and message.content.lower() in ['yes', 'no']
            msg = await bot.wait_for('message', check=check)
            if msg.content.lower() != 'yes':
                await ctx.send('Thanks for playing!')
                break
            continue

        # Check for dealer Blackjack
        if dealer_hand.value == 21:
            await ctx.send("Blackjack! Dealer wins!")
            dealer_wins(member_id, player_chips.bet)
            await ctx.send(f'Player\'s total chips: {get_cash(member_id)}')
            await ctx.send('Do you want to play again? Enter yes or no:')
            def check(message):
                return message.author == ctx.author and message.channel == ctx.channel and message.content.lower() in ['yes', 'no']
            msg = await bot.wait_for('message', check=check)
            if msg.content.lower() != 'yes':
                await ctx.send('Thanks for playing!')
                break
            continue

        await ctx.send(embed=show_some(player_hand, dealer_hand))

        # Player's turn
        while True:
            await ctx.send("Would you like to Hit or Stand? Enter 'h' or 's':")

            def check(message):
                return message.author == ctx.author and message.channel == ctx.channel and message.content.lower() in ['h', 's']
            msg = await bot.wait_for('message', check=check)

            if msg.content.lower() == 'h':
                hit(deck, player_hand)
                await ctx.send(embed=show_some(player_hand, dealer_hand))
                if player_hand.value > 21:
                    await ctx.send(player_busts(member_id, player_chips.bet))
                    break
            else:
                await ctx.send("Player stands. Dealer is playing.")
                break

        # Dealer's turn
        if player_hand.value <= 21:
            while dealer_hand.value < 17:
                hit(deck, dealer_hand)

            await ctx.send(embed=show_all(player_hand, dealer_hand))

            # Determine winner
            if dealer_hand.value > 21:
                await ctx.send(dealer_busts(member_id, player_chips.bet))
            elif dealer_hand.value > player_hand.value:
                await ctx.send(dealer_wins(member_id, player_chips.bet))
            elif dealer_hand.value < player_hand.value:
                await ctx.send(player_wins(member_id, player_chips.bet))
            else:
               
