import discord
from discord.ext import commands
from pymongo import MongoClient
from dotenv import load_dotenv
import os
from config import GUILD_ID

# Load environment variables
load_dotenv()

class HabitTracking(commands.Cog):
    """Cog for tracking user habits."""

    def __init__(self, aurabot):
        self.aurabot = aurabot

        # MongoDB setup
        mongo_url = os.getenv("MONGO_URL")
        if not mongo_url:
            raise ValueError("MongoDB connection string is not set in .env")

        # Establish MongoDB connection
        self.cluster = MongoClient(mongo_url)
        self.db = self.cluster["AuraBotDB"]
        self.collection = self.db["habit_tracking"]

        # Debugging: Check MongoDB connection
        print("Connected to MongoDB for habit tracking!")
        print("Existing collections:", self.db.list_collection_names())

    async def cog_load(self):
        """Register commands when the cog is loaded."""
        guild = discord.Object(id=GUILD_ID)  # Ensure GUILD_ID is correct
        self.aurabot.tree.add_command(self.add_habit, guild=guild)
        self.aurabot.tree.add_command(self.view_habits, guild=guild)
        self.aurabot.tree.add_command(self.clear_habits, guild=guild)

    @discord.app_commands.command(name="addhabit", description="Add a habit to track.")
    async def add_habit(self, interaction: discord.Interaction, habit: str):
        """Handles /addhabit command."""
        user_id = interaction.user.id
        user_data = self.collection.find_one({"_id": user_id})

        if user_data:
            self.collection.update_one({"_id": user_id}, {"$addToSet": {"habits": habit}})
            await interaction.response.send_message(f"Habit `{habit}` added to your tracking list.")
        else:
            self.collection.insert_one({"_id": user_id, "habits": [habit]})
            await interaction.response.send_message(f"Habit `{habit}` added to a new tracking list.")

    @discord.app_commands.command(name="viewhabits", description="View your tracked habits.")
    async def view_habits(self, interaction: discord.Interaction):
        """Handles /viewhabits command."""
        user_id = interaction.user.id
        user_data = self.collection.find_one({"_id": user_id})

        if user_data and "habits" in user_data:
            habits = user_data["habits"]
            if habits:
                await interaction.response.send_message("Your tracked habits:\n- " + "\n- ".join(habits))
            else:
                await interaction.response.send_message("You don't have any tracked habits yet.")
        else:
            await interaction.response.send_message("You don't have any tracked habits yet.")

    @discord.app_commands.command(name="clearhabits", description="Clear all your tracked habits.")
    async def clear_habits(self, interaction: discord.Interaction):
        """Handles /clearhabits command."""
        user_id = interaction.user.id
        result = self.collection.delete_one({"_id": user_id})

        if result.deleted_count > 0:
            await interaction.response.send_message("All your tracked habits have been cleared.")
        else:
            await interaction.response.send_message("You have no habits to clear.")

# Required setup function
async def setup(aurabot):
    await aurabot.add_cog(HabitTracking(aurabot))
    print("HabitTracking cog successfully added!")
