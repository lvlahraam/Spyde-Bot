import discord, sys, time, io, typing
from discord.ext import commands
from core.views import pagination

class Information(commands.Cog, description="Stalking people is wrong and bad!"):
    def __init__(self, bot):
        self.bot = bot

    # Stats
    @commands.command(name="stats", aliases=["st"], help="Shows bot's stats")
    async def stats(self, ctx:commands.Context):
        abmbed = discord.Embed(
            color=self.bot.color,
            title=F"{self.bot.user.name} Stats",
            timestamp=ctx.message.created_at
        )
        abmbed.add_field(name="Platform:", value=sys.platform, inline=False)
        abmbed.add_field(name="Python Version:", value=sys.version, inline=False)
        abmbed.add_field(name="Discord.py Version:", value=discord.__version__, inline=False)
        abmbed.add_field(name="Commands:", value=len(self.bot.commands), inline=False)
        abmbed.add_field(name="Guilds:", value=len(self.bot.guilds), inline=False)
        abmbed.add_field(name="Uptime:", value=F"{discord.utils.format_dt(self.bot.uptime, style='f')} ({discord.utils.format_dt(self.bot.uptime, style='R')})", inline=False)
        abmbed.add_field(name="Developer:", value="Mahraam#5124 (494496285676535811)", inline=False)
        abmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        await ctx.reply(embed=abmbed)

    # Invite
    @commands.command(name="invite", aliases=["inv"], help="Gives an invite link for the bot")
    async def invite(self, ctx:commands.Context):
        invmbed = discord.Embed(
            color=self.bot.color,
            title="Here is the invite link for the bot",
            timestamp=ctx.message.created_at
        )
        invmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        invite = discord.utils.oauth_url(self.bot.user.id, permissions=discord.Permissions.all(), scopes=['bot', 'application.commands'])
        view = discord.ui.View().add_item(item=discord.ui.Button(emoji="🔗", label="Invite URL", url=invite))
        await ctx.reply(embed=invmbed, view=view)

    # Ping
    @commands.command(name="ping", aliases=["pi"], help="Shows bot's ping")
    async def ping(self, ctx:commands.Context):
        unpimbed = discord.Embed(
            color=self.bot.color,
            title="🎾 Pinging...",
            timestamp=ctx.message.created_at
        )
        unpimbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        tstart = time.perf_counter()
        pstart = time.perf_counter()
        await self.bot.postgres.execute("SELECT 1")
        unpimsg = await ctx.reply(embed=unpimbed)
        tend = time.perf_counter()
        pend = time.perf_counter()
        dopimbed = discord.Embed(
            color=self.bot.color,
            title="🏓 Pong:",
            timestamp=ctx.message.created_at
        )
        dopimbed.add_field(name="Websocket:", value=F"{self.bot.latency*1000}ms", inline=False)
        dopimbed.add_field(name="Typing:", value=F"{(tend-tstart)*1000}ms", inline=False)
        dopimbed.add_field(name="Postgres:", value=F"{(pend-pstart)*1000}", inline=False)
        dopimbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        await unpimsg.edit(embed=dopimbed)

    # Avatar
    @commands.command(name="avatar", aliases=["av"], help="Shows yours or the given user's avatar")
    async def avatar(self, ctx:commands.Context, user:discord.User=commands.Option(description="The user to get the avatar of", default=None)):
        user = user or ctx.author
        avmbed = discord.Embed(
            color=self.bot.color,
            title=F"{user.name}'s Avatar",
            timestamp=ctx.message.created_at
        )
        avmbed.set_image(url=user.display_avatar.url)
        avmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        await ctx.reply(embed=avmbed)

    # Banner
    @commands.command(name="banner", aliases=["br"], help="Shows yours or the given user's banner")
    async def banner(self, ctx:commands.Context, user:discord.User=commands.Option(description="The user to get the banner of", default=None)):
        user = user or ctx.author
        fetch = await self.bot.fetch_user(user.id)
        brmbed = discord.Embed(
            color=self.bot.color,
            timestamp=ctx.message.created_at
        )
        brmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        if fetch.banner:
            brmbed.set_image(url=fetch.banner.url)
        else: brmbed.title = F"{user.name} doesn't have banner"
        await ctx.reply(embed=brmbed)

    # UserInfo
    @commands.command(name="userinfo", aliases=["ui"], help="Shows yours or the given user's info")
    @commands.guild_only()
    async def userinfo(self, ctx:commands.Context, member:discord.Member=commands.Option(description="The member to get the avatar of", default=None)):
        member = member or ctx.author
        fetch = await self.bot.fetch_user(member.id)
        gi = [
            F"***Username:*** {member.name}",
            F"***Discriminator:*** {member.discriminator}",
            F"***ID:*** {member.id}",
            F"***Mention:*** {member.mention}",
            F"***Activity:*** {member.activity.name or '*Nothing*'}",
            F"***Status:*** {member.status}",
            F"***Web-Status:*** {member.web_status}",
            F"***Desktop-Status:*** {member.desktop_status}",
            F"***Mobile-Status:*** {member.mobile_status}",
            F"***Registered:*** {discord.utils.format_dt(member.created_at, style='F')} ({discord.utils.format_dt(member.created_at, style='R')})"
        ]
        si = [
            F"***Joined:*** {discord.utils.format_dt(member.joined_at, style='F')} ({discord.utils.format_dt(member.joined_at, style='R')})",
            F"***Roles:*** [{len(member.roles)}]",
            F"***Top-Role:*** {member.top_role.mention}",
            F"***Boosting:*** {'True' if member in ctx.guild.premium_subscribers else 'False'}",
            F"***Nickname:*** {member.nick}",
            F"***Voice:*** {member.voice.channel.mention or '*Not in a voice*'}"
        ]
        uimbed = discord.Embed(
            color=fetch.accent_color or self.bot.color,
            title=F"{member.name}'s Information",
            timestamp=ctx.message.created_at
        )
        uimbed.add_field(name="Global-Information:", value="\n".join(g for g in gi), inline=False)
        uimbed.add_field(name="Server-Information:", value="\n".join(s for s in si), inline=False)
        uimbed.set_thumbnail(url=member.display_avatar.url)
        if fetch.banner: uimbed.set_image(url=fetch.banner.url)
        uimbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        await ctx.reply(embed=uimbed)

    # Permissions
    @commands.command(name="permissions", aliases=["perms"], help="Shows yours or the given member's permissions")
    @commands.guild_only()
    async def permissions(self, ctx:commands.Context, member:discord.Member=commands.Option(description="The member to get the permissions of", default=None)):
        member = member or ctx.author
        ai = []
        di = []
        for permission, value in member.guild_permissions:
            permission = permission.replace("_", " ").title()
            if value:
                ai.append(F"🥗 {permission}")
            if not value:
                di.append(F"🏮 {permission}")
        permsmbed = discord.Embed(
            color=self.bot.color,
            title=F"{member.name}'s Permissions",
            timestamp=ctx.message.created_at
        )
        if len(ai) > 0: permsmbed.add_field(name="Allowed:", value="\n".join(a for a in ai), inline=False)
        if len(di) > 0: permsmbed.add_field(name="Denied:", value="\n".join(d for d in di), inline=False)
        permsmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        await ctx.reply(embed=permsmbed)

    # Spotify
    @commands.command(name="spotify", aliases=["sy"], help="Shows info about yours or the given member's spotify activity")
    async def spotify(self, ctx:commands.Context, member:discord.Member=commands.Option(description="The member to get the spotify activity of", default=None)):
        member = member or ctx.author
        await ctx.defer()
        member = (await ctx.guild.query_members(user_ids=[member.id], presences=True))[0]
        symbed = discord.Embed(
            timestamp=ctx.message.created_at
        )
        symbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        for activity in member.activities:
            if isinstance(activity, discord.Spotify):
                params = {
                    'title': activity.title,
                    'cover_url': activity.album_cover_url,
                    'duration_seconds': activity.duration.seconds,
                    'start_timestamp': activity.start.timestamp(),
                    'artists': activity.artists[:3]
                }
                session = await self.bot.session.get("https://api.jeyy.xyz/discord/spotify", params=params)
                response = io.BytesIO(await session.read())
                symbed.color = activity.color
                symbed.url = activity.track_url
                symbed.title = activity.title
                symbed.add_field(name="Artist(s)", value=", ".join(artist for artist in activity.artists), inline=False)
                symbed.add_field(name="Album", value=activity.album, inline=False)
                symbed.add_field(name="Track ID", value=activity.track_id, inline=False)
                symbed.add_field(name="Party ID", value=activity.party_id, inline=False)
                symbed.add_field(name="Listening Since:", value=discord.utils.format_dt(activity.start, style='R'), inline=False)
                symbed.set_author(name=member, icon_url=member.display_avatar.url)
                symbed.set_thumbnail(url=activity.album_cover_url)
                symbed.set_image(url="attachment://spotify.png")
                await ctx.reply(file=discord.File(fp=response, filename="spotify.png"), embed=symbed)
                break
        else:
            symbed.color = self.bot.color
            symbed.title = F"{member.name} is not listening to Spotify"
            await ctx.reply(embed=symbed)

    # Icon
    @commands.command(name="icon", aliases=["ic"], help="Shows the server's icon")
    @commands.guild_only()
    async def icon(self, ctx:commands.Context):
        icmbed = discord.Embed(
            color=self.bot.color,
            title=F"{ctx.guild.name}'s Icon",
            timestamp=ctx.message.created_at
        )
        icmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        if ctx.guild.icon:
            icmbed.set_image(url=ctx.guild.icon.url)
        else: icmbed.title = F"{ctx.guild.name} doesn't have icon"
        await ctx.reply(embed=icmbed)

    # ServerInfo
    @commands.command(name="serverinfo", aliases=["si"], help="Shows the server's info")
    @commands.guild_only()
    async def serverinfo(self, ctx:commands.Context):
        oi = [
            F"***Username:*** {ctx.guild.owner.name}",
            F"***Discriminator:*** {ctx.guild.owner.discriminator}",
            F"***ID:*** {ctx.guild.owner.id}",
            F"***Mention:*** {ctx.guild.owner.mention}",
            F"***Registered:*** {discord.utils.format_dt(ctx.guild.owner.created_at, style='F')} ({discord.utils.format_dt(ctx.guild.owner.created_at, style='R')})"
        ]
        si = [
            F"***Name:*** {ctx.guild.name}",
            F"***ID:*** {ctx.guild.id}",
            F"***Description:*** {ctx.guild.description or '*No Description*'}",
            F"***Created-At:*** {discord.utils.format_dt(ctx.guild.created_at, style='F')} ({discord.utils.format_dt(ctx.guild.created_at, style='R')})",
            F"***Region:*** {ctx.guild.region}",
            F"***MFA:*** {ctx.guild.mfa_level}",
            F"***Verification:*** {ctx.guild.verification_level}",
            F"***File-Size-Limit:*** {ctx.guild.filesize_limit}",
            F"***Members:*** {ctx.guild.member_count}",
            F"***Default-Role:*** {ctx.guild.default_role.mention}",
            F"***Boost-Role:*** {ctx.guild.premium_subscriber_role.mention or '*No boost-role*'}",
            F"***Boost-Level:*** {ctx.guild.premium_tier}",
            F"***Boosters:*** {', '.join(ctx.guild.premium_subscribers[:10])}",
            F"***Categories:*** {len(ctx.guild.categories)}",
            F"***Channels:*** {len(ctx.guild.channels)}",
            F"***AFK-Channel:*** {ctx.guild.afk_channel.mention or '*No AFK channel*'}",
            F"***AFK-Timeout:*** {ctx.guild.afk_timeout}"
        ]
        simbed = discord.Embed(
            color=self.bot.color,
            title=F"{ctx.guild.name}'s Information",
            timestamp=ctx.message.created_at
        )
        simbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        simbed.add_field(name="Owner-Information:", value="\n".join(o for o in oi), inline=False)
        simbed.add_field(name="Server-Information:", value="\n".join(s for s in si), inline=False)
        if ctx.guild.icon: simbed.set_thumbnail(url=ctx.guild.icon.url)
        if ctx.guild.banner: simbed.set_image(url=ctx.guild.banner.url)
        await ctx.reply(embed=simbed)

    # Emojis
    @commands.command(name="emojis", aliases=["es"], help="Shows every emoji with or without the given name")
    @commands.guild_only()
    async def emojis(self, ctx:commands.Context, *, name:str=commands.Option(description="The name you want to be searched for", default=None)):
        ps = []
        for guild in self.bot.guilds:
            for emoji in guild.emojis:
                if name:
                    if name in emoji.name.lower(): ps.append(emoji)
                else: ps.append(emoji)
        if not ps: return await ctx.reply(F"Couldn't find any emoji with {name}")
        es = []
        for p in ps:
            e = discord.Embed(
                color=discord.Color.blurple(),
                timestamp=ctx.message.created_at
            )
            e.add_field(name="Name:", value=p.name, inline=False)
            e.add_field(name="ID:", value=p.id, inline=False)
            e.add_field(name="Animated:", value=p.animated, inline=False)
            e.add_field(name="Requires Colons:", value=p.require_colons, inline=False)
            e.add_field(name="Available", value=p.available, inline=False)
            e.add_field(name="Twitch", value=p.managed, inline=False)
            e.add_field(name="Created At", value=F"{discord.utils.format_dt(p.created_at, style='f')} ({discord.utils.format_dt(p.created_at, style='R')})", inline=False)
            e.set_thumbnail(url=p.url)
            e.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
            es.append(e)
        await pagination.ViewPagination(ctx, es).start() if len(es) > 1 else await ctx.reply(embed=es[0])

    # EmojiInfo
    @commands.command(name="emojiinfo", aliases=["ei"], help="Gives information about the given emoji")
    @commands.guild_only()
    async def emojiinfo(self, ctx:commands.Context, emoji:typing.Union[discord.Emoji, discord.PartialEmoji]=commands.Option(description="The emoji to get the info of")):
        emmbed = discord.Embed(
            color=self.bot.color,
            title=F"{emoji.name}'s Information",
            timestamp=ctx.message.created_at
        )
        emmbed.add_field(name="Name:", value=emoji.name, inline=False)
        emmbed.add_field(name="ID:", value=emoji.id, inline=False)
        emmbed.add_field(name="Animated:", value=emoji.animated, inline=False)
        emmbed.add_field(name="Requires Colons:", value=emoji.require_colons, inline=False)
        emmbed.add_field(name="Available", value=emoji.available, inline=False)
        emmbed.add_field(name="Twitch", value=emoji.managed, inline=False)
        emmbed.add_field(name="Created At", value=F"{discord.utils.format_dt(emoji.created_at, style='f')} ({discord.utils.format_dt(emoji.created_at, style='R')})", inline=False)
        emmbed.set_thumbnail(url=emoji.url)
        emmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        await ctx.reply(embed=emmbed)

def setup(bot):
    bot.add_cog(Information(bot))
