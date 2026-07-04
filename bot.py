import discord
from discord.ext import commands
import os

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

# تست
@bot.command()
async def ping(ctx):
    await ctx.send("🏓 Pong!")

# سلام
@bot.command()
async def hello(ctx):
    await ctx.send(f"سلام {ctx.author.name} 👋")

bot.run(os.getenv("TOKEN"))