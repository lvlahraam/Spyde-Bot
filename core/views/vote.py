import discord

class ViewVote(discord.ui.View):
    def __init__(self, ctx, usage, voters):
        super().__init__(timeout=15)
        self.ctx = ctx
        self.usage = usage
        self.vote = 0
        self.voters = voters
        self.voted = {}
    
    @discord.ui.button(emoji="➕", style=discord.ButtonStyle.green)
    async def upvote(self, button:discord.ui.Button, interaction:discord.Interaction):
        if not self.voted.get(interaction.user.id):
            self.vote += 1
            self.counter.label = F"{self.vote}/{self.voters}"
            self.voted[interaction.user.id] = True
            await interaction.response.edit_message(view=button.view)
            return await interaction.response.send_message(content=F"{interaction.user.mention} has voted for: {self.usage}", delete_after=2.5)
        await interaction.response.send_message(content=F"{interaction.user.mention} you can't vote more than one time", ephemeral=True)

    @discord.ui.button(style=discord.ButtonStyle.gray, disabled=True)
    async def counter(self, button:discord.ui.Button, interaction:discord.Interaction):
        return

    @discord.ui.button(emoji="➖", style=discord.ButtonStyle.red)
    async def downvote(self, button:discord.ui.Button, interaction:discord.Interaction):
        if self.voted.get(interaction.user.id):
            self.vote -= 1
            self.counter.label = F"{self.vote}/{self.voters}"
            await interaction.response.edit_message(view=button.view)
            return await interaction.response.send_message(content=F"{interaction.user.mention} has removed his vote for: {self.usage}")
        await interaction.response.send_message(content=F"{interaction.user.mention} you have never voted", ephemeral=True)

    async def start(self, interaction:discord.Interaction=None):
        self.counter.label = F"0/{self.voters}"
        votembed = discord.Embed(
            title="Voting starts",
            description=F"Vote for {self.usage}\nTimeout is {self.timeout}s",
            timestamp=self.ctx.message.created_at,
        )
        votembed.set_footer(text=self.ctx.author, icon_url=self.ctx.author.avatar.url)
        await interaction.response.send_message(embed=votembed, view=self) if interaction else await self.ctx.reply(embed=votembed, view=self)

    async def on_timeout(self):
        for children in self.children:
            children.disabled = True
        await self.message.delete()

    async def interaction_check(self, item:discord.ui.Item, interaction:discord.Interaction):
        if self.ctx.voice_client:
            if interaction.user.voice:
                for member in self.ctx.me.voice.channel.members:
                    if interaction.user.id == member.id: return True
                await interaction.response.send_message(F"Only the people in {self.ctx.me.voice.channel.mention} can use this", ephemeral=True)
                return False
            await interaction.response.send_message("You must be in voice channel", ephemeral=True)
            return False
        await interaction.response.send_message("I'm not in a voice channel", ephemeral=True)
        return False
