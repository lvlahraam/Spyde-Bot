import discord, sys, time, typing
from discord.ext import commands
from core.views import pagination


class Information(commands.Cog, description="Stalking people is wrong and bad!"):
    def __init__(self, bot):
        self.bot = bot

    # Stats
    @commands.hybrid_command(
        name="stats", aliases=["st"], description="Shows bot's stats"
    )
    async def stats(self, ctx: commands.Context):
        abmbed = discord.Embed(
            color=self.bot.color,
            title=f"{self.bot.user.name} Stats",
            timestamp=ctx.message.created_at,
        )
        abmbed.add_field(name="Platform:", value=sys.platform, inline=False)
        abmbed.add_field(name="Python Version:", value=sys.version, inline=False)
        abmbed.add_field(
            name="Discord.py Version:", value=discord.__version__, inline=False
        )
        abmbed.add_field(name="Commands:", value=len(self.bot.commands), inline=False)
        abmbed.add_field(name="Guilds:", value=len(self.bot.guilds), inline=False)
        abmbed.add_field(
            name="Uptime:",
            value=f"{discord.utils.format_dt(self.bot.uptime, style='f')} ({discord.utils.format_dt(self.bot.uptime, style='R')})",
            inline=False,
        )
        abmbed.add_field(
            name="Developer:", value="Mahraam#5124 (494496285676535811)", inline=False
        )
        abmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        await ctx.reply(embed=abmbed)

    # Invite
    @commands.hybrid_command(
        name="invite", aliases=["inv"], description="Gives an invite link for the bot"
    )
    async def invite(self, ctx: commands.Context):
        invmbed = discord.Embed(
            color=self.bot.color,
            title="Here is the invite link for the bot",
            timestamp=ctx.message.created_at,
        )
        invmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        view = discord.ui.View()
        view.add_item(
            item=discord.ui.Button(
                emoji="🔗",
                label="Invite URL",
                url=discord.utils.oauth_url(
                    self.bot.user.id,
                    permissions=discord.Permissions.all(),
                    scopes=["bot", "applications.commands"],
                ),
            )
        )
        await ctx.reply(embed=invmbed, view=view)

    # Ping
    @commands.hybrid_command(
        name="ping", aliases=["pi"], description="Shows bot's ping"
    )
    async def ping(self, ctx: commands.Context):
        unpimbed = discord.Embed(
            color=self.bot.color, title="🎾 Pinging...", timestamp=ctx.message.created_at
        )
        unpimbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        tstart = time.perf_counter()
        unpimsg = await ctx.reply(embed=unpimbed)
        tend = time.perf_counter()
        dopimbed = discord.Embed(
            color=self.bot.color, title="🏓 Pong:", timestamp=ctx.message.created_at
        )
        dopimbed.add_field(
            name="Websocket:", value=f"{self.bot.latency*1000}ms", inline=False
        )
        dopimbed.add_field(
            name="Typing:", value=f"{(tend-tstart)*1000}ms", inline=False
        )
        dopimbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        await unpimsg.edit(embed=dopimbed)

    # Avatar
    @commands.hybrid_command(
        name="avatar",
        aliases=["av"],
        description="Shows yours or the given user's avatar",
        brief="[user]",
    )
    @discord.app_commands.describe(user="The user you want the avatar from")
    async def avatar(self, ctx: commands.Context, user: discord.User = None):
        user = user or ctx.author
        avmbed = discord.Embed(
            color=self.bot.color,
            title=f"{user.name}'s Avatar",
            timestamp=ctx.message.created_at,
        )
        avmbed.set_image(url=user.display_avatar.url)
        avmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        await ctx.reply(embed=avmbed)

    # Banner
    @commands.hybrid_command(
        name="banner",
        aliases=["br"],
        description="Shows yours or the given user's banner",
        brief="[user]",
    )
    @discord.app_commands.describe(user="The user you want the banner from")
    async def banner(self, ctx: commands.Context, user: discord.User = None):
        user = user or ctx.author
        fetch = await self.bot.fetch_user(user.id)
        brmbed = discord.Embed(color=self.bot.color, timestamp=ctx.message.created_at)
        brmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        if fetch.banner:
            brmbed.title = f"{user.name}'s Banner"
            brmbed.set_image(url=fetch.banner.url)
        else:
            brmbed.title = f"{user.name} doesn't have banner"
        await ctx.reply(embed=brmbed)

    # UserInfo
    @commands.hybrid_command(
        name="userinfo",
        aliases=["ui"],
        description="Shows yours or the given user's info",
        brief="[user]",
    )
    @commands.guild_only()
    @discord.app_commands.describe(user="The user you want to get the info from")
    async def userinfo(self, ctx: commands.Context, user: discord.User = None):
        user = user or ctx.author
        fetch = await self.bot.fetch_user(user.id)
        gi = [
            f"***Username:*** {user}",
            f"***Discriminator:*** {user.discriminator}",
            f"***ID:*** {user.id}",
            f"***Mention:*** {user.mention}",
            f"***Registered:*** {discord.utils.format_dt(user.created_at, style='F')} ({discord.utils.format_dt(user.created_at, style='R')})",
        ]
        uimbed = discord.Embed(
            color=fetch.accent_color or self.bot.color,
            title=f"{user.name}'s Information",
            timestamp=ctx.message.created_at,
        )
        if user in ctx.guild.members:
            gi.append(
                f"***Activity:*** {user.activity.name if user.activity else '*Nothing*'}"
            )
            gi.append(f"***Status:*** {user.status}")
            gi.append(f"***Web-Status:*** {user.web_status}")
            gi.append(f"***Desktop-Status:*** {user.desktop_status}")
            gi.append(f"***Mobile-Status:*** {user.mobile_status}")
            si = [
                f"***Joined:*** {discord.utils.format_dt(user.joined_at, style='F')} ({discord.utils.format_dt(user.joined_at, style='R')})",
                f"***Roles:*** [{len(user.roles)}]",
                f"***Top-Role:*** {user.top_role.mention}",
                f"***Boosting:*** {'True' if user in ctx.guild.premium_subscribers else 'False'}",
                f"***Nickname:*** {user.nick}",
                f"***Voice:*** {user.voice.channel.mention if user.voice else '*Not in a voice*'}",
            ]
            uimbed.add_field(
                name="Server-Information:", value="\n".join(s for s in si), inline=False
            )
        uimbed.add_field(
            name="Global-Information:", value="\n".join(g for g in gi), inline=False
        )
        uimbed.set_thumbnail(url=user.display_avatar.url)
        if fetch.banner:
            uimbed.set_image(url=fetch.banner.url)
        uimbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        await ctx.reply(embed=uimbed)

    # Permissions
    @commands.hybrid_command(
        name="permissions",
        aliases=["perms"],
        description="Shows yours or the given member's permissions",
        brief="[member]",
    )
    @commands.guild_only()
    @discord.app_commands.describe(
        member="The member you want to get the permissions from"
    )
    async def permissions(self, ctx: commands.Context, member: discord.Member = None):
        member = member or ctx.author
        ai = []
        di = []
        for permission, value in member.guild_permissions:
            permission = permission.replace("_", " ").title()
            if value:
                ai.append(f"🥗 {permission}")
            if not value:
                di.append(f"🏮 {permission}")
        permsmbed = discord.Embed(
            color=self.bot.color,
            title=f"{member.name}'s Permissions",
            timestamp=ctx.message.created_at,
        )
        if len(ai) > 0:
            permsmbed.add_field(
                name="Allowed:", value="\n".join(a for a in ai), inline=False
            )
        if len(di) > 0:
            permsmbed.add_field(
                name="Denied:", value="\n".join(d for d in di), inline=False
            )
        permsmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        await ctx.reply(embed=permsmbed)

    # Icon
    @commands.hybrid_command(
        name="icon", aliases=["ic"], description="Shows the server's icon"
    )
    @commands.guild_only()
    async def icon(self, ctx: commands.Context):
        icmbed = discord.Embed(
            color=self.bot.color,
            title=f"{ctx.guild.name}'s Icon",
            timestamp=ctx.message.created_at,
        )
        icmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        if ctx.guild.icon:
            icmbed.set_image(url=ctx.guild.icon.url)
        else:
            icmbed.title = f"{ctx.guild.name} doesn't have icon"
        await ctx.reply(embed=icmbed)

    # ServerInfo
    @commands.hybrid_command(
        name="serverinfo", aliases=["si"], description="Shows the server's info"
    )
    @commands.guild_only()
    async def serverinfo(self, ctx: commands.Context):
        oi = [
            f"***Username:*** {ctx.guild.owner.name}",
            f"***Discriminator:*** {ctx.guild.owner.discriminator}",
            f"***ID:*** {ctx.guild.owner.id}",
            f"***Mention:*** {ctx.guild.owner.mention}",
            f"***Registered:*** {discord.utils.format_dt(ctx.guild.owner.created_at, style='F')} ({discord.utils.format_dt(ctx.guild.owner.created_at, style='R')})",
        ]
        si = [
            f"***Name:*** {ctx.guild.name}",
            f"***ID:*** {ctx.guild.id}",
            f"***Description:*** {ctx.guild.description or '*No Description*'}",
            f"***Created-At:*** {discord.utils.format_dt(ctx.guild.created_at, style='F')} ({discord.utils.format_dt(ctx.guild.created_at, style='R')})",
            f"***Region:*** {ctx.guild.region}",
            f"***MFA:*** {ctx.guild.mfa_level}",
            f"***Verification:*** {ctx.guild.verification_level}",
            f"***File-Size-Limit:*** {ctx.guild.filesize_limit}",
            f"***Members:*** {ctx.guild.member_count}",
            f"***Default-Role:*** {ctx.guild.default_role.mention}",
            f"***Boost-Role:*** {ctx.guild.premium_subscriber_role.mention or '*No boost-role*'}",
            f"***Boost-Level:*** {ctx.guild.premium_tier}",
            f"***Boosters:*** {', '.join(ctx.guild.premium_subscribers[:10])}",
            f"***Categories:*** {len(ctx.guild.categories)}",
            f"***Channels:*** {len(ctx.guild.channels)}",
            f"***AFK-Channel:*** {ctx.guild.afk_channel.mention or '*No AFK channel*'}",
            f"***AFK-Timeout:*** {ctx.guild.afk_timeout}",
        ]
        simbed = discord.Embed(
            color=self.bot.color,
            title=f"{ctx.guild.name}'s Information",
            timestamp=ctx.message.created_at,
        )
        simbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        simbed.add_field(
            name="Owner-Information:", value="\n".join(o for o in oi), inline=False
        )
        simbed.add_field(
            name="Server-Information:", value="\n".join(s for s in si), inline=False
        )
        if ctx.guild.icon:
            simbed.set_thumbnail(url=ctx.guild.icon.url)
        if ctx.guild.banner:
            simbed.set_image(url=ctx.guild.banner.url)
        await ctx.reply(embed=simbed)

    # Emojis
    @commands.hybrid_command(
        name="emojis",
        aliases=["es"],
        description="Shows every emoji with or without the given name",
    )
    @commands.guild_only()
    @discord.app_commands.describe(name="The name you want to look for in the emojis")
    async def emojis(self, ctx: commands.Context, *, name: str = None):
        esemojis = []
        for guild in self.bot.guilds:
            for emoji in guild.emojis:
                if name:
                    if name in emoji.name.lower():
                        esemojis.append(emoji)
                else:
                    esemojis.append(emoji)
        if not esemojis:
            return await ctx.reply(f"Couldn't find any emoji with {name}")
        esembeds = []
        for p in esemojis:
            esmbed = discord.Embed(
                color=discord.Color.blurple(), timestamp=ctx.message.created_at
            )
            esmbed.add_field(name="Name:", value=p.name, inline=False)
            esmbed.add_field(name="ID:", value=p.id, inline=False)
            esmbed.add_field(name="Animated:", value=p.animated, inline=False)
            esmbed.add_field(
                name="Requires Colons:", value=p.require_colons, inline=False
            )
            esmbed.add_field(name="Available", value=p.available, inline=False)
            esmbed.add_field(name="Twitch", value=p.managed, inline=False)
            esmbed.add_field(
                name="Created At",
                value=f"{discord.utils.format_dt(p.created_at, style='f')} ({discord.utils.format_dt(p.created_at, style='R')})",
                inline=False,
            )
            esmbed.set_thumbnail(url=p.url)
            esmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
            esembeds.append(esmbed)
        await pagination.ViewPagination(ctx, esembeds).start() if len(
            esembeds
        ) > 1 else await ctx.reply(embed=esembeds[0])

    # EmojiInfo
    @commands.command(
        name="emojiinfo",
        aliases=["ei"],
        description="Gives information about the given emoji",
    )
    @commands.guild_only()
    @discord.app_commands.describe(emoji="The emoji you want info from")
    async def emojiinfo(
        self,
        ctx: commands.Context,
        emoji: typing.Union[discord.Emoji, discord.PartialEmoji],
    ):
        emmbed = discord.Embed(
            color=self.bot.color,
            title=f"{emoji.name}'s Information",
            timestamp=ctx.message.created_at,
        )
        emmbed.add_field(name="Name:", value=emoji.name, inline=False)
        emmbed.add_field(name="ID:", value=emoji.id, inline=False)
        emmbed.add_field(name="Animated:", value=emoji.animated, inline=False)
        emmbed.add_field(
            name="Requires Colons:", value=emoji.require_colons, inline=False
        )
        emmbed.add_field(name="Available", value=emoji.available, inline=False)
        emmbed.add_field(name="Twitch", value=emoji.managed, inline=False)
        emmbed.add_field(
            name="Created At",
            value=f"{discord.utils.format_dt(emoji.created_at, style='f')} ({discord.utils.format_dt(emoji.created_at, style='R')})",
            inline=False,
        )
        emmbed.set_thumbnail(url=emoji.url)
        emmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        await ctx.reply(embed=emmbed)


async def setup(bot):
    await bot.add_cog(Information(bot))
