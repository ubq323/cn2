import os, sys 
import discord
from discord.ext import commands

from fractions import Fraction

import logging
logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s [%(name)s] %(message)s")
logger = logging.getLogger("cn15 bot")

import sqlite3
db = sqlite3.connect("database.db")
db.row_factory = sqlite3.Row 

migrations = [
	"create table players ( discord_id text primary key, wp_num int default 0, wp_den int default 1 );",
]

def player_exists(d_id):
    row = db.execute("select 1 from players where discord_id = ?;", (d_id,)).fetchone()
    return row is not None 

cur_ver = db.execute("pragma user_version;").fetchone()[0]
print(cur_ver)
for idx,m in enumerate(migrations[cur_ver:]):
    db.execute(m)
db.execute(f"pragma user_version = {len(migrations)};")

bot = commands.Bot("£")

@bot.event
async def on_ready():
    logger.info("pain")

@bot.command()
async def ping(ctx):
    await ctx.send("pong")

@bot.group(invoke_without_command=True)
async def wp(ctx, who: discord.Member = None):
    """Get WP of player."""
    if who is None:
        who = ctx.author
    d_id = who.id
    row = db.execute("select wp_num, wp_den from players where discord_id = ?;", (d_id,)).fetchone()
    if row is None:
        await ctx.send("i do not have any records of that player")
    else:
        num = row["wp_num"]
        den = row["wp_den"]
        wp = Fraction(num,den)
        await ctx.send(f"wp of {who.display_name} is {wp}")

@wp.command()
async def add(ctx, who: discord.Member, delta: Fraction):
    """Change player's WP by given amount"""
    row = db.execute("select wp_num, wp_den from players where discord_id = ?;", (who.id,)).fetchone()
    if row is None:
        return await ctx.send("i do not have any records of that player")
    num = row["wp_num"]
    den = row["wp_den"]
    old = Fraction(num,den)
    new = old + delta
    db.execute("update players set wp_num = ?, wp_den = ? where discord_id = ?;",(new.numerator,new.denominator,who.id))
    db.commit()
    await ctx.send(f"updated {who.display_name}'s WP by {delta} from {old} to {new}")
    
    
@wp.command(name="set")
async def set_(ctx, who: discord.Member, val: Fraction):
    """Set player's WP to a given value"""
    if not player_exists(who.id):
        return await ctx.send("i do not have any records of that player")
    db.execute("update players set wp_num = ?, wp_den = ? where discord_id = ?;",(val.numerator,val.denominator,who.id))
    db.commit()
    await ctx.send(f"set {who.display_name}'s WP to {val}")

@bot.group(invoke_without_command=True)
async def player():
    pass

@player.command()
async def exists(ctx, who:discord.Member):
    if player_exists(who.id):
        await ctx.send(f"{who.display_name} exists")
    else:
        await ctx.send(f"{who.display_name} does not exist")

@player.command()
async def create(ctx, who: discord.Member):
    if player_exists(who.id):
        return await ctx.send("that player already exists!")
    db.execute("insert into players (discord_id) values (?);", (who.id,))
    db.commit()
    await ctx.send(f"{who.display_name} was created")
    
    

if __name__ == "__main__":
    token = os.getenv("TOKEN", None)
    if token is None:
        sys.exit("set envvar TOKEN")
    else:
        bot.run(token.strip())
        
