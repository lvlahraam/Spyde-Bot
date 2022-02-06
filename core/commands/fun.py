import discord, random
from discord.ext import commands

class CounterView(discord.ui.View):
    def __init__(self, ctx):
        super().__init__(timeout=5)
        self.ctx = ctx
        self.clicks = 0
        self.clickers = {}
    @discord.ui.button(emoji="👏", style=discord.ButtonStyle.green)
    async def click(self, button:discord.ui.Button, interaction:discord.Interaction):
        await interaction.response.edit_message(view=button.view)
        self.clicks += 1
        self.clickers[interaction.user] = 1 if not self.clickers.get(interaction.user) else self.clickers[interaction.user] + 1

    async def on_timeout(self):
        otmbed = discord.Embed(
            color=self.ctx.bot.color,
            description="",
            timestamp=self.ctx.message.created_at
        )
        if self.clicks > 0:
            otmbed.title = F"Button was clicked {self.clicks} times"
            for user, click in self.clickers.items():
                otmbed.description += F"{user.mention} clicked {click} times\n"
        else:
            otmbed.title = ("No one clicked the button")
        otmbed.set_footer(text=self.ctx.author, icon_url=self.ctx.author.display_avatar.url)
        await self.message.edit(embed=otmbed, view=None)

class NitroView(discord.ui.View):
    def __init__(self, ctx):
        super().__init__(timeout=None)
        self.ctx = ctx
    @discord.ui.button(label="ACCEPT", style=discord.ButtonStyle.green)
    async def accept(self, button:discord.ui.Button, interaction:discord.Interaction):
        await interaction.response.send_message(content="https://imgur.com/NQinKJB", ephemeral=True)

class Fun(commands.Cog, description="You sad? Use these to at least have a smile!"):
    def __init__(self, bot):
        self.bot = bot

    # Say
    @commands.command(name="say", help="Says the given text")
    async def say(self, ctx:commands.Context, *, text:str=commands.Option(description="The text to say")):
        await ctx.reply(F"{text} | {ctx.author.mention}")

    # Sarcasm
    @commands.command(name="sarcasm", help="Says the given text in a sarcastic way")
    async def sarcasm(self, ctx:commands.Context, *, text:str=commands.Option(description="The text you want to be sarcastic")):
        await ctx.reply(F"{''.join(c.upper() if i % 2 == 0 else c for i, c in enumerate(text))} | {ctx.author.mention}")

    # PP
    @commands.command(name="pp", help="Tells yours or the given user's pp size")
    async def pp(self, ctx:commands.Context, user:discord.User=commands.Option(description="The user to get the pp size of", default=None)):
        user = user or ctx.author
        size = random.randint(1, 35)
        ppmbed = discord.Embed(
            color=self.bot.color,
            title=F"{user.name}'s PP Size:",
            description=F"8{'='*size}D ({size}cm)",
            timestamp=ctx.message.created_at
        )
        ppmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        await ctx.reply(embed=ppmbed)

    # Counter
    @commands.command(name="counter", aliases=["ctr"], help="Starts an counter")
    async def counter(self, ctx:commands.Context):
        ctrmbed = discord.Embed(
            color=self.bot.color,
            title="Click the button for counting",
            timestamp=ctx.message.created_at
        )
        ctrmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        view = CounterView(ctx)
        view.message = await ctx.reply(embed=ctrmbed, view=view)

    # Nitro
    @commands.command(name="nitro", help="Gifts free Nitro")
    async def nitro(self, ctx:commands.Context):
        bnitrombed = discord.Embed(
            color=self.bot.color,
            title="A WILD NITRO GIFT APPEARS?!",
            description="Expires in 48 hours\nClick the button for claiming Nitro.",
            timestamp=ctx.message.created_at
        )
        bnitrombed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        view = NitroView(ctx)
        view.message = await ctx.reply(embed=bnitrombed, view=view)

    # Meme
    @commands.command(name="meme", aliases=["me"], help="Shows a random meme")
    async def meme(self, ctx:commands.Context):
        session = await self.bot.session.get("https://some-random-api.ml/meme")
        response = await session.json()
        membed = discord.Embed(
            color=self.bot.color,
            title="Here is a random meme for you",
            description=F"{response['caption']} - {response['category'].title()}",
            timestamp=ctx.message.created_at
        )
        membed.set_image(url=response['image'])
        membed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        await ctx.reply(embed=membed)

    # Quote
    @commands.command(name="quote", aliases=["qe"], help="Tells you a random quote")
    async def quote(self, ctx:commands.Context):
        mode = random.choice(["quotes", "today", "author", "random"])
        session = await self.bot.session.get(F"https://zenquotes.io/api/{mode}")
        response = await session.json(content_type=None)
        qembed = discord.Embed(
            color=self.bot.color,
            title="Here is a random quote",
            timestamp=ctx.message.created_at
        )
        qembed.add_field(name="Quote:", value=response[0]["q"], inline=False)
        qembed.add_field(name="Author", value=response[0]["a"], inline=False)
        qembed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        await ctx.reply(embed=qembed)

def setup(bot):
    bot.add_cog(Fun(bot))
