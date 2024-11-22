import discord
from discord.ext import commands
from pymongo import MongoClient
from dotenv import load_dotenv
import os
from config import GUILD_ID

# Load environment variables
load_dotenv()

class MoodLogging(commands.Cog):
    """Cog for logging user moods."""

    def __init__(self, aurabot):
        self.aurabot = aurabot

        # MongoDB setup
        mongo_url = os.getenv("MONGO_URL")
        if not mongo_url:
            raise ValueError("MongoDB connection string is not set in .env")

        # Establish MongoDB connection
        self.cluster = MongoClient(mongo_url)
        self.db = self.cluster["AuraBotDB"]
        self.collection = self.db["mood_logging"]

        # Debugging: Check MongoDB connection
        print("Connected to MongoDB for mood logging!")
        print("Existing collections:", self.db.list_collection_names())

    async def cog_load(self):
        """Register commands when the cog is loaded."""
        guild = discord.Object(id=GUILD_ID)  # Ensure GUILD_ID is correct
        self.aurabot.tree.add_command(self.log_mood, guild=guild)
        self.aurabot.tree.add_command(self.view_moods, guild=guild)

    @discord.app_commands.command(name="logmood", description="Log your mood for the day.")
    async def log_mood(self, interaction: discord.Interaction, mood: str):
        """Handles /logmood command."""
        user_id = interaction.user.id
        user_data = self.collection.find_one({"_id": user_id})

        if not user_data:
            # If user doesn't exist, create a new profile with the first mood entry
            self.collection.insert_one({"_id": user_id, "moods": [{"mood": mood, "timestamp": interaction.created_at}]})
            await interaction.response.send_message(f"Your mood `{mood}` has been logged!")
        else:
            # Append the new mood entry to the existing profile
            self.collection.update_one(
                {"_id": user_id},
                {"$push": {"moods": {"mood": mood, "timestamp": interaction.created_at}}}
            )
            await interaction.response.send_message(f"Your mood `{mood}` has been logged!")

    @discord.app_commands.command(name="viewmoods", description="View your logged moods.")
    async def view_moods(self, interaction: discord.Interaction):
        """Handles /viewmoods command."""
        user_id = interaction.user.id
        user_data = self.collection.find_one({"_id": user_id})

        if user_data and "moods" in user_data:
            moods = user_data["moods"]
            if moods:
                mood_list = "\n".join(
                    [f"- {entry['mood']} (logged at {entry['timestamp'].strftime('%Y-%m-%d %H:%M:%S')})" for entry in moods]
                )
                await interaction.response.send_message(f"Your logged moods:\n{mood_list}")
            else:
                await interaction.response.send_message("You haven't logged any moods yet.")
        else:
            await interaction.response.send_message("You haven't logged any moods yet.")

# Required setup function
async def setup(aurabot):
    await aurabot.add_cog(MoodLogging(aurabot))
    print("MoodLogging cog successfully added!")

