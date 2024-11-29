import discord
from discord.ext import tasks
from discord import Interaction
import logging
from datetime import datetime, timezone
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
        
        try:
            self.cluster = MongoClient(mongo_url, serverSelectionTimeOutMS=5000)
            # Test connection
            self.cluster.server_info()
        except Exception as e:
            raise ConnectionError(f"Failed to connect to MongoDB: {e}")
        
        # set up database and collections
        self.cluster = MongoClient(mongo_url)
        self.db = self.cluster["AuraBotDB"]
        self.mood_collection = self.db["mood_logging"]
        self.reminder_collection = self.db["reminders"]

        #Start the reminder task loop
        self.send_reminders.start()

        # Debugging: Check MongoDB connection, temp replaced by raise ConnectionError(f"Failed to connect to MongoDB: {e}")
        # print("Connected to MongoDB for mood logging!")
        # print("Existing collections:", self.db.list_collection_names())

    async def cog_load(self):
        """Register commands when the cog is loaded."""
        guild = discord.Object(id=GUILD_ID)  # Ensure GUILD_ID is correct
        self.aurabot.tree.add_command(self.log_mood, guild=guild)
        self.aurabot.tree.add_command(self.view_moods, guild=guild)
        self.aurabot.tree.add_command(self.set_reminder, guild=guild)
        self.aurabot.tree.add_command(self.stop_reminder, guild=guild)
        logging.info("Commands registered: logmood, viewmoods, setmoodreminder, stopmoodreminder")


    @discord.app_commands.command(name="logmood", description="Log your mood for the day.")
    async def log_mood(self, interaction: discord.Interaction, mood: str):
        """Handles /logmood command."""
        await interaction.response.defer() #acknowledge interaction first
        try:
            user_id = interaction.user.id
            self.mood_collection.update_one( #use correct collection
                {"_id": user_id},
                {"$push": {"moods": {"mood": mood, "timestamp": datetime.now(timezone.utc)}}},
                upsert=True
            )
            await interaction.followup.send(f"Your mood: {mood} has been logged!")
        except Exception as e:
            logging.error(f"Error logging mood: {e}")
            await interaction.followup.send("Failed to log your mood. Please try again.")



    @discord.app_commands.command(name="viewmoods", description="View your logged moods.")
    async def view_moods(self, interaction: discord.Interaction):
        """Handles /viewmoods command."""
        await interaction.response.defer() # acknowledge interaction first
        try:
            user_id = interaction.user.id
            user_data = self.mood_collection.find_one({"_id": user_id}) #use correct collection

            if user_data and "moods" in user_data:
                moods = user_data["moods"]
                if moods:
                    mood_list = "\n".join(
                        [f"- {entry['mood']} (logged at {entry['timestamp'].strftime('%Y-%m-%d %H:%M:%S')})" for entry in moods]
                    )
                    await interaction.followup.send(f"Your logged moods:\n{mood_list}")
                else:
                    await interaction.followup.send("You haven't logged any moods yet.")
            else:
                await interaction.followup.send("You haven't logged any moods yet.")
        except Exception as e:
            logging.error(f"Error retrieving moods: {e}")
            await interaction.followup.send("Failed to retrieve your moods. Please try again later.")
    


    @discord.app_commands.command(name="setmoodreminder", description="Set a daily mood logging reminder (format: HH:MM in 24-hour).")
    async def set_reminder(self, interaction: discord.Interaction, time: str):
        """Set daily reminders to log moods."""
        try:
            hour, minute = map(int, time.split(":"))
            if not (0 <= hour < 24 and 0 <= minute < 60):
                raise ValueError("Invalid time range")
            
            
            user_id = interaction.user.id
            self.reminder_collection.update_one(
                 {"_id": user_id},
                 {"$set": {"time": time, "enabled": True}},
                 upsert=True
            )
            await interaction.response.send_message(f"Reminder set for {time}. I'll DM you daily to log your mood!")
        except ValueError:
            await interaction.response.send_message("Invalid time format! Use HH:MM in 24-hour format.")
        except Exception as e:
            logging.error(f"Error setting reminder: {e}")
            await interaction.response.send_message("Failed to set a reminder. Please try again later.")



    @discord.app_commands.command(name="stopmoodreminder", description="Stop receiving daily reminders.")
    async def stop_reminder(self, interaction: discord.Interaction):
        """Stop daily reminders."""
        try:
            user_id = interaction.user.id
            result = self.reminder_collection.update_one({"_id": user_id}, {"$set": {"enabled": False}})
            if result.modified_count > 0:
                await interaction.response.send_message("Mood logging reminders disabled.")
            else:
                await interaction.response.send_message("No active reminders found to disable.")
        except Exception as e:
            logging.error(f"Error stopping reminder: {e}")
            await interaction.response.send_message("Failed to stop reminders. Please try again later.")



    @tasks.loop(minutes=1)
    async def send_reminders(self):
        """Send mood logging reminders to users at their specified time."""
        now = datetime.now(timezone.utc).strftime("%H:%M")
        try:
            reminders = self.reminder_collection.find({"time": now, "enabled": True})
            for reminder in reminders:
                user_id = reminder["_id"]
                user = self.aurabot.get_user(user_id)
                if user:
                    try:
                        await user.send("⏰ Don't forget to log your mood today!")
                    except discord.Forbidden:
                        logging.warning(f"Unable to send DM to user {user_id}. DMs may be disabled.")
        except Exception as e:
            logging.error(f"Error sending reminders: {e}")



    @send_reminders.before_loop
    async def before_send_reminders(self):
        """Wait until the bot is ready before starting reminders."""
        await self.aurabot.wait_until_ready()


# Required setup function
async def setup(aurabot):
    await aurabot.add_cog(MoodLogging(aurabot))
    print("MoodLogging cog successfully added!")

