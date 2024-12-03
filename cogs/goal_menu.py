import discord
from discord.ext import commands
from discord.ui import View, Button

class GoalMenu(commands.Cog):
    """Cog for the Goal Tracking menu."""

    def __init__(self, aurabot):
        self.aurabot = aurabot

    @discord.app_commands.command(name="goalmenu", description="Open the Goal Tracking menu.")
    async def goal_menu(self, interaction: discord.Interaction):
        """Command to display the Goal Tracking menu."""
        menu_view = GoalMenuView()
        await interaction.response.send_message("Choose an action for Goal Tracking:", view=menu_view, ephemeral=True)

class GoalMenuView(View):
    """Interactive view for the Goal Tracking menu."""

    def __init__(self):
        super().__init__()

        # Add buttons to the menu
        self.add_item(Button(label="Create Goal", style=discord.ButtonStyle.primary, custom_id="create_goal"))
        self.add_item(Button(label="Update Goal", style=discord.ButtonStyle.secondary, custom_id="update_goal"))
        self.add_item(Button(label="View Goal", style=discord.ButtonStyle.success, custom_id="view_goal"))

    async def interaction_check(self, interaction: discord.Interaction):
        """Ensure only the command user can interact with the menu."""
        return True

    @discord.ui.button(label="Create Goal", style=discord.ButtonStyle.primary, custom_id="create_goal")
    async def create_goal(self, interaction: discord.Interaction, button: Button):
        """Redirect to the create goal command."""
        await interaction.response.send_message(
            "Use the `/creategoal` command to create a goal! Example:\n`/creategoal goal: 'My Goal' deadline: 'YYYY-MM-DD'`",
            ephemeral=True,
        )

    @discord.ui.button(label="Update Goal", style=discord.ButtonStyle.secondary, custom_id="update_goal")
    async def update_goal(self, interaction: discord.Interaction, button: Button):
        """Redirect to the update goal command."""
        await interaction.response.send_message(
            "Use the `/updategoal` command to update your goal progress! Example:\n`/updategoal goal: 'My Goal' progress: 10`",
            ephemeral=True,
        )

    @discord.ui.button(label="View Goal", style=discord.ButtonStyle.success, custom_id="view_goal")
    async def view_goal(self, interaction: discord.Interaction, button: Button):
        """Redirect to the view goal command."""
        await interaction.response.send_message(
            "Use the `/viewgoal` command to check your progress! Example:\n`/viewgoal goal: 'My Goal'`",
            ephemeral=True,
        )

# Setup function for cog
async def setup(aurabot):
    await aurabot.add_cog(GoalMenu(aurabot))
