import discord

class ViewVote(discord.ui.View):
    def __init__(self, ctx, usage, job, message, voters):
        super().__init__(timeout=15)
        self.ctx = ctx
        self.usage = usage
        self.job = job
        self.message = message
        self.vote = 0
        self.voters = voters
        self.already = []
    
    @discord.ui.button(emoji="👍", style=discord.ButtonStyle.blurple)
    async def upvote(self, button:discord.ui.Button, interaction:discord.Interaction):
        if interaction.user.id in self.already:
            return await interaction.response.send_message(content=F"{interaction.user.mention} you can't vote more than one time", ephemeral=True)
        self.vote += 1
        self.counter.label = F"{self.vote}/{self.voters}"
        self.already.append(interaction.user.id)
        if self.vote == self.voters:
            button.disabled = True
            await interaction.response.edit_message(content=F"Everyone voted for: {self.usage}")
            await interaction.response.send_message(content=self.message)
            return await self.job()
        await interaction.response.send_message(content=F"{interaction.user.mention} has voted for: {self.usage}")

    @discord.ui.button(style=discord.ButtonStyle.gray, disabled=True)
    async def counter(self, button:discord.ui.Button, interaction:discord.Interaction):
        return

    @discord.ui.button(emoji="👎", style=discord.ButtonStyle.red)
    async def downvote(self, button:discord.ui.Button, interaction:discord.Interaction):
        if interaction.user.id in self.already:
            self.vote -= 1
            self.counter.label = F"{self.vote}/{self.voters}"
            for _id in self.already:
                if _id == interaction.user.id:
                    self.already.remove(_id)
                    break
            return await interaction.response.send_message(content=F"{interaction.user.mention} has removed his vote for: {self.usage}")
        await interaction.response.send_message(content=F"{interaction.user.mention} you have never voted", ephemeral=True)

    async def start(self, interaction:discord.Interaction=None):
        self.counter.label = F"0/{self.voters}"
        votembed = discord.Embed(
            title="Voting starts",
            description=F"Vote for {self.usage}\nTimeout is {self.timeout}",
            timestamp=self.ctx.message.created_at,
        )
        votembed.set_footer(text=self.ctx.author, icon_url=self.ctx.author.avatar.url)
        await interaction.response.send_message(embed=votembed, view=self) if interaction else await self.ctx.reply(embed=votembed, view=self)

    async def on_timeout(self):
        for children in self.children:
            children.disabled = True
        if self.vote == self.voters: return
        if self.vote != self.voters: return await self.ctx.send(content=F"Voting for {self.usage} has been ended\nVotes didn't reach the needed amount {self.voters}", view=self.view)

    async def interaction_check(self, item, interaction:discord.Interaction):
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
