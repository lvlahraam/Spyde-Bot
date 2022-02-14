import discord, typing
from discord.ext import commands
from core.views import confirm, ticket

class Settings(commands.Cog, description="Setting up the bot with these!"):
    def __init__(self, bot):
        self.bot = bot

    # Prefix
    @commands.command(name="prefix", aliases=["pf"], help="Setting up the prefix with these, Consider using subcommands", invoke_without_command=True)
    @commands.guild_only()
    async def prefix(self, ctx:commands.Context, options:typing.Literal["set", "reset", "show"]=commands.Option(description="The option you want to use"), *, prefix:str=commands.Option(description="The prefix you want to be set", default=None)):
        pfmbed = discord.Embed(
            color=self.bot.color,
            timestamp=ctx.message.created_at
        )
        pfmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        if options == "set":
            if not prefix:
                pfmbed.title = "You need to pass a string for prefix"
            else:
                pfmbed.description = prefix
                if prefix == self.bot.prefixes[ctx.guild.id]:
                    pfmbed.title = "Prefix is the same"
                else:
                    data = await self.bot.postgres.fetchval("SELECT prefix FROM prefixes WHERE guild_id=$1", ctx.guild.id)
                    if not data:
                        await self.bot.postgres.execute("INSERT INTO prefixes(guild_name,guild_id,prefix) VALUES($1,$2,$3)", ctx.guild.name, ctx.guild.id, prefix)
                    else:
                        await self.bot.postgres.fetch("UPDATE prefixes SET prefix=$1 WHERE guild_id=$2", prefix, ctx.guild.id)
                    self.bot.prefixes[ctx.guild.id] = prefix
                    pfmbed.title = "Changed prefix:"
        elif options == "reset":
            pfmbed.description = self.bot.default_prefix
            data = await self.bot.postgres.fetchval("SELECT prefix FROM prefixes WHERE guild_id=$1", ctx.guild.id)
            if data:
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
    @commands.command(name="welcome", aliases=["wel"], help="Setting up the welcomer with these")
    @commands.guild_only()
    async def welcome(self, ctx:commands.Context, option:typing.Literal["toggle", "channel", "message", "show"]=commands.Option(description="The option you want to use"), *, value:typing.Union[discord.TextChannel, str]=commands.Option(description="The value you want to set", default=None)):
        welmbed = discord.Embed(
            color=self.bot.color,
            timestamp=ctx.message.created_at
        )
        welmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        welcome = await self.bot.postgres.fetchval("SELECT * FROM welcome WHERE guild_id=$1", ctx.guild.id)
        if option == "toggle":
            if not welcome:
                welmbed.title = "Welcome has been turned on"
                await self.bot.postgres.execute("INSERT INTO welcome(guild_name,guild_id,msg,ch) VALUES($1,$2,$3,$4)", ctx.guild.name, ctx.guild.id, "Welcome to .guild .member", ctx.guild.system_channel.id)
            else:
                welmbed.title = "Welcome has been turned off"
                await self.bot.postgres.execute("DELETE FROM welcome WHERE guild_id=$1", ctx.guild.id)
        elif option == "channel":
            if type(value) == discord.TextChannel:
                welmbed.title = "Welcome channel has been changed to:"
                welmbed.description = value.mention
                if not welcome:
                    await self.bot.postgres.execute("INSERT INTO welcome(guild_name,guild_id,msg,ch) VALUES($1,$2,$3,$4)", ctx.guild.name, ctx.guild.id, "Welcome .member to here .guild", value.id)
                else:
                    await self.bot.postgres.execute("UPDATE welcome SET ch=$1 WHERE guild_id=$2", value.id, ctx.guild.id)
            else:
                welmbed.title = "You need to pass a text channel"
        elif option == "message":
            if type(value) == str:
                welmbed.title = "Welcome message has been changed to:"
                welmbed.description = value
                if not welcome:
                    await self.bot.postgres.execute("INSERT INTO welcome(guild_name,guild_id,msg,ch) VALUES($1,$2,$3,$4)", ctx.guild.name, ctx.guild.id, value, ctx.guild.system_channel.id)
                else:
                    await self.bot.postgres.execute("UPDATE welcome SET msg=$1 WHERE guild_id=$2", value, ctx.guild.id)
            else:
                welmbed.title = "You need to pass a string"
        elif option == "show":
            if not welcome:
                welmbed.title = "Welcome is turned off"
            else:
                msg = await self.bot.postgres.fetchval("SELECT msg FROM welcome WHERE guild_id=$1", ctx.guild.id)
                ch = discord.utils.get(ctx.guild.text_channels, id=(await self.bot.postgres.fetchval("SELECT ch FROM welcome WHERE guild_id=$1", ctx.guild.id)))
                welmbed.title = "Status for welcome"
                welmbed.description = F"Turned On\n{msg}\n{ch.mention}"
        await ctx.reply(embed=welmbed)
    
    # Goodbye
    @commands.command(name="goodbye", aliases=["bye"], help="Setting up the goodbyer with this")
    @commands.guild_only()
    async def goodbye(self, ctx:commands.Context, option:typing.Literal["toggle", "channel", "message", "show"]=commands.Option(description="The option you want to use"), *, value:typing.Union[discord.TextChannel, str]=commands.Option(description="The value you want to set", default=None)):
        byembed = discord.Embed(
            color=self.bot.color,
            timestamp=ctx.message.created_at
        )
        byembed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        goodbye = await self.bot.postgres.fetchval("SELECT * FROM goodbye WHERE guild_id=$1", ctx.guild.id)
        if option == "toggle":
            if not goodbye:
                byembed.title = "Goodbye has been turned on"
                await self.bot.postgres.execute("INSERT INTO goodbye(guild_name,guild_id,msg,ch) VALUES($1,$2,$3,$4)", ctx.guild.name, ctx.guild.id, "Thank you .member for being here", ctx.guild.system_channel.id)
            else:
                byembed.title = "Goodbye has been turned off"
                await self.bot.postgres.execute("DELETE FROM goodbye WHERE guild_id=$1", ctx.guild.id)
        elif option == "channel":
            if type(value) == discord.TextChannel:
                byembed.title = "Goodbye channel has been changed to:"
                byembed.description = value.mention
                if not goodbye:
                    await self.bot.postgres.execute("INSERT INTO goodbye(guild_name,guild_id,msg,ch) VALUES($1,$2,$3,$4)", ctx.guild.name, ctx.guild.id, "Thank you .member for being here", value.id)
                else:
                    await self.bot.postgres.execute("UPDATE goodbye SET ch=$1 WHERE guild_id=$2", value.id, ctx.guild.id)
            else:
                byembed.title = "You need to pass a text channel"
        elif option == "message":
            if type(value) == str:
                byembed.title = "Goodbye message has been changed to:"
                byembed.description = value
                if not goodbye:
                    await self.bot.postgres.execute("INSERT INTO goodbye(guild_name,guild_id,msg,ch) VALUES($1,$2,$3,$4)", ctx.guild.name, ctx.guild.id, value, ctx.guild.system_channel.id)
                else:
                    await self.bot.postgres.execute("UPDATE goodbye SET msg=$1 WHERE guild_id=$2", value, ctx.guild.id)
            else:
                byembed.title = "You need to pass a string"
        elif option == "show":
            if not goodbye:
                byembed.title = "Goodbye is turned off"
            else:
                msg = await self.bot.postgres.fetchval("SELECT msg FROM goodbye WHERE guild_id=$1", ctx.guild.id)
                ch = discord.utils.get(ctx.guild.text_channels, id=(await self.bot.postgres.fetchval("SELECT ch FROM goodbye WHERE guild_id=$1", ctx.guild.id)))
                byembed.title = "Status for Goodbye"
                byembed.description = F"Turned On\n{msg}\n{ch.mention}"
        await ctx.reply(embed=byembed)

    # Ticket
    @commands.command(name="ticket", aliases=["tk"], help="Setting up ticketer with this")
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
        if option == "on":
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
        elif option == "off":
            if not num:
                tkmbed.title += " is already turned off"
                return await ctx.reply(embed=tkmbed)
            await self.bot.postgres.execute("DELETE FROM tickets WHERE guild_id=$1", ctx.guild.id)
            tkmbed.title += " has been turned off"
            tkmbed.description = "You can Delete the categor(y/ies) and channel(s)"
            return await ctx.reply(embed=tkmbed)
        elif option == "status":
            if not num:
                tkmbed.title += " is turned off"
                return await ctx.reply(embed=tkmbed)
            cag = await self.bot.postgres.fetchval("SELECT cag FROM tickets WHERE guild_id = $1", ctx.guild.id)
            category = self.bot.get_channel(cag)
            tkmbed.title += " is turned on"
            tkmbed.description = F"Tickets are now created in the {category.mention} cateogry"
            return await ctx.reply(embed=tkmbed)
        elif option == "view":
            if not num:
                tkmbed.title += " is turned off"
                return await ctx.reply(embed=tkmbed)
            tkmbed.title += " message has been sent"
            await ctx.send(embed=tkviewmbed, view=ticket.TicketView(self.bot))
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
