import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

# load .env file if present
load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

# You can customize the command prefix
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())


async def load_cogs():
    """Load all cogs from the cogs folder."""
    for filename in os.listdir("cogs"):
        if filename.endswith(".py"):
            await bot.load_extension(f"cogs.{filename[:-3]}")
            print(f"Cog loaded: {filename[:-3]}")


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("------")
    
    # Synchronize slash commands with Discord
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash commands")
    except Exception as e:
        print(f"Failed to sync slash commands: {e}")


@bot.command(name="ping")
async def ping(ctx):
    """A simple ping command."""
    await ctx.send("Pong!")


async def main():
    """Start the bot."""
    async with bot:
        await load_cogs()
        await bot.start(TOKEN)


if __name__ == "__main__":
    if TOKEN is None:
        print("Error: DISCORD_TOKEN environment variable not set.\n"
              "Create a .env file or set the variable in your environment.")
    else:
        import asyncio
        asyncio.run(main())
