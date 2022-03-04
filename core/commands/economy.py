import discord, random
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
            cambed.description = F"Balance is: {balance['balance']}$"
        cambed.description += "\nYou can gain money by using other commands!"
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
                gmbed.add_field(name="Transfer:", value=F"{amount}$ has been removed from {ctx.author.mention}!\n{amount}$ has been added to {user.mention}!", inline=False)
                gmbed.add_field(name="Balance", value=F"{user.mention} now has {giving['balance']+amount}$!\n{ctx.author.mention} now has {author['balance']-amount}$!", inline=False)
        else:
            gmbed.title = F"{ctx.author.name} doesn't have a account yet!"
        await ctx.reply(embed=gmbed)

    # Balance
    @commands.command(name="balance", aliases=["bal"], description="Shows your balance")
    async def balance(self, ctx:commands.Context):
        author = await self.bot.mongodb.economy.find_one({"user_id": ctx.author.id})
        balmbed = discord.Embed(
            color=self.bot.color,
            timestamp=ctx.message.created_at
        )
        balmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        if author:
            balmbed.title = "Balance!"
            balmbed.description = F"Balance is: {author['balance']}$"
        else:
            balmbed.title = F"{ctx.author.name} doesn't have a account yet!"
        await ctx.reply(embed=balmbed)

    # Daily
    @commands.command(name="daily", aliases=["di"], description="Adds a random amount of money to your balance, per day")
    @commands.cooldown(1, 86400, commands.BucketType.user)
    async def daily(self, ctx:commands.Context):
        author = await self.bot.mongodb.economy.find_one({"user_id": ctx.author.id})
        dimbed = discord.Embed(
            color=self.bot.color,
            timestamp=ctx.message.created_at
        )
        dimbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        if author:
            dimbed.title = "Daily!"
            payback = random.randrange(1, 500)
            await self.bot.mongodb.economy.update_one({"user_id": ctx.author.id}, {"$set": {"balance": author["balance"]+payback}})
            dimbed.add_field(name="Transfer:", value=F"{payback}$ has been added to {ctx.author.mention}!", inline=False)
            dimbed.add_field(name="Balance:", value=F"{ctx.author.mention} now has {author['balance']+payback}$!", inline=False)
        else:
            dimbed.title = F"{ctx.author.name} doesn't have a account yet!"
        await ctx.reply(embed=dimbed)

    # Weekly
    @commands.command(name="weekly", aliases=["wk"], description="Adds a random amount of money to your balance, per week")
    @commands.cooldown(1, 604800, commands.BucketType.user)
    async def weekly(self, ctx:commands.Context):
        author = await self.bot.mongodb.economy.find_one({"user_id": ctx.author.id})
        wkmbed = discord.Embed(
            color=self.bot.color,
            timestamp=ctx.message.created_at
        )
        wkmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        if author:
            wkmbed.title = "Weekly!"
            payback = random.randrange(500, 1000)
            await self.bot.mongodb.economy.update_one({"user_id": ctx.author.id}, {"$set": {"balance": author["balance"]+payback}})
            wkmbed.add_field(name="Transfer:", value=F"{payback}$ has been added to {ctx.author.mention}!", inline=False)
            wkmbed.add_field(name="Balance:", value=F"{ctx.author.mention} now has {author['balance']+payback}$!", inline=False)
        else:
            wkmbed.title = F"{ctx.author.name} doesn't have a account yet!"
        await ctx.reply(embed=wkmbed)

def setup(bot):
    bot.add_cog(Economy(bot))
