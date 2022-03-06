import discord, pomice, io, textwrap, contextlib, traceback
from discord.ext import commands

class Owner(commands.Cog, description="Only my Developer can use these!"):
    def __init__(self, bot):
        self.bot = bot

    # Eval
    @commands.command(name="eval", help="Evaluates the given code")
    @commands.is_owner()
    async def _eval(self, ctx, *, body:str=commands.Option(description="The python code to evaluate")):
        env = {
            "self": self,
            "discord": discord,
            "commands": commands,
            "player": pomice.Player,
            "track": pomice.Track,
            "bot": self.bot,
            "ctx": ctx,
            "message": ctx.message,
            "author": ctx.author,
            "guild": ctx.guild,
            "channel": ctx.channel,
        }
        env.update(globals())
        if body.startswith("```") and body.endswith("```"):
            body = "\n".join(body.split("\n")[1:-1])
        body = body.strip("` \n")
        stdout = io.StringIO()
        to_compile = F"async def func():\n{textwrap.indent(body, '  ')}"
        try:
            exec(to_compile, env)
        except Exception as e:
            return await ctx.reply(F"```py\n{e.__class__.__name__}: {e}\n```")
        func = env["func"]
        try:
            with contextlib.redirect_stdout(stdout):
                ret = await func()
        except Exception as e:
            value = stdout.getvalue()
            await ctx.reply(F"```py\n{value}{traceback.format_exc()}\n```")
        else:
            value = stdout.getvalue()
            try:
                await ctx.message.add_reaction("\u2705")
            except:
                pass
            if ret is None:
                if value:
                    await ctx.reply(F"```py\n{value}\n```")
            else:
                await ctx.reply(F"```py\n{value}{ret}\n```")

    # Load
    @commands.command(name="load", aliases=["ld"], help="Loads the given cog")
    @commands.is_owner()
    async def load(self, ctx:commands.Context, *, cog:str=commands.Option(description="The cog's name you want to load")):
        loadmbed = discord.Embed(
            color=self.bot.color,
            title=F"Loaded {cog}.",
            timestamp=ctx.message.created_at
        )
        loadmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        self.bot.load_extension(cog)
        await ctx.reply(embed=loadmbed)

    # Unload
    @commands.command(name="unload", aliases=["uld"], help="Unloads the given cog")
    @commands.is_owner()
    async def unload(self, ctx:commands.Context, *, cog:commands.Option(description="The cog's name you want to unload")):
        unloadmbed = discord.Embed(
            color=self.bot.color,
            title=F"Unloaded {cog}.",
            timestamp=ctx.message.created_at
        )
        unloadmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        self.bot.unload_extension(cog)
        await ctx.reply(embed=unloadmbed)
  
    # Reload
    @commands.command(name="reload", aliases=["rld"], help="Reloads the given or every cog")
    @commands.is_owner()
    async def reload(self, ctx:commands.Context, *, cog:str=commands.Option(description="The cog'(s) name you want to reload", default=None)):
        rldmbed = discord.Embed(
            color=self.bot.color,
            description="",
            timestamp=ctx.message.created_at
        )
        rldmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        if not cog:
            rldmbed.title = "Reloaded every cog"
            rldmbed.description += F"Commands:\n"
            for command in self.bot._commands:
                try:
                    self.bot.reload_extension(F"core.commands.{command}")
                    rldmbed.description += F"🥗 {command}\n"
                except Exception as error:
                    rldmbed.description += F"🏮 {command}\n"
                    rldmbed.description += F"🔰 {error}\n"
            rldmbed.description += F"Events:\n"
            for event in self.bot._events:
                try:
                    self.bot.reload_extension(F"core.events.{event}")
                    rldmbed.description += F"🥗 {event}\n"
                except Exception as error:
                    rldmbed.description += F"🏮 {event}\n"
                    rldmbed.description += F"🔰 {error}\n"
            return await ctx.reply(embed=rldmbed)
        rldmbed.title = F"Reloaded {cog}."
        self.bot.reload_extension(cog)
        await ctx.reply(embed=rldmbed)

    # Toggle
    @commands.command(name="toggle", toggle=["tg"], help="Toggles on and off the given command")
    @commands.is_owner()
    async def toggle(self, ctx:commands.Context, command:str):
        command = self.bot.get_command(command)
        tgmbed = discord.Embed(
            color=self.bot.color,
            title=F"Toggled",
            timestamp=ctx.message.created_at
        )
        tgmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        if not command.enabled:
            command.enabled = True
            tgmbed.description = F"Enabled {command.name} command"
        else:
            command.enabled = False
            tgmbed.description = F"Disabled {command.name} command"
        await ctx.reply(embed=tgmbed)

    # Shutdown
    @commands.command(name="shutdown",  help="Shutdowns the bot")
    @commands.is_owner()
    async def logout(self, ctx:commands.Context):
        shutdownmbed = discord.Embed(
            color=self.bot.color,
            title="Shutting-down",
            timestamp=ctx.message.created_at
        )
        shutdownmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        await ctx.reply(embed=shutdownmbed)
        await self.bot.close()

    # Blacklist
    @commands.command(name="blacklist", aliases=["bl"], help="Puts-in or Puts-out the given user from blacklist")
    @commands.is_owner()
    async def blacklist(self, ctx:commands.Context, user:discord.User=commands.Option(description="The user you want to blacklist", default=None), *, reason:str=commands.Option(description="The reason for blacklisting the user", default=None)):
        reason = reason or "Unspecified"
        blmbed = discord.Embed(
            color=self.bot.color,
            description="",
            timestamp=ctx.message.created_at
        )
        blmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        if not user:
            blacklists = await self.bot.mongodb.blacklist.find().to_list(length=None)
            if not blacklists:
                blmbed.title = "Nobody is in Blacklist"
            else:
                blmbed.title = "Users in Blacklist"
                for users in blacklists:
                    user = self.bot.get_user(users["user_id"])
                    blmbed.description += F"{user} | {user.mention} - {users['reason']}\n"
        else:
            blacklisted = await self.bot.mongodb.blacklist.find_one({"user_id": user.id})
            if not blacklisted:
                await self.bot.mongodb.blacklist.insert_one({"user_name": user.name, "user_id": user.id, "reason": reason})
                blmbed.title = F"Added {user} to blacklist"
            else:
                await self.bot.mongodb.blacklist.delete_many({"user_id": user.id})
                blmbed.title = F"Removed {user} from blacklist"
        await ctx.reply(embed=blmbed)

    # Screenshot
    @commands.command(name="screenshot", aliases=["ss"], help="Gives a preview from the given website")
    @commands.is_owner()
    @commands.bot_has_guild_permissions(attach_files=True)
    async def screenshot(self, ctx:commands.Context, *, website:str=commands.Option(description="The website you want to take a screenshot from"), delay:int=commands.Option(description="The delay in seconds", default=None)):
        delay = delay or 0
        session = await self.bot.session.get(F"https://api.screenshotmachine.com?key=a95edd&url={website}&dimension=1366xfull&delay={delay}")
        response = io.BytesIO(await session.read())
        ssmbed = discord.Embed(
            color=self.bot.color,
            title="Here is your screenshot",
            timestamp=ctx.message.created_at
        )
        ssmbed.set_image(url="attachment://screenshot.png")
        ssmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        await ctx.reply(file=discord.File(fp=response, filename="screenshot.png"), embed=ssmbed)

def setup(bot):
    bot.add_cog(Owner(bot))
