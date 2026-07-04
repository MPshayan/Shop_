import discord
from discord.ext import commands
import os
import sqlite3
from datetime import datetime

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ================= DATABASE =================
conn = sqlite3.connect("shop.db")
c = conn.cursor()

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

c.execute("""
CREATE TABLE IF NOT EXISTS wallet (
    user TEXT PRIMARY KEY,
    balance INTEGER DEFAULT 0
)
""")

conn.commit()

# ================= CONFIG =================
LOG_CHANNEL_ID = 1522694424180555899

# ================= HELPERS =================
def get_balance(user):
    c.execute("SELECT balance FROM wallet WHERE user=?", (user,))
    r = c.fetchone()

    if r:
        return r[0]

    c.execute("INSERT INTO wallet (user, balance) VALUES (?, ?)", (user, 0))
    conn.commit()
    return 0


async def send_log(guild, text):
    try:
        ch = guild.get_channel(LOG_CHANNEL_ID)
        if ch:
            await ch.send(text)
    except:
        pass


# ================= INIT PRODUCTS =================
def init_products():
    c.execute("SELECT COUNT(*) FROM products")
    if c.fetchone()[0] == 0:
        c.executemany("""
        INSERT INTO products VALUES (?,?,?)
        """, [
            ("1", "Sandwich", 2000),
            ("2", "Taco", 1500),
            ("3", "Burger", 2200),
            ("4", "Donut", 1500),
            ("5", "Cookie", 1500),
            ("6", "Hotdog", 2000),
            ("7", "Pancake", 1500),
            ("8", "Softdrink", 2200),
            ("9", "Water", 1500),
        ])
        conn.commit()

init_products()

# ================= READY =================
@bot.event
async def on_ready():
    print(f"✅ Yakuza Shop Online as {bot.user}")

# ================= WALLET =================
@bot.command()
async def balance(ctx, user: str = None):
    user = user or ctx.author.name
    bal = get_balance(user)
    await ctx.send(f"💰 {user} Balance: {bal:,}")


@bot.command()
async def addmoney(ctx, user: str, amount: int):
    if not ctx.author.guild_permissions.administrator:
        return await ctx.send("❌ No permission")

    bal = get_balance(user)
    new = bal + amount

    c.execute("UPDATE wallet SET balance=? WHERE user=?", (new, user))
    conn.commit()

    await ctx.send(f"✅ +{amount:,} added to {user}")


@bot.command()
async def removemoney(ctx, user: str, amount: int):
    if not ctx.author.guild_permissions.administrator:
        return await ctx.send("❌ No permission")

    bal = get_balance(user)
    new = max(0, bal - amount)

    c.execute("UPDATE wallet SET balance=? WHERE user=?", (new, user))
    conn.commit()

    await ctx.send(f"❌ -{amount:,} removed from {user}")


@bot.command()
async def resetmoney(ctx, user: str):
    if not ctx.author.guild_permissions.administrator:
        return await ctx.send("❌ No permission")

    c.execute("UPDATE wallet SET balance=0 WHERE user=?", (user,))
    conn.commit()

    await ctx.send(f"♻️ {user} reset done")

# ================= SHOP =================
@bot.command()
async def shop(ctx):
    c.execute("SELECT * FROM products")
    items = c.fetchall()

    msg = "🛒 Yakuza Shop:\n\n"
    for i in items:
        msg += f"{i[0]}. {i[1]} - {i[2]:,}\n"

    await ctx.send(msg)


@bot.command()
async def buy(ctx, item_id, amount: int):
    c.execute("SELECT name, price FROM products WHERE id=?", (item_id,))
    item = c.fetchone()

    if not item:
        return await ctx.send("❌ Item not found")

    total = item[1] * amount
    user = ctx.author.name

    bal = get_balance(user)
    if bal < total:
        return await ctx.send("❌ Not enough money")

    new_bal = bal - total

    c.execute("UPDATE wallet SET balance=? WHERE user=?", (new_bal, user))

    c.execute("""
    INSERT INTO orders (user, item, amount, total)
    VALUES (?,?,?,?)
    """, (user, item[0], amount, total))

    conn.commit()

    await ctx.send(
        f"✅ {user} bought {amount}x {item[0]}\n💰 {total:,}"
    )

    await send_log(ctx.guild,
        f"🛒 ORDER\nUser: {user}\nItem: {item[0]}\nTotal: {total:,}\nTime: {datetime.now()}"
    )

# ================= HISTORY =================
@bot.command()
async def history(ctx, user: str):
    c.execute("SELECT item, amount, total FROM orders WHERE user=?", (user,))
    data = c.fetchall()

    if not data:
        return await ctx.send("❌ No history")

    msg = f"📜 History of {user}\n\n"
    total = 0

    for d in data:
        msg += f"{d[1]}x {d[0]} = {d[2]:,}\n"
        total += d[2]

    msg += f"\n💰 Total: {total:,}"

    await ctx.send(msg)

# ================= REPORT =================
@bot.command()
async def report(ctx):
    if not ctx.author.guild_permissions.administrator:
        return await ctx.send("❌ No permission")

    c.execute("SELECT user, SUM(total) FROM orders GROUP BY user")
    data = c.fetchall()

    msg = "📊 REPORT\n\n"
    for d in data:
        msg += f"{d[0]} → {d[1]:,}\n"

    await ctx.send(msg)

# ================= NICK =================
@bot.command()
async def nick(ctx, member: discord.Member, *, name):
    if not ctx.author.guild_permissions.administrator:
        return await ctx.send("❌ No permission")

    await member.edit(nick=name)
    await ctx.send(f"✏️ Nick changed to {name}")

# ================= TXT =================
@bot.command()
async def txt(ctx, *, text):
    await ctx.message.delete()
    await ctx.send(f"{text}\n\n━━━━━━━━━━\nSend By {ctx.author.name}")

# ================= HELP (FIXED) =================
@bot.command(name="helpp")
async def help_command(ctx):
    msg = """
📖 YAKUZA SHOP HELP

🛒 SHOP
!shop
!buy <id> <amount>

💰 WALLET
!balance
!addmoney
!removemoney
!resetmoney

📜 INFO
!history
!report

👑 ADMIN
!nick @user name
!txt message

━━━━━━━━━━
Yakuza Shop System
"""
    await ctx.send(msg)

# ================= RUN =================
bot.run(os.getenv("TOKEN"))
