import discord
from discord.ext import commands

class Economy(commands.Cog, description="Are you good at keeping money?!"):
    def __init__(self, bot):
        self.bot = bot

    # CreateAccount
    @commands.command(name="createaccount", aliases=["ca"], description="Create an bank account")
    async def createaccount(self, ctx:commands.Context):
        balance = await self.bot.mongodb.economy.find_one({"user_id": ctx.author.id})
        cambed = discord.Embed(
            color=self.bot.color,
            timestamp=ctx.message.created_at
        )
        cambed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        if not balance:
            await self.bot.mongodb.economy.insert_one({"user_name": ctx.author.name, "user_id": ctx.author.id, "balance": 0})
            cambed.title = "Account has been created!"
            cambed.description = "Balance is: 0$"
        else:
            cambed.title = "Account already exists!"
            cambed.description = F"Balance is: {balance['balance']}"
        cambed += "\nYou can use other commands to gain money!"
        await ctx.reply(embed=cambed)

    # GiveMoney
    @commands.command(name="givemoney", aliases=["gm"], help="Gives the amount of given money from your balance to the given user")
    async def givemoney(self, ctx:commands.Context, amount:int=commands.Option(description="The amount you want give"), user:discord.User=commands.Option(description="The user you want to give the amount to")):
        author = await self.bot.mongodb.economy.find_one({"user_id": ctx.author.id})
        giving = await self.bot.mongodb.economy.find_one({"user_id": user.id})
        gmbed = discord.Embed(
            color=self.bot.color,
            timestamp=ctx.message.created_at
        )
        gmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        if author:
            if not giving:
                gmbed.title = F"{user.name} doesn't have a account yet!"
            elif amount > author["balance"]:
                gmbed.title = F"{ctx.author.name} doesn't have enough money!"
            else:
                await self.bot.mongodb.economy.update_one({"user_id": ctx.author.id}, {"$set": {"balance": author["balance"]-amount}})
                await self.bot.mongodb.economy.update_one({"user_id": user.id}, {"$set": {"balance": giving["balance"]+amount}})
                gmbed.title = "Money has been transfered!"
                gmbed.description = F"{amount}$ has been removed from {ctx.author.mention}!\n{amount}$ has been added to {user.mention}!"
                gmbed.description = F"{user.mention} now has {giving['balance']+amount}$!\n{ctx.author.mention} now has {author['balance']-amount}$!"
        else:
            gmbed.title = F"{ctx.author.name} doesn't have a account yet!"
        await ctx.reply(embed=gmbed)

def setup(bot):
    bot.add_cog(Economy(bot))
