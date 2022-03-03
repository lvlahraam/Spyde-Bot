import discord, asyncio, typing, string, random
from discord.ext import commands
from core.views import confirm, pagination

import discord, expr

class CalculatorButton(discord.ui.Button):
    def __init__(self, view, **kwargs):
        self.mainview = view
        self.embed = view.embed
        self.options = {
        "7": "7",
        "8": "8",
        "9": "9",
        "/": "/",
        "4": "4",
        "5": "5",
        "6": "6",
        "*": "*",
        "1": "1",
        "2": "2",
        "3": "3",
        "-": "-",
        "0": "0",
        ".": ".",
        "=": "=",
        "+": "+"
        }
        self.math = ""

    async def callback(self, interaction:discord.Interaction):
        if self.label != "=" or self.label != "^":
            equalbutton = discord.utils.get(self.mainview.children, custom_id="equalbutton")
            equalbutton.disabled = False
            resetbutton = discord.utils.get(self.mainview.children, custom_id="resetbutton")
            resetbutton.disabled = False
            option = self.option[self.label]
            self.math += option
            self.embed.description = self.math
        if self.label == "=":
            self.disabled = True
            result = expr.evaluate(self.math)
            self.embed.description += F"\nResult: {result}"
        if self.label == "^":
            self.disabled = True
            self.math = ""
            self.embed.description = "Enter more numbers..."
        await interaction.response.edit_message(embed=self.embed, view=self.view)


class CalculatorView(discord.ui.View):
    def __init__(self, ctx, embed):
        self.ctx = ctx
        self.embed = embed
        self.add_item(CalculatorButton(label="/", row=0, view=self))
        self.add_item(CalculatorButton(label="*", row=0, view=self))
        self.add_item(CalculatorButton(label="-", row=0, view=self))
        self.add_item(CalculatorButton(label="+", row=0, view=self))
        self.add_item(CalculatorButton(label="7", row=1, view=self))
        self.add_item(CalculatorButton(label="8", row=1, view=self))
        self.add_item(CalculatorButton(label="9", row=1, view=self))
        self.add_item(CalculatorButton(label="%", row=1, view=self))
        self.add_item(CalculatorButton(label="4", row=2, view=self))
        self.add_item(CalculatorButton(label="5", row=2, view=self))
        self.add_item(CalculatorButton(label="6", row=2, view=self))
        self.add_item(CalculatorButton(label="(", row=2, view=self))
        self.add_item(CalculatorButton(label="1", row=3, view=self))
        self.add_item(CalculatorButton(label="2", row=3, view=self))
        self.add_item(CalculatorButton(label="3", row=3, view=self))
        self.add_item(CalculatorButton(label=")", row=3, view=self))
        self.add_item(CalculatorButton(label="0", row=4, view=self))
        self.add_item(CalculatorButton(label=".", row=4, view=self))
        self.add_item(CalculatorButton(label="=", row=4, disabled=True, custom_id="equalbutton", view=self))
        self.add_item(CalculatorButton(label="^", row=4, disabled=True, custom_id="resetbutton", view=self))

    async def interaction_check(self, item:discord.ui.Item, interaction:discord.Interaction):
        if interaction.user.id != self.ctx.author.id:
            icheckmbed = discord.Embed(
                color=self.ctx.bot.color,
                title=F"You can't use this",
                description=F"{interaction.user.mention} - Only {self.ctx.author.mention} can use this\nCause they did the command\nIf you want to use this, do what they did",
                timestamp=interaction.message.created_at
            )
            icheckmbed.set_author(name=interaction.user, icon_url=interaction.user.display_avatar.url)
            await interaction.response.send_message(embed=icheckmbed, ephemeral=True)
            return False
        return True

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

    # Calculator
    @commands.command(name="calculator", aliases=["cal"], help="Calculates the given equation")
    async def calculator(self, ctx:commands.Context):
        calmbed = discord.Embed(
            color=self.bot.color,
            title="Calculator",
            timestamp=ctx.message.created_at
        )
        calmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        view = CalculatorView(ctx, calmbed)
        await ctx.reply(embed=calmbed, view=view)

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
    async def backup(self, ctx:commands.Context, option:typing.Literal["create", "delete", "info", "list", "load"]=commands.Option(description="The option you want to use"), *, value:str=commands.Option(description="The value you want to use", default=None)):
        bumbed = discord.Embed(
            color=self.bot.color,
            timestamp=ctx.message.created_at
        )
        bumbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        if option == "create":
            backups = await self.bot.mongodb.backups.find({"user_id": ctx.author.id}).to_list(length=None)
            if len(backups) <= 25:
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
                    await self.bot.mongodb.backups.insert_one({"name": name, "user_name": ctx.author.name, "user_id": ctx.author.id, "guild_name": ctx.guild.name, "guild_id": ctx.guild.id, "channels": channels, "roles": roles, "emojis": emojis, "stickers": stickers, "icon": ctx.guild.icon.url if ctx.guild.icon else None, "banner": ctx.guild.banner.url if ctx.guild.banner else None, "time": discord.utils.utcnow()})
                    bumbed.title = "Backup has been created..."
                    bumbed.description = F"Under the name of **{name}**"
                    await message.delete()
            else:
                bumbed.title = "You can't create more than 25 backups"
        elif option == "delete":
            if value:
                backup = await self.bot.mongodb.backups.find_one({"name": value, "user_id": ctx.author.id})
                if backup:
                    bumbed.title = F"Backup Info - {backup['guild_name']} / [{backup['name']}]"
                    chpag = commands.Paginator(suffix="...\n```", max_size=2048)
                    for channel in backup['channels']:
                        if type(channel) == discord.CategoryChannel: known = "/"
                        if type(channel) == discord.TextChannel: known = "#"
                        if type(channel) == discord.VoiceClient: known = ">"
                        if type(channel) == discord.StageChannel: known = ")"
                        chpag.add_line(F"{known} {channel.name}")
                    ropag = commands.Paginator(suffix="...\n```", max_size=2048)
                    for role in backup['roles']:
                        ropag.add_line(role.name)
                    if backup['icon']: bumbed.set_image(url=backup['icon'])
                    if backup['banner']: bumbed.set_thumbnail(url=backup['banner'])
                    view = confirm.ViewConfirm(ctx)
                    view.message = await ctx.reply(content="Are you sure if you want to delete this backup?", embed=bumbed, view=view)
                    await view.wait()
                    if view.value:
                        await self.bot.mongodb.backups.delete_one({"name": backup['name'], "user_id": backup['user_id']})
                        bumbed.title = "Backup has been deleted"
                else:
                    bumbed.title = "Couldn't find any backup with this name"
            else:
                bumbed.title = "You must pass an name"
        elif option == "info":
            if value:
                backup = await self.bot.mongodb.backups.find_one({"name": value, "user_id": ctx.author.id})
                if backup:
                    bumbed.title = F"Backup Info - {backup['guild_name']} / [{backup['name']}]"
                    chpag = commands.Paginator(suffix="...\n```", max_size=2048)
                    for channel in backup['channels']:
                        if type(channel) == discord.CategoryChannel: known = "/"
                        if type(channel) == discord.TextChannel: known = "#"
                        if type(channel) == discord.VoiceClient: known = ">"
                        if type(channel) == discord.StageChannel: known = ")"
                        chpag.add_line(F"{known} {channel.name}")
                    ropag = commands.Paginator(suffix="...\n```", max_size=2048)
                    for role in backup['roles']:
                        ropag.add_line(role.name)
                    if backup['icon']: bumbed.set_image(url=backup['icon'])
                    if backup['banner']: bumbed.set_thumbnail(url=backup['banner'])
                else:
                    bumbed.title = "Couldn't find any backup with this name"
            else:
                bumbed.title = "You must pass an name"
        elif option == "list":
            backups = await self.bot.mongodb.backups.find({"user_id": ctx.author.id}).to_list(length=None)
            if len(backups) > 0:
                bumbed.title = "Backups"
                bumbed.description = "```"
                for backup in backups:
                    bumbed.description += F"{backup['guild_name']} / [{backup['name']}] - {discord.utils.format_dt(backup['time'], style='f')} ({discord.utils.format_dt(backup['time'], style='R')})\n"
                bumbed.description += "```"
            else:
                bumbed.title = "You don't have any backups"
        elif option == "load":
            if value:
                backup = await self.bot.mongodb.backups.find_one({"name": value, "user_id": ctx.author.id})
                if backup:
                    bumbed.title = F"Backup Info - {backup['guild_name']} / [{backup['name']}]"
                    chpag = commands.Paginator(suffix="...\n```", max_size=2048)
                    for channel in backup['channels']:
                        if type(channel) == discord.CategoryChannel: known = "/"
                        if type(channel) == discord.TextChannel: known = "#"
                        if type(channel) == discord.VoiceClient: known = ">"
                        if type(channel) == discord.StageChannel: known = ")"
                        chpag.add_line(F"{known} {channel.name}")
                    ropag = commands.Paginator(suffix="...\n```", max_size=2048)
                    for role in backup['roles']:
                        ropag.add_line(role.name)
                    if backup['icon']: bumbed.set_image(url=backup['icon'])
                    if backup['banner']: bumbed.set_thumbnail(url=backup['banner'])
                    view = confirm.ViewConfirm(ctx)
                    view.message = await ctx.reply(content="Are you sure if you want to load this backup?", embed=bumbed, view=view)
                    await view.wait()
                    if view.value:
                        bumbed.title = F"Loading Backup!"
                        bumbed.description = F"{backup['guild_name']} / [{backup['name']}]\nThis might take a while..."
                        for channel in ctx.guild.channels:
                            await channel.delete()
                        for role in ctx.guild.roles:
                            await role.delete()
                        for emoji in ctx.guild.emojis:
                            await emoji.delete()
                        for sticker in ctx.guild.stickers:
                            await sticker.delete()
                        await asyncio.sleep(2.5)
                        for channel in backup['channels']:
                            await ctx.guild._create_channel(channel.name, type=channel.type, overwrites=channel.overwrites, category=channel.category)
                        for role in backup['roles']:
                            await ctx.guild.create_role(name=role.name, permissions=role.permissions, colour=role.colour, hoist=role.hoist, mentionable=role.mentionable)
                        for emoji in backup['emojis']:
                            await ctx.guild.create_custom_emoji(name=emoji.name, image=emoji.url)
                        for sticker in backup['stickers']:
                            await ctx.guild.create_sticker(name=sticker.name, image=sticker.url)
                        await asyncio.sleep(2.5)
                        bumbed.title = F"Backup Loaded!"
                        return await ctx.guild.text_channels[0].send(embed=bumbed)
                else:
                    bumbed.title = "Couldn't find any backup with this name"
            else:
                bumbed.title = "You must pass an name"
        await ctx.reply(embed=bumbed)

    # Notes
    @commands.command(name="notes", aliases=["nt"], help="Taking notes with this")
    async def notes(self, ctx:commands.Context, option:typing.Literal["add", "remove", "clear", "show"]=commands.Option(description="The option you want to use"), *, value:str=commands.Option(description="The value you want to use", default=None)):
        ntmbed = discord.Embed(
            color=self.bot.color,
            timestamp=ctx.message.created_at
        ) 
        ntmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        notes = await self.bot.mongodb.notes.find({"user_id": ctx.author.id}).to_list(length=None)
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
                note = await self.bot.mongodb.notes.find_one({"user_id": ctx.author.id, "task": value})
                if note:
                    ntmbed.title = "Removed the task from your notes:"
                    await self.bot.mongodb.notes.delete_one({"user_id": ctx.author.id, "task": value})
                else:
                    ntmbed.title = "This number is not in your notes:"
        elif option == "clear":
            if not notes:
                ntmbed.title = "You don't have any note"
            else:
                tasks = []
                counter = 0
                for stuff in notes:
                    tasks.append(F"[{counter}.]({stuff['jump_url']}) {stuff['task']}\n")
                    counter += 1
                ntmbed.title=F"{ctx.author.display_name}'s notes:"
                ntmbed.description="".join(task for task in tasks)
                view = confirm.ViewConfirm(ctx)
                view.message = await ctx.reply(content="Are you sure if you want to clear everything:", embed=ntmbed, view=view)
                await view.wait()
                if view.value:
                    await self.bot.mongodb.notes.delete_many({"user_id": ctx.author.id})
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
