import discord

class ViewConfirm(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.value = None

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green)
    async def confirm(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.value = True
        self.clear_items()
        await interaction.response.edit_message(content="Confirmed", view=button.view, delete_after=2.5)
        self.stop()

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red)
    async def cancel(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.value = False
        self.clear_items()
        await interaction.response.edit_message(content="Cancelled", view=button.view, delete_after=2.5)
        self.stop()
