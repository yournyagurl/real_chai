import datetime as dt
import os
import json
import logging
import random
from datetime import datetime, timedelta
import pytz
import asyncio
import subprocess
from dotenv import load_dotenv
from dateutil import parser as date_parser
import discord
from discord.ext import commands, tasks
from eliDb import initialize_database, add_member, add_cash, get_cash, add_xp, get_xp, reset_xp, remove_cash, remove_xp, get_xp_leaderboard, get_pet_details, update_pet_feedings, check_pet_health, adopt_pet, rename_pet, fetch_random_pet_from_store, add_shop_item, get_cash_leaderboard, deposit, withdraw, get_bank_balance, update_last_claim_times, get_last_claim_times, get_inventory, get_shop_items, add_shop_item, edit_shop_item, delete_shop_item, add_inventory_item, use_inventory_item
import traceback
import sqlite3

# Load environment variables from .env file
load_dotenv()

# Retrieve the token from environment variables
TOKEN = os.getenv('DISCORD_TOKEN_CHAI')

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')

# Function to load the prefix from the JSON file
def get_prefix():
    try:
        with open('variables.json', 'r') as f:
            data = json.load(f)
        return data.get('prefix', ';')
    except (FileNotFoundError, json.JSONDecodeError):
        return ';'

# Function to save the new prefix to the JSON file
def set_prefix(new_prefix):
    try:
        with open('variables.json', 'r') as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {}
    data['prefix'] = new_prefix
    with open('variables.json', 'w') as f:
        json.dump(data, f, indent=4)
  
# Create an instance of a Client with the appropriate intents
intents = discord.Intents.default()
intents.guilds = True
intents.messages = True
intents.voice_states = True
intents.message_content = True
intents.members = True

# Initialize the bot with intents and dynamic command prefix
bot = commands.Bot(command_prefix=get_prefix(), intents=intents)
custom_color = discord.Color.from_rgb(179, 202, 25)

active_users = {}
#
#
#
#
#
#
#
@bot.command(description="Sends the bot's latency.")
async def ping(ctx):
    latency = bot.latency * 1000  # Latency in milliseconds
    embed = discord.Embed(title="Pong!", description=f"**Latency is {latency:.2f} ms**", color=custom_color)
    await ctx.send(embed=embed)

# greeting
@bot.event
async def on_message(message):
    if bot.user.mentioned_in(message) and ' say hi' in message.content.lower():
        await message.channel.send('hi, i\'m plum')
    
    minute_key = message.created_at.strftime("%Y-%m-%d %H:%M")
    if minute_key not in active_users:
        active_users[minute_key] = set()
        active_users[minute_key].add(message.author.id)
        logging.info(f"User {message.author.id} is active at {minute_key}")

        await bot.process_commands(message)

# display user details
@bot.command(name='who')
async def who(ctx, member: discord.Member = None):
    """Display information about a member."""
    if member is None:
        member = ctx.author

    user = await bot.fetch_user(member.id)
    banner_url = user.banner.url if user.banner else None

    embed = discord.Embed(title=f"{member.display_name}'s file", color=custom_color)
    embed.set_thumbnail(url=member.avatar.url)
    embed.add_field(name="Username", value=member.name, inline=True)
    embed.add_field(name="Server Nickname", value=member.nick, inline=True)
    embed.add_field(name="Display Name", value=member.display_name, inline=True)
    embed.add_field(name="User ID", value=member.id, inline=True)
    embed.add_field(name="Account Created", value=member.created_at.strftime("%Y-%m-%d %H:%M:%S"), inline=True)
    embed.add_field(name="Joined Server", value=member.joined_at.strftime("%Y-%m-%d %H:%M:%S"), inline=True)
    if banner_url:
        embed.set_image(url=banner_url)
    
    await ctx.send(embed=embed)
#
#
#
#
#
#
#
#
#
#
#

# level commands

# my xp command
@bot.command(name='myxp')
async def myxp(ctx, member: discord.Member = None):
    """Display XP"""
    if member is None:
        member = ctx.author

    myxp = get_xp(member.id)  # Pass member ID to get_xp
    embed = discord.Embed(title=f"{member.display_name}'s experience", color=custom_color)
    embed.add_field(name="Your XP", value=f":four_leaf_clover: {myxp}", inline=False)
    await ctx.send(embed=embed)

# add xp 
@bot.command(name='addxp')
async def addxp(ctx, xp: int = None, member: discord.Member = None):
    """Add xp to member"""
    if not ctx.message.author.guild_permissions.administrator:
        await ctx.send("You don't have permission to use this command.")
        return
    
    if member is None:
        await ctx.send("Please mention a valid member.")
        return
    
    if xp is None:
        await ctx.send("Please provide a valid amount of XP to add.")
        return
    
    try:
        xp_int = int(xp)
    except ValueError:
        await ctx.send("Invalid amount. Please provide a valid integer.")
        return

    print(f"Adding {xp_int} XP to Member ID: {member.id}")
    add_xp(member.id, xp_int)
    logging.info(f"Added {xp_int} XP to Member ID: {member.id}")
    await ctx.send(f"Added {xp_int} XP to {member.display_name}.")

# reset xp
@bot.command(name='ResetXp')
async def ResetXp(ctx, target=None):
    if ctx.message.author.guild_permissions.administrator:
        if target is None:
            await ctx.send("Please specify a target")
            return
        if target.lower() == 'role':
            await reset_xp_for_role(ctx)
        elif target.lower() == 'everyone':
            await reset_xp_for_everyone(ctx)
        else:
            try:
                member = await commands.MemberConverter().convert(ctx, target)
                await reset_xp_for_member(ctx, member)
            except commands.errors.MemberNotFound:
                await ctx.send("Member not found.")
    else:
        await ctx.send("You do not have permission to use this command.")

# Function to reset XP for members with a specific role
async def reset_xp_for_role(ctx):
    if ctx.message.author.guild_permissions.administrator:
        role_name = "Your Role Name Here"  # Change this to the name of the role you want to target
        role = discord.utils.get(ctx.guild.roles, name=role_name)
    if role:
        for member in role.members:
            reset_xp(member.id, 0)  # Reset XP to 0 for each member
        await ctx.send(f"XP reset to 0 for members with the role {role_name}.")
    else:
        await ctx.send(f"Role '{role_name}' not found.")

# Function to reset XP for everyone in the server
async def reset_xp_for_everyone(ctx):
    if ctx.message.author.guild_permissions.administrator:
      for member in ctx.guild.members:
        if not member.bot:  # Ignore bot accounts
            reset_xp(member.id, 0)  # Reset XP to 0 for each member
        await logging.info("XP reset to 0 for everyone in the server.")

# Function to reset XP for a specified member
async def reset_xp_for_member(ctx, member):
    reset_xp(member.id, 0)  # Reset XP to 0 for the specified member
    await ctx.send(f"XP reset to 0 for {member.display_name}.")


# Remove XP
@bot.command(name='RemoveXp')
async def remove_xp_command(ctx, xp: int, member: discord.Member):
        """Remove Xp"""
        if ctx.message.author.guild_permissions.administrator:
            if member is None:
                embed = discord.Embed(title="Oops!", description="Please add a member")
                await ctx.send(embed=embed)
        
            if xp is None:
                embed = discord.Embed(title="Oops!", description="It's **';addcash <amount> @<user>'**")
                await ctx.send(embed=embed)
                return
        
            try:
                xp_int = int(xp)
        
            except ValueError:
                embed = discord.Embed(title="Oops!", description="It's **';addcash <amount> @<user>'**")
                await ctx.send(embed=embed)
                return
        
            remove_xp(member.id, xp_int)
            await ctx.send(f"Added {xp} XP to {member.display_name}.")



# XP leaderboard
@bot.command(name="leaderboard-xp")
async def lb_xp(ctx):
    """XP Leaderboard"""
    # Get the leaderboard from the database
    leaderboard = get_xp_leaderboard()
    
    # Create an embed to display the leaderboard
    embed = discord.Embed(title="XP Leaderboard", color=discord.Color.blue())
    
    # Add top users to the embed
    for user_id, xp in leaderboard:
        user = await bot.fetch_user(user_id)
        embed.add_field(name=f"{user.name}", value=f"{xp} XP", inline=False)
    
    # Send the embed
    await ctx.send(embed=embed)



#
#
#
#
#
#
#
#




# economy commands 


# wallet command
@bot.command(name='bal')
async def wallet(ctx, member: discord.Member = None):
    """Display Cash and Bank Balance"""
    if member is None:
        member = ctx.author

    bank_balance = get_bank_balance(member.id)
    cash = get_cash(member.id)
    
    logging.info(f"Member ID: {member.id}, Cash: {cash}, Bank Balance: {bank_balance}")

    embed = discord.Embed(title=f"{member.display_name}'s Wallet", color=custom_color)
    embed.add_field(name=":four_leaf_clover: Cash", value=f"{cash}", inline=True)
    embed.add_field(name=":bank: Bank", value=f"{bank_balance}", inline=True)
    await ctx.send(embed=embed)

# add cash command
@bot.command(name='addcash')
async def addcash(ctx, amount: int = None, member: discord.Member = None):
    """Add Cash (for debugging)"""
    if ctx.message.author.guild_permissions.administrator:
     if member is None:
        member = ctx.author
    
     if amount is None:
        await ctx.send("Please add an amount")
        return
    
    try:
        amount_int = int(amount)
    except ValueError:
        embed = discord.Embed(title="Oops!", description="It's **';addcash <amount> @<user>'**")
        await ctx.send(embed=embed)
        return

    print(f"Adding {amount} :four_leaf_clover: to Member ID: {member.id}")
    add_cash(member.id, amount)
    logging.info(f"Added {amount_int} cash to Member ID: {member.id}")
    await ctx.send(f"Added {amount}:four_leaf_clover: to {member.display_name}'s account.")

# remove cash command
@bot.command(name="removecash")
async def removecash(ctx, amount:int = None, member: discord.Member = None) :
    """Remove cash from one member"""
    if ctx.message.author.guild_permissions.administrator:
        if member is None:
            embed = discord.Embed(title="Oops!", description="please mention a member")
            await ctx.send(embed = embed)
    
    if amount is None:
        embed = discord.Embed(title="Oops!", description="Please add an amount")
        await ctx.send(embed=embed)

    try:
        amount_int = int(amount)
    except ValueError:
        embed = discord.Embed(title="Oops!", description="It's **';removecash <amount> @<user>'**")
        await ctx.send(embed=embed)
        return
    
    print(f"Removed {amount} :four_leaf_clover: from {member.display_name}'s account")
    remove_cash(member.id, amount)
    logging.info(f"removed {amount_int} cash from member {member.id}")
    await ctx.send(f"Removed {amount} :four_leaf_clover: from {member.display_name}'s account")

# Cash leaderboard
@bot.command(name="leaderboard-cash")
async def lb_cash(ctx):
    """XP Leaderboard"""
    # Get the leaderboard from the database
    leaderboard = get_cash_leaderboard()
    
    # Create an embed to display the leaderboard
    embed = discord.Embed(title="Cash Leaderboard", color=custom_color)
    
    # Add top users to the embed
    for user_id, cash in leaderboard:
        user = await bot.fetch_user(user_id)
        embed.add_field(name=f"{user.name}", value=f"{cash} :four_leaf_clover: ", inline=False)
    
    # Send the embed
    await ctx.send(embed=embed)

@bot.command(name="deposit")
async def deposit_command(ctx, amount: int = None):
    member_id = ctx.author.id
    
    current_cash = get_cash(member_id)
    
    if amount is None or amount > current_cash:
        await ctx.send("You don't have enough cash to deposit that amount.")
    else:
        deposit(member_id, amount)
        embed = discord.Embed(title="Transaction Alert!", description=f"Deposited {amount}", color=custom_color)
        await ctx.send(embed=embed)

@bot.command(name="withdraw")
async def withdraw_command(ctx, amount: int = None):
    member_id = ctx.author.id
    bank_balance = get_bank_balance(member_id)
    
    if amount is None or amount > bank_balance:
        await ctx.send("You don't have enough funds in the bank to withdraw that amount.")
    else:
        withdraw(member_id, amount)
        embed = discord.Embed(title="Transaction Alert!", description=f"Withdrawed {amount}", color=custom_color)
        await ctx.send(embed=embed)


# Define income amounts for roles


# Define the role names that should receive a daily income
daily_role_names = ["Verified 18+"]  # Replace with your role names

# Amount of daily income
daily_income_amount = 500

@bot.event
async def on_ready():
    print(f'Bot is ready. Logged in as {bot.user}')

@bot.command(name="daily")
async def daily(ctx):
    """Give the user their daily income if they have the required role and it's been 24 hours since the last claim."""
    member = ctx.author

    if any(role.name in daily_role_names for role in member.roles):
        last_claim_time = get_last_claim_times(member.id, 'daily')
        now = datetime.now()
        
        if not last_claim_time or (now - date_parser.parse(last_claim_time)).days >= 1:
            add_cash(member.id, daily_income_amount)
            update_last_claim_times(member.id, 'daily', now.isoformat())
            embed = discord.Embed(title="Income Collected!", description=f"You have received your weekly income of :four_leaf_clover: {daily_income_amount}", color=custom_color)
            embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
            await ctx.send(embed=embed)
        else:
            next_claim_time = date_parser.parse(last_claim_time) + timedelta(days=1)
            time_left = next_claim_time - now
            hours, remainder = divmod(int(time_left.total_seconds()), 3600)
            minutes, _ = divmod(remainder, 60)
            embed = discord.Embed(title="Income Not Available Yet", description=f"You need to wait {hours} hours and {minutes} minutes before claiming your next weekly income.", color=discord.Color.red())
            embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
            await ctx.send(embed=embed)
    else:
        embed = discord.Embed(title="oops", description="You do not have the required role to receive a daily income. Get verified or boost to recieve role income :D")
        await ctx.send(embed = embed)

last_weekly_payout_date = {}

user_balances = {}

weekly_role_income = {
    "Shamrock": 5000,  # Replace with your role names and income amounts
    "₊˚໒ Staff ୭₊˚": 2500,
    "Vanity Link" : 2000,
}
# Run the bot
@bot.command(name="weekly")
async def weekly(ctx):
    """Give the user their weekly income if they have the required role and it's been 7 days since the last claim."""
    member = ctx.author
    member_id = member.id
    member_roles = [role.name for role in member.roles if role.name in weekly_role_income]

    if member_roles:
        total_weekly_income = 0

        for role_name in member_roles:
            total_weekly_income += weekly_role_income[role_name]
        
        # Get the last weekly claim time from the database
        last_weekly_claim = get_last_claim_times(member_id, 'weekly')

        if last_weekly_claim is None or (datetime.now() - date_parser.parse(last_weekly_claim)).days >= 7:
            # If eligible, update last claim time and give weekly income
            update_last_claim_times(member_id, 'weekly', datetime.now())
            add_cash(member.id, total_weekly_income)
            embed = discord.Embed(title="Income Collected!", description=f"You have received your weekly income of :four_leaf_clover: {total_weekly_income}", color=discord.Color.green())
            embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
            await ctx.send(embed=embed)
        else:
            # Calculate time left before next claim
            next_claim_time = date_parser.parse(last_weekly_claim) + timedelta(days=7)
            time_left = next_claim_time - datetime.now()
            hours, remainder = divmod(int(time_left.total_seconds()), 3600)
            minutes, _ = divmod(remainder, 60)
            embed = discord.Embed(title="Income Not Available Yet", description=f"You need to wait {hours} hours and {minutes} minutes before claiming your next weekly income.", color=discord.Color.red())
            embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
            await ctx.send(embed=embed)
    else:
        await ctx.send("You do not have the required role to receive a weekly income.")


@bot.command(name="collect")
async def collect(ctx):
    embed = discord.Embed(title="Wrong command", description="the command is ;daily and ;weekly :/, get it right!!!")
    embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
    embed.set_image(url="https://media.discordapp.net/attachments/1247339536900558960/1250617867955736676/8toqxn.jpg?ex=666b9827&is=666a46a7&hm=d23be4dcfd52fa2e37f97f5b3e0a1c27270be3c04f2537bea653f07496b6af77&=&format=webp")
    await ctx.send(embed=embed)

# Run the bot
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#

# SHOP COMMANDS

@bot.command(name='inv')
async def inventory(ctx):
    member = ctx.author
    member_id = member.id

    inventory = get_inventory(member_id)

    if inventory:
        embed = discord.Embed(title="Inventory", color=custom_color)
        for item_name, quantity in inventory:
            embed.add_field(name=item_name, value=f"Quantity: {quantity}", inline=True)
        await ctx.send(embed=embed)
    else:
        await ctx.send("Your inventory is empty.")

@bot.command(name='shop')
async def shop(ctx):
    shop_items = get_shop_items()

    if shop_items:
        embed = discord.Embed(title="Shop Items", color=custom_color)
        for item_name, item_price in shop_items:
            embed.add_field(name=item_name, value=f"Price: {item_price}", inline=False)
        await ctx.send(embed=embed)
    else:
        await ctx.send("There are no items available in the shop.")


@bot.command(name='additem')
async def add_item(ctx):
    await ctx.send("Please provide the name of the item.")
    name = await bot.wait_for('message', check=lambda m: m.author == ctx.author and m.channel == ctx.channel)

    await ctx.send("Please provide the price of the item.")
    price = await bot.wait_for('message', check=lambda m: m.author == ctx.author and m.channel == ctx.channel)

    await ctx.send("Is the item consumable? (yes/no)")
    consumable = await bot.wait_for('message', check=lambda m: m.author == ctx.author and m.channel == ctx.channel)

    await ctx.send("Please mention the role assigned to this item. If none, type 'none'.")
    role_assigned = await bot.wait_for('message', check=lambda m: m.author == ctx.author and m.channel == ctx.channel)

    try:
        add_shop_item(name.content, int(price.content), consumable.content.lower() == 'yes', role_assigned.content)
        await ctx.send(f"Item '{name.content}' added to the shop.")
    except Exception as e:
        await ctx.send(f"An error occurred: {e}")



@bot.command(name='deleteitem')
async def delete_item(ctx, item_name):
    delete_shop_item(item_name)
    await ctx.send("Item deleted from the shop.")

@bot.command(name='edititem')
async def edit_item(ctx, item_id: int, name=None, price=None, consumable=None, role_assigned=None):
    edit_shop_item(item_id, name, price, consumable, role_assigned)
    await ctx.send("Item details updated.")

@bot.command(name='buy')
async def buy_item(ctx, item_name):
    member_id = ctx.author.id

    # Check if the item exists in the shop
    shop_items = get_shop_items()
    item = next((item for item in shop_items if item[0] == item_name), None)

    if not item:
        await ctx.send("This item does not exist in the shop.")
        return

    # Check if the member has enough cash to buy the item
    cash_balance = get_cash(member_id)
    item_price = item[1]  # Price of the item

    if cash_balance < item_price:
        await ctx.send("You don't have enough cash to buy this item.")
        return

    # Deduct the price of the item from the member's balance
    remove_cash(member_id, item_price)

    # Add the item to the member's inventory
    add_inventory_item(member_id, item_name)

    await ctx.send(f"Congratulations! You have bought {item_name} for {item_price} cash.")

async def give_role(ctx, role_name_or_id: str, member: discord.Member):
    guild = ctx.guild
    try:
        # Attempt to retrieve the role by ID first
        role = discord.utils.get(guild.roles, id=int(role_name_or_id))
        if not role:
            # If role ID retrieval fails, attempt to retrieve by name
            role = discord.utils.get(guild.roles, name=role_name_or_id)

        if role:
            # Check if the user already has the role
            if role in member.roles:
                await ctx.send(f"{member.mention}, you already have the {role.name} role.")
            else:
                # Attempt to assign the role
                await member.add_roles(role)
                await ctx.send(f"{member.mention}, you have been given the {role.name} role.")
                logging.info(f"{member} was given the {role.name} role manually.")
        else:
            await ctx.send(f"{ctx.author.mention}, the role '{role_name_or_id}' does not exist.")
            logging.warning(f"Role '{role_name_or_id}' not found.")
    except ValueError:
        await ctx.send(f"{ctx.author.mention}, please provide a valid role name or ID.")
    except discord.Forbidden:
        await ctx.send(f"{ctx.author.mention}, I do not have permission to manage roles.")
    except Exception as e:
        await ctx.send(f"{ctx.author.mention}, an unexpected error occurred: {e}")
        logging.exception(f"Unexpected error occurred while giving role to {member}: {e}")

@bot.command(name='use')
async def use_item(ctx, member: discord.Member, *, item_name: str):
    member_id = ctx.author.id  # Get the ID of the command invoker (ctx.author)
    guild = ctx.guild

    try:
        role_identifier = use_inventory_item(member_id, item_name)

        if role_identifier:
            # Check if role_identifier is a name or ID
            try:
                role_id = int(role_identifier)
                role = discord.utils.get(guild.roles, id=role_id)
            except ValueError:
                role = discord.utils.get(guild.roles, name=role_identifier)

            if role:
                # Check if the bot has permission to manage roles for the member
                if not ctx.guild.me.guild_permissions.manage_roles:
                    await ctx.send(f"{ctx.author.mention}, I do not have permission to manage roles.")
                    return

                # Check if the bot's role is higher than the role to be assigned
                if role.position >= ctx.guild.me.top_role.position:
                    await ctx.send(f"{ctx.author.mention}, I cannot assign the role '{role.name}' because it is higher than my highest role.")
                    return

                # Assign the role using the give_role function
                await give_role(ctx, str(role.id), member)
                logging.info(f"{member} used {item_name} and received the {role.name} role.")
            else:
                await ctx.send(f"{ctx.author.mention}, you have successfully used {item_name}, but the role '{role_identifier}' does not exist or I cannot assign it.")
                logging.warning(f"Role '{role_identifier}' not found or cannot be assigned by {bot.user}.")
        else:
            await ctx.send(f"{ctx.author.mention}, you have successfully used {item_name}.")
            logging.info(f"{ctx.author} used {item_name} without receiving a role.")
    except ValueError as e:
        await ctx.send(f"{ctx.author.mention}, an error occurred: {e}")
        logging.error(f"ValueError occurred while using item '{item_name}': {e}")
    except discord.Forbidden:
        await ctx.send(f"{ctx.author.mention}, I do not have permission to manage roles.")
        logging.error(f"Bot does not have permission to manage roles.")
    except Exception as e:
        await ctx.send(f"{ctx.author.mention}, an unexpected error occurred: {e}")
        logging.exception(f"Unexpected error occurred while using item '{item_name}': {e}")

#
#
#
#
#
#

# gambling commands

# Define card ranks, suits, and values
# Card values
suits = ['♢', '♧', '♡', '♤']
values = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']

# Create a full deck of cards
deck = [f'{value}{suit}' for suit in suits for value in values]

# Card values for blackjack
card_values = {
    '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10,
    'J': 10, 'Q': 10, 'K': 10, 'A': 11
}

# Deal a card
def deal_card():
    return random.choice(deck)

# Calculate hand value
def calculate_hand_value(hand):
    value = sum(card_values[card[:-1]] for card in hand)
    aces = sum(1 for card in hand if card[:-1] == 'A')
    while value > 21 and aces:
        value -= 10
        aces -= 1
    return value
error_color = discord.Color.from_rgb(204,0,0)


@bot.command(name='blackjack')
@commands.cooldown(1, 86400, commands.BucketType.user)
async def blackjack(ctx, bet: int):
    member_id = ctx.author.id
    current_cash = get_cash(member_id)

    if bet < 100 or bet > 1000:
        embed = discord.Embed(title="Error!", description='Bet must be between 100 and 1000.', color=error_color)
        await ctx.send(embed=embed)
        return

    if current_cash < bet:
        embed = discord.Embed(title="Error!", description=f'You do not have enough cash to place this bet. Your current cash is {current_cash}.', color=error_color)
        await ctx.send(embed=embed)
        return

    # Deduct the bet from the player's cash
    remove_cash(member_id, bet)

    player_hand = [deal_card(), deal_card()]
    dealer_hand = [deal_card(), deal_card()]
    
    embed = discord.Embed(title="Blackjack", description=f"Bet: {bet}", color=discord.Color.blue())
    embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
    embed.add_field(name="Your Hand", value=f'{" ".join(player_hand)} (value: {calculate_hand_value(player_hand)})', inline=False)
    embed.add_field(name="Dealer's Hand", value=f'{dealer_hand[0]} ?', inline=False)
    
    message = await ctx.send(embed=embed)

    while calculate_hand_value(player_hand) < 21:
        await ctx.send('Do you want to hit or stand? (respond with `hit` or `stand`)')
        
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel and m.content.lower() in ['hit', 'stand']
        
        try:
            msg = await bot.wait_for('message', check=check, timeout=30.0)
        except asyncio.TimeoutError:
            await ctx.send('You took too long to respond. Standing by default.')
            break

        if msg.content.lower() == 'hit':
            player_hand.append(deal_card())
            embed.set_field_at(0, name="Your Hand", value=f'{" ".join(player_hand)} (value: {calculate_hand_value(player_hand)})', inline=False)
            await message.edit(embed=embed)
        else:
            break

    player_value = calculate_hand_value(player_hand)
    if player_value > 21:
        await ctx.send(f'You busted with a hand value of {player_value}. You lose your bet of {bet}.')
        return

    embed.set_field_at(1, name="Dealer's Hand", value=f'{" ".join(dealer_hand)} (value: {calculate_hand_value(dealer_hand)})', inline=False)
    await message.edit(embed=embed)
    
    while calculate_hand_value(dealer_hand) < 17:
        dealer_hand.append(deal_card())
        embed.set_field_at(1, name="Dealer's Hand", value=f'{" ".join(dealer_hand)} (value: {calculate_hand_value(dealer_hand)})', inline=False)
        await message.edit(embed=embed)

    dealer_value = calculate_hand_value(dealer_hand)
    if dealer_value > 21:
        await ctx.send(f'Dealer busts with a hand value of {dealer_value}. You win {bet * 2}!')
        add_cash(member_id, bet + bet)
    elif dealer_value > player_value:
        await ctx.send(f'Dealer wins with {dealer_value} against your {player_value}. You lose your bet of {bet}.')
    elif dealer_value < player_value:
        await ctx.send(f'You win with {player_value} against dealer\'s {dealer_value}. You win {bet * 2}!')
        add_cash(member_id, bet + bet)
    else:
        await ctx.send(f'It\'s a tie with both having {player_value}. Your bet of {bet} is returned.')
        add_cash(member_id, bet)

@blackjack.error
async def blackjack_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        embed = discord.Embed(title="Nuh uh!", description=f"You're going too fast. Try again in {error.retry_after // 3600} hours.", color=error_color)
        await ctx.send(embed=embed)
    elif isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(title="Error!", description='Please enter a valid bet amount between 100 and 1000.', color=error_color)
        await ctx.send(embed=embed)
    elif isinstance(error, commands.BadArgument):
        embed = discord.Embed(title="Error!", description='Please enter a valid numerical bet amount.', color=error_color)
        await ctx.send(embed=embed)
    else:
        # Default error handling
        embed = discord.Embed(title="Error!", description="Something went wrong.", color=error_color)
        await ctx.send(embed=embed)

    embed.set_author(name=ctx.author.display_name)
#
#
#
#
#
#
#
#
#

# ROULETTE COMMAND

class RouletteGame:
    def __init__(self):
        self.slots = {
            '0': 'green',
            '00': 'green',
            '1': 'red', '2': 'black', '3': 'red', '4': 'black', '5': 'red',
            '6': 'black', '7': 'red', '8': 'black', '9': 'red', '10': 'black',
            '11': 'black', '12': 'red', '13': 'black', '14': 'red', '15': 'black',
            '16': 'red', '17': 'black', '18': 'red', '19': 'red', '20': 'black',
            '21': 'red', '22': 'black', '23': 'red', '24': 'black', '25': 'red',
            '26': 'black', '27': 'red', '28': 'black', '29': 'black', '30': 'red',
            '31': 'black', '32': 'red', '33': 'black', '34': 'red', '35': 'black',
            '36': 'red'
        }

    async def play_roulette(self, ctx, bet_amount: int, space: str):
        member_id = ctx.author.id
        current_cash = get_cash(member_id)  # Replace with your method to retrieve user's cash

        if bet_amount <= 0 or bet_amount > current_cash:
            embed = discord.Embed(title="Error!", description='Invalid bet amount.', color=error_color)
            embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
            await ctx.send(embed=embed)
            return

        remove_cash(member_id, bet_amount)

        # Determine the multiplier based on the space bet on
        if space in ["odd", "even", "black", "red"]:
            multiplier = 2
        else:
            multiplier = 35

        result = random.choice(list(self.slots.keys()))

        result_prompt = f"The ball landed on: **{self.slots[result]} {result}**!\n\n"

        if space == "black":
            win = 1 if self.slots[result] == "black" else 0

        elif space == "red":
            win = 1 if self.slots[result] == "red" else 0

        elif space == "even":
            result_num = int(result)
            win = 1 if (result_num % 2) == 0 else 0

        elif space == "odd":
            result_num = int(result)
            win = 1 if (result_num % 2) != 0 else 0

        elif space.isdigit():  # Check if the space is a specific number
            win = 1 if space == result else 0

        else:
            # This should not happen under normal circumstances
            print("Unexpected condition.")

        if win:
            winnings = bet_amount * multiplier
            add_cash(member_id, winnings)
            result_prompt += f"🎉  **Winner:**  🎉\n{ctx.author.mention} won {str(winnings)}!"
            color = discord.Color.green()
        else:
            result_prompt += "**No Winner :(**"
            color = error_color

        embed = discord.Embed(title="Roulette Result", description=result_prompt, color=color)
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
        await ctx.send(embed=embed)

roulette_game = RouletteGame()

@bot.command(name='roulette')
@commands.cooldown(1, 86400, commands.BucketType.user)
async def roulette(ctx, bet_amount: int, space: str):
    await roulette_game.play_roulette(ctx, bet_amount, space)

@roulette.error
async def roulette_error(ctx, error):
    traceback.print_exc() 
    if isinstance(error, commands.CommandOnCooldown):
        embed = discord.Embed(title="Nuh uh!", description=f"You're going too fast. Try again in {error.retry_after // 3600} hours.", color=error_color)
        await ctx.send(embed=embed)
    elif isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(title="Error!", description='Please enter a valid bet amount between 100 and 1000.', color=error_color)
        await ctx.send(embed=embed)
    elif isinstance(error, commands.BadArgument):
        embed = discord.Embed(title="Error!", description='Please enter a valid numerical bet amount.', color=error_color)
        await ctx.send(embed=embed)
    else:
        # Default error handling
        embed = discord.Embed(title="Error!", description="Something went wrong.", color=error_color)
        await ctx.send(embed=embed)

#
#
#
#
#
#
#
#
#
#
#
#


# slots
class SlotsGame:
    def __init__(self):
        self.symbols = ['🍒', '🍋', '🔔', '🍉', '⭐', '7️⃣']

    def spin(self):
        return random.choices(self.symbols, k=3)

    def calculate_winnings(self, bet_amount, result):
        if result[0] == result[1] == result[2]:
            return bet_amount * 2  # Jackpot
        else:
            return 0  # No win

    async def play_slots(self, ctx, bet_amount: int):
        member_id = ctx.author.id
        current_cash = get_cash(member_id)  # Replace with your method to retrieve user's cash

        if bet_amount <= 0 or bet_amount > current_cash:
            embed = discord.Embed(title="Error!", description='Invalid bet amount.', color=error_color)
            embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
            await ctx.send(embed=embed)
            return

        remove_cash(member_id, bet_amount)

        result = self.spin()
        winnings = self.calculate_winnings(bet_amount, result)

        result_prompt = f"**Result:** {' '.join(result)}\n\n"

        if winnings > 0:
            self.add_cash(member_id, winnings)
            result_prompt += f"🎉  **Winner:**  🎉\n{ctx.author.mention} won {str(winnings)}!"
            color = discord.Color.green()
        else:
            result_prompt += "**No Winner :(**"
            color = error_color

        embed = discord.Embed(title="Slots Result", description=result_prompt, color=color)
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
        await ctx.send(embed=embed)

slots_game = SlotsGame()


@bot.command(name='slots')
@commands.cooldown(1, 86400, commands.BucketType.user)
async def slots(ctx, bet_amount: int):
    await slots_game.play_slots(ctx, bet_amount)

@slots.error
async def slots_error(ctx, error):
    traceback.print_exc()
    if isinstance(error, commands.CommandOnCooldown):
        embed = discord.Embed(
            title="Nuh uh!",
            description=f"You're going too fast. Try again in {error.retry_after // 3600} hours.",
            color=error_color
        )
        await ctx.send(embed=embed)
    elif isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(
            title="Error!",
            description='Please enter a valid bet amount between 100 and 1000.',
            color=error_color
        )
        await ctx.send(embed=embed)
        ctx.command.reset_cooldown(ctx)  # Reset cooldown for the command
    elif isinstance(error, commands.BadArgument):
        embed = discord.Embed(
            title="Error!",
            description='Please enter a valid numerical bet amount.',
            color=error_color
        )
        await ctx.send(embed=embed)
    else:
        # Default error handling
        embed = discord.Embed(
            title="Error!",
            description="Something went wrong.",
            color=error_color
        )
        await ctx.send(embed=embed)


#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
# PETS

@bot.command(name='adopt')
async def adopt_pet_command(ctx):
    try:
        # Fetch a random pet from PetStore
        pet = fetch_random_pet_from_store()

        if not pet:
            await ctx.send("No pets available in the PetStore.")
            return

        # Add pet to the user's Pets table
        member_id = ctx.author.id
        if adopt_pet(member_id, pet[1], pet[2], '2024-06-14', 'Newborn'):  # Replace with actual AdoptionDate and Level
            # Construct and send embed message
            embed = discord.Embed(title="Adopted Pet", description=f"You adopted {pet[1]}!", color=discord.Color.green())
            embed.set_thumbnail(url=pet[2])  # Set thumbnail to pet's image_url
            embed.add_field(name="Name", value=pet[1], inline=True)
            embed.add_field(name="Level", value='Newborn', inline=True) 
            embed.add_field(name="Adoption Date", value='2024-06-14', inline=False)  # Replace with actual AdoptionDate
 # Replace with actual Level

            await ctx.send(embed=embed)
        else:
            await ctx.send("Failed to add pet to your Pets. Please try again later.")

    except Exception as e:
        print("Error adopting pet:", e)
        await ctx.send("An error occurred while adopting the pet. Please try again later.")

@bot.command(name='renamepet')
async def rename_pet_command(ctx, current_name: str, new_name: str):
    try:
        member_id = ctx.author.id

        # Check if the user owns the pet with the current name
        connection = sqlite3.connect("eli.db")
        cursor = connection.cursor()

        cursor.execute("SELECT * FROM Pets WHERE MemberId = ? AND PetName = ?", (member_id, current_name))
        pet = cursor.fetchone()

        cursor.close()
        connection.close()

        if not pet:
            await ctx.send(f"You don't have a pet named {current_name}.")
            return

        # Rename the pet
        if rename_pet(member_id, current_name, new_name):
            await ctx.send(f"Successfully renamed your pet from {current_name} to {new_name}.")
        else:
            await ctx.send("Failed to rename your pet. Please try again later.")

    except Exception as e:
        print("Error renaming pet:", e)
        await ctx.send("An error occurred while renaming your pet. Please try again later.")

@bot.command(name='status')
async def pet_status(ctx):
    member_id = ctx.author.id
    pet_details = get_pet_details(member_id)

    if pet_details:
        pet_name = pet_details[2]  # Assuming PetName is the third column in the database
        pet_image_url = pet_details[4]  # Assuming image_url is the fifth column in the database
        pet_level = pet_details[6]  # Assuming Level is the seventh column in the database
        last_fed_date = pet_details[3]  # Assuming LastFedDate is the fourth column in the database

        embed = discord.Embed(title="Your Pet Status", description=f"Here's your pet **{pet_name}'s** status:", color=custom_color)
        embed.set_thumbnail(url=pet_image_url)
        embed.add_field(name="Name", value=pet_name, inline=True)
        embed.add_field(name="Level", value=pet_level, inline=True)
        embed.add_field(name="Last Fed Date", value=last_fed_date if last_fed_date else "Not fed yet", inline=False)

        await ctx.send(embed=embed)
    else:
        await ctx.send("You don't have a pet yet. Use `;adopt` to adopt a pet!")

@bot.command(name='feed')
async def feed_pet_command(ctx, pet_name: str):
    try:
        member_id = ctx.author.id

        connection = sqlite3.connect("eli.db")
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM Pets WHERE MemberId = ? AND PetName = ?", (member_id, pet_name))
        pet = cursor.fetchone()
        cursor.close()
        connection.close()

        if not pet:
            await ctx.send(f"You don't have a pet named {pet_name}.")
            return

        level = update_pet_feedings(member_id, pet_name)
        embed = discord.Embed(title="Feeding Time!", description=f'Thanks for feeding {pet_name}', color=custom_color)
        await ctx.send(embed = embed)

    except Exception as e:
        print("Error feeding pet:", e)
        await ctx.send("An error occurred while feeding your pet. Please try again later.")

@tasks.loop(hours=24)
async def daily_pet_check():
    check_pet_health()

@daily_pet_check.before_loop
async def before_daily_pet_check():
    await bot.wait_until_ready()


#
#
#
#
#
#
#

text_chat_users = {}

@bot.event
async def on_message(message):
    if bot.user.mentioned_in(message) and 'say hi' in message.content.lower():
        await message.channel.send("hi, i'm plum")

    minute_key = message.created_at.strftime("%Y-%m-%d %H:%M")
    if minute_key not in text_chat_users:
        text_chat_users[minute_key] = set()
    text_chat_users[minute_key].add(message.author.id)
    logging.info(f"User {message.author.id} sent a message at {minute_key}")

    await bot.process_commands(message)

# Background task to add XP for active users
@tasks.loop(minutes=1)
async def xp_for_chat():
    utc_now = datetime.now(pytz.utc)
    minute_key = (utc_now - timedelta(minutes=1)).strftime("%Y-%m-%d %H:%M")

    if minute_key in text_chat_users:
        for user_id in text_chat_users[minute_key]:
            xp_to_add_chat = random.randint(1, 5)
            add_xp(user_id, xp_to_add_chat)
            logging.info(f"Added {xp_to_add_chat} XP to user {user_id} for being active at {minute_key}")
        del text_chat_users[minute_key]
        logging.info(f"Processed and cleared active users for {minute_key}")
voice_channel_users = {}
# Dictionary to track user XP
user_xp = {}

# Set the desired timezone
timezone = pytz.timezone("America/New_York")

@bot.event
async def on_voice_state_update(member, before, after):
    current_time = datetime.now(tz=timezone)
    channel_before = before.channel
    channel_after = after.channel

    # User joined a voice channel
    if channel_before is None and channel_after is not None:
        if channel_after not in voice_channel_users:
            voice_channel_users[channel_after] = {}
        voice_channel_users[channel_after][member] = current_time
        print(f'{member} joined {channel_after} at {current_time}')
    
    # User left a voice channel
    elif channel_before is not None and channel_after is None:
        if channel_before in voice_channel_users and member in voice_channel_users[channel_before]:
            join_time = voice_channel_users[channel_before].pop(member)
            duration = current_time - join_time
            print(f'{member} left {channel_before} after {duration}')
            if not voice_channel_users[channel_before]:
                del voice_channel_users[channel_before]
    
    # User switched voice channels
    elif channel_before is not None and channel_after is not None:
        if channel_before in voice_channel_users and member in voice_channel_users[channel_before]:
            join_time = voice_channel_users[channel_before].pop(member)
            duration = current_time - join_time
            if not voice_channel_users[channel_before]:
                del voice_channel_users[channel_before]
        if channel_after not in voice_channel_users:
            voice_channel_users[channel_after] = {}
        voice_channel_users[channel_after][member] = current_time


@tasks.loop(minutes=3)
async def award_xp():
    current_time = datetime.now(tz=timezone)
    for channel, members in voice_channel_users.items():
        for member, join_time in members.items():
            duration = current_time - join_time
            xp_gained = random.randint(5, 10)
            add_xp(member.id, xp_gained)
            print(f'{member} earned {xp_gained} XP for being in {channel}')

@bot.command(name="Stats")
async def stats(ctx, member: discord.Member):
    current_time = datetime.now(tz=timezone)
    xp = user_xp.get(member.id, 0)
    for channel, members in voice_channel_users.items():
        if member in members:
            join_time = members[member]
            duration = current_time - join_time
            await ctx.send(f'{member.name} has been in {channel} for {duration.total_seconds()} seconds and has {xp} XP.')
            return
    await ctx.send(f'{member.name} is not currently in a voice channel and has {xp} XP.')

@bot.command()
async def active(ctx):
    active_users = []
    current_time = datetime.now(tz=timezone)
    for channel, members in voice_channel_users.items():
        user_durations = [
            f'{member.name} (for {(current_time - join_time).total_seconds()} seconds)'
            for member, join_time in members.items()
        ]
        active_users.append(f'**{channel}**: {", ".join(user_durations)}')
    if active_users:
        await ctx.send('\n'.join(active_users))
    else:
        await ctx.send('No users are currently in voice channels.')
 
 #
 #
 #
 #
 #
 #
 #
 
@bot.event
async def on_member_join(member):
    if not member.bot:  # Ignore bot accounts
        add_member(member.id)
        logging.info(f"Member {member.name} ({member.id}) has been added to the database on member join event.")


@bot.event
async def on_ready():
    print(f'Ready! Logged in as {bot.user}')

    xp_for_chat.start()
    award_xp.start()

    activity = discord.Activity(type=discord.ActivityType.watching, name="Eli crying, screaming and sobbing")
    await bot.change_presence(activity=activity)

    for guild in bot.guilds:
        for member in guild.members:
            if not member.bot:  # Ignore bot accounts
                add_member(member.id)
                logging.info(f"Adding member {member.id} on ready event.")
    print("All members have been added to the database.")



initialize_database()

# Start the bot
bot.run(TOKEN) 
