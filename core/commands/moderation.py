import discord, typing
from discord.ext import commands

class Moderation(commands.Cog, description="Was someone being bad?"):
    def __init__(self, bot):
        self.bot = bot

    # Ban
    @commands.command(name="ban", aliases=["bn"], help="Bans the given user")
    @commands.guild_only()
    @commands.has_guild_permissions(ban_members=True)
    @commands.bot_has_guild_permissions(ban_members=True)
    async def ban(self, ctx:commands.Context, member:discord.Member=commands.Option(description="The member you want to ban"), *, reason:str=commands.Option(description="The reason for banning the user", default=None)):
        reason = reason or "Unspecified"
        bnmbed = discord.Embed(
            color=self.bot.color,
            timestamp=ctx.message.created_at
        )
        bnmbed.add_field(name="User:", value=member.mention)
        bnmbed.add_field(name="Moderator:", value=ctx.author.mention)
        bnmbed.add_field(name="Reason:", value=reason)
        bnmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        if ctx.author.top_role.position > member.top_role.position:
            bnmbed.title = "Banned:"
            await ctx.guild.ban(member, reason=F"{ctx.author}\n{reason}")
        else:
            bnmbed.title = "You can't ban this user!"
        await ctx.reply(embed=bnmbed)

    # Unban
    @commands.command(name="unban", aliases=["un"], help="Unbans the given user")
    @commands.guild_only()
    @commands.has_guild_permissions(ban_members=True)
    @commands.bot_has_guild_permissions(ban_members=True)
    async def unban(self, ctx:commands.Context, user:discord.User=commands.Option(description="The user you want to unban"), *, reason:str=commands.Option(description="The reason for unbanning the user", default=None)):
        reason = reason or "Unspecified"
        unmbed = discord.Embed(
            color=self.bot.color,
            title="Unbanned:",
            timestamp=ctx.message.created_at
        )
        unmbed.add_field(name="User:", value=user.mention)
        unmbed.add_field(name="Moderator:", value=ctx.author.mention)
        unmbed.add_field(name="Reason:", value=reason)
        unmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        await ctx.guild.unban(user)
        await ctx.reply(embed=unmbed)

    # Kick
    @commands.command(name="kick", aliases=["kc"], help="Kicks the given user")
    @commands.guild_only()
    @commands.has_guild_permissions(kick_members=True)
    @commands.bot_has_guild_permissions(kick_members=True)
    async def kick(self, ctx:commands.Context, member:discord.Member=commands.Option(description="The member you want to kick"), *, reason:str=commands.Option(description="The reason for kicking the member", default=None)):
        reason = reason or "Unspecified"
        kcmbed = discord.Embed(
            color=self.bot.color,
            
            timestamp=ctx.message.created_at
        )
        kcmbed.add_field(name="Member:", value=member.mention)
        kcmbed.add_field(name="Moderator:", value=ctx.author.mention)
        kcmbed.add_field(name="Reason:", value=reason)
        kcmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        if ctx.author.top_role.position > member.top_role.position:
            kcmbed.title = "Kicked:"
            await ctx.guild.ban(member, reason=F"{ctx.author}\n{reason}")
        else:
            kcmbed.title = "You can't kick this user!"
        await ctx.guild.kick(user=member, reason=reason)
        await ctx.reply(embed=kcmbed)

    # Timeout
    @commands.command(name="timeout", aliases=["to"], help="Timeouts or Untimeoutes the given user based on the given option")
    @commands.guild_only()
    @commands.has_guild_permissions(moderate_members=True)
    @commands.bot_has_guild_permissions(moderate_members=True)
    async def timeout(self, ctx:commands.Context, member:discord.Member=commands.Option(description="The member you want to timeout"), option:typing.Literal["1minutes", "5minutes", "15minutes", "30minutes", "1hour", "6hour", "12hour", "1day", "1week", "untimeout"]=commands.Option(description="The duration/option for (un)timeouting the member"), *, reason:str=commands.Option(description="The reason for (un)timeouting the member", default=None)):
        reason = reason or "Unspecified"
        tombed = discord.Embed(
            color=self.bot.color,
            timestamp=ctx.message.created_at
        )
        tombed.add_field(name="Member:", value=member.mention)
        tombed.add_field(name="Moderator:", value=ctx.author.mention)
        tombed.add_field(name="Member:", value=reason)
        tombed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        if ctx.author.top_role.position > member.top_role.position:
            if option == "untimeout":
                if member.timeout_until:
                    tombed.title = "UnTimed-out"
                    await member.edit(timeout_until=None, reason=reason)
                    return await ctx.send(embed=tombed)
                tombed.title = "UnTimed-out Failed"
                tombed.description = "The member is not timed-out"
                return await ctx.send(embed=tombed)
            times = {
                "1minutes": 1,
                "5minutes": 5,
                "15minutes": 15,
                "30minutes": 30,
                "1hour": 60,
                "6hour": 360,
                "12hour": 720,
                "1day": 1440,
                "1week": 10080
            }
            until = times[option] * 60 * 1000
            tombed.title = "Timed-out"
            await member.edit(timeout_until=until, reason=reason)
        else:
            tombed.title = "You can't (un)timeout this user!"
        await ctx.send(embed=tombed)

    # Slowmode
    @commands.command(name="slowmode", aliases=["sm"], help="Changes the slowmode of this or the given channel to the given seconds")
    @commands.guild_only()
    @commands.has_guild_permissions(manage_channels=True)
    @commands.bot_has_guild_permissions(manage_channels=True)
    async def slowmode(self, ctx:commands.Context, times:typing.Literal["0seconds", "5seconds", "10seconds", "15seconds", "30seconds", "1minutes", "2minutes", "5minutes", "10minutes", "15minutes", "30minutes", "1hour", "2hour", "6hour"]=commands.Option(description="The seconds for slowmode"), channel:typing.Union[discord.TextChannel, discord.Thread]=commands.Option(description="The channel you want to change the slowmode of", default=None)):
        channel = channel or ctx.channel
        smmbed = discord.Embed(
            color=self.bot.color,
            title="Slowdown:",
            timestamp=ctx.message.created_at
        )
        smmbed.add_field(name="Channel:", value=channel.mention)
        smmbed.add_field(name="Slowmode:", value=times)
        smmbed.add_field(name="Moderator:", value=ctx.author.mention)
        smmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        seconds = {
            "0seconds": 0,
            "5seconds": 5,
            "10seconds": 10,
            "15seconds": 15,
            "30seconds": 30,
            "1minutes": 60,
            "2minutes": 120,
            "5minutes": 300,
            "10minutes": 600,
            "15minutes": 900,
            "30minutes": 1800,
            "1hour": 3600,
            "2hour": 7200,
            "6hour": 21600
        }
        await channel.edit(reason=F"Channel: {channel.mention}\nSeconds: {times}\nBy: {ctx.author}", slowmode_delay=seconds[times])
        await ctx.reply(embed=smmbed)

    # Lock
    @commands.command(name="lock", aliases=["lc"], help="Locks this or the given channel")
    @commands.guild_only()
    @commands.has_guild_permissions(manage_channels=True)
    @commands.bot_has_guild_permissions(manage_channels=True)
    async def lock(self, ctx:commands.Context, channel:typing.Union[discord.TextChannel, discord.StageChannel, discord.VoiceChannel, discord.Thread]=commands.Option(description="The channel you want to lock", default=None), *, reason:str=commands.Option(description="The reason for locking the channel", default=None)):
        channel = channel or ctx.channel
        reason = reason or "Unspecified"
        over = channel.overwrites_for(ctx.guild.default_role)
        over.connect = False
        over.speak = False
        over.request_to_speak = False
        over.send_messages = False
        over.add_reactions = False
        over.create_public_threads = False
        over.create_private_threads = False
        lcmbed = discord.Embed(
            color=self.bot.color,
            timestamp=ctx.message.created_at
        )
        lcmbed.add_field(name="Channel:", value=channel.mention)
        lcmbed.add_field(name="Moderator:", value=ctx.author.mention)
        lcmbed.add_field(name="Reason:", value=reason)
        lcmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        if not channel.permissions_for(ctx.guild.default_role).send_messages:
            lcmbed.title = "Is already locked:"
            return await ctx.reply(embed=lcmbed)
        else:
            await channel.set_permissions(ctx.guild.default_role, overwrite=over)
            lcmbed.title = "Locked:"
            await ctx.reply(embed=lcmbed)

    # Unlock
    @commands.command(name="unlock", aliases=["ulc"], help="Unlocks this or the given channel")
    @commands.guild_only()
    @commands.has_guild_permissions(manage_channels=True)
    @commands.bot_has_guild_permissions(manage_channels=True)
    async def unlock(self, ctx:commands.Context, channel:typing.Union[discord.TextChannel, discord.StageChannel, discord.VoiceChannel, discord.Thread]=commands.Option(description="The channel you want to unlock", default=None), *, reason:str=commands.Option(description="The reason for unlocking the channel", default=None)):
        channel = channel or ctx.channel
        reason = reason or "Unspecified"
        over = channel.overwrites_for(ctx.guild.default_role)
        over.connect = None
        over.speak = None
        over.request_to_speak = None
        over.send_messages = None
        over.add_reactions = None
        over.create_public_threads = None
        over.create_private_threads = None
        ulcmbed = discord.Embed(
            color=self.bot.color,
            timestamp=ctx.message.created_at
        )
        ulcmbed.add_field(name="Channel:", value=channel.mention)
        ulcmbed.add_field(name="Moderator:", value=ctx.author.mention)
        ulcmbed.add_field(name="Reason:", value=reason)
        ulcmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        if channel.permissions_for(ctx.guild.default_role).send_messages:
            ulcmbed.title = "Is already unlocked:"
            return await ctx.reply(embed=ulcmbed)
        else:
            await channel.set_permissions(ctx.guild.default_role, overwrite=over)
            ulcmbed.title = "Unlocked:"
            await ctx.reply(embed=ulcmbed)

    # Clear
    @commands.command(name="clear", aliases=["cr"], help="Deletes messages for the given amount")
    @commands.guild_only()
    @commands.has_guild_permissions(manage_messages=True)
    @commands.bot_has_guild_permissions(manage_messages=True)
    async def clear(self, ctx:commands.Context, *, amount:int=commands.Option(description="The amount of messages you want to clear")):
        pumbed = discord.Embed(
            color=self.bot.color,
            timestamp=ctx.message.created_at
        )
        pumbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        if amount > 100:
            pumbed.title = "Can't clear more than 100 messages"
            return await ctx.reply(embed=pumbed, delete_after=5)
        await ctx.channel.purge(limit=amount+1)
        pumbed.title = F"Deleted {amount} amount of messages"
        await ctx.reply(embed=pumbed, delete_after=5)

def setup(bot):
    bot.add_cog(Moderation(bot))
