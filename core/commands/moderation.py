from re import L
import discord, typing
from discord.ext import commands


class Moderation(commands.Cog, description="Was someone being bad?"):
    def __init__(self, bot):
        self.bot = bot

    # Clear
    @commands.hybrid_command(
        name="clear",
        aliases=["cr"],
        description="Deletes messages for the given amount",
        brief="<amount>",
    )
    @commands.guild_only()
    @commands.has_guild_permissions(manage_messages=True)
    @commands.bot_has_guild_permissions(manage_messages=True)
    @discord.app_commands.describe(amount="The amount of messages you want to delete")
    async def clear(self, ctx: commands.Context, amount: int):
        crmbed = discord.Embed(color=self.bot.color, timestamp=ctx.message.created_at)
        crmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        if amount > 100:
            crmbed.title = "Can't clear more than 100 messages"
        else:
            deleted = await ctx.channel.purge(limit=amount + 1)
            crmbed.title = f"Deleted {len(deleted)} amount of messages"
        await ctx.reply(embed=crmbed, delete_after=5)

    # Ban
    @commands.hybrid_command(
        name="ban",
        aliases=["bn"],
        description="Bans the given member [for the given reason]",
        brief="<member> [reason]",
    )
    @commands.guild_only()
    @commands.has_guild_permissions(ban_members=True)
    @commands.bot_has_guild_permissions(ban_members=True)
    @discord.app_commands.describe(
        member="The member you want to ban", reason="The reason for banning the member"
    )
    async def ban(
        self, ctx: commands.Context, member: discord.Member, reason: str = None
    ):
        reason = reason or f"Unspecified"
        bnmbed = discord.Embed(color=self.bot.color, timestamp=ctx.message.created_at)
        bnmbed.add_field(name="Member:", value=member.mention, inline=False)
        bnmbed.add_field(name="Moderator:", value=ctx.author.mention, inline=False)
        bnmbed.add_field(name="Reason:", value=reason, inline=False)
        bnmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        if ctx.author.top_role.position > member.top_role.position:
            bnmbed.title = "Banned:"
            await ctx.guild.ban(member, reason=reason)
        else:
            bnmbed.title = "You can't ban this member!"
        await ctx.reply(embed=bnmbed)

    # Unban
    @commands.hybrid_command(
        name="unban",
        aliases=["un"],
        description="Unbans the given user [for the given reason]",
        brief="<user> [reason]",
    )
    @commands.guild_only()
    @commands.has_guild_permissions(ban_members=True)
    @commands.bot_has_guild_permissions(ban_members=True)
    @discord.app_commands.describe(
        user="The user you want to unban", reason="The reason for unbanning the user"
    )
    async def unban(
        self, ctx: commands.Context, user: discord.User, reason: str = None
    ):
        reason = reason or "Unspecified"
        unmbed = discord.Embed(
            color=self.bot.color, title="Unbanned:", timestamp=ctx.message.created_at
        )
        unmbed.add_field(name="User:", value=user.mention, inline=False)
        unmbed.add_field(name="Moderator:", value=ctx.author.mention, inline=False)
        unmbed.add_field(name="Reason:", value=reason, inline=False)
        unmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        await ctx.guild.unban(user=user, reason=reason)
        await ctx.reply(embed=unmbed)

    # Kick
    @commands.hybrid_command(
        name="kick",
        aliases=["kc"],
        description="Kicks the given member [for the given reason]",
        brief="<member> [reason]",
    )
    @commands.guild_only()
    @commands.has_guild_permissions(kick_members=True)
    @commands.bot_has_guild_permissions(kick_members=True)
    @discord.app_commands.describe(
        member="The member you want to kick", reason="The reason for kicking the member"
    )
    async def kick(
        self, ctx: commands.Context, member: discord.Member, reason: str = None
    ):
        reason = reason or "Unspecified"
        kcmbed = discord.Embed(color=self.bot.color, timestamp=ctx.message.created_at)
        kcmbed.add_field(name="Member:", value=member.mention, inline=False)
        kcmbed.add_field(name="Moderator:", value=ctx.author.mention, inline=False)
        kcmbed.add_field(name="Reason:", value=reason, inline=False)
        kcmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        if ctx.author.top_role.position > member.top_role.position:
            kcmbed.title = "Kicked:"
            await ctx.guild.kick(member, reason=reason)
        else:
            kcmbed.title = "You can't kick this user!"
        await ctx.reply(embed=kcmbed)

    # Warn
    @commands.hybrid_command(
        name="warn",
        aliases=["wn"],
        description="Shows or Adds or Removes a Warn from the user [based on the given reason and option]",
    )
    @commands.guild_only()
    @commands.has_guild_permissions(ban_members=True)
    @commands.bot_has_guild_permissions(ban_members=True)
    @discord.app_commands.describe(
        option="Do you want to add or remove or clear the warn(s) or do you want to show the warns",
        member="The memebr you want to add or remove or show the warn(s) from",
        extra="The reason for adding or the number for removing a warn",
    )
    async def warn(
        self,
        ctx: commands.Context,
        option: typing.Literal["show", "add", "remove", "clear"],
        member: discord.Member,
        *,
        extra: str = None,
    ):
        wnmbed = discord.Embed(
            color=self.bot.color, description="", timestamp=ctx.message.created_at
        )
        wnmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        warns = await self.bot.mongodb.warns.find(
            {"guild_id": ctx.guild.id, "user_id": member.id}
        ).to_list(length=None)
        if option == "show":
            if not warns:
                wnmbed.title = "User doesn't have any warns to show"
            else:
                wnmbed.title = "User's Warns:"
                for warn in warns:
                    wnmbed.description += (
                        f"{warn['number']}. {warn['reason']} ({warn['moderator']})\n"
                    )
        elif option == "add":
            warnban = await self.bot.mongodb.warnbans.find_one(
                {"guild_id": ctx.guild.id}
            )
            extra = extra or "Unspecified"
            if warnban and len(warns) + 1 == warnban["number"]:
                wnmbed.title += "User has been banned (WarnBan)"
                wnmbed.description += "Cause they reached the number for warnban"
                await self.bot.mongodb.warns.delete_one(
                    {"guild_id": ctx.guild.id, "user_id": member.id}
                )
                await ctx.guild.ban(user=member, reason=extra)
            else:
                await self.bot.mongodb.warns.insert_one(
                    {
                        "guild_name": ctx.guild.name,
                        "guild_id": ctx.guild.id,
                        "user_name": member.name,
                        "user_id": member.id,
                        "number": len(warns) + 1,
                        "reason": extra,
                        "moderator": ctx.author.name,
                    }
                )
                wnmbed.title = "Added a warn to User's Warns:"
                wnmbed.description += f"Reason: {extra}\nModerator: {ctx.author.name}"
        elif option == "remove":
            if not extra:
                wnmbed.title = (
                    "You need to pass the reason of the warn you want to remove"
                )
            else:
                if extra.isdigit():
                    warn = await self.bot.mongodb.warns.find_one(
                        {
                            "guild_id": ctx.guild.id,
                            "user_id": member.id,
                            "number": int(extra),
                        }
                    )
                    if not warn:
                        wnmbed.title = "User doesn't have a warn with the given number"
                    else:
                        wnmbed.title = "User's warn have been removed"
                        wnmbed.description += (
                            f"{warn['number']}. {warn['reason']} ({warn['moderator']})"
                        )
                        await self.bot.mongodb.warns.delete_one(
                            {
                                "guild_id": ctx.guild.id,
                                "user_id": member.id,
                                "number": int(extra),
                            }
                        )
                        counter = 1
                        newwarns = await self.bot.mongodb.warns.find(
                            {"guild_id": ctx.guild.id, "user_id": member.id}
                        ).to_list(length=None)
                        for warn in newwarns:
                            await self.bot.mongodb.warns.update_one(
                                {
                                    "guild_id": ctx.guild.id,
                                    "user_id": member.id,
                                    "reason": warn["reason"],
                                },
                                {"$set": {"number": counter}},
                            )
                            counter += 1
                else:
                    wnmbed.title = "For removing a warn you must pass a number"
        else:
            if not warns:
                wnmbed.title = "User doesn't have a warn with the given number"
            else:
                wnmbed.title = "Cleared user's warns:"
                for warn in warns:
                    wnmbed.description += (
                        f"{warn['number']}. {warn['reason']} ({warn['moderator']})\n"
                    )
                await self.bot.mongodb.warns.delete_many(
                    {"guild_id": ctx.guild.id, "user_id": member.id}
                )
        await ctx.reply(embed=wnmbed)

    # WarnBan
    @commands.hybrid_command(
        name="warnban",
        aliases=["wbn"],
        description="Turns On or Off or Changes the specfic given number for banning the user when the user's warns reaches that",
    )
    @commands.guild_only()
    @commands.has_guild_permissions(ban_members=True)
    @commands.bot_has_guild_permissions(ban_members=True)
    @discord.app_commands.describe(
        option="Do you want to turn on or turn off",
        number="The number for when a user reaches it and would get banned",
    )
    async def warnban(
        self,
        ctx: commands.Context,
        option: typing.Literal["on", "change", "off"],
        number: int = None,
    ):
        wbnmbed = discord.Embed(color=self.bot.color, timestamp=ctx.message.created_at)
        wbnmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        warnban = await self.bot.mongodb.warnbans.find_one({"guild_id": ctx.guild.id})
        if option == "on":
            if warnban:
                wbnmbed.title = "WarnBan is already on"
                wbnmbed.description = "You can try to change it"
            else:
                if not number:
                    wbnmbed.title = "You need to pass a number"
                else:
                    wbnmbed.title = f"WarnBan has been turned on with {number}"
                    await self.bot.mongodb.warnbans.insert_one(
                        {
                            "guild_name": ctx.guild.name,
                            "guild_id": ctx.guild.id,
                            "number": number,
                        }
                    )
        elif option == "change":
            if not warnban:
                wbnmbed.title = "WarnBan is not on"
            else:
                if not number:
                    wbnmbed.title = "You need to pass a number"
                else:
                    wbnmbed.title = f"WarnBan has been changed to {number}"
                    await self.bot.mongodb.warnbans.update_one(
                        {"guild_id": ctx.guild.id}, {"$set": {"number": number}}
                    )
        else:
            if not warnban:
                wbnmbed.title = "WarnBan is already off"
            else:
                wbnmbed.title = "WarnBan has been turned off"
                await self.bot.mongodb.warnbans.delete_one({"guild_id": ctx.guild.id})
        await ctx.reply(embed=wbnmbed)


async def setup(bot):
    await bot.add_cog(Moderation(bot))
