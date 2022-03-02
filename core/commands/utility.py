import discord, asyncio, typing, string, random
from discord.ext import commands
from core.views import confirm, pagination

class Utility(commands.Cog, description="Useful stuff that are open to everyone"):
    def __init__(self, bot):
        self.bot = bot

    # Cleanup
    @commands.command(name="cleanup", aliases=["cu"], help="Deletes bot's messagess for the given amount")
    async def cleanup(self, ctx:commands.Context, *, amount:int=commands.Option(description="The amount of the bot messages you want to cleanup")):
        cumbed = discord.Embed(
            color=self.bot.color,
            title=F"Cleaned-up {amount} of bot messages",
        )
        cumbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        await ctx.channel.purge(limit=amount, check=lambda m: m.author.id == self.bot.user.id, bulk=False)
        await ctx.reply(embed=cumbed, delete_after=5)

    # Remind
    @commands.command(name="remind", aliases=["rm"], help="Reminds you with the given task and seconds")
    async def remind(self, ctx:commands.Context, seconds:int=commands.Option(description="The seconds you want to get reminded at"), *, task:str=commands.Option(description="The task you want to get reminded of")):
        await ctx.reply(F"{ctx.author.mention}, in {seconds} seconds:, I will remind you About: **{task}**", allowed_mentions=discord.AllowedMentions(users=True))
        await asyncio.sleep(seconds)
        view = discord.ui.View()
        view.add_item(item=discord.ui.Button(label="Go to original message", url=ctx.message.jump_url))
        await ctx.reply(F"{ctx.author.mention} Reminded you, as you said in {seconds} seconds, it's been **{discord.utils.format_dt(ctx.message.created_at, style='R')}**, About: **{task}**", view=view, allowed_mentions=discord.AllowedMentions(users=True))

    # AFK
    @commands.command(name="afk", help="Makes you AFK")
    async def afk(self, ctx:commands.Context, *, reason:str=commands.Option(description="The reason for being AFK", default=None)):
        reason = reason or "Unspecified"
        afk = self.bot.afks.get(ctx.author.id)
        afkmbed  = discord.Embed(
            color=self.bot.color,
            timestamp=ctx.message.created_at
        )
        afkmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        if not afk:
            afk = self.bot.afks[ctx.author.id] = {"time":discord.utils.utcnow(), "reason":reason, "jump_url":ctx.message.jump_url}
            view = discord.ui.View()
            view.add_item(item=discord.ui.Button(label="Go to original message", url=afk["jump_url"]))
            afkmbed.title = "Set your AFK"
            afkmbed.description = F"Reason: **{afk['reason']}**"
            await ctx.reply(embed=afkmbed)

    # Backup
    @commands.command(name="backup", aliases=["bu"], help="Backing-up data with this")
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @commands.bot_has_permissions(administrator=True)
    async def backup(self, ctx:commands.Context, option:typing.Literal["create", "delete", "list"]=commands.Option(description="The option you want to use"), *, value:str=commands.Option(description="The value you want to use", default=None)):
        bumbed = discord.Embed(
            color=self.bot.color,
            timestamp=ctx.message.created_at
        )
        bumbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        if option == "create":
            view = confirm.ViewConfirm(ctx)
            view.message = await ctx.reply(content="Are you sure if you want to create a backup for this server?", view=view)
            await view.wait()
            if view.value:
                bumbed.title = "Creating backup..."
                message = await ctx.reply(embed=bumbed)
                channels = []
                for channel in ctx.guild.channels:
                    channels.append(channel)
                roles = []
                for role in ctx.guild.roles:
                    roles.append(role)
                emojis = []
                for emoji in ctx.guild.emojis:
                    emojis.append(emoji)
                stickers = []
                for sticker in ctx.guild.stickers:
                    stickers.append(sticker)
                name = "".join(random.choice(F"{string.ascii_uppercase}{string.digits}") for _ in range(10))
                await self.bot.mongodb.backups.insert_one({"name": name, "user_name": ctx.author, "user_id": ctx.author.id, "guild_name": ctx.guild, "guild_id": ctx.guild.id, "channels": channels, "roles": roles, "emojis": emojis, "stickers": stickers, "icon": ctx.guild.icon, "banner": ctx.guild.banner, "time": discord.utils.utcnow()})
                bumbed.title = "Backup has been created..."
                bumbed.description = F"Under the name of **{name}**"
        elif option == "delete":
            if value:
                backup = await self.bot.mongodb.backups.find_one({"name": value, "user_id": ctx.author.id})
                if backup:
                    bumbed.title = F"Backup Info - {backup['guild_name']} / [{backup['name']}]"
                    bumbed.description = F"{discord.utils.format_dt(backup['time'], style='F')} ({discord.utils.format_dt(backup['time'], style='R')})"
                    bumbed.add_field(name="Channels:", value="\n".join(f'{channel.name}' for channel in backup['channels']))
                    bumbed.add_field(name="Roles:", value="\n".join(f'{role.name}' for role in backup['roles']))
                    view = confirm.ViewConfirm(ctx)
                    view.message = await ctx.reply(content="Are you sure if you want to delete this backup?", embed=bumbed, view=view)
                    await view.wait()
                    if view.value:
                        await self.bot.mongodb.backups.delete_one({"name": backup['name'], "user_id": backup['user_id']})
                        bumbed.title = "Backup has been deleted"
                else:
                    bumbed = "Couldn't find any backup with this name"
            else:
                bumbed = "You must pass an name"

    # Notes
    @commands.command(name="notes", aliases=["nt"], help="Taking notes with this")
    async def notes(self, ctx:commands.Context, option:typing.Literal["add", "remove", "clear", "show"]=commands.Option(description="The option you want to use"), *, value:str=commands.Option(description="The value you want to use", default=None)):
        ntmbed = discord.Embed(
            color=self.bot.color,
            timestamp=ctx.message.created_at
        ) 
        ntmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        notes = await self.bot.mongodb.notes.find({"user_id": ctx.author.id}).to_list(length=100)
        if option == "add":
            note = await self.bot.mongodb.notes.find_one({"user_id": ctx.author.id, "task": value})
            ntmbed.description = value
            if note:
                ntmbed.title = "This task already in your notes:"
            else:
                ntmbed.title = "Added the task to your notes:"
                await self.bot.mongodb.notes.insert_one({"user_name": ctx.author.name, "user_id": ctx.author.id, "task": value, "jump_url": ctx.message.jump_url})
        elif option == "remove":
            if not notes:
                ntmbed.title = "You don't have any note"
            else:
                ntmbed.description = value
                note = await self.bot.mongodb.find_one({"user_id": ctx.author.id, "task": value})
                if note:
                    ntmbed.title = "Removed the task from your notes:"
                    await self.bot.mongodb.notes.delete_one({"user_id": ctx.author.id, "task": value})
                else:
                    ntmbed.title = "This number is not in your notes:"
        elif option == "clear":
            if not notes:
                ntmbed.title = "You don't have any note"
            else:
                view = confirm.ViewConfirm(ctx)
                view.message = await ctx.reply(content="Are you sure if you want to clear everything:", view=view)
                await view.wait()
                if view.value:
                    await self.bot.mongodb.delete_many({"user_id": ctx.author.id})
                    ntmbed.title = "Cleared your notes!"
        elif option == "show":
            if not notes: 
                ntmbed.title = F"{ctx.author.display_name} doesn't have any note"
            else:
                tasks = []
                counter = 0
                for stuff in notes:
                    tasks.append(F"[{counter}.]({stuff['jump_url']}) {stuff['task']}\n")
                    counter += 1
                ntmbed.title=F"{ctx.author.display_name}'s notes:"
                ntmbed.description="".join(task for task in tasks)
        await ctx.reply(embed=ntmbed)

def setup(bot):
    bot.add_cog(Utility(bot))
