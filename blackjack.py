import discord
from discord.ext import commands
import random
import asyncio
from eliDb import add_cash, remove_cash, get_cash

intents = discord.Intents.default()
intents.guilds = True
intents.messages = True
intents.voice_states = True
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix=';', intents=intents)
error_color = discord.Color.from_rgb(204, 0, 0)


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
        current_cash = 1000  # Replace with your method to retrieve user's cash

        if bet_amount <= 0 or bet_amount > current_cash:
            embed = discord.Embed(title="Error!", description='Invalid bet amount.', color=error_color)
            embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
            await ctx.send(embed=embed)
            return

        self.remove_cash(member_id, bet_amount)

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

    def remove_cash(self, member_id, amount):
        # Implement your logic to remove cash from user's balance
        pass

    def add_cash(self, member_id, amount):
        # Implement your logic to add cash to user's balance
        pass

slots_game = SlotsGame()


@bot.command(name='slots')
@commands.cooldown(1, 86400, commands.BucketType.user)
async def slots(ctx, bet_amount: int):
    await slots_game.play_slots(ctx, bet_amount)

@slots.error
async def slots_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        retry_after = round(error.retry_after / 3600, 2)
        embed = discord.Embed(
            title="Nuh uh!",
            description=f"You're going too fast. Try again in {retry_after} hours.",
            color=error_color
        )
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
        await ctx.send(embed=embed)
    elif isinstance(error, commands.BadArgument) or isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(title="Error!", description='Invalid arguments.', color=error_color)
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
        await ctx.send(embed=embed)

bot.run('MTI0MTc0NTU5ODg2NDk1MzM0NA.GLA-hF.GmiGVIDzpkicuSuCaY0XCaH8yNhosaVz4LoedA')
