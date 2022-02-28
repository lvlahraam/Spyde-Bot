import discord, asyncio, typing
from discord.ext import commands
from core.views import confirm

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


    # Notes
    @commands.command(name="notes", aliases=["nt"], help="Taking notes with this")
    async def notes(self, ctx:commands.Context, option:typing.Literal["add", "remove", "clear", "show"]=commands.Option(description="The options you want to use", default=None), *, value:typing.Union[str, int]=commands.Option(description="The value you want to use", default=None)):
        ntmbed = discord.Embed(
            color=self.bot.color,
            timestamp=ctx.message.created_at
        ) 
        ntmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        notes = self.bot.mongodb.notes.find({"user_id": ctx.author.id})
        if option == "add":
            if type(value) == str:
                note = await self.bot.mongodb.notes.find_one({"user_id": ctx.author.id, "task": value})
                ntmbed.description = value
                if note:
                    ntmbed.title = "This task already in your notes:"
                else:
                    ntmbed.title = "Added the task to your notes:"
                    await self.bot.mongodb.notes.insert_one({"user_name": ctx.author.name, "user_id": ctx.author.id, "task": value, "jump_url": ctx.message.jump_url})
            else:
                ntmbed.title = "You need to specify a task as string"
        elif option == "remove":
            if not notes:
                ntmbed.title = "You don't have any note"
            else:
                if type(value) == int:
                    tasks = []
                    for stuff in notes:
                        tasks.append(stuff["task"])
                    if len(tasks) < value:
                        ntmbed.title = "This number is not in your notes:"
                        ntmbed.description = value
                    else:
                        ntmbed.title = "Removed the task from your notes:"
                        ntmbed.description = tasks[value]
                        await self.bot.mongodb.notes.delete_one({"user_id": ctx.author.id, "task": tasks[value]})
                else:
                    ntmbed.title = "You need to specify a task as number"
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
