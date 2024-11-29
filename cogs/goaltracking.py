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

        print("GoalTracking cog loaded and connected to MongoDB!")

    async def cog_load(self):
        guild = discord.Object(id=GUILD_ID)
        self.aurabot.tree.add_command(self.add_goal, guild=guild)
        self.aurabot.tree.add_command(self.view_goals, guild=guild)

    @discord.app_commands.command(name="addgoal", description="Add a goal to track.")
    async def add_goal(self, interaction: discord.Interaction, goal: str, target: int, unit: str):
        print(f"/addgoal invoked with goal={goal}, target={target}, unit={unit}")
        user_id = interaction.user.id
        self.collection.update_one(
            {"_id": user_id},
            {"$addToSet": {"goals": {"goal": goal, "target": target, "unit": unit, "progress": 0}}},
            upsert=True
        )
        await interaction.response.send_message(f"Goal `{goal}` with target `{target} {unit}` added.")

    @discord.app_commands.command(name="viewgoals", description="View your goals.")
    async def view_goals(self, interaction: discord.Interaction):
        print("/viewgoals invoked")
        user_id = interaction.user.id
        user_data = self.collection.find_one({"_id": user_id})
        if not user_data or "goals" not in user_data:
            await interaction.response.send_message("You don't have any goals yet.")
            return

        embed = discord.Embed(title="Your Goals", color=discord.Color.blue())
        for g in user_data["goals"]:
            embed.add_field(name=g["goal"], value=f"Target: {g['target']} {g['unit']} | Progress: {g['progress']}", inline=False)
        await interaction.response.send_message(embed=embed)

# Required setup function
async def setup(aurabot):
    await aurabot.add_cog(GoalTracking(aurabot))
    print("GoalTracking cog successfully added!")
