import discord # loads Discord libraries
from discord.ext import commands # allows command prefix !
from discord import app_commands # allows command prefix /
from typing import Final
import os
from dotenv import load_dotenv


load_dotenv()
TOKEN: Final[str] = os.getenv('DISCORD_TOKEN')

class AuraBot(commands.Bot):     
    async def on_ready(self): # runs when AuraBot successfully connects to server
        print(f'{self.user} is logged in and active! Wassup! Wassup! Wassup!')
        
        # syncs commands to Discord
        try: 
            guild = discord.Object(id = 1306495714138001489)
            synced = await self.tree.sync(guild = guild)
            print(f'Synced {len(synced)} commands to guild {guild.id}')
        
        except Exception as e:
            print(f'Error syncing commands: {e}')
        
    async def on_message(self, message): # when a message is called on server, this function is called
        if message.author == self.user: # prevents Aurabot from replying to itself
            return
        
        if message.content.startswith('Hi!'): # if a user send "Hi!", AuraBot responds
            await message.channel.send(f'Hi {message.author}')
        

# allows Aurabot to listen to events it has access to 
intents = discord.Intents.default()
intents.message_content = True
aurabot = AuraBot(command_prefix = "!", intents = intents) # aurabot object

GUILD_ID = discord.Object(id = 1306495714138001489) # development mode for Discord

# commands aurabot can handle when a user types / in chat (name = 'must be all lowercase')

# /wassup - AuraBot says 'Wassup!' three times
@aurabot.tree.command(name = 'wassup', description = "Say Wassup! x3", guild = GUILD_ID) 
async def sayWassup(interaction: discord.Interaction):
    await interaction.response.send_message("Wassup! Wassup! Wassup!")

# /parrot - AuraBot repeats user input
@aurabot.tree.command(name = 'parrot', description = "Repeats user input", guild = GUILD_ID) 
async def repeat(interaction: discord.Interaction, repeat: str):
    await interaction.response.send_message(repeat)
    
for filename in os.listdir('./functions'):
        if filename.endswith('.py'):
            aurabot.load_extension(f'functions.{filename[:-3]}')
    

# connects code to Discord bot -- .env is not pushed for security
aurabot.run(TOKEN) # after this

# run in terminal (make sure you are in AuraBot directory): python main.py 
# check Discord server to see if AuraBot is online
        