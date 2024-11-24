import discord
from discord.ext import commands
from pymongo import MongoClient
from dotenv import load_dotenv
import os
from config import GUILD_ID

# Load environment variables
load_dotenv()

class GoalTracking(commands.Cog):
    """Cog for tracking user goals."""

    def __init__(self, aurabot):
        self.aurabot = aurabot

        # MongoDB setup
        mongo_url = os.getenv("MONGO_URL")
        if not mongo_url:
            raise ValueError("MongoDB connection string is not set in .env")

        # Establish MongoDB connection
        self.cluster = MongoClient(mongo_url)
        self.db = self.cluster["AuraBotDB"]
        self.collection = self.db["goal_tracking"]

        # Debugging: Check MongoDB connection
        print("Connected to MongoDB for goal tracking!")
        print("Existing collections:", self.db.list_collection_names())

    async def cog_load(self):
        """Register commands when the cog is loaded."""
        guild = discord.Object(id=GUILD_ID)  # Ensure GUILD_ID is correct
        self.aurabot.tree.add_command(self.add_goal, guild=guild)
        self.aurabot.tree.add_command(self.view_goals, guild=guild)
        self.aurabot.tree.add_command(self.clear_goals, guild=guild)

    @discord.app_commands.command(name="addgoal", description="Add a goal to track.")
    async def add_goal(self, interaction: discord.Interaction, goal: str):
        """Handles /addgoal command."""
        user_id = interaction.user.id
        user_data = self.collection.find_one({"_id": user_id})

        if user_data:
            self.collection.update_one({"_id": user_id}, {"$addToSet": {"goals": goal}})
            await interaction.response.send_message(f"Goal `{goal}` added to your tracking list.")
        else:
            self.collection.insert_one({"_id": user_id, "goals": [goal]})
            await interaction.response.send_message(f"Goal `{goal}` added to a new tracking list.")

    @discord.app_commands.command(name="viewgoals", description="View your tracked goals.")
    async def view_goals(self, interaction: discord.Interaction):
        """Handles /viewgoals command."""
        user_id = interaction.user.id
        user_data = self.collection.find_one({"_id": user_id})

        if user_data and "goals" in user_data:
            goals = user_data["goals"]
            if goals:
                await interaction.response.send_message("Your tracked goals:\n- " + "\n- ".join(goals))
            else:
                await interaction.response.send_message("You don't have any tracked goals yet.")
        else:
            await interaction.response.send_message("You don't have any tracked goals yet.")

    @discord.app_commands.command(name="cleargoals", description="Clear all your tracked goals.")
    async def clear_goals(self, interaction: discord.Interaction):
        """Handles /cleargoals command."""
        user_id = interaction.user.id
        result = self.collection.delete_one({"_id": user_id})

        if result.deleted_count > 0:
            await interaction.response.send_message("All your tracked goals have been cleared.")
        else:
            await interaction.response.send_message("You have no goals to clear.")

# Required setup function
async def setup(aurabot):
    await aurabot.add_cog(GoalTracking(aurabot))
    print("GoalTracking cog successfully added!")
