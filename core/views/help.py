import discord, contextlib
from discord.ext import commands

class HelpSelect(discord.ui.Select):
    def __init__(self, view, **kwargs):
        super().__init__(**kwargs)
        self.help = view.help
        self.hompage = view.homepage
        self.cogs = view.cogs
        self.home = view.home
    def gts(self, command):
        return F"• **{command.qualified_name}** {command.signature} - {command.help or 'No help found...'}\n"
    async def callback(self, interaction:discord.Interaction):
        self.home.disabled = False
        cog = self.cogs.get(self.values[0])
        helpmbed = discord.Embed(
            color=self.help.context.bot.color,
            title=F"{self.help.emojis.get(cog.qualified_name) or '❓'} {cog.qualified_name}",
            description=F"{cog.description}\n\n{''.join(self.gts(command) for command in cog.walk_commands())}",
            timestamp=self.help.context.message.created_at
        )
        helpmbed.set_thumbnail(url=self.help.context.me.display_avatar.url)
        helpmbed.set_author(name=interaction.user, icon_url=interaction.user.display_avatar.url)
        helpmbed.set_footer(text="<> is required | [] is optional")
        await interaction.response.edit_message(embed=helpmbed, view=self.view)
class HelpView(discord.ui.View):
    def __init__(self, help, mapping):
        super().__init__(timeout=None)
        self.help = help
        self.mapping = mapping
        self.homepage = discord.Embed(
            color=self.help.context.bot.color,
            title=F"{self.help.context.me.name}'s Help",
            description="For more help or information use the menu.",
            timestamp=self.help.context.message.created_at
        )
        self.cogs = {}
        options = [
            discord.SelectOption(emoji="🏠", label=F"Home Page", description="The home page of this message", value="homepage"),
            discord.SelectOption(emoji="💣", label=F"Delete Message", description="Deletes this message", value="deletemessage")
        ]
        for cog, commands in self.mapping.items():
            if cog and not cog.qualified_name.startswith("On") and not cog.qualified_name in self.help.context.bot._others:
                self.cogs[cog.qualified_name] = cog
                option = discord.SelectOption(emoji=self.help.emojis.get(cog.qualified_name) or '❓', label=F"{cog.qualified_name} Category", description=cog.description, value=cog.qualified_name)
                options.append(option)
        self.add_item(item=HelpSelect(placeholder="Where do you want to go...", options=options, min_values=1, max_values=1, view=self))
        self.add_item(item=discord.ui.Button(emoji="🔗", label="Invite Bot", url=discord.utils.oauth_url(self.help.context.bot.user.id, permissions=discord.Permissions.all(), scopes=['bot', 'applications.commands'])))

    @discord.ui.button(emoji="🏠", label=F"Home Page", style=discord.ButtonStyle.green, disabled=True)
    async def home(self, button:discord.ui.Button, interaction:discord.Interaction):
        button.disabled = True
        await interaction.response.edit_message(embed=self.homepage)

    @discord.ui.button(emoji="💣", label=F"Delete Message", style=discord.ButtonStyle.blurple)
    async def delete(self, button:discord.ui.Button, interaction:discord.Interaction):
        await interaction.message.delete()
        await interaction.response.send_message(content="Deleted the message...", ephemeral=True)

    async def on_timeout(self):
        try:
            for item in self.children:
                if isinstance(item, discord.ui.Select):
                    item.placeholder = "Disabled due to being timed out..."
                item.disabled = True
            await self.message.edit(view=self)
        except discord.NotFound:
            return
    async def interaction_check(self, item:discord.ui.Item, interaction:discord.Interaction):
        if interaction.user.id == self.help.context.author.id:
            return True
        icheckmbed = discord.Embed(
            color=self.help.context.bot.color,
            title="You can't use this",
            description=F"{interaction.user.mention} - Only {self.help.context.author.mention} can use that\nCause they did the command\nIf you wanted to use the command, do what they did",
            timestamp=self.help.context.message.created_at
        )
        icheckmbed.set_thumbnail(url=self.help.context.me.display_avatar.url)
        icheckmbed.set_author(name=interaction.user, icon_url=interaction.user.display_avatar.url)
        await interaction.response.send_message(embed=icheckmbed, ephemeral=True)
        return False

class CustomHelp(commands.HelpCommand):
    def __init__(self):
        super().__init__(
            command_attrs={
                "help": "The help command for this bot",
                "aliases": ["h"]
            }
        )
        self.emojis = {
            "Fun": "😹",
            "Game": "🕹️",
            "Information": "🔎",
            "Moderation": "🎩",
            "Music": "🎶",
            "Owner": "👑",
            "Settings": "🔧",
            "Utility": "🧰"
        }

    # Help Main
    async def send_bot_help(self, mapping):
        view = HelpView(self, mapping)
        view.homepage.add_field(name="Prefix:", value=self.context.prefix or "In DM you don't need to use prefix", inline=False)
        view.homepage.add_field(name="Arguments:", value="[] means the argument is optional.\n<> means the argument is required.\n***DO NOT TYPE THESE SYMBOLS WHEN USING A COMMAND***", inline=False)
        view.homepage.set_thumbnail(url=self.context.me.display_avatar.url)
        view.homepage.set_author(name=self.context.author, icon_url=self.context.author.display_avatar.url)
        view.message = await self.context.reply(embed=view.homepage, view=view)
        return

    # Help Cog
    async def send_cog_help(self, cog):
        hcogmbed = discord.Embed(
            color=self.context.bot.color,
            title=F"{self.emojis.get(cog.qualified_name) if self.emojis.get(cog.qualified_name) else '❓'} {cog.qualified_name} Category [{len(cog.get_commands())}]",
            description=F"{cog.description}\n\n",
            timestamp=self.context.message.created_at
        )
        for command in cog.walk_commands():
            hcogmbed.description += F"• **{self.get_command_signature(command)}** - {command.help or 'No help found...'}\n"
        hcogmbed.set_thumbnail(url=self.context.me.display_avatar.url)
        hcogmbed.set_author(name=self.context.author, icon_url=self.context.author.display_avatar.url)
        hcogmbed.set_footer(text="<> is required | [] is optional")
        await self.context.reply(embed=hcogmbed)
        return

    # Help Command
    async def send_command_help(self, command):
        hcmdmbed = discord.Embed(
            color=self.context.bot.color,
            title=self.get_command_signature(command),
            description=command.help or "No help found...",
            timestamp=self.context.message.created_at
        )
        hcmdmbed.set_thumbnail(url=self.context.me.display_avatar.url)
        hcmdmbed.set_author(name=self.context.author, icon_url=self.context.author.display_avatar.url)
        hcmdmbed.set_footer(text="<> is required | [] is optional")
        if cog := command.cog:
            hcmdmbed.add_field(name="Category:", value=F"{self.emojis.get(cog.qualified_name) if self.emojis.get(cog.qualified_name) else '❓'} {cog.qualified_name}")
        can_run = "No"
        with contextlib.suppress(commands.CommandError):
            if await command.can_run(self.context):
                can_run = "Yes"  
        hcmdmbed.add_field(name="Usable", value=can_run)
        if command._buckets and (cooldown := command._buckets._cooldown):
            hcmdmbed.add_field(name="Cooldown", value=F"{cooldown.rate} per {cooldown.per:.0f} seconds")
        await self.context.reply(embed=hcmdmbed)
        return

    # Help Group
    async def send_group_help(self, group):
        hgroupmbed = discord.Embed(
            color=self.context.bot.color,
            title=self.get_command_signature(group),
            description=F"{group.help or 'No help found...'}\n\n",
            timestamp=self.context.message.created_at
        )
        hgroupmbed.set_thumbnail(url=self.context.me.display_avatar.url)
        hgroupmbed.set_author(name=self.context.author, icon_url=self.context.author.display_avatar.url)
        hgroupmbed.set_footer(text="<> is required | [] is optional")
        for command in group.commands:
            hgroupmbed.description += F"• **{self.get_command_signature(command)}** - {command.help or 'No help found...'}\n"
        if cog := command.cog:
            hgroupmbed.add_field(name="Category", value=F"{self.emojis.get(cog.qualified_name) if self.emojis.get(cog.qualified_name) else '❓'} {cog.qualified_name}")
        can_run = "No"
        with contextlib.suppress(commands.CommandError):
            if await command.can_run(self.context):
                can_run = "Yes"
        hgroupmbed.add_field(name="Usable", value=can_run)
        if command._buckets and (cooldown := command._buckets._cooldown):
            hgroupmbed.add_field(name="Cooldown", value=F"{cooldown.rate} per {cooldown.per:.0f} seconds")
        await self.context.reply(embed=hgroupmbed)
        return

    # Help Error
    async def send_error_message(self, error):
        herrormbed = discord.Embed(
            color=self.context.bot.color,
            title=error,
            timestamp=self.context.message.created_at
        )
        herrormbed.set_thumbnail(url=self.context.me.display_avatar.url)
        herrormbed.set_author(name=self.context.author, icon_url=self.context.author.display_avatar.url)
        await self.context.reply(embed=herrormbed)
        return
