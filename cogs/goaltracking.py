import discord
from discord.ext import commands, tasks
from pymongo import MongoClient
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta
import math
from config import GUILD_ID


#Purpose: This cog allows users to:
#Add goals.
#View progress and streaks.
#Check in daily to log progress.
#Earn rewards for maintaining streaks.




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

        # Start background task
        self.check_streaks.start()

        print("GoalTracking cog loaded and connected to MongoDB!")

    async def cog_load(self):
        guild = discord.Object(id=GUILD_ID)
        self.aurabot.tree.add_command(self.add_goal, guild=guild)
        self.aurabot.tree.add_command(self.view_goals, guild=guild)
        self.aurabot.tree.add_command(self.checkin, guild=guild)
        self.aurabot.tree.add_command(self.view_rewards, guild=guild)

    @discord.app_commands.command(name="addgoal", description="Add a goal to track.")
    async def add_goal(self, interaction: discord.Interaction, goal: str, target: int, unit: str, duration: int):
        print(f"/addgoal invoked with goal={goal}, target={target}, unit={unit}, duration={duration}")
        user_id = interaction.user.id
        start_date = datetime.now(datetime.timezone.utc)  # Store as timezone-aware datetime
        self.collection.update_one(
            {"_id": user_id},
            {
                "$addToSet": {
                    "goals": {
                        "goal": goal,
                        "target": target,
                        "unit": unit,
                        "progress": 0,
                        "duration": duration,
                        "start_date": start_date,  # Proper datetime object
                        "streak": 0,
                        "last_checked_in": None,
                    }
                }
            },
            upsert=True
        )
        await interaction.response.send_message(
            f"Goal `{goal}` with target `{target} {unit}` over `{duration} days` added. Good luck!"
        )

    @discord.app_commands.command(name="viewgoals", description="View your goals.")
    async def view_goals(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        user_data = self.collection.find_one({"_id": user_id})
        if not user_data or "goals" not in user_data:
            await interaction.response.send_message("You don't have any goals yet.")
            return

        embed = discord.Embed(title="Your Goals", color=discord.Color.blue())
        for g in user_data["goals"]:
            progress = self.progress_bar(g["progress"], g["target"])
            embed.add_field(
                name=g["goal"],
                value=f"Target: {g['target']} {g['unit']} | Progress: {progress} | Streak: {g['streak']} days",
                inline=False
            )
        await interaction.response.send_message(embed=embed)

    @discord.app_commands.command(name="checkin", description="Log progress for the day.")
    async def checkin(self, interaction: discord.Interaction, goal: str, progress: int):
        user_id = interaction.user.id
        user_data = self.collection.find_one({"_id": user_id})

        if not user_data or "goals" not in user_data:
            await interaction.response.send_message("You don't have any goals yet.")
            return

        for g in user_data["goals"]:
            if g["goal"].lower() == goal.lower():
                days_elapsed = (datetime.now(datetime.timezone.utc) - g["start_date"]).days
                if days_elapsed > g["duration"]:
                    await interaction.response.send_message("This goal has already ended.")
                    return

                if g["last_checked_in"] and g["last_checked_in"].date() == datetime.now(datetime.timezone.utc).date():
                    await interaction.response.send_message("You already checked in today!")
                    return

                g["progress"] += progress
                g["streak"] += 1
                g["last_checked_in"] = datetime.now(datetime.timezone.utc)
                message = f"Progress logged! Current streak: {g['streak']} days."

                if g["streak"] % 7 == 0:  # Weekly reward
                    message += " 🎉 You've earned a weekly reward!"
                self.collection.update_one(
                    {"_id": user_id},
                    {"$set": {"goals": user_data["goals"]}}
                )
                await interaction.response.send_message(message)
                return

        await interaction.response.send_message(f"Goal `{goal}` not found.")

    @discord.app_commands.command(name="rewards", description="View your rewards.")
    async def view_rewards(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        user_data = self.collection.find_one({"_id": user_id})
        if not user_data or "goals" not in user_data:
            await interaction.response.send_message("You haven't earned any rewards yet.")
            return

        embed = discord.Embed(title="Your Rewards", color=discord.Color.gold())
        for g in user_data["goals"]:
            embed.add_field(
                name=g["goal"],
                value=f"Streak: {g['streak']} days | Rewards: {g['streak'] // 7} weekly rewards",
                inline=False
            )
        await interaction.response.send_message(embed=embed)

    @tasks.loop(hours=24)
    async def check_streaks(self):
        """Background task to check streaks daily and notify users."""
        for user_data in self.collection.find():
            user_id = user_data["_id"]
            for g in user_data.get("goals", []):
                # Log the goal data to inspect its structure
                print(f"Goal Data: {g}")

                # Ensure g is a dictionary and has the 'start_date' key
                if isinstance(g, dict) and "start_date" in g:
                    start_date = g["start_date"]

                    # If start_date is a string, try converting it to a datetime object
                    if isinstance(start_date, str):
                        try:
                            start_date = datetime.fromisoformat(start_date)  # Try converting string to datetime
                        except ValueError:
                            continue  # If conversion fails, skip this goal

                    # If start_date is not a datetime, skip this goal
                    elif not isinstance(start_date, datetime):
                        continue

                    # Proceed if start_date is valid
                    days_elapsed = (datetime.now(datetime.timezone.utc) - start_date).days
                    if g["streak"] < days_elapsed <= g["duration"]:
                        user = await self.aurabot.fetch_user(user_id)
                        await user.send(
                            f"⚠️ You missed progress for your goal `{g['goal']}` yesterday! Log today's progress to keep your streak alive."
                        )
                else:
                    # If goal data is not a dictionary or does not contain 'start_date', log the issue
                    print(f"Invalid goal format: {g}")

    def progress_bar(self, progress, target, length=20):
        """Generate a progress bar string."""
        percent = (progress / target) * 100
        filled_length = math.ceil((length * progress) / target)
        bar = "█" * filled_length + "-" * (length - filled_length)
        return f"[{bar}] {percent:.1f}%"

# Required setup function
async def setup(aurabot):
    await aurabot.add_cog(GoalTracking(aurabot))
    print("GoalTracking cog successfully added!")
