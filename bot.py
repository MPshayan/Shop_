import discord
from discord.ext import commands
import os
import sqlite3

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# 🧠 دیتابیس
conn = sqlite3.connect("shop.db")
c = conn.cursor()

# ساخت جدول‌ها
c.execute("""
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user TEXT,
    item TEXT,
    amount INTEGER,
    total INTEGER
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS products (
    id TEXT PRIMARY KEY,
    name TEXT,
    price INTEGER
)
""")

conn.commit()

# 🛒 اگر خالی بود، محصولات پیشفرض
def init_products():
    c.execute("SELECT COUNT(*) FROM products")
    if c.fetchone()[0] == 0:
        c.executemany("""
        INSERT INTO products VALUES (?,?,?)
        """, [
            ("1", "Item One", 50000),
            ("2", "Item Two", 100000),
            ("3", "Item Three", 25000),
        ])
        conn.commit()

init_products()

# -----------------------
@bot.event
async def on_ready():
    print(f"Yakuza Shop Online as {bot.user}")

# -----------------------
# 🛒 نمایش محصولات
# -----------------------
@bot.command()
async def shop(ctx):
    c.execute("SELECT * FROM products")
    items = c.fetchall()

    msg = "🛒 Yakuza Shop:\n\n"
    for i in items:
        msg += f"{i[0]}. {i[1]} - {i[2]:,}\n"

    await ctx.send(msg)

# -----------------------
# 🛒 خرید
# -----------------------
@bot.command()
async def buy(ctx, item_id, amount: int):

    c.execute("SELECT name, price FROM products WHERE id=?", (item_id,))
    item = c.fetchone()

    if not item:
        await ctx.send("❌ آیتم وجود ندارد")
        return

    total = item[1] * amount
    user = ctx.author.name

    c.execute("""
    INSERT INTO orders (user, item, amount, total)
    VALUES (?,?,?,?)
    """, (user, item[0], amount, total))

    conn.commit()

    await ctx.send(
        f"✅ {user} خرید کرد:\n"
        f"{amount}x {item[0]}\n"
        f"💰 {total:,}"
    )

# -----------------------
# 📜 تاریخچه
# -----------------------
@bot.command()
async def history(ctx, user: str):

    c.execute("SELECT item, amount, total FROM orders WHERE user=?", (user,))
    data = c.fetchall()

    if not data:
        await ctx.send("❌ هیچ خریدی پیدا نشد")
        return

    msg = f"📜 History of {user}:\n\n"
    total_all = 0

    for d in data:
        msg += f"🛒 {d[1]}x {d[0]} = {d[2]:,}\n"
        total_all += d[2]

    msg += f"\n💰 Total: {total_all:,}"

    await ctx.send(msg)

# -----------------------
# 📊 گزارش ادمین
# -----------------------
@bot.command()
async def report(ctx):

    if not ctx.author.guild_permissions.administrator:
        await ctx.send("❌ دسترسی نداری")
        return

    c.execute("SELECT user, SUM(total) FROM orders GROUP BY user")
    data = c.fetchall()

    msg = "📊 SHOP REPORT:\n\n"

    for d in data:
        msg += f"👤 {d[0]} → {d[1]:,}\n"

    await ctx.send(msg)

# -----------------------
bot.run(os.getenv("TOKEN"))
