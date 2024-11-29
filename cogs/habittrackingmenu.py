import discord
from discord.ext import commands
from config import GUILD_ID  # Import your guild ID

class HabitTrackingMenu(commands.Cog):
    """Cog for displaying the habit tracking menu."""

    def __init__(self, aurabot):
        self.aurabot = aurabot

    @discord.app_commands.command(name="habittracking", description="Displays habit tracking options.")
    async def habittracking_menu(self, interaction: discord.Interaction):
        """Handles /habittrackingmenu command to display options."""
        embed = discord.Embed(
            title="Habit Tracking Menu",
            description="Here are the commands you can use for habit tracking:",
            color=discord.Color.green()
        )
        embed.add_field(name="/addhabit", value="Add a habit to track.", inline=False)
        embed.add_field(name="/viewhabits", value="View your tracked habits.", inline=False)
        embed.add_field(name="/clearhabits", value="Clear all your tracked habits.", inline=False)
        await interaction.response.send_message(embed=embed)

    async def cog_load(self):
        """Register commands when the cog is loaded."""
        guild = discord.Object(id=GUILD_ID)  # Ensure the guild ID is correct
        self.aurabot.tree.add_command(self.habittracking_menu, guild=guild)

# Required setup function
async def setup(aurabot):
    await aurabot.add_cog(HabitTrackingMenu(aurabot))
