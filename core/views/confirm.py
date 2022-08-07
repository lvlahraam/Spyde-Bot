import discord


class ViewConfirm(discord.ui.View):
    def __init__(self, ctx):
        super().__init__(timeout=None)
        self.ctx = ctx
        self.value = None

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green)
    async def confirm(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        self.value = True
        self.clear_items()
        await interaction.response.edit_message(view=button.view)
        await interaction.followup.send(content="Confirmed", ephemeral=True)
        self.stop()

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.value = False
        self.clear_items()
        await interaction.response.edit_message(view=button.view)
        await interaction.followup.send(content="Cancelled", ephemeral=True)
        self.stop()
