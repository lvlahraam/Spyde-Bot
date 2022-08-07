import discord, io, textwrap, contextlib, traceback
from discord.ext import commands


class Owner(commands.Cog, description="Only my Developer can use these!"):
    def __init__(self, bot):
        self.bot = bot

    # Eval
    @commands.hybrid_command(
        name="eval",
        aliases=["ev"],
        description="Evaluates the given code",
        brief="<code>",
    )
    @commands.is_owner()
    @discord.app_commands.describe(code="The python code to evaluate")
    async def _eval(self, ctx: commands.Context, *, code: str):
        env = {
            "self": self,
            "discord": discord,
            "commands": commands,
            "bot": self.bot,
            "ctx": ctx,
            "message": ctx.message,
            "author": ctx.author,
            "guild": ctx.guild,
            "channel": ctx.channel,
        }
        env.update(globals())
        if code.startswith("```") and code.endswith("```"):
            code = "\n".join(code.split("\n")[1:-1])
        code = code.strip("` \n")
        stdout = io.StringIO()
        to_compile = f"async def func():\n{textwrap.indent(code, '  ')}"
        try:
            exec(to_compile, env)
        except Exception as e:
            return await ctx.reply(f"```py\n{e.__class__.__name__}: {e}\n```")
        func = env["func"]
        try:
            with contextlib.redirect_stdout(stdout):
                ret = await func()
        except Exception as e:
            value = stdout.getvalue()
            await ctx.reply(f"```py\n{value}{traceback.format_exc()}\n```")
        else:
            value = stdout.getvalue()
            try:
                await ctx.message.add_reaction("\u2705")
            except:
                pass
            if ret is None:
                if value:
                    await ctx.reply(f"```py\n{value}\n```")
            else:
                await ctx.reply(f"```py\n{value}{ret}\n```")

    # Sync
    @commands.hybrid_command(
        name="sync",
        aliases=["syc"],
        description="Syncs the commands [for the given guildid]",
        brief="[guildid]",
    )
    @commands.is_owner()
    @discord.app_commands.describe(
        guildid="The guild you want to sync the commands for"
    )
    async def sync(self, ctx: commands.Context, guildid: int = None):
        await self.bot.tree.sync(guild=None if not guildid else discord.Object(guildid))
        await ctx.reply(
            f"Commands have been synced {'globally' if not guildid else f'localy for {guildid}'}"
        )

    # Unsync
    @commands.hybrid_command(
        name="unsync",
        aliases=["usyc"],
        description="Unsyncs the commands [for the given guildid]",
        brief="[guildid]",
    )
    @commands.is_owner()
    @discord.app_commands.describe(
        guildid="The guild you want to unsync the commands for"
    )
    async def unsync(self, ctx: commands.Context, guildid: int = None):
        self.bot.tree.clear_commands(
            guild=None if not guildid else discord.Object(guildid)
        )
        await self.bot.tree.sync(guild=None if not guildid else discord.Object(guildid))
        await ctx.reply(
            f"Commands have been unsynced {'globally' if not guildid else f'localy for {guildid}'}"
        )

    # Load
    @commands.hybrid_command(
        name="load",
        aliases=["ld"],
        description="Loads the given extension based on the given category",
        brief="<category> <extension>",
    )
    @commands.is_owner()
    @discord.app_commands.describe(
        category="The category of the extension",
        extension="The extension you want to load",
    )
    async def load(self, ctx: commands.Context, *, category: str, extension: str):
        loadmbed = discord.Embed(
            color=self.bot.color,
            title=f"Loaded {extension}.",
            timestamp=ctx.message.created_at,
        )
        loadmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        await self.bot.load_extension(f"core.{category}.{extension}")
        await ctx.reply(embed=loadmbed)

    # Unload
    @commands.hybrid_command(
        name="unload",
        aliases=["uld"],
        description="Unloads the given extension based on the given category",
        brief="<category> <extensions>",
    )
    @commands.is_owner()
    @discord.app_commands.describe(
        category="The category of the extension",
        extension="The extension you want to unload",
    )
    async def unload(self, ctx: commands.Context, *, category: str, extension: str):
        unloadmbed = discord.Embed(
            color=self.bot.color,
            title=f"Unloaded {extension}.",
            timestamp=ctx.message.created_at,
        )
        unloadmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        await self.bot.unload_extension(f"core.{category}.{extension}")
        await ctx.reply(embed=unloadmbed)

    # Reload
    @commands.hybrid_command(
        name="reload",
        aliases=["rld"],
        description="Reloads every cog or the given cog",
        brief="[extension]",
    )
    @commands.is_owner()
    @discord.app_commands.describe(extension="The extension you want to reload")
    async def reload(self, ctx: commands.Context, *, extension: str = None):
        rldmbed = discord.Embed(
            color=self.bot.color, description="", timestamp=ctx.message.created_at
        )
        rldmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        if not extension:
            rldmbed.title = "Reloaded every cog"
            rldmbed.description += f"Commands:\n"
            for command in self.bot._commands:
                try:
                    self.bot.reload_extension(f"core.commands.{command}")
                    rldmbed.description += f"🥗 {command}\n"
                except Exception as error:
                    rldmbed.description += f"🏮 {command}\n"
                    rldmbed.description += f"🔰 {error}\n"
            rldmbed.description += f"Events:\n"
            for event in self.bot._events:
                try:
                    self.bot.reload_extension(f"core.events.{event}")
                    rldmbed.description += f"🥗 {event}\n"
                except Exception as error:
                    rldmbed.description += f"🏮 {event}\n"
                    rldmbed.description += f"🔰 {error}\n"
        else:
            rldmbed.title = f"Reloaded {extension}."
            self.bot.reload_extension(extension)
        await ctx.reply(embed=rldmbed)

    # Toggle
    @commands.hybrid_command(
        name="toggle",
        toggle=["tg"],
        description="Toggles on and off the given command",
        brief="<command>",
    )
    @commands.is_owner()
    @discord.app_commands.describe(command="The command you want to toggle")
    async def toggle(self, ctx: commands.Context, command: str):
        command = self.bot.get_command(command)
        tgmbed = discord.Embed(
            color=self.bot.color, title=f"Toggled", timestamp=ctx.message.created_at
        )
        tgmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        if not command.enabled:
            command.enabled = True
            tgmbed.description = f"Enabled {command.name} command"
        else:
            command.enabled = False
            tgmbed.description = f"Disabled {command.name} command"
        await ctx.reply(embed=tgmbed)

    # Shutdown
    @commands.hybrid_command(name="shutdown", description="Shutdowns the bot")
    @commands.is_owner()
    async def logout(self, ctx: commands.Context):
        shutdownmbed = discord.Embed(
            color=self.bot.color,
            title="Shutting-down",
            timestamp=ctx.message.created_at,
        )
        shutdownmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        await ctx.reply(embed=shutdownmbed)
        await self.bot.close()

    # Blacklist
    @commands.hybrid_command(
        name="blacklist",
        aliases=["bl"],
        description="Shows the blacklist and Adds or Removes the given user from blacklist [for the given reason]",
        brief=f"<user> [reason]",
    )
    @commands.is_owner()
    @discord.app_commands.describe(
        user="The user you want to add or remove from blacklist",
        reason="The reason for adding or removing the user from blacklist",
    )
    async def blacklist(
        self, ctx: commands.Context, user: discord.User, *, reason: str = None
    ):
        reason = reason or "Unspecified"
        blmbed = discord.Embed(
            color=self.bot.color, description="", timestamp=ctx.message.created_at
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
                    blmbed.description += (
                        f"{user} | {user.mention} - {users['reason']}\n"
                    )
        else:
            blacklisted = await self.bot.mongodb.blacklist.find_one(
                {"user_id": user.id}
            )
            if not blacklisted:
                await self.bot.mongodb.blacklist.insert_one(
                    {"user_name": user.name, "user_id": user.id, "reason": reason}
                )
                blmbed.title = f"Added {user} to blacklist"
            else:
                await self.bot.mongodb.blacklist.delete_many({"user_id": user.id})
                blmbed.title = f"Removed {user} from blacklist"
        await ctx.reply(embed=blmbed)


async def setup(bot):
    await bot.add_cog(Owner(bot))
