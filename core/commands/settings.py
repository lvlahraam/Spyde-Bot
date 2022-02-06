import discord, typing
from discord.ext import commands
from core.views import confirm, ticket

class Settings(commands.Cog, description="Setting up the bot with these!"):
    def __init__(self, bot):
        self.bot = bot

    # Prefix
    @commands.group(name="prefix", aliases=["pf"], help="Setting up the prefix with these, Consider using subcommands", invoke_without_command=True)
    @commands.guild_only()
    async def prefix(self, ctx:commands.Context, options:typing.Literal["set", "reset", "show"]=commands.Option(description="The option you want to use"), *, prefix:str=commands.Option(description="The prefix you want to be set", default=None)):
        pfmbed = discord.Embed(
            color=self.bot.color,
            timestamp=ctx.message.created_at
        )
        pfmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        if options == "set":
            if not prefix:
                raise commands.MissingRequiredArgument(param=prefix)
            else:
                pfmbed.description = prefix
                dataprefix = await self.bot.postgres.fetchval("SELECT prefix FROM prefixes WHERE guild_id=$1", ctx.guild.id)
                if dataprefix == prefix:
                    pfmbed.title = "Prefix is the same"
                    return await ctx.reply(embed=pfmbed)
                else:
                    if not prefix:
                        await self.bot.postgres.execute("INSERT INTO prefixes(guild_name,guild_id,prefix) VALUES($1,$2,$3)", ctx.guild.name, ctx.guild.id, prefix)
                    else:
                        await self.bot.postgres.fetch("UPDATE prefixes SET prefix=$1 WHERE guild_id=$2", prefix, ctx.guild.id)
                    self.bot.prefixes[ctx.guild.id] = prefix
                    pfmbed.title = "Changed prefix:"
        elif options == "reset":
            pfmbed.description = self.bot.default_prefix
            dataprefix = await self.bot.postgres.fetchval("SELECT prefix FROM prefixes WHERE guild_id=$1", ctx.guild.id)
            if dataprefix:
                await self.bot.postgres.execute("DELETE FROM prefixes WHERE guild_id=$1", ctx.guild.id)
                pfmbed.title = "Resetted to:"
                self.bot.prefixes[ctx.guild.id] = self.bot.default_prefix
            else:
                pfmbed.title = "Prefix was never changed"
                self.bot.prefixes[ctx.guild.id]
        elif options == "show":
            pfmbed.title = F"My Prefix here is:"
            pfmbed.description = self.bot.prefixes.get(ctx.guild.id)
        await ctx.reply(embed=pfmbed)

    # Welcome
    @commands.group(name="welcome", aliases=["wel"], help="Setting up the welcomer with these, Consider using subcommands", invoke_without_command=True)
    @commands.guild_only()
    async def welcome(self, ctx:commands.Context):
        await ctx.send_help("welcome")

    # Welcome-Status
    @welcome.command(name="status", aliases=["st"], help="Shows the status for welcome")
    @commands.guild_only()
    async def welcome_status(self, ctx:commands.Context):
        welcome = await self.bot.postgres.fetchval("SELECT * FROM welcome WHERE guild_id=$1", ctx.guild.id)
        welstmbed = discord.Embed(
            color=self.bot.color,
            timestamp=ctx.message.created_at
        )
        welstmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        if not welcome:
            welstmbed.title = "Welcome is turned off"
        else:
            msg = await self.bot.postgres.fetchval("SELECT msg FROM welcome WHERE guild_id=$1", ctx.guild.id)
            ch = discord.utils.get(ctx.guild.text_channels, id=(await self.bot.postgres.fetchval("SELECT ch FROM welcome WHERE guild_id=$1", ctx.guild.id)))
            welstmbed.title = "Status for welcome"
            welstmbed.description = F"Turned On\n{msg}\n{ch.mention}"
        await ctx.reply(embed=welstmbed)

    # Welcome-Toggle
    @welcome.command(name="toggle", aliases=["tg"], help="Toggles off or on the welcome")
    @commands.guild_only()
    @commands.has_guild_permissions(administrator=True)
    async def welcome_toggle(self, ctx:commands.Context):
        welcome = await self.bot.postgres.fetchval("SELECT * FROM welcome WHERE guild_id=$1", ctx.guild.id)
        weltgmbed = discord.Embed(
            color=self.bot.color,
            timestamp=ctx.message.created_at
        )
        weltgmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        if not welcome:
            await self.bot.postgres.execute("INSERT INTO welcome(guild_name,guild_id,msg,ch) VALUES($1,$2,$3,$4)", ctx.guild.name, ctx.guild.id, "Welcome to .guild .member", ctx.guild.system_channel.id)
            weltgmbed.title = "Welcome has been turned on"
        else:
            await self.bot.postgres.execute("DELETE FROM welcome WHERE guild_id=$1", ctx.guild.id)
            weltgmbed.title = "Welcome has been turned off"
        await ctx.reply(embed=weltgmbed)

    # Welcome-Channel
    @welcome.command(name="channel", aliases=["ch"], help="Changes the welcome channel to the new given channel")
    @commands.guild_only()
    @commands.has_guild_permissions(administrator=True)
    async def welcome_channel(self, ctx:commands.Context, channel:discord.TextChannel):
        welcome = await self.bot.postgres.fetchval("SELECT * FROM welcome WHERE guild_id=$1", ctx.guild.id)
        welchmbed = discord.Embed(
            color=self.bot.color,
            title="Welcome channel has been changed to:",
            description=channel.mention,
            timestamp=ctx.message.created_at
        )
        welchmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        if not welcome:
            await self.bot.postgres.execute("INSERT INTO welcome(guild_name,guild_id,msg,ch) VALUES($1,$2,$3,$4)", ctx.guild.name, ctx.guild.id, "Welcome .member to here .guild", channel.id)
        else:
            await self.bot.postgres.execute("UPDATE welcome SET ch=$1 WHERE guild_id=$2", channel.id, ctx.guild.id)
        await ctx.reply(embed=welchmbed)

    # Welcome-Message
    @welcome.command(name="message", aliases=["msg"], help="Changes the welcome message to the new given message")
    @commands.guild_only()
    @commands.has_guild_permissions(administrator=True)
    async def welcome_message(self, ctx:commands.Context, *, msg:str):
        welcome = await self.bot.postgres.fetchval("SELECT * FROM welcome WHERE guild_id=$1", ctx.guild.id)
        welmsgmbed = discord.Embed(
            color=self.bot.color,
            title="Welcome message has been changed to:",
            description=msg,
            timestamp=ctx.message.created_at
        )
        welmsgmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        if not welcome:
            await self.bot.postgres.execute("INSERT INTO welcome(guild_name,guild_id,msg,ch) VALUES($1,$2,$3,$4)", ctx.guild.name, ctx.guild.id, msg, ctx.guild.system_channel.id)
        else:
            await self.bot.postgres.execute("UPDATE welcome SET msg=$1 WHERE guild_id=$2", msg, ctx.guild.id)
        await ctx.reply(embed=welmsgmbed)

    # Goodbye
    @commands.group(name="goodbye", aliases=["bye"], help="Setting up the goodbyer with these, Consider using subcommands", invoke_without_command=True)
    @commands.guild_only()
    async def goodbye(self, ctx:commands.Context):
        await ctx.send_help("goodbye")

    # Goodbye-Status
    @goodbye.command(name="status", aliases=["st"], help="Changes the status for goodbye")
    @commands.guild_only()
    async def goodbye_status(self, ctx:commands.Context):
        goodbye = await self.bot.postgres.fetchval("SELECT * FROM goodbye WHERE guild_id=$1", ctx.guild.id)
        byestmbed = discord.Embed(
            color=self.bot.color,
            timestamp=ctx.message.created_at
        )
        byestmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        if not goodbye:
            byestmbed.title = "Goodbye is turned off"
        else:
            msg = await self.bot.postgres.fetchval("SELECT msg FROM goodbye WHERE guild_id=$1", ctx.guild.id)
            ch = discord.utils.get(ctx.guild.text_channels, id=(await self.bot.postgres.fetchval("SELECT ch FROM goodbye WHERE guild_id=$1", ctx.guild.id)))
            byestmbed.title = "Status for goodbye"
            byestmbed.description = F"Turned On\n{msg}\n{ch.mention}"
        await ctx.reply(embed=byestmbed)

    # Goodbye-Toggle
    @goodbye.command(name="toggle", aliases=["tg"], help="Toggles off or on the goodbye")
    @commands.guild_only()
    @commands.has_guild_permissions(administrator=True)
    async def goodbye_toggle(self, ctx:commands.Context):
        goodbye = await self.bot.postgres.fetchval("SELECT * FROM goodbye WHERE guild_id=$1", ctx.guild.id)
        byetgmbed = discord.Embed(
            color=self.bot.color,
            timestamp=ctx.message.created_at
        )
        byetgmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        if not goodbye:
            await self.bot.postgres.execute("INSERT INTO goodbye(guild_name,guild_id,msg,ch) VALUES($1,$2,$3,$4)", ctx.guild.name, ctx.guild.id, "Thank you .member for being here .guild", ctx.guild.system_channel.id)
            byetgmbed.title = "Goodbye has been turned on"
        else:
            await self.bot.postgres.execute("DELETE FROM goodbye WHERE guild_id=$1", ctx.guild.id)
            byetgmbed.title = "Goodbye has been turned off"
        await ctx.reply(embed=byetgmbed)

    # Goodbye-Channel
    @goodbye.command(name="channel", aliases=["ch"], help="Changes the goodbye channel to the new given channel")
    @commands.guild_only()
    @commands.has_guild_permissions(administrator=True)
    async def goodbye_channel(self, ctx:commands.Context, channel:discord.TextChannel):
        goodbye = await self.bot.postgres.fetchval("SELECT * FROM goodbye WHERE guild_id=$1", ctx.guild.id)
        byechmbed = discord.Embed(
            color=self.bot.color,
            title="Goodbye channel has been changed to:",
            description=channel.mention,
            timestamp=ctx.message.created_at
        )
        byechmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        if not goodbye:
            await self.bot.postgres.execute("INSERT INTO goodbye(guild_name,guild_id,msg,ch) VALUES($1,$2,$3,$4)", ctx.guild.name, ctx.guild.id, "Thank you .member for being here .guild", channel.id)
        else:
            await self.bot.postgres.execute("UPDATE goodbye SET ch=$1 WHERE guild_id=$2", channel.id, ctx.guild.id)
        await ctx.reply(embed=byechmbed)

    # Goodbye-Message
    @goodbye.command(name="message", aliases=["msg"], help="Changes the goodbye message to the new given message")
    @commands.guild_only()
    @commands.has_guild_permissions(administrator=True)
    async def goodbye_message(self, ctx:commands.Context, *, msg:str):
        goodbye = await self.bot.postgres.fetchval("SELECT * FROM goodbye WHERE guild_id=$1", ctx.guild.id)
        byemsgmbed = discord.Embed(
            color=self.bot.color,
            timestamp=ctx.message.created_at
        )
        byemsgmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        if not goodbye:
            await self.bot.postgres.execute("INSERT INTO goodbye(guild_name,guild_id,msg,ch) VALUES($1,$2,$3,$4)", ctx.guild.name, ctx.guild.id, msg, ctx.guild.system_channel.id)
        else:
            await self.bot.postgres.execute("UPDATE goodbye SET msg=$1 WHERE guild_id=$2", msg, ctx.guild.id)
        await ctx.reply(embed=byemsgmbed)

    # Ticket
    @commands.command(name="ticket", aliases=["tk"], help="Setting up ticketer based one the given option: On, Off, Status, View")
    @commands.guild_only()
    @commands.has_guild_permissions(administrator=True)
    @commands.bot_has_guild_permissions(manage_channels=True)
    async def ticket(self, ctx:commands.Context, option:typing.Literal["on", "off", "status", "view"]):
        tkmbed = discord.Embed(
            color=self.bot.color,
            title="📮 Ticketer",
            timestamp=ctx.message.created_at,
        )
        tkmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        tkviewmbed = discord.Embed(
            color=self.bot.color,
            title="📮 Ticketer",
            description=F"Use the button to open a ticket",
        )
        num = await self.bot.postgres.fetchval("SELECT num FROM tickets WHERE guild_id = $1", ctx.guild.id)
        if option == "On":
            if num:
                tkmbed.title += " is already turned on"
                return await ctx.reply(embed=tkmbed)
            cag = await ctx.guild.create_category("Tickets")
            await self.bot.postgres.execute("INSERT INTO tickets(guild_name,guild_id,cag,num) VALUES($1,$2,$3,$4)", ctx.guild.name, ctx.guild.id, cag.id, 1)
            ch = await cag.create_text_channel(F"Open", reason=F"Setting up ticketer", topic=F"Opening a ticket")
            await ch.set_permissions(ctx.guild.default_role, send_messages=False)
            tkmbed.title += " has been turned on"
            tkmbed.description = F"Tickets are now created in {cag.mention} cateogry and {ch.mention}\nPlease don't delete the channel, if you did,\nPlease use this command `.ticket Off` to turn off the ticketer\nYou can see the status of the ticketer with `.ticket Status`"
            await ch.send(embed=tkviewmbed, view=ticket.TicketView(self.bot))
            return await ctx.reply(embed=tkmbed)
        elif option == "Off":
            if not num:
                tkmbed.title += " is already turned off"
                return await ctx.reply(embed=tkmbed)
            await self.bot.postgres.execute("DELETE FROM tickets WHERE guild_id=$1", ctx.guild.id)
            tkmbed.title += " has been turned off"
            tkmbed.description = "You can Delete the categor(y/ies) and channel(s)"
            return await ctx.reply(embed=tkmbed)
        elif option == "Status":
            if not num:
                tkmbed.title += " is turned off"
                return await ctx.reply(embed=tkmbed)
            cag = await self.bot.postgres.fetchval("SELECT cag FROM tickets WHERE guild_id = $1", ctx.guild.id)
            category = self.bot.get_channel(cag)
            tkmbed.title += " is turned on"
            tkmbed.description = F"Tickets are now created in the {category.mention} cateogry"
            return await ctx.reply(embed=tkmbed)
        elif option == "View":
            if not num:
                tkmbed.title += " is turned off"
                return await ctx.reply(embed=tkmbed)
            tkmbed.title += " message has been sent"
            await ctx.reply(embed=tkviewmbed, view=ticket.TicketView(self.bot))
            return await ctx.reply(embed=tkmbed)

    # Leave
    @commands.command(name="leave", aliases=["lv"], help="Makes the bot leave")
    @commands.has_guild_permissions(administrator=True)
    async def leave(self, ctx:commands.Context):
        lvmbed = discord.Embed(
            color=self.bot.color,
            timestamp=ctx.message.created_at
        )
        lvmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        view = confirm.ViewConfirm(ctx)
        view.message = await ctx.reply(content="Are you sure you want the bot to leave:", view=view)
        await view.wait()
        if view.value:
            lvmbed.title = F"{self.bot.user} has left"
            await ctx.reply(embed=lvmbed, delete_after=2.5)
            await ctx.me.guild.leave()

def setup(bot):
    bot.add_cog(Settings(bot))
