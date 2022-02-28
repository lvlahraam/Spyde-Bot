import discord
from discord.ext import commands

class Economy(commands.Cog, description="Buying Bitcoin and NFTs with these!"):
    def __init__(self, bot):
        self.bot = bot

    # GiveMoney
    @commands.command(name="givemoney", aliases=["gm"], help="Gives the amount of given money from your balance to the given user")
    async def givemoney(self, ctx:commands.Context, amount:int=commands.Option(description="The amount you want give"), user:discord.User=commands.Option(description="The user you want to give the amount to")):
        author = await self.bot.mongodb.economy.find_one({"user_id": ctx.author.id})
        giving = await self.bot.mongodb.economy.find_one({"user_id": user.id})
        gmbed = discord.Embed(
            color=self.bot.color,
            timestamp=ctx.message.created_at
        )
        if author:
            if not giving:
                gmbed.title = F"{user.name} doesn't have a account yet!"
            elif amount > author["balance"]:
                gmbed.title = F"{ctx.author.name} doesn't have enough money!"
            else:
                await self.bot.mongodb.economy.update_one({"user_id": ctx.author.id}, {"$set": {"balance": author["balance"]-amount}})
                await self.bot.mongodb.economy.update_one({"user_id": user.id}, {"$set": {"balance": giving["balance"]+amount}})
                gmbed.title = F"{user.name} now has {giving['balance']+amount}$!"
        else:
            gmbed.title = F"{ctx.author.name} doesn't have a account yet!"
        await ctx.reply(embed=gmbed)

def setup(bot):
    bot.add_cog(Economy(bot))
