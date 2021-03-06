import discord, asyncio
from discord.ext import commands

class DeleteTicketView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(emoji="💣", style=discord.ButtonStyle.red, custom_id="persistent_ticket:red")
    async def delete(self, button:discord.ui.Button, interaction:discord.Interaction):
        button.disabled = True
        tkdeletembed = discord.Embed(
            color=self.bot.color,
            title="Ticket has been deleted",
            description=F"{interaction.user.mention} has deleted the ticket\nWait at least for 2.5 seconds",
            timestamp=interaction.message.created_at,
        )
        tkdeletembed.set_footer(text=interaction.user, icon_url=interaction.user.avatar.url)
        await interaction.response.edit_message(view=button.view)
        await interaction.followup.send(embed=tkdeletembed)
        await asyncio.sleep(2.5)
        await interaction.channel.delete(reason=F"{interaction.user.display_name} ({interaction.user.id}) has deleted the ticket")
        

class CloseTicketView(discord.ui.View):
    def __init__(self, bot, opener, chorinal):
        super().__init__(timeout=None)
        self.bot = bot
        self.opener = opener
        self.chorinal = chorinal

    @discord.ui.button(emoji="🔒", style=discord.ButtonStyle.green, custom_id="persistent_ticket:green")
    async def close(self, button:discord.ui.Button, interaction:discord.Interaction):
        button.disabled = True
        tkclosembed = discord.Embed(
            color=self.bot.color,
            title="Ticket has been closed",
            description=F"{interaction.user.mention} has closed the ticket\nUse the button to delete the ticket",
            timestamp=interaction.message.created_at
        )
        tkclosembed.set_footer(text=interaction.user, icon_url=interaction.user.avatar.url)
        await interaction.channel.edit(name=F"{interaction.channel.name}-closed", reason=F"{interaction.user} closed the ticket", topic=F"{interaction.channel.topic} - Closed by {interaction.user}")
        await interaction.response.edit_message(view=button.view)
        await interaction.followup.send(embed=tkclosembed, view=DeleteTicketView(self.bot))
        await interaction.channel.set_permissions(self.opener, view_channel=False)
        await self.chorinal.set_permissions(interaction.user, view_channel=False)

class TicketView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(emoji="🔓", style=discord.ButtonStyle.blurple, custom_id="persistent_ticket:blurple")
    async def open(self, button:discord.ui.Button, interaction:discord.Interaction):
        ticket = await self.bot.mongodb.tickets.find_one({"guild_id": interaction.channel.guild.id})
        cag = ticket["category"]
        num = ticket["number"]
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
        await self.bot.mongodb.tickets.find_one_and_update({"guild_id": interaction.channel.guild.id}, {"$set": {"number": num+1}})
        await interaction.response.send_message(content=F"Your ticket has been opened in {channel.mention}", ephemeral=True)
        await interaction.channel.set_permissions(interaction.user, view_channel=False)
        await channel.send(embed=tkopenmbed, view=CloseTicketView(self.bot, interaction.user, interaction.channel), allowed_mentions=discord.AllowedMentions.all())
