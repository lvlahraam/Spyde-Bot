import discord
from discord.ext import commands

class OnMessage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_message(self, message:discord.Message):
        if message.author.bot: return
        if message.content in (F"<@{self.bot.user.id}>", F"<@!{self.bot.user.id}>"):
            pfmbed = discord.Embed(
                color=self.bot.color,
                title="My Prefix here is:",
                description=self.bot.prefixes.get(message.guild.id),
                timestamp=message.created_at
            )
            pfmbed.set_footer(text=message.author, icon_url=message.author.display_avatar.url)
            await message.reply(embed=pfmbed)
        if self.bot.afks.get(message.author.id):
            view = discord.ui.View()
            view.add_item(item=discord.ui.Button(label="Go to original message", url=self.bot.afks[message.author.id]["jump_url"]))
            omafkmbed = discord.Embed(
                color=self.bot.color,
                title="Removed your AFK",
                timestamp=message.created_at
            )
            omafkmbed.add_field(name="Reason:", value=self.bot.afks[message.author.id], inline=False)
            omafkmbed.add_field(name="Since:", value=discord.utils.format_dt(self.bot.afks[message.author.id]["time"], style="R"), inline=False)
            omafkmbed.set_footer(text=message.author, icon_url=message.author.display_avatar.url)
            await message.reply(embed=omafkmbed, view=view)
            del self.bot.afks[message.author.id]

def setup(bot):
    bot.add_cog(OnMessage(bot))
