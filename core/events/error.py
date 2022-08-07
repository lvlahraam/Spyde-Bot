import discord, traceback
from discord.ext import commands


class OnError(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(
        self, ctx: commands.Context, error: commands.CommandError
    ):
        if isinstance(error, commands.CommandInvokeError):
            error = error.original
        print(
            "".join(traceback.format_exception(type(error), error, error.__traceback__))
        )
        errmbed = discord.Embed(
            color=self.bot.color,
            title=f"❌ An Error Occurred: {ctx.command}",
            description=f"- {error}",
            timestamp=ctx.message.created_at,
        )
        errmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        await ctx.reply(embed=errmbed)


async def setup(bot):
    await bot.add_cog(OnError(bot))
