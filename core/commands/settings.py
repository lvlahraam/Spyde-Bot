import discord, typing
from discord.ext import commands


class Settings(commands.Cog, description="Setting up the bot with these!"):
    def __init__(self, bot):
        self.bot = bot

    # Prefix
    @commands.hybrid_command(
        name="prefix",
        aliases=["pf"],
        description="Setting up the prefix with this",
        brief="set - reset - show",
    )
    @commands.guild_only()
    @commands.has_guild_permissions(administrator=True)
    @discord.app_commands.describe(
        options="The option you want use", prefix="The prefix you want to set"
    )
    async def prefix(
        self,
        ctx: commands.Context,
        options: typing.Literal["set", "reset", "show"],
        *,
        prefix: str = None,
    ):
        pfmbed = discord.Embed(color=self.bot.color, timestamp=ctx.message.created_at)
        pfmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        if options == "set":
            if not ctx.author.guild_permissions.administrator:
                raise commands.MissingPermissions(["administrator"])
            elif not prefix:
                pfmbed.title = "You need to pass a string for prefix"
            else:
                pfmbed.description = prefix
                if prefix == self.bot.prefixes[ctx.guild.id]:
                    pfmbed.title = "Prefix is the same"
                else:
                    data = await self.bot.mongodb.prefixes.find_one(
                        {"guild_id": ctx.guild.id}
                    )
                    if not data:
                        await self.bot.mongodb.prefixes.insert_one(
                            {
                                "guild_name": ctx.guild.name,
                                "guild_id": ctx.guild.id,
                                "prefix": prefix,
                            }
                        )
                    else:
                        await self.bot.mongodb.prefixes.update_one(
                            {"guild_id": ctx.guild.id}, {"$set": {"prefix": prefix}}
                        )
                    self.bot.prefixes[ctx.guild.id] = prefix
                    pfmbed.title = "Changed prefix:"
        elif options == "reset":
            if not ctx.author.guild_permissions.administrator:
                raise commands.MissingPermissions(["administrator"])
            pfmbed.description = self.bot.default_prefix
            data = await self.bot.mongodb.prefixes.find_one({"guild_id": ctx.guild.id})
            if data:
                await self.bot.mongodb.prefixes.delete_one({"guild_id": ctx.guild.id})
                pfmbed.title = "Resetted to:"
                self.bot.prefixes[ctx.guild.id] = self.bot.default_prefix
            else:
                pfmbed.title = "Prefix was never changed"
                self.bot.prefixes[ctx.guild.id]
        elif options == "show":
            pfmbed.title = f"Current prefix:"
            pfmbed.description = self.bot.prefixes.get(ctx.guild.id)
        await ctx.reply(embed=pfmbed)


async def setup(bot):
    await bot.add_cog(Settings(bot))
