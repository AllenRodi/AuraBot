import asyncio
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
        print("Connected to MongoDB!")
        print("Existing collections:", self.db.list_collection_names())

    async def cog_load(self):
        """Register commands when the cog is loaded."""
        guild = discord.Object(id=GUILD_ID)  # Ensure GUILD_ID is correct
        self.aurabot.tree.add_command(self.create_profile, guild=guild)
        self.aurabot.tree.add_command(self.view_profile, guild=guild)
        print("Registered /createprofile and /viewprofile commands.")

    @discord.app_commands.command(name="createprofile", description="Create your user profile")
    async def create_profile(self, interaction: discord.Interaction):
        """Handles the /createprofile command."""
        await interaction.response.send_message("Please provide your profile bio:")

        # Wait for the user's response
        try:
            user_message = await self.aurabot.wait_for(
                "message",
                check=lambda m: m.author == interaction.user and m.channel == interaction.channel,
                timeout=600  # 10 minutes timeout
            )
        except asyncio.TimeoutError:
            await interaction.followup.send("You took too long to respond. Try again later.")
            return

        # Store the profile in MongoDB
        user_id = interaction.user.id
        bio = user_message.content

        # Check if the user already has a profile
        existing_profile = self.collection.find_one({"_id": user_id})
        if existing_profile:
            self.collection.update_one({"_id": user_id}, {"$set": {"bio": bio}})
            await interaction.followup.send("Your profile bio has been updated.")
        else:
            self.collection.insert_one({"_id": user_id, "bio": bio})
            await interaction.followup.send("Your profile has been created!")

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
    await aurabot.add_cog(CreateProfile(aurabot))
