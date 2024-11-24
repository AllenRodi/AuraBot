import discord
from discord.ext import commands
from pymongo import MongoClient
from dotenv import load_dotenv
import os
from config import GUILD_ID

# Load environment variables
load_dotenv()

class ViewGoal(commands.Cog):
    """Cog for viewing user goals stored in MongoDB."""

    def __init__(self, aurabot):
        self.aurabot = aurabot

        # MongoDB setup
        mongo_url = os.getenv("MONGO_URL")  # Ensure connection string is in .env
        if not mongo_url:
            raise ValueError("MongoDB connection string is not set in .env")

        self.cluster = MongoClient(mongo_url)
        self.db = self.cluster["AuraBotDB"]  # Replace with your database name
        self.collection = self.db["user_goals"]  # Goals collection

    async def cog_load(self):
        """Register the /viewgoal command when the cog is loaded."""
        guild = discord.Object(id=GUILD_ID)
        self.aurabot.tree.add_command(self.view_goals, guild=guild)

    @discord.app_commands.command(name="viewgoals", description="View your personal goals")
    async def view_goals(self, interaction: discord.Interaction):
        """Handles the /viewgoals command."""
        user_id = interaction.user.id
        goals = self.collection.find({"_id": user_id})

        if goals.count() > 0:
            # Build a list of user goals
            goal_list = "\n".join([f"- {goal['goal']}" for goal in goals])
            await interaction.response.send_message(f"Here are your goals:\n{goal_list}")
        else:
            await interaction.response.send_message("You don't have any goals yet! Use /addgoal to set one.")

# Required setup function
async def setup(aurabot):
    await aurabot.add_cog(ViewGoal(aurabot))
