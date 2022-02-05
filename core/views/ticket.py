import discord
from discord.ext import commands

class CloseTicketView(discord.ui.View):
    def __init__(self, bot, opener, chorinal):
        super().__init__(timeout=None)
        self.bot = bot
        self.opener = opener
        self.chorinal = chorinal

    @discord.ui.button(emoji="🔒", style=discord.ButtonStyle.red, custom_id="persistent_ticket:red")
    async def close(self, button:discord.ui.Button, interaction:discord.Interaction):
        button.disabled = True
        tkclosmbed = discord.Embed(
            color=self.bot.color,
            title="Ticket has been closed",
            description=F"{interaction.user.mention} has closed the ticket",
            timestamp=interaction.message.created_at,
        )
        tkclosmbed.set_footer(text=interaction.user, icon_url=interaction.user.avatar.url)
        await interaction.channel.edit(name=F"{interaction.channel.name}-closed", reason="Closed Ticket", topic=F"{interaction.channel.topic} - Closed by {interaction.user}")
        await interaction.response.edit_message(view=button.view)
        await interaction.followup.send(embed=tkclosmbed)
        await interaction.channel.set_permissions(self.opener, view_channel=False)
        await self.chorinal.set_permissions(interaction.user, view_channel=False)

class TicketView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(emoji="🔓", style=discord.ButtonStyle.blurple, custom_id="persistent_ticket:blurple")
    async def open(self, button:discord.ui.Button, interaction:discord.Interaction):
        cag = await self.bot.postgres.fetchval("SELECT cag FROM tickets WHERE guild_id = $1", interaction.guild.id)
        num = await self.bot.postgres.fetchval("SELECT num FROM tickets WHERE guild_id = $1", interaction.guild.id)
        category = interaction.guild.get_channel(cag)
        if not category:
            category = await interaction.guild.create_category("Tickets")
        channel = await category.create_text_channel(F"ticket-{num}", reason=F"{interaction.user} opened a ticket", topic=F"{interaction.user} opened a ticket")
        await channel.set_permissions(interaction.user, view_channel=True)
        await channel.set_permissions(interaction.guild.default_role, view_channel=False)
        tkopenmbed = discord.Embed(
            color=self.bot.color,
            title="Ticket has been opened",
            description=F"{interaction.user.mention} has opened a ticket\nUse the button to close the ticket",
            timestamp=interaction.message.created_at,
        )
        tkopenmbed.set_footer(text=interaction.user, icon_url=interaction.user.display_avatar.url)
        await self.bot.postgres.execute("UPDATE tickets SET num = $1 WHERE guild_id = $2", num+1, interaction.guild.id)
        await interaction.response.send_message(content=F"Your ticket has been opened in {channel.mention}", ephemeral=True)
        await interaction.channel.set_permissions(interaction.user, view_channel=False)
        await channel.send(embed=tkopenmbed, view=CloseTicketView(self.bot, interaction.user, interaction.channel), allowed_mentions=discord.AllowedMentions.all())
