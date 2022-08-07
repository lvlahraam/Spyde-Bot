import discord, asyncio, typing, string, random
from discord.ext import commands
from core.views import confirm


class Utility(commands.Cog, description="Useful stuff that are open to everyone"):
    def __init__(self, bot):
        self.bot = bot

    # Cleanup
    @commands.hybrid_command(
        name="cleanup",
        aliases=["cu"],
        description="Deletes bot's messagess for the given amount",
        brief="<amount>",
    )
    @commands.guild_only()
    @discord.app_commands.describe(
        amount="The amount of the bot message you want to cleanup"
    )
    async def cleanup(self, ctx: commands.Context, *, amount: int):
        cumbed = discord.Embed(
            color=self.bot.color,
            title=f"Cleaned-up {amount} of bot messages",
        )
        cumbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        await ctx.channel.purge(
            limit=amount, check=lambda m: m.author.id == ctx.me.id, bulk=False
        )
        await ctx.reply(embed=cumbed, delete_after=5)

    # AwayFromKeyboard
    @commands.hybrid_command(
        name="awayfromkeyboard",
        aliases=["afk"],
        description="Makes you AFK [for the given reason]",
        brief="[reason]",
    )
    @commands.guild_only()
    @discord.app_commands.describe(reason="The reason for going afk")
    async def afk(self, ctx: commands.Context, *, reason: str = None):
        reason = reason or "Unspecified"
        afk = self.bot.afks.get(ctx.author.id)
        afkmbed = discord.Embed(color=self.bot.color, timestamp=ctx.message.created_at)
        afkmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        if not afk:
            afk = self.bot.afks[ctx.author.id] = {
                "time": discord.utils.utcnow(),
                "reason": reason,
                "jump_url": ctx.message.jump_url,
            }
            view = discord.ui.View()
            view.add_item(
                item=discord.ui.Button(
                    label="Go to original message", url=afk["jump_url"]
                )
            )
            afkmbed.title = "Set your AFK"
            afkmbed.description = f"Reason: **{afk['reason']}**"
            await ctx.reply(embed=afkmbed)


async def setup(bot):
    await bot.add_cog(Utility(bot))
