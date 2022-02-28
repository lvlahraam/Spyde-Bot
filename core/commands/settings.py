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
                    data = await self.bot.mongodb.prefixes.find_one({"guild_id": ctx.guild.id})
                    if not data:
                        await self.bot.mongodb.prefixes.insert_one(await self.bot.mongodb.prefixes.insert_one({"guild_name": ctx.guild.name, "guild_id": ctx.guild.id, "prefix": prefix}))
                    else:
                        await self.bot.mongodb.prefixes.update_one({"guild_id": ctx.guild.id}, {"$set": {"prefix": prefix}})
                    self.bot.prefixes[ctx.guild.id] = prefix
                    pfmbed.title = "Changed prefix:"
        elif options == "reset":
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
        welcome = await self.bot.mongodb.welcome.find_one({"guild_id": ctx.guild.id})
        if option == "toggle":
            if not welcome:
                welmbed.title = "Welcome has been turned on"
                await self.bot.mongodb.welcome.insert_one({"guild_name": ctx.guild.name, "guild_id": ctx.guild.id, "message": "Welcome to .guild .member", "channel": ctx.guild.system_channel.id or ctx.guild.text_channels[0].id})
            else:
                welmbed.title = "Welcome has been turned off"
                await self.bot.mongodb.welcome.delete_one({"guild_id": ctx.guild.id})
        elif option == "channel":
            if type(value) == discord.TextChannel:
                welmbed.title = "Welcome channel has been changed to:"
                welmbed.description = value.mention
                if not welcome:
                    await self.bot.mongodb.welcome.insert_one({"guild_name": ctx.guild.name, "guild_id": ctx.guild.id, "message": "Welcome to .guild .member", "channel": value.id})
                else:
                    await self.bot.mongodb.welcome.update_one({"guild_id": ctx.guild.id}, {"$set": {"channel": value.id}})
            else:
                welmbed.title = "You need to pass a text channel"
        elif option == "message":
            if type(value) == str:
                welmbed.title = "Welcome message has been changed to:"
                welmbed.description = value
                if not welcome:
                    await self.bot.mongodb.welcome.insert_one({"guild_name": ctx.guild.name, "guild_id": ctx.guild.id, "message": value, "channel": ctx.guild.system_channel.id or ctx.guild.text_channels[0].id})
                else:
                    await self.bot.mongodb.welcome.update_one({"guild_id": ctx.guild.id}, {"$set": {"message": value}})
            else:
                welmbed.title = "You need to pass a string"
        elif option == "show":
            if not welcome:
                welmbed.title = "Welcome is turned off"
            else:
                wel = await self.bot.mongodb.welcome.find_one({"guild_id": ctx.guild.id})
                ch = discord.utils.get(ctx.guild.text_channels, id=wel["channel"])
                welmbed.title = "Status for welcome"
                welmbed.description = F"Turned On\n{wel['message']}\n{ch.mention}"
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
        goodbye = await self.bot.mongodb.goodbye.find_one({"guild_id": ctx.guild.id})
        if option == "toggle":
            if not goodbye:
                byembed.title = "Goodbye has been turned on"
                await self.bot.mongodb.goodbye.insert_one({"guild_name": ctx.guild.name, "guild_id": ctx.guild.id, "message": "Thank you .member for being here .guild", "channel": ctx.guild.system_channel.id or ctx.guild.text_channels[0].id})
            else:
                byembed.title = "Goodbye has been turned off"
                await self.bot.mongodb.goodbye.delete_one({"guild_id": ctx.guild.id})
        elif option == "channel":
            if type(value) == discord.TextChannel:
                byembed.title = "Goodbye channel has been changed to:"
                byembed.description = value.mention
                if not goodbye:
                    await self.bot.mongodb.goodbye.insert_one({"guild_name": ctx.guild.name, "guild_id": ctx.guild.id, "message": "Thank you .member for being here", "channel": value.id})
                else:
                    await self.bot.mongodb.goodbye.update_one({"guild_id": ctx.guild.id}, {"$set": {"channel": value.id}})
            else:
                byembed.title = "You need to pass a text channel"
        elif option == "message":
            if type(value) == str:
                byembed.title = "Goodbye message has been changed to:"
                byembed.description = value
                if not goodbye:
                    await self.bot.mongodb.goodbye.insert_one({"guild_name": ctx.guild.name, "guild_id": ctx.guild.id, "message": value, "channel": ctx.guild.system_channel.id or ctx.guild.text_channels[0].id})
                else:
                    await self.bot.mongodb.goodbye.update_one({"guild_id": ctx.guild.id}, {"$set": {"message": value}})
            else:
                byembed.title = "You need to pass a string"
        elif option == "show":
            if not goodbye:
                byembed.title = "Goodbye is turned off"
            else:
                bye = await self.bot.mongodb.goodbye.find_one({"guild_id": ctx.guild.id})
                ch = discord.utils.get(ctx.guild.text_channels, id=bye["channel"])
                byembed.title = "Status for Goodbye"
                byembed.description = F"Turned On\n{bye['message']}\n{ch.mention}"
        await ctx.reply(embed=byembed)

    # Ticket
    @commands.command(name="ticket", aliases=["tk"], help="Setting up ticketer with this")
    @commands.guild_only()
    @commands.has_guild_permissions(administrator=True)
    @commands.bot_has_guild_permissions(manage_channels=True)
    async def ticket(self, ctx:commands.Context, option:typing.Literal["on", "off", "status", "button", "category"], *, value:discord.CategoryChannel=commands.Option(description="The category you want to set", default=None)):
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
        number = await self.bot.mongodb.tickets.find_one({"guild_id": ctx.guild.id})
        if option == "on":
            if number:
                tkmbed.title += " is already turned on"
            else:
                category = await ctx.guild.create_category("Tickets")
                await self.bot.mongodb.tickets.insert_one({"guild_name": ctx.guild.name, "guild_id": ctx.guild.id, "category": category.id, "number": 1})
                ch = await category.create_text_channel(F"Open", reason=F"Setting up ticketer", topic=F"Opening a ticket")
                await ch.set_permissions(ctx.guild.default_role, send_messages=False)
                tkmbed.title += " has been turned on"
                tkmbed.description = F"Tickets are now created in {category.mention} cateogry and {ch.mention}\nPlease don't delete the channel, if you did,\nPlease use this command `.ticket Off` to turn off the ticketer\nYou can see the status of the ticketer with `.ticket Status`"
                await ch.send(embed=tkviewmbed, view=ticket.TicketView(self.bot))
        elif option == "off":
            if not number:
                tkmbed.title += " is already turned off"
            else:
                await self.bot.mongodb.tickets.delete_one({"guild_id": ctx.guild.id})
                tkmbed.title += " has been turned off"
                tkmbed.description = "You can Delete the categor(y/ies) and channel(s)"
        elif option == "status":
            if not number:
                tkmbed.title += " is turned off"
            else:
                mongo = await self.bot.mongodb.tickets.find_one({"guild_id": ctx.guild.id})
                category = self.bot.get_channel(mongo["category"])
                tkmbed.title += " is turned on"
                tkmbed.description = F"Tickets are now created in the {category.mention} cateogry"
        elif option == "button":
            if not number:
                tkmbed.title += " is turned off"
            else:
                tkmbed.title += " message has been sent"
                await ctx.send(embed=tkviewmbed, view=ticket.TicketView(self.bot))
        elif option == "category":
            if value:
                tkmbed.title += " category has been set"
                tkmbed.description = F"Tickets are now created in {value.mention} cateogry"
                if number:
                    await self.bot.mongodb.tickets.update_one({"guild_id": ctx.guild.id}, {"$set": {"category": value}})
                else:
                    await self.bot.mongodb.tickets.insert_one({"guild_name": ctx.guild.name, "guild_id": ctx.guild.id, "category": value.id, "number": 1})
            else:
                tkmbed.title += " you must pass a category for value"
        await ctx.reply(embed=tkmbed)

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
            await ctx.reply(embed=lvmbed)
            await ctx.me.guild.leave()

def setup(bot):
    bot.add_cog(Settings(bot))
