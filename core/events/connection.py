import discord
from discord.ext import commands
from core.views import ticket

class OnConnect(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_connect(self):
        self.bot.uptime = discord.utils.utcnow()
        print(F"Connected as: {self.bot.user} - {self.bot.user.id}\nConnected to discord.")

class OnReady(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        print(F"Readied as: {self.bot.user} - {self.bot.user.id}\nReady in discord.")
        if not self.bot.persistent_views_added:
            self.bot.add_view(ticket.TicketView(self.bot))
            self.bot.add_view(ticket.CloseTicketView(self.bot, None, None))
            self.bot.persistent_views_added = True
        await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=F"over {len(self.bot.guilds)} G's & {len(self.bot.users)} U's"))

class OnDisconnect(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_disconnect(self):
        print(F"Disconnected as: {self.bot.user} - {self.bot.user.id}\nDisconnected from discord.")
        if not self.bot.session.closed:
            await self.bot.session.close()

def setup(bot):
    bot.add_cog(OnConnect(bot))
    bot.add_cog(OnReady(bot))
    bot.add_cog(OnDisconnect(bot))
