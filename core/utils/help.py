import discord, contextlib
from discord.ext import commands

class ButtonUI(discord.ui.Button):
    def __init__(self, view, **kwargs):
        super().__init__(**kwargs)
        self.help = view.help
        self.mapping = view.mapping
        self.homepage = view.homepage
    def gts(self, command):
        return F"• **{command.qualified_name}** {command.signature} - {command.help or 'No help found...'}\n"
    async def callback(self, interaction:discord.Interaction):
        if self.custom_id == "home":
            await interaction.response.edit_message(embed=self.homepage)
        elif self.custom_id == "delete":
            await interaction.message.delete()
        else:
            for cog, commands in self.mapping.items():
                name = cog.qualified_name if cog else "Alone"
                description = cog.description if cog else "Commands without category"
                cmds = cog.walk_commands() if cog else commands
                if self.custom_id == name:
                    mbed = discord.Embed(
                        color=self.help.context.bot.color,
                        title=F"{self.help.emojis.get(name) if self.help.emojis.get(name) else '❓'} {name} Category",
                        description=F"{description}\n\n{''.join(self.gts(command) for command in cmds)}",
                        timestamp=self.help.context.message.created_at
                    )
                    mbed.set_thumbnail(url=self.help.context.me.display_avatar.url)
                    mbed.set_author(name=interaction.user, icon_url=interaction.user.display_avatar.url)
                    mbed.set_footer(text="<> is required | [] is optional")
                    await interaction.response.edit_message(embed=mbed)
class ButtonView(discord.ui.View):
    def __init__(self, help, mapping):
        super().__init__(timeout=None)
        self.help = help
        self.mapping = mapping
        self.homepage = discord.Embed(
            color=self.help.context.bot.color,
            title=F"{self.help.context.me.name}'s Help",
            description="For more help or information use and click on the buttons.",
            timestamp=self.help.context.message.created_at
        )
        self.add_item(item=ButtonUI(emoji="🏠", label="Home", style=discord.ButtonStyle.green, custom_id="home", view=self))
        for cog, commands in self.mapping.items():
            if cog and not cog.qualified_name.startswith("On") and cog.qualified_name not in self.help.context.bot._others:
                self.add_item(item=ButtonUI(emoji=self.help.emojis.get(cog.qualified_name), label=cog.qualified_name, style=discord.ButtonStyle.blurple, custom_id=cog.qualified_name, view=self))
        self.add_item(item=ButtonUI(emoji="💣", label="Delete", style=discord.ButtonStyle.red, custom_id="delete", view=self))

    async def interaction_check(self, interaction:discord.Interaction):
        if interaction.user.id == self.help.context.author.id: return True
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
            "Owner": "👑",
            "Utility": "🧰"
        }

    # Help Main
    async def send_bot_help(self, mapping):
        view = ButtonView(self, mapping)
        view.homepage.add_field(name="Prefix:", value=self.context.prefix or "In DM you don't need to use prefix")
        view.homepage.add_field(name="Arguments:", value="[] means the argument is optional.\n<> means the argument is required.\n***DO NOT TYPE THESE WHEN USING A COMMAND***")
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
