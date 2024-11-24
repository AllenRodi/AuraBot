import discord
import asyncio
from discord.ext import commands
from pymongo import MongoClient
from dotenv import load_dotenv
import os
from config import GUILD_ID

# Load environment variables
load_dotenv()

class AddGoal(commands.Cog):
    """Cog for adding goals to a user's profile in MongoDB."""

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
        """Register the /addgoal command when the cog is loaded."""
        guild = discord.Object(id=GUILD_ID)
        self.aurabot.tree.add_command(self.add_goal, guild=guild)

    @discord.app_commands.command(name="addgoal", description="Add a personal goal")
    async def add_goal(self, interaction: discord.Interaction):
        """Handles the /addgoal command."""
        await interaction.response.send_message("What goal would you like to add?")

        # Wait for user's response
        try:
            user_message = await self.aurabot.wait_for(
                "message",
                check=lambda m: m.author == interaction.user and m.channel == interaction.channel,
                timeout=600  # 10 minutes timeout
            )
        except asyncio.TimeoutError:
            await interaction.followup.send("You took too long to respond. Try again later.")
            return

        # Save the goal to MongoDB
        user_id = interaction.user.id
        goal = user_message.content

        self.collection.insert_one({"_id": user_id, "goal": goal})
        await interaction.followup.send(f"Your goal has been added: **{goal}**")

# Required setup function
async def setup(aurabot):
    await aurabot.add_cog(AddGoal(aurabot))
