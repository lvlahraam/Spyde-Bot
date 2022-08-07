import discord, contextlib
from discord.ext import commands


class HelpButton(discord.ui.Button):
    def __init__(self, view, **kwargs):
        super().__init__(**kwargs)
        self.help = view.help
        self.homepage = view.homepage
        self.cogs = view.cogs
        self.home = view.home

    def gts(self, command):
        return f"• **{command.qualified_name}** *({', '.join(command.aliases)})* {command.brief or ''} - {command.description or 'No description found...'}\n"

    async def callback(self, interaction: discord.Interaction):
        if self.label == "Home":
            self.disabled = True
            self.style = discord.ButtonStyle.grey
            await interaction.response.edit_message(embed=self.homepage, view=self.view)
        elif self.label == "Delete":
            await interaction.message.delete()
            await interaction.response.send_message(
                content="Deleted the message...", ephemeral=True
            )
        else:
            self.home.disabled = False
            self.home.style = discord.ButtonStyle.green
            cog = self.cogs.get(self.label)
            helpmbed = discord.Embed(
                color=self.help.context.bot.color,
                title=f"{self.help.emojis.get(cog.qualified_name) or '❓'} {cog.qualified_name}",
                description=f"{cog.description}\n\n{''.join(self.gts(command) for command in cog.walk_commands())}",
                timestamp=self.help.context.message.created_at,
            )
            helpmbed.set_author(
                name=interaction.user, icon_url=interaction.user.display_avatar.url
            )
            helpmbed.set_footer(text="() is aliases | <> is required | [] is optional")
            await interaction.response.edit_message(embed=helpmbed, view=self.view)


class HelpButtonView(discord.ui.View):
    def __init__(self, help, mapping):
        super().__init__(timeout=None)
        self.help = help
        self.mapping = mapping
        self.homepage = discord.Embed(
            color=self.help.context.bot.color,
            title=f"{self.help.context.me.name}'s Help",
            description="For more help or information use the menu.",
            timestamp=self.help.context.message.created_at,
        )
        self.cogs = {}
        self.add_item(
            item=HelpButton(emoji="🏠", label="Help", style=discord.ButtonStyle.green)
        )
        for cog, commands in self.mapping.items():
            if cog and not cog.qualified_name.startswith("On"):
                self.cogs[cog.qualified_name] = cog
                self.add_item(
                    item=HelpButton(
                        view=self,
                        emoji=self.help.emojis.get(cog.qualified_name),
                        label="Scissors",
                        style=discord.ButtonStyle.blurple,
                    )
                )
        self.add_item(
            item=HelpButton(emoji="💣", label="Delete", style=discord.ButtonStyle.red)
        )

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id == self.help.context.author.id:
            return True
        icmbed = discord.Embed(
            color=self.help.context.bot.color,
            title="You can't use this",
            description=f"{interaction.user.mention} - Only {self.help.context.author.mention} can use that\nCause they did the command\nIf you wanted to use the command, do what they did",
            timestamp=self.help.context.message.created_at,
        )
        icmbed.set_thumbnail(url=self.help.context.me.display_avatar.url)
        icmbed.set_author(
            name=interaction.user, icon_url=interaction.user.display_avatar.url
        )
        await interaction.response.send_message(embed=icmbed, ephemeral=True)
        return False


class HelpSelect(discord.ui.Select):
    def __init__(self, view, **kwargs):
        super().__init__(**kwargs)
        self.help = view.help
        self.hompage = view.homepage
        self.cogs = view.cogs
        self.home = view.home

    def gts(self, command):
        return f"• **{command.qualified_name}** *({', '.join(command.aliases)})* {command.brief or ''} - {command.description or 'No description found...'}\n"

    async def callback(self, interaction: discord.Interaction):
        self.home.disabled = False
        self.home.style = discord.ButtonStyle.green
        cog = self.cogs.get(self.values[0])
        helpmbed = discord.Embed(
            color=self.help.context.bot.color,
            title=f"{self.help.emojis.get(cog.qualified_name) or '❓'} {cog.qualified_name}",
            description=f"{cog.description}\n\n{''.join(self.gts(command) for command in cog.walk_commands())}",
            timestamp=self.help.context.message.created_at,
        )
        helpmbed.set_author(
            name=interaction.user, icon_url=interaction.user.display_avatar.url
        )
        helpmbed.set_footer(text="() is aliases | <> is required | [] is optional")
        await interaction.response.edit_message(embed=helpmbed, view=self.view)


class HelpSelectView(discord.ui.View):
    def __init__(self, help, mapping):
        super().__init__(timeout=None)
        self.help = help
        self.mapping = mapping
        self.homepage = discord.Embed(
            color=self.help.context.bot.color,
            title=f"{self.help.context.me.name}'s Help",
            description="For more help or information use the menu.",
            timestamp=self.help.context.message.created_at,
        )
        self.cogs = {}
        options = []
        for cog, commands in self.mapping.items():
            if cog and not cog.qualified_name.startswith("On"):
                self.cogs[cog.qualified_name] = cog
                option = discord.SelectOption(
                    emoji=self.help.emojis.get(cog.qualified_name) or "❓",
                    label=f"{cog.qualified_name} Category ({len(commands)})",
                    description=cog.description,
                    value=cog.qualified_name,
                )
                options.append(option)
        self.add_item(
            item=HelpSelect(
                placeholder="Where do you want to go...",
                options=options,
                min_values=1,
                max_values=1,
                view=self,
            )
        )
        self.add_item(
            item=discord.ui.Button(
                emoji="🔗",
                label="Invite Bot",
                url=discord.utils.oauth_url(
                    self.help.context.bot.user.id,
                    permissions=discord.Permissions.all(),
                    scopes=["bot", "applications.commands"],
                ),
            )
        )

    @discord.ui.button(
        emoji="🏠", label=f"Home Page", style=discord.ButtonStyle.grey, disabled=True
    )
    async def home(self, interaction: discord.Interaction, button: discord.ui.Button):
        button.disabled = True
        button.style = discord.ButtonStyle.grey
        await interaction.response.edit_message(embed=self.homepage, view=button.view)

    @discord.ui.button(
        emoji="💣", label=f"Delete Message", style=discord.ButtonStyle.red
    )
    async def delete(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.message.delete()
        await interaction.response.send_message(
            content="Deleted the message...", ephemeral=True
        )

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id == self.help.context.author.id:
            return True
        icmbed = discord.Embed(
            color=self.help.context.bot.color,
            title="You can't use this",
            description=f"{interaction.user.mention} - Only {self.help.context.author.mention} can use that\nCause they did the command\nIf you wanted to use the command, do what they did",
            timestamp=self.help.context.message.created_at,
        )
        icmbed.set_thumbnail(url=self.help.context.me.display_avatar.url)
        icmbed.set_author(
            name=interaction.user, icon_url=interaction.user.display_avatar.url
        )
        await interaction.response.send_message(embed=icmbed, ephemeral=True)
        return False


class CustomHelp(commands.HelpCommand):
    def __init__(self):
        super().__init__(
            command_attrs={"help": "The help command for this bot", "aliases": ["h"]}
        )
        self.emojis = {
            "Economy": "💸",
            "Fun": "😹",
            "Game": "🕹️",
            "Information": "🔎",
            "Moderation": "🎩",
            "Music": "🎶",
            "Owner": "👑",
            "Settings": "🔧",
            "Utility": "🧰",
        }

    def get_command_signature(self, command: commands.Command, group: bool):
        return f"• **{command.qualified_name}** *({', '.join(command.aliases)})* {command.brief or ''} {f'- {command.description}' if group is True else ''}\n"

    # Help Main
    async def send_bot_help(self, mapping):
        view = HelpSelectView(self, mapping)
        view.homepage.add_field(
            name="Prefix:",
            value=self.context.prefix or "In DM you don't need to use prefix",
            inline=False,
        )
        view.homepage.add_field(
            name="Arguments:",
            value="() means you can use the command with another name.\n<> means the argument is required.\n[] means the argument is optional.\n\n***DO NOT TYPE THESE SYMBOLS WHEN USING A COMMAND***",
            inline=False,
        )
        view.homepage.set_author(
            name=self.context.author, icon_url=self.context.author.display_avatar.url
        )
        view.message = await self.context.reply(embed=view.homepage, view=view)
        return

    # Help Cog
    async def send_cog_help(self, cog):
        hcogmbed = discord.Embed(
            color=self.context.bot.color,
            title=f"{self.emojis.get(cog.qualified_name) if self.emojis.get(cog.qualified_name) else '❓'} {cog.qualified_name} Category [{len(cog.get_commands())}]",
            description=f"{cog.description}\n\n",
            timestamp=self.context.message.created_at,
        )
        for command in cog.walk_commands():
            hcogmbed.description += self.get_command_signature(command, True)
        hcogmbed.set_thumbnail(url=self.context.me.display_avatar.url)
        hcogmbed.set_author(
            name=self.context.author, icon_url=self.context.author.display_avatar.url
        )
        hcogmbed.set_footer(text="() is aliases | <> is required | [] is optional")
        await self.context.reply(embed=hcogmbed)
        return

    # Help Command
    async def send_command_help(self, command):
        hcmdmbed = discord.Embed(
            color=self.context.bot.color,
            title=self.get_command_signature(command, False),
            description=command.description or "No description found...",
            timestamp=self.context.message.created_at,
        )
        hcmdmbed.set_thumbnail(url=self.context.me.display_avatar.url)
        hcmdmbed.set_author(
            name=self.context.author, icon_url=self.context.author.display_avatar.url
        )
        hcmdmbed.set_footer(text="() is aliases | <> is required | [] is optional")
        if cog := command.cog:
            hcmdmbed.add_field(
                name="Category:",
                value=f"{self.emojis.get(cog.qualified_name) if self.emojis.get(cog.qualified_name) else '❓'} {cog.qualified_name}",
            )
        can_run = "No"
        with contextlib.suppress(commands.CommandError):
            if await command.can_run(self.context):
                can_run = "Yes"
        hcmdmbed.add_field(name="Usable", value=can_run)
        if command._buckets and (cooldown := command._buckets._cooldown):
            hcmdmbed.add_field(
                name="Cooldown", value=f"{cooldown.rate} per {cooldown.per:.0f} seconds"
            )
        await self.context.reply(embed=hcmdmbed)
        return

    # Help Group
    async def send_group_help(self, group):
        hgroupmbed = discord.Embed(
            color=self.context.bot.color,
            title=self.get_command_signature(group, True),
            description=f"{group.help or 'No description found...'}\n\n",
            timestamp=self.context.message.created_at,
        )
        hgroupmbed.set_thumbnail(url=self.context.me.display_avatar.url)
        hgroupmbed.set_author(
            name=self.context.author, icon_url=self.context.author.display_avatar.url
        )
        hgroupmbed.set_footer(text="() is aliases | <> is required | [] is optional")
        for command in group.commands:
            hgroupmbed.description += f"• **{self.get_command_signature(command, True)}** - {command.description or 'No description found...'}\n"
        if cog := command.cog:
            hgroupmbed.add_field(
                name="Category",
                value=f"{self.emojis.get(cog.qualified_name) if self.emojis.get(cog.qualified_name) else '❓'} {cog.qualified_name}",
            )
        can_run = "No"
        with contextlib.suppress(commands.CommandError):
            if await command.can_run(self.context):
                can_run = "Yes"
        hgroupmbed.add_field(name="Usable", value=can_run)
        if command._buckets and (cooldown := command._buckets._cooldown):
            hgroupmbed.add_field(
                name="Cooldown", value=f"{cooldown.rate} per {cooldown.per:.0f} seconds"
            )
        await self.context.reply(embed=hgroupmbed)
        return

    # Help Error
    async def send_error_message(self, error):
        herrormbed = discord.Embed(
            color=self.context.bot.color,
            title=error,
            timestamp=self.context.message.created_at,
        )
        herrormbed.set_thumbnail(url=self.context.me.display_avatar.url)
        herrormbed.set_author(
            name=self.context.author, icon_url=self.context.author.display_avatar.url
        )
        await self.context.reply(embed=herrormbed)
        return
