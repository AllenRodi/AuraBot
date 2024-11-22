import discord
from discord.ext import commands
from pymongo import MongoClient
from dotenv import load_dotenv
import os
from config import GUILD_ID

# Load environment variables
load_dotenv()

class ViewProfile(commands.Cog):
    """Cog for viewing user profiles stored in MongoDB."""

    def __init__(self, aurabot):
        self.aurabot = aurabot

        # MongoDB setup
        mongo_url = os.getenv("MONGO_URL")  # Securely load the connection string
        if not mongo_url:
            raise ValueError("MongoDB connection string is not set in .env")

        # Establish MongoDB connection
        self.cluster = MongoClient(mongo_url)
        self.db = self.cluster["AuraBotDB"]  # Replace with your database name
        self.collection = self.db["user_profiles"]

    async def cog_load(self):
        """Register commands when the cog is loaded."""
        guild = discord.Object(id=GUILD_ID)  # Ensure GUILD_ID is correct
        self.aurabot.tree.add_command(self.view_profile, guild=guild)

    @discord.app_commands.command(name="viewprofile", description="View your profile bio")
    async def view_profile(self, interaction: discord.Interaction):
        """Handles the /viewprofile command."""
        user_id = interaction.user.id
        profile = self.collection.find_one({"_id": user_id})

        if profile:
            await interaction.response.send_message(f"Here is your profile bio:\n{profile['bio']}")
        else:
            await interaction.response.send_message("You don't have a profile yet! Use /createprofile to create one.")

# Required setup function
async def setup(aurabot):
    await aurabot.add_cog(ViewProfile(aurabot))
