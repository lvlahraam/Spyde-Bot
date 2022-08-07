import discord
from discord.ext import commands


class OnConnection(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_connect(self):
        self.bot.uptime = discord.utils.utcnow()
        print(
            f"Connected as: {self.bot.user} - {self.bot.user.id}\nConnected to discord."
        )

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Readied as: {self.bot.user} - {self.bot.user.id}\nReady in discord.")
        await self.bot.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name=f"over {len(self.bot.guilds)} G's & {len(self.bot.users)} U's",
            )
        )

    @commands.Cog.listener()
    async def on_disconnect(self):
        print(
            f"Disconnected as: {self.bot.user} - {self.bot.user.id}\nDisconnected from discord."
        )


async def setup(bot):
    await bot.add_cog(OnConnection(bot))
