import discord
from discord.ext import commands

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
        await self.bot.change_presence(status=discord.Status.dnd, activity=discord.Activity(type=discord.ActivityType.watching, name=F"over Sym {len(self.bot.guilds)} | {self.bot.default_prefix}help"))

class OnDisconnect(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_disconnect(self):
        print(F"Disconnected as: {self.bot.user} - {self.bot.user.id}\nDisconnected from discord.")

def setup(bot):
    bot.add_cog(OnConnect(bot))
    bot.add_cog(OnReady(bot))
    bot.add_cog(OnDisconnect(bot))
