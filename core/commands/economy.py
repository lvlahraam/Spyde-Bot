import discord
from discord.ext import commands

class Economy(commands.Cog, description="Buying Bitcoin and NFTs with these!"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="addmoney", aliases=["am"], help="Adds the given amount of momey to you or the given user")
    @commands.is_owner()
    async def addmoney(self, ctx:commands.Context, amount:int=commands.Option(description="The amount you want give"), user:discord.User=commands.Option(description="The user you want to give the amount to", default=None)):
        user = user or ctx.author
        await ctx.send("Economy is not ready")

def setup(bot):
    bot.add_cog(Economy(bot))
