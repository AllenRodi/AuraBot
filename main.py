import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from config import GUILD_ID  # Import GUILD_ID
import asyncio

# Load environment variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

class AuraBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True  # Allows AuraBot to read message content

        # Initialize the bot with a command prefix and intents
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # Dynamically load all cogs
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                try:
                    await self.load_extension(f'cogs.{filename[:-3]}')
                    print(f"Successfully loaded cog: {filename[:-3]}")
                except Exception as e:
                    print(f"Failed to load cog {filename[:-3]}: {e}")

        # Sync commands
        try:
            if GUILD_ID:
                guild = discord.Object(id=GUILD_ID)
                await self.tree.clear_commands(guild=guild)
                synced = await self.tree.sync(guild=guild)
                print(f"Cleared and resynced {len(synced)} commands to guild {GUILD_ID}")
            else:
                print("GUILD_ID is not set. Falling back to global commands.")
                synced = await self.tree.sync()
                print(f"Synced {len(synced)} global commands.")
            print(f"Commands registered in tree: {[cmd.name for cmd in synced]}")
        except Exception as e:
            print(f"Error syncing commands: {e}")

    async def on_ready(self):
        print(f'{self.user} is logged in and active! Wassup! Wassup! Wassup!')

# Initialize and run the bot
async def main():
    aurabot = AuraBot()
    async with aurabot:
        await aurabot.start(TOKEN)

if __name__ == '__main__':
    asyncio.run(main())
