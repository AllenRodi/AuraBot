import discord
from discord.ext import commands
from pymongo import MongoClient
from config import MONGO_URI

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client['aurabot']
profiles_collection = db['profiles']

class MoodLogging(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="moodlogging", description="Log your mood for the day.")
    async def moodlogging(self, ctx: discord.ApplicationContext):
        # Check if user has a profile
        user_id = str(ctx.author.id)
        profile = profiles_collection.find_one({"user_id": user_id})
        if not profile:
            await ctx.respond("You need to create a profile first using `/createprofile`.", ephemeral=True)
            return

        # Mood categories for the user to choose from
        categories = ["Happy 😊", "Sad 😢", "Angry 😠", "Stressed 😟", "Relaxed 😌"]
        options = [discord.SelectOption(label=category, value=category) for category in categories]

        # Dropdown menu for selecting mood
        class MoodDropdown(discord.ui.Select):
            def __init__(self):
                super().__init__(
                    placeholder="Select a mood to log...",
                    options=options,
                )

            async def callback(self, interaction: discord.Interaction):
                selected_mood = self.values[0]
                # Update mood log in MongoDB
                profiles_collection.update_one(
                    {"user_id": user_id},
                    {"$push": {"mood_logs": {"mood": selected_mood, "timestamp": ctx.created_at}}},
                )
                await interaction.response.send_message(
                    f"Your mood has been logged as **{selected_mood}**! Thank you!", ephemeral=True
                )

        # Create a view with the dropdown
        class MoodView(discord.ui.View):
            def __init__(self):
                super().__init__()
                self.add_item(MoodDropdown())

        # Show dropdown to the user
        await ctx.respond("Please select your mood from the options below:", view=MoodView(), ephemeral=True)


# Add the cog to the bot
def setup(bot):
    bot.add_cog(MoodLogging(bot))

