import discord, random
from discord.ext import commands
from core.views import confirm


class Economy(commands.Cog, description="Are you good at keeping money?!"):
    def __init__(self, bot):
        self.bot = bot

    # CreateAccount
    @commands.hybrid_command(
        name="createaccount",
        aliases=["ca"],
        description="Creates a bank account for you",
    )
    async def createaccount(self, ctx: commands.Context):
        balance = await self.bot.mongodb.economy.find_one({"user_id": ctx.author.id})
        cambed = discord.Embed(color=self.bot.color, timestamp=ctx.message.created_at)
        cambed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        if not balance:
            await self.bot.mongodb.economy.insert_one(
                {
                    "user_name": ctx.author.name,
                    "user_id": ctx.author.id,
                    "balance": 0,
                    "transitions": "",
                }
            )
            cambed.title = "Bank account has been created!"
            cambed.description = "Balance is: 0$"
        else:
            cambed.title = "Bank account already exists!"
            cambed.description = f"Balance is: {balance['balance']}$"
        cambed.description += "\nYou can gain money by using other commands!"
        await ctx.reply(embed=cambed)

    # DeleteAccount
    @commands.hybrid_command(
        name="deleteaccount", aliases=["da"], description="Deletes your bank account"
    )
    async def deleteaccount(self, ctx: commands.Context):
        balance = await self.bot.mongodb.economy.find_one({"user_id": ctx.author.id})
        dambed = discord.Embed(color=self.bot.color, timestamp=ctx.message.created_at)
        dambed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        if not balance:
            dambed.title = "You don't have a bank account!"
            dambed.description = "At first you need to create a bank account"
            return await ctx.reply(embed=dambed)
        dambed.title = "Deleting your bank account!"
        dambed.description = "Are you sure you want to delete you bank account ?\nEverything will be gone\nBut you can create another bank account later"
        view = confirm.ViewConfirm(ctx)
        view.message = await ctx.reply(embed=dambed, view=view)
        await view.wait()
        if view.value:
            await self.bot.mongodb.economy.delete_one({"user_id": ctx.author.id})
            dambed.title = "Deleted your bank account!"
            dambed.description = "But you can still create another bank account!"
            await view.message.edit(embed=dambed)

    # GiveMoney
    @commands.hybrid_command(
        name="givemoney",
        aliases=["gm"],
        description="Gives the amount of given money from your balance to the given user",
        brief="<user> <amount>",
    )
    @discord.app_commands.describe(
        amount="The amount of money you want to give to the user",
        user="The user you want to give money to",
    )
    async def givemoney(self, ctx: commands.Context, amount: int, user: discord.User):
        author = await self.bot.mongodb.economy.find_one({"user_id": ctx.author.id})
        giving = await self.bot.mongodb.economy.find_one({"user_id": user.id})
        gmbed = discord.Embed(color=self.bot.color, timestamp=ctx.message.created_at)
        gmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        if author:
            if not giving:
                gmbed.title = f"{user.name} doesn't have a bank account!"
            elif amount > author["balance"]:
                gmbed.title = f"You don't have enough money!"
            else:
                await self.bot.mongodb.economy.update_one(
                    {"user_id": ctx.author.id},
                    {
                        "$set": {
                            "balance": author["balance"] - amount,
                            "transitions": f"{author['transitions']}\nGave {amount}$ to {user.display_avatar}",
                        }
                    },
                )
                await self.bot.mongodb.economy.update_one(
                    {"user_id": user.id},
                    {
                        "$set": {
                            "balance": giving["balance"] + amount,
                            "transitions": f"{giving['transitions']}\nGot {amount}$ from {ctx.author.name}",
                        }
                    },
                )
                gmbed.title = "Money has been transfered!"
                gmbed.add_field(
                    name="Transfer:",
                    value=f"{amount}$ has been removed from {ctx.author.mention}!\n{amount}$ has been added to {user.mention}!",
                    inline=False,
                )
                gmbed.add_field(
                    name="Balance",
                    value=f"{user.mention} now has {giving['balance']+amount}$!\n{ctx.author.mention} now has {author['balance']-amount}$!",
                    inline=False,
                )
        else:
            gmbed.title = f"You don't have a bank account!"
        await ctx.reply(embed=gmbed)

    # Balance
    @commands.hybrid_command(
        name="balance", aliases=["bal"], description="Shows your balance"
    )
    async def balance(self, ctx: commands.Context):
        author = await self.bot.mongodb.economy.find_one({"user_id": ctx.author.id})
        balmbed = discord.Embed(color=self.bot.color, timestamp=ctx.message.created_at)
        balmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        if author:
            balmbed.title = "Balance!"
            balmbed.description = f"Balance is: {author['balance']}$"
        else:
            balmbed.title = f"You don't have a bank account!"
        await ctx.reply(embed=balmbed)

    # Transitions
    @commands.hybrid_command(
        name="transitions", aliases=["tn"], description="Shows your transitions"
    )
    async def transitions(self, ctx: commands.Context):
        author = await self.bot.mongodb.economy.find_one({"user_id": ctx.author.id})
        tnmbed = discord.Embed(color=self.bot.color, timestamp=ctx.message.created_at)
        tnmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        if author:
            tnmbed.title = "Transitions!"
            tnmbed.description = (
                author["transitions"]
                if len(author["transitions"]) > 1
                else "You don't have any transitions"
            )
        else:
            tnmbed.title = f"You don't have a bank account!"
        await ctx.reply(embed=tnmbed)

    # Daily
    @commands.hybrid_command(
        name="daily",
        aliases=["di"],
        description="Adds a random amount of money to your balance, per day",
    )
    @commands.cooldown(1, 86400, commands.BucketType.user)
    async def daily(self, ctx: commands.Context):
        author = await self.bot.mongodb.economy.find_one({"user_id": ctx.author.id})
        dimbed = discord.Embed(color=self.bot.color, timestamp=ctx.message.created_at)
        dimbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        if author:
            dimbed.title = "Daily!"
            payback = random.randrange(1, 500)
            await self.bot.mongodb.economy.update_one(
                {"user_id": ctx.author.id},
                {
                    "$set": {
                        "balance": author["balance"] + payback,
                        "transitions": f"{author['transitions']}\nGot {payback}$ from Daily",
                    }
                },
            )
            dimbed.add_field(
                name="Transfer:",
                value=f"{payback}$ has been added to {ctx.author.mention}!",
                inline=False,
            )
            dimbed.add_field(
                name="Balance:",
                value=f"{ctx.author.mention} now has {author['balance']+payback}$!",
                inline=False,
            )
        else:
            dimbed.title = f"You don't have a bank account!"
        await ctx.reply(embed=dimbed)

    # Weekly
    @commands.hybrid_command(
        name="weekly",
        aliases=["wk"],
        description="Adds a random amount of money to your balance, per week",
    )
    @commands.cooldown(1, 604800, commands.BucketType.user)
    async def weekly(self, ctx: commands.Context):
        author = await self.bot.mongodb.economy.find_one({"user_id": ctx.author.id})
        wkmbed = discord.Embed(color=self.bot.color, timestamp=ctx.message.created_at)
        wkmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        if author:
            wkmbed.title = "Weekly!"
            payback = random.randrange(500, 1000)
            await self.bot.mongodb.economy.update_one(
                {"user_id": ctx.author.id},
                {
                    "$set": {
                        "balance": author["balance"] + payback,
                        "transitions": f"{author['transitions']}\nGot {payback}$ from Weekly",
                    }
                },
            )
            wkmbed.add_field(
                name="Transfer:",
                value=f"{payback}$ has been added to {ctx.author.mention}!",
                inline=False,
            )
            wkmbed.add_field(
                name="Balance:",
                value=f"{ctx.author.mention} now has {author['balance']+payback}$!",
                inline=False,
            )
        else:
            wkmbed.title = f"YOu don't have a bank account!"
        await ctx.reply(embed=wkmbed)


async def setup(bot):
    await bot.add_cog(Economy(bot))
