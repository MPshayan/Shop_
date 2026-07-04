import discord
from discord.ext import commands
import os

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# دیتای ساده (فعلاً داخل رم)
products = {
    "nitro": "Discord Nitro - 10$",
    "boost": "Server Boost - 3$"
}

orders = []

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    
@bot.command()
async def kir(ctx):
    await ctx.send("تو کونت")
# 📦 لیست محصولات
@bot.command()
async def shop(ctx):
    msg = "**🛒 Yakuza Shop Products:**\n"
    for k, v in products.items():
        msg += f"🔹 {k} → {v}\n"
    await ctx.send(msg)

# 🛒 ثبت سفارش
@bot.command()
async def order(ctx, item):
    if item in products:
        orders.append((ctx.author.name, item))
        await ctx.send(f"✅ سفارش ثبت شد: {item}")
    else:
        await ctx.send("❌ این محصول وجود ندارد")

# 📊 دیدن سفارش‌ها (فقط استاف)
@bot.command()
async def orders_list(ctx):
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("❌ دسترسی نداری")
        return

    if not orders:
        await ctx.send("هیچ سفارشی نیست")
        return

    msg = "**📦 Orders:**\n"
    for o in orders:
        msg += f"👤 {o[0]} → {o[1]}\n"

    await ctx.send(msg)

# ➕ اضافه کردن محصول (استاف)
@bot.command()
async def add(ctx, name, price):
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("❌ دسترسی نداری")
        return

    products[name] = price
    await ctx.send(f"✅ اضافه شد: {name} - {price}")

bot.run(os.getenv("TOKEN"))
