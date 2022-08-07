import discord, random
from discord.ext import commands


class CounterView(discord.ui.View):
    def __init__(self, ctx):
        super().__init__(timeout=5)
        self.ctx = ctx
        self.clicks = 0
        self.clickers = {}

    @discord.ui.button(emoji="👏", style=discord.ButtonStyle.green)
    async def click(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(view=button.view)
        self.clicks += 1
        self.clickers[interaction.user] = (
            1
            if not self.clickers.get(interaction.user)
            else self.clickers[interaction.user] + 1
        )

    async def on_timeout(self):
        otmbed = discord.Embed(
            color=self.ctx.bot.color,
            description="",
            timestamp=self.ctx.message.created_at,
        )
        if self.clicks > 0:
            otmbed.title = f"Button was clicked {self.clicks} times"
            for user, click in self.clickers.items():
                otmbed.description += f"{user.mention} clicked {click} times\n"
        else:
            otmbed.title = "No one clicked the button"
        otmbed.set_footer(
            text=self.ctx.author, icon_url=self.ctx.author.display_avatar.url
        )
        await self.message.edit(embed=otmbed, view=None)


class NitroView(discord.ui.View):
    def __init__(self, ctx):
        super().__init__(timeout=None)
        self.ctx = ctx

    @discord.ui.button(label="ACCEPT", style=discord.ButtonStyle.green)
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            content="https://imgur.com/NQinKJB", ephemeral=True
        )


class Fun(commands.Cog, description="You sad? Use these to at least have a smile!"):
    def __init__(self, bot):
        self.bot = bot

    # Say
    @commands.hybrid_command(
        name="say", aliases=["sy"], description="Says the given text"
    )
    @discord.app_commands.describe(text="The text you want the bot to say")
    async def say(self, ctx: commands.Context, *, text: str):
        await ctx.reply(f"{text} | {ctx.author.mention}")

    # Sarcasm
    @commands.hybrid_command(
        name="sarcasm",
        aliases=["sm"],
        description="Says the given text in a sarcastic way",
    )
    @discord.app_commands.describe(
        text="The text you want the bot to say in a sarcastic way"
    )
    async def sarcasm(self, ctx: commands.Context, *, text: str):
        await ctx.reply(
            f"{''.join(c.upper() if i % 2 == 0 else c for i, c in enumerate(text))} | {ctx.author.mention}"
        )

    # PP
    @commands.hybrid_command(
        name="ppsize",
        aliases=["pp"],
        description="Tells yours or the given user's pp size",
    )
    @discord.app_commands.describe(user="The user to get the pp size from")
    async def pp(self, ctx: commands.Context, user: discord.User = None):
        user = user or ctx.author
        size = random.randint(1, 35)
        ppmbed = discord.Embed(
            color=self.bot.color,
            title=f"{user.name}'s PP Size:",
            description=f"8{'='*size}D ({size}cm)",
            timestamp=ctx.message.created_at,
        )
        ppmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        await ctx.reply(embed=ppmbed)

    # Counter
    @commands.hybrid_command(
        name="counter", aliases=["ctr"], description="Starts an counter"
    )
    async def counter(self, ctx: commands.Context):
        ctrmbed = discord.Embed(
            color=self.bot.color,
            title="Click the button for counting",
            timestamp=ctx.message.created_at,
        )
        ctrmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        view = CounterView(ctx)
        view.message = await ctx.reply(embed=ctrmbed, view=view)

    # Nitro
    @commands.hybrid_command(
        name="nitro", aliases=["nt"], description="Gifts free Nitro"
    )
    async def nitro(self, ctx: commands.Context):
        bnitrombed = discord.Embed(
            color=self.bot.color,
            title="A WILD NITRO GIFT APPEARS?!",
            description="Expires in 48 hours\nClick the button for claiming Nitro.",
            timestamp=ctx.message.created_at,
        )
        bnitrombed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        view = NitroView(ctx)
        view.message = await ctx.reply(embed=bnitrombed, view=view)

    # Meme
    @commands.hybrid_command(
        name="meme", aliases=["me"], description="Shows a random meme"
    )
    async def meme(self, ctx: commands.Context):
        session = await self.bot.session.get("https://some-random-api.ml/meme")
        response = await session.json()
        membed = discord.Embed(
            color=self.bot.color,
            title="Here is a random meme for you",
            description=f"{response['caption']} - {response['category'].title()}",
            timestamp=ctx.message.created_at,
        )
        membed.set_image(url=response["image"])
        membed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        await ctx.reply(embed=membed)

    # Quote
    @commands.command(
        name="quote", aliases=["qe"], description="Tells you a random quote"
    )
    async def quote(self, ctx: commands.Context):
        mode = random.choice(["quotes", "today", "author", "random"])
        session = await self.bot.session.get(f"https://zenquotes.io/api/{mode}")
        response = await session.json(content_type=None)
        qembed = discord.Embed(
            color=self.bot.color,
            title="Here is a random quote",
            timestamp=ctx.message.created_at,
        )
        qembed.add_field(name="Quote:", value=response[0]["q"], inline=False)
        qembed.add_field(name="Author", value=response[0]["a"], inline=False)
        qembed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        await ctx.reply(embed=qembed)


async def setup(bot):
    await bot.add_cog(Fun(bot))
