import discord
from discord.ext import commands
from pymongo import MongoClient
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

class GoalTracking(commands.Cog):
    """Cog for goal tracking with streaks and rewards."""

    def __init__(self, aurabot):
        self.aurabot = aurabot

        # MongoDB setup
        mongo_url = os.getenv("MONGO_URL")
        if not mongo_url:
            raise ValueError("MongoDB connection string is not set in .env")
        self.cluster = MongoClient(mongo_url)
        self.db = self.cluster["AuraBotDB"]
        self.collection = self.db["user_goals"]

    @discord.app_commands.command(name="creategoal", description="Create a new goal.")
    async def create_goal(self, interaction: discord.Interaction, goal: str, deadline: str = None):
        """
        Command to create a new goal.
        - goal: The description of the goal.
        - deadline: Optional target date for the goal in YYYY-MM-DD format.
        """
        user_id = interaction.user.id

        try:
            # Parse deadline if provided
            deadline_date = datetime.strptime(deadline, "%Y-%m-%d") if deadline else None
        except ValueError:
            await interaction.response.send_message("Invalid date format. Use YYYY-MM-DD.")
            return

        goal_data = {
            "_id": f"{user_id}_{goal.lower()}",
            "user_id": user_id,
            "goal": goal,
            "deadline": deadline_date,
            "progress": 0,
            "streak": 0,
            "last_update": None,
            "rewards": 0,
        }

        # Insert goal into database
        self.collection.insert_one(goal_data)
        await interaction.response.send_message(f"Goal '{goal}' created successfully!")

    @discord.app_commands.command(name="updategoal", description="Update progress on your goal.")
    async def update_goal(self, interaction: discord.Interaction, goal: str, progress: int):
        """
        Command to update progress on a goal.
        - goal: The goal to update.
        - progress: The amount of progress to add (e.g., 10%).
        """
        user_id = interaction.user.id
        goal_id = f"{user_id}_{goal.lower()}"
        goal_data = self.collection.find_one({"_id": goal_id})

        if not goal_data:
            await interaction.response.send_message(f"Goal '{goal}' not found. Use /creategoal to create it.")
            return

        # Calculate streaks and rewards
        now = datetime.now()
        streak = goal_data["streak"]
        last_update = goal_data["last_update"]

        if last_update:
            last_update_date = datetime.strptime(last_update, "%Y-%m-%d")
            if (now - last_update_date).days == 1:  # Increment streak if updated daily
                streak += 1
            else:
                streak = 1  # Reset streak if more than 1 day passes
        else:
            streak = 1  # Initialize streak on first update

        # Update progress and calculate rewards
        new_progress = goal_data["progress"] + progress
        rewards = goal_data["rewards"] + (progress // 10)  # Earn 1 reward point for every 10% progress

        # Update database
        self.collection.update_one(
            {"_id": goal_id},
            {
                "$set": {
                    "progress": new_progress,
                    "streak": streak,
                    "last_update": now.strftime("%Y-%m-%d"),
                    "rewards": rewards,
                }
            },
        )
        await interaction.response.send_message(
            f"Progress updated for goal '{goal}'.\n"
            f"**New Progress:** {new_progress}%\n"
            f"**Streak:** {streak} days\n"
            f"**Rewards:** {rewards} points"
        )

    @discord.app_commands.command(name="viewgoal", description="View progress on a goal.")
    async def view_goal(self, interaction: discord.Interaction, goal: str):
        """
        Command to view progress, streaks, and rewards on a specific goal.
        - goal: The goal to view.
        """
        user_id = interaction.user.id
        goal_id = f"{user_id}_{goal.lower()}"
        goal_data = self.collection.find_one({"_id": goal_id})

        if not goal_data:
            await interaction.response.send_message(f"Goal '{goal}' not found. Use /creategoal to create it.")
            return

        # Display goal details
        progress = goal_data["progress"]
        streak = goal_data["streak"]
        rewards = goal_data["rewards"]
        deadline = goal_data["deadline"].strftime("%Y-%m-%d") if goal_data["deadline"] else "No deadline"

        await interaction.response.send_message(
            f"**Goal:** {goal}\n"
            f"**Progress:** {progress}%\n"
            f"**Streak:** {streak} days\n"
            f"**Rewards:** {rewards} points\n"
            f"**Deadline:** {deadline}"
        )

# Setup function for cog
async def setup(aurabot):
    await aurabot.add_cog(GoalTracking(aurabot))
