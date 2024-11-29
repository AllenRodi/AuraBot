import discord
from discord.ext import commands
from pymongo import MongoClient
from dotenv import load_dotenv
import os
from config import GUILD_ID

# Load environment variables
load_dotenv()

class CreateProfile(commands.Cog):
    """Cog for creating user profiles and storing them in MongoDB."""

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

        # Debugging: Check MongoDB connection
        print("Connected to MongoDB for CreateProfile!")
        print("Existing collections:", self.db.list_collection_names())

    async def cog_load(self):
        """Register commands when the cog is loaded."""
        guild = discord.Object(id=GUILD_ID)  # Ensure GUILD_ID is correct
        self.aurabot.tree.add_command(self.create_profile, guild=guild)

    @discord.app_commands.command(name="createprofile", description="Create your profile using your Discord username.")
    async def create_profile(self, interaction: discord.Interaction):
        """Handles the /createprofile command."""
        user_id = interaction.user.id
        username = interaction.user.display_name  # Get the user's Discord username

        # Check if the user already has a profile
        existing_profile = self.collection.find_one({"_id": user_id})

        if existing_profile:
            # If profile exists, show the existing username
            existing_username = existing_profile.get("username", "No username set.")
            await interaction.response.send_message(f"You already have a profile with the username: **{existing_username}**")
        else:
            # Create a new profile with the username
            self.collection.insert_one({"_id": user_id, "username": username})
            await interaction.response.send_message(f"Your profile has been created with your username: **{username}**")

# Required setup function
async def setup(aurabot):
    await aurabot.add_cog(CreateProfile(aurabot))
