import discord
from discord.ext import commands
from config import GUILD_ID  # Import GUILD_ID

class Menu(commands.Cog):
    def __init__(self, aurabot):
        self.aurabot = aurabot

    @discord.app_commands.command(name="menu", description="Displays the list of available commands")
    async def menu(self, interaction: discord.Interaction):
        """Respond with a menu of commands."""
        embed = discord.Embed(
            title="Command Menu",
            description="Here are the commands currently available:",
            color=discord.Color.blue()
        )

        # Fetch all registered slash commands
        commands = self.aurabot.tree.get_commands(guild=discord.Object(id=GUILD_ID))
        for cmd in commands:
            embed.add_field(
                name=f"/{cmd.name}",
                value=cmd.description or "No description provided.",
                inline=False
            )

        await interaction.response.send_message(embed=embed)

    async def cog_load(self):
        """Register the menu command when the cog is loaded."""
        guild = discord.Object(id=GUILD_ID)
        self.aurabot.tree.add_command(self.menu, guild=guild)

# Required setup function to add the cog
async def setup(aurabot):
    await aurabot.add_cog(Menu(aurabot))
    print("Menu cog successfully added!")
