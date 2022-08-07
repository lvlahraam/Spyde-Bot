import discord, random
from discord.ext import commands


class RPSButtons(discord.ui.Button):
    def __init__(self, view, **kwargs):
        super().__init__(**kwargs)
        self.ctx = view.ctx
        self.botoption = view.botoption
        self.useroption = view.useroption

    async def callback(self, interaction: discord.Interaction):
        if self.label == "Rock":
            self.useroption = "Rock"
        elif self.label == "Paper":
            self.useroption = "Paper"
        elif self.label == "Scissors":
            self.useroption = "Scissors"
        self.view.clear_items()
        if self.useroption == self.botoption:
            tierpsmbed = discord.Embed(
                color=self.ctx.bot.color,
                description=f"We both chose **{self.botoption}**, __It's a tie__",
                timestamp=interaction.message.created_at,
            )
            tierpsmbed.set_footer(
                text=interaction.user, icon_url=interaction.user.display_avatar.url
            )
            await interaction.response.edit_message(embed=tierpsmbed, view=self.view)
        else:
            if (
                self.useroption == "Rock"
                and self.botoption == "Scissors"
                or self.useroption == "Paper"
                and self.botoption == "Rock"
                or self.useroption == "Scissors"
                and self.botoption == "Paper"
            ):
                wonrpsmbed = discord.Embed(
                    color=self.ctx.bot.color,
                    description=f"You chose **{self.useroption}** & I chose **{self.botoption}**, __You won **|** I lost__",
                    timestamp=interaction.message.created_at,
                )
                wonrpsmbed.set_footer(
                    text=interaction.user, icon_url=interaction.user.display_avatar.url
                )
                await interaction.response.edit_message(
                    embed=wonrpsmbed, view=self.view
                )
            elif (
                self.useroption == "Scissors"
                and self.botoption == "Rock"
                or self.useroption == "Rock"
                and self.botoption == "Paper"
                or self.useroption == "Paper"
                and self.botoption == "Scissors"
            ):
                lostrpsmbed = discord.Embed(
                    color=self.ctx.bot.color,
                    description=f"I chose **{self.botoption}** & You chose **{self.useroption}**, __I won **|** You lost__",
                    timestamp=interaction.message.created_at,
                )
                lostrpsmbed.set_footer(
                    text=interaction.user, icon_url=interaction.user.display_avatar.url
                )
                await interaction.response.edit_message(
                    embed=lostrpsmbed, view=self.view
                )


class RPSView(discord.ui.View):
    def __init__(self, ctx):
        super().__init__(timeout=None)
        self.ctx = ctx
        self.botoption = random.choice(["Rock", "Paper", "Scissors"])
        self.useroption = ""
        self.add_item(
            item=RPSButtons(
                emoji="🗻", label="Rock", style=discord.ButtonStyle.green, view=self
            )
        )
        self.add_item(
            item=RPSButtons(
                emoji="🧻", label="Paper", style=discord.ButtonStyle.red, view=self
            )
        )
        self.add_item(
            item=RPSButtons(
                emoji="✂️",
                label="Scissors",
                style=discord.ButtonStyle.blurple,
                view=self,
            )
        )

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id == self.ctx.author.id:
            return True
        else:
            icheckmbed = discord.Embed(
                color=self.ctx.bot.color,
                title=f"You can't use this",
                description=f"{interaction.user.mention} - Only {self.ctx.author.mention} can use this\nCause they did the command\nIf you want to use this, do what they did",
                timestamp=interaction.message.created_at,
            )
            icheckmbed.set_author(
                name=interaction.user, icon_url=interaction.user.display_avatar.url
            )
            await interaction.response.send_message(embed=icheckmbed, ephemeral=True)
            return False


class CFButtons(discord.ui.Button):
    def __init__(self, view, **kwargs):
        super().__init__(**kwargs)
        self.ctx = view.ctx
        self.coinresult = view.coinresult
        self.botoption = view.botoption
        self.useroption = view.useroption

    async def callback(self, interaction: discord.Interaction):
        if self.label == "Heads":
            self.useroption = "Heads"
            self.botoption = "Tails"
        elif self.label == "Tails":
            self.useroption = "Tails"
            self.botoption = "Heads"
        self.view.clear_items()
        if self.useroption == self.coinresult:
            wonrpsmbed = discord.Embed(
                color=self.ctx.bot.color,
                description=f"You chose **{self.useroption}** & I chose **{self.botoption}**\nIt was **{self.coinresult}**, __You won **|** I lost__",
                timestamp=interaction.message.created_at,
            )
            wonrpsmbed.set_footer(
                text=interaction.user, icon_url=interaction.user.display_avatar.url
            )
            await interaction.response.edit_message(embed=wonrpsmbed, view=self.view)
        else:
            lostrpsmbed = discord.Embed(
                color=self.ctx.bot.color,
                description=f"I chose **{self.botoption}** & You chose **{self.useroption}**\nIt was **{self.coinresult}**, __I won **|** You lost__",
                timestamp=interaction.message.created_at,
            )
            lostrpsmbed.set_footer(
                text=interaction.user, icon_url=interaction.user.display_avatar.url
            )
            await interaction.response.edit_message(embed=lostrpsmbed, view=self.view)


class CFView(discord.ui.View):
    def __init__(self, ctx):
        super().__init__(timeout=None)
        self.ctx = ctx
        self.coinresult = random.choice(["Heads", "Tails"])
        self.botoption = ""
        self.useroption = ""
        self.add_item(
            item=CFButtons(
                emoji="💀", label="Heads", style=discord.ButtonStyle.red, view=self
            )
        )
        self.add_item(
            item=CFButtons(
                emoji="⚡", label="Tails", style=discord.ButtonStyle.green, view=self
            )
        )

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id == self.ctx.author.id:
            return True
        else:
            icheckmbed = discord.Embed(
                color=self.ctx.bot.color,
                title=f"You can't use this",
                description=f"{interaction.user.mention} - Only {self.ctx.author.mention} can use this\nCause they did the command\nIf you want to use this, do what they did",
                timestamp=interaction.message.created_at,
            )
            icheckmbed.set_author(
                name=interaction.user, icon_url=interaction.user.display_avatar.url
            )
            await interaction.response.send_message(embed=icheckmbed, ephemeral=True)
            return False


class GuessButtons(discord.ui.Button):
    def __init__(self, view, **kwargs):
        super().__init__(**kwargs)
        self.ctx = view.ctx
        self.choose = view.choose
        self.number = view.number

    async def callback(self, interaction: discord.Interaction):
        if self.label == self.number:
            self.choose = True
        elif self.label != self.number:
            self.choose = False
        self.view.clear_items()
        if self.choose == True:
            truembed = discord.Embed(
                color=self.ctx.bot.color,
                title="You guessed correctly",
                description=f"The number was **{self.number}**",
            )
            truembed.set_footer(
                text=interaction.user, icon_url=interaction.user.display_avatar.url
            )
            await interaction.response.edit_message(embed=truembed, view=self.view)
        else:
            falsembed = discord.Embed(
                color=self.ctx.bot.color,
                title="You guessed incorrectly",
                description=f"The correct answer was **{self.number}** but you chose **{self.label}**",
            )
            falsembed.set_footer(
                text=interaction.user, icon_url=interaction.user.display_avatar.url
            )
            await interaction.response.edit_message(embed=falsembed, view=self.view)


class GuessView(discord.ui.View):
    def __init__(self, ctx):
        super().__init__(timeout=None)
        self.ctx = ctx
        self.choose = None
        self.number = random.randint(0, 4)
        for _ in range(1, 5):
            self.add_item(
                item=GuessButtons(label=_, style=discord.ButtonStyle.green, view=self)
            )

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id == self.ctx.author.id:
            return True
        else:
            icheckmbed = discord.Embed(
                color=self.ctx.bot.color,
                title=f"You can't use this",
                description=f"{interaction.user.mention} - Only {self.ctx.author.mention} can use this\nCause they did the command\nIf you want to use this, do what they did",
                timestamp=interaction.message.created_at,
            )
            icheckmbed.set_author(
                name=interaction.user, icon_url=interaction.user.display_avatar.url
            )
            await interaction.response.send_message(embed=icheckmbed, ephemeral=True)
            return False


class Game(commands.Cog, description="Arcade but without having to go outside!"):
    def __init__(self, bot):
        self.bot = bot

    # RockPaperScissors
    @commands.hybrid_command(
        name="rockpaperscissors",
        aliases=["rps"],
        description="Starts an Rock-Paper-Scissors game",
    )
    async def rockpaperscissors(self, ctx: commands.Context):
        rpsmbed = discord.Embed(
            color=self.bot.color,
            description="Choose your tool with the buttons:",
            timestamp=ctx.message.created_at,
        )
        rpsmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        view = RPSView(ctx)
        view.message = await ctx.reply(embed=rpsmbed, view=view)

    # Coinflip
    @commands.hybrid_command(
        name="coinflip", aliases=["cf"], description="Starts an Coin-Flip game"
    )
    async def coinflip(self, ctx: commands.Context):
        cfmbed = discord.Embed(
            color=self.bot.color,
            description="Choose what you think the side would be with the buttons:",
            timestamp=ctx.message.created_at,
        )
        cfmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        view = CFView(ctx)
        view.message = await ctx.reply(embed=cfmbed, view=view)

    # Guess
    @commands.hybrid_command(
        name="guess", aliases=["gs"], description="Starts an Guessing game"
    )
    async def guess(self, ctx: commands.Context):
        gsmbed = discord.Embed(
            color=self.bot.color,
            description="Try to guess the number with the buttons:",
            timestamp=ctx.message.created_at,
        )
        gsmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        view = GuessView(ctx)
        view.message = await ctx.reply(embed=gsmbed, view=view)


async def setup(bot):
    await bot.add_cog(Game(bot))
