import discord
from discord.ext import commands
import random
import asyncio
from eliDb import adopt_pet, rename_pet, fetch_random_pet_from_store, get_pet_details
import sqlite3

intents = discord.Intents.default()
intents.guilds = True
intents.messages = True
intents.voice_states = True
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix=';', intents=intents)
error_color = discord.Color.from_rgb(204, 0, 0)

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

        embed = discord.Embed(title="Your Pet Status", description=f"Here's your pet {pet_name}'s status:", color=discord.Color.blue())
        embed.set_thumbnail(url=pet_image_url)
        embed.add_field(name="Name", value=pet_name, inline=True)
        embed.add_field(name="Level", value=pet_level, inline=True)
        embed.add_field(name="Last Fed Date", value=last_fed_date if last_fed_date else "Not fed yet", inline=False)

        await ctx.send(embed=embed)
    else:
        await ctx.send("You don't have a pet yet. Use `;adopt` to adopt a pet!")

bot.run('MTI0MTc0NTU5ODg2NDk1MzM0NA.GLA-hF.GmiGVIDzpkicuSuCaY0XCaH8yNhosaVz4LoedA')
