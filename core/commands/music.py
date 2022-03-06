# NOTE: THIS BOT DOES NOT DOWNLOAD FILE ON THE DIRECTORY
import discord, pomice, asyncio, datetime, io
from discord.ext import commands
from core.views import confirm, pagination

class ViewPlayer(discord.ui.View):
    def __init__(self, ctx, music):
        super().__init__(timeout=None)
        self.ctx = ctx
        self.music = music
        self.add_item(item=discord.ui.Button(emoji="🔗", url=self.ctx.voice_client.current.uri))

    @discord.ui.button(emoji="⏯", style=discord.ButtonStyle.green)
    async def ue(self, button:discord.ui.Button, interaction:discord.Interaction):
        if self.ctx.voice_client.is_playing or self.ctx.voice_client.is_paused:
            params = {
                'title': self.ctx.voice_client.current.author,
                'thumbnail_url': self.ctx.voice_client.current.thumbnail,
                'seconds_played': self.ctx.voice_client.position/1000,
                'total_seconds': self.ctx.voice_client.current.length/1000,
                'line_1': self.ctx.voice_client.current.title,
                'line_2': self.ctx.voice_client.current.requester.display_name
            }
            session = await self.ctx.bot.session.get("https://api.jeyy.xyz/discord/player", params=params)
            response = io.BytesIO(await session.read())
            if self.ctx.voice_client.is_paused:
                await interaction.response.send_message("Resumed:", file=discord.File(fp=response, filename="player.png"), ephemeral=True)
                return await self.ctx.voice_client.set_pause(pause=False)
            await interaction.response.send_message("Paused:", file=discord.File(fp=response, filename="player.png"), ephemeral=True)
            return await self.ctx.voice_client.set_pause(pause=True)
        return await interaction.response.send_message("Resume/Pause: Nothing is playing", ephemeral=True)

    @discord.ui.button(emoji="⏹", style=discord.ButtonStyle.red)
    async def stop(self, button:discord.ui.Button, interaction:discord.Interaction):
        if self.ctx.voice_client.is_playing or self.ctx.voice_client.is_paused:
            params = {
                'title': self.ctx.voice_client.current.author,
                'thumbnail_url': self.ctx.voice_client.current.thumbnail,
                'seconds_played': self.ctx.voice_client.position/1000,
                'total_seconds': self.ctx.voice_client.current.length/1000,
                'line_1': self.ctx.voice_client.current.title,
                'line_2': self.ctx.voice_client.current.requester.display_name
            }
            session = await self.ctx.bot.session.get("https://api.jeyy.xyz/discord/player", params=params)
            response = io.BytesIO(await session.read())
            if not self.ctx.voice_client.queue.empty():
                for _ in range(self.ctx.voice_client.queue.qsize()):
                    self.ctx.voice_client.queue.get_nowait()
                    self.ctx.voice_client.queue.task_done()
                for _ in range(len(self.ctx.voice_client.lqueue)):
                    self.ctx.voice_client.lqueue.pop(0)
            await interaction.response.send_message("Stopped:", file=discord.File(fp=response, filename="player.png"), ephemeral=True)
            return await self.ctx.voice_client.stop()
        return await interaction.response.send_message("Stop: Nothing is playing", ephemeral=True)

    @discord.ui.button(emoji="⏺", style=discord.ButtonStyle.red)
    async def destroy(self, button:discord.ui.Button, interaction:discord.Interaction):
        if not self.ctx.voice_client.queue.empty():
            for _ in range(self.ctx.voice_client.queue.qsize()):
                self.ctx.voice_client.queue.get_nowait()
                self.ctx.voice_client.queue.task_done()
            for _ in range(len(self.ctx.voice_client.lqueue)):
                self.ctx.voice_client.lqueue.pop(0)
        if self.ctx.voice_client.is_playing or self.ctx.voice_client.is_paused:
            params = {
                'title': self.ctx.voice_client.current.author,
                'thumbnail_url': self.ctx.voice_client.current.thumbnail,
                'seconds_played': self.ctx.voice_client.position/1000,
                'total_seconds': self.ctx.voice_client.current.length/1000,
                'line_1': self.ctx.voice_client.current.title,
                'line_2': self.ctx.voice_client.current.requester.display_name
            }
            session = await self.ctx.bot.session.get("https://api.jeyy.xyz/discord/player", params=params)
            response = io.BytesIO(await session.read())
            await interaction.response.send_message("Destroyed:", file=discord.File(fp=response, filename="player.png"), ephemeral=True)
        else:
            await interaction.response.send_message("Destroyed", ephemeral=True)
        return await self.ctx.voice_client.destroy()

    @discord.ui.button(emoji="⏭", style=discord.ButtonStyle.blurple)
    async def skip(self, button:discord.ui.Button, interaction:discord.Interaction):
        if self.ctx.voice_client.is_playing or self.ctx.voice_client.is_paused:
            params = {
                'title': self.ctx.voice_client.current.author,
                'thumbnail_url': self.ctx.voice_client.current.thumbnail,
                'seconds_played': self.ctx.voice_client.position/1000,
                'total_seconds': self.ctx.voice_client.current.length/1000,
                'line_1': self.ctx.voice_client.current.title,
                'line_2': self.ctx.voice_client.current.requester.display_name
            }
            session = await self.ctx.bot.session.get("https://api.jeyy.xyz/discord/player", params=params)
            response = io.BytesIO(await session.read())
            if not self.ctx.voice_client.queue.empty():
                await interaction.response.send_message("Skipped:", file=discord.File(fp=response, filename="player.png"), ephemeral=True)
                return await self.ctx.voice_client.stop()
            return await interaction.response.send_message("Skip: There is nothing in the queue", ephemeral=True)
        return await interaction.response.send_message("Skip: Nothing is playing", ephemeral=True)

    @discord.ui.button(emoji="🔁", style=discord.ButtonStyle.blurple)
    async def loop(self, button:discord.ui.Button, interaction:discord.Interaction):
        if self.ctx.voice_client.is_playing or self.ctx.voice_client.is_paused:
            params = {
                'title': self.ctx.voice_client.current.author,
                'thumbnail_url': self.ctx.voice_client.current.thumbnail,
                'seconds_played': self.ctx.voice_client.position/1000,
                'total_seconds': self.ctx.voice_client.current.length/1000,
                'line_1': self.ctx.voice_client.current.title,
                'line_2': self.ctx.voice_client.current.requester.display_name
            }
            session = await self.ctx.bot.session.get("https://api.jeyy.xyz/discord/player", params=params)
            response = io.BytesIO(await session.read())
            if not self.ctx.voice_client.loop:
                self.ctx.voice_client.loop = self.ctx.voice_client.current
                return await interaction.response.send_message(F"Loop: has been turned on", file=discord.File(fp=response, filename="player.png"), ephemeral=True)
            self.ctx.voice_client.loop = None
            return await interaction.response.send_message(F"Loop: has been turned off", file=discord.File(fp=response, filename="player.png"), ephemeral=True)
        return await interaction.response.send_message.send("Loop: Nothing is playing", ephemeral=True)

    async def nowplaying(self, interaction:discord.Interaction):
        if self.ctx.voice_client.is_playing or self.ctx.voice_client.is_paused:
            npmbed = discord.Embed(
                color=self.ctx.bot.color,
                title="Playing:",
                timestamp=self.ctx.voice_client.current.ctx.message.created_at
            )
            params = {
                'title': self.ctx.voice_client.current.author,
                'thumbnail_url': self.ctx.voice_client.current.thumbnail,
                'seconds_played': self.ctx.voice_client.position/1000,
                'total_seconds': self.ctx.voice_client.current.length/1000,
                'line_1': self.ctx.voice_client.current.title,
                'line_2': self.ctx.voice_client.current.requester.display_name
            }
            session = await self.ctx.bot.session.get("https://api.jeyy.xyz/discord/player", params=params)
            response = io.BytesIO(await session.read())
            npmbed.set_image(url="attachment://player.png")
            view = discord.ui.View()
            view.add_item(item=discord.ui.Button(emoji="🔗", label="URL", url=self.ctx.voice_client.current.uri))
            return await interaction.response.send_message(embed=npmbed, file=discord.File(fp=response, filename="player.png"), view=view, ephemeral=True)
        return await interaction.response.send_message.send("Queue: Nothing is playing", ephemeral=True)

    @discord.ui.button(emoji="🎦", style=discord.ButtonStyle.grey)
    async def queue(self, button:discord.ui.Button, interaction:discord.Interaction):
        if len(self.ctx.voice_client.lqueue) > 1:
            counter = 1
            es = []
            paginator = commands.Paginator(prefix=None, suffix=None)
            for i in self.ctx.voice_client.lqueue:
                paginator.add_line(F"#{counter}  {i}")
                counter += 1
            for page in paginator.pages:
                qumbed = discord.Embed(
                    color=self.ctx.bot.color,
                    title="Queue",
                    description=page,
                    timestamp=interaction.message.created_at
                )
                qumbed.set_footer(text=interaction.user, icon_url=interaction.user.display_avatar.url)
                es.append(qumbed)
            return await pagination.ViewPagination(self.ctx, es).start(interaction) if len(es) > 1 else await interaction.response.send_message(embed=es[0], ephemeral=True)
        return await self.nowplaying(interaction)

    @discord.ui.button(emoji="🔢", style=discord.ButtonStyle.grey)
    async def lyrics(self, button:discord.ui.Button, interaction:discord.Interaction):
        if self.ctx.voice_client.is_playing or self.ctx.voice_client.is_paused:
            lyrics = await self.ctx.bot.openrobot.lyrics(F"{self.ctx.voice_client.current.title}{f' - {self.ctx.voice_client.current.artist}' if not '-' in str(self.ctx.voice_client.current.title) else ''}")
            if lyrics.lyrics:
                lys = lyrics.lyrics.split('\n')
                es = []
                paginator = commands.Paginator(prefix=None, suffix=None)
                for l in lys:
                    paginator.add_line(l)
                for page in paginator.pages:
                    lymbed = discord.Embed(
                    color=self.ctx.bot.color,
                        title=lyrics.title,
                        description=page,
                        timestamp=self.ctx.message.created_at
                    )
                    lymbed.set_thumbnail(url=lyrics.images.track or discord.Embed.Empty)
                    lymbed.set_author(name=lyrics.artist, icon_url=lyrics.images.background or discord.Embed.Empty)
                    lymbed.set_footer(text=interaction.user, icon_url=interaction.user.display_avatar.url)
                    es.append(lymbed)
                return await pagination.ViewPagination(self.ctx, es).start(interaction) if len(es) > 1 else await interaction.response.send_message(embed=es[0], ephemeral=True)
            params = {
                'title': self.ctx.voice_client.current.author,
                'thumbnail_url': self.ctx.voice_client.current.thumbnail,
                'seconds_played': self.ctx.voice_client.position/1000,
                'total_seconds': self.ctx.voice_client.current.length/1000,
                'line_1': self.ctx.voice_client.current.title,
                'line_2': self.ctx.voice_client.current.requester.display_name
            }
            session = await self.ctx.bot.session.get("https://api.jeyy.xyz/discord/player", params=params)
            response = io.BytesIO(await session.read())
            return await interaction.response.send_message(F"Lyrics: Didn't find anything", file=discord.File(fp=response, filename="player.png"), ephemeral=True)
        return await interaction.response.send_message.send("Lyrics: Nothing is playing", ephemeral=True)

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

class Music(commands.Cog, description="Jamming out with these!"):
    def __init__(self, bot):
        self.bot = bot

    def duration(self, length):
        return '%d:%d:%d'%((length/(1000*60*60))%24, (length/(1000*60))%60, (length/1000)%60)

    def bar(self, position, length, size=10):
        done = int((position/length)*size)
        return F"{'🟣'*done}{'⚫'*(size-done)}"

    def bot_voice(ctx:commands.Context):
        if ctx.voice_client:
            return True
        raise commands.CheckFailure("I'm not in a voice channel")

    def user_voice(ctx:commands.Context):
        if ctx.author.voice:
            return True
        raise commands.CheckFailure("You must be in voice channel") if not ctx.me.voice or not ctx.me.voice.channel else commands.CheckFailure(F"You must be in voice channel, {ctx.me.voice.channel.mention}")

    def full_voice(ctx:commands.Context):
        if ctx.me.voice:
            if ctx.author.voice:
                if ctx.me.voice.channel == ctx.author.voice.channel:
                    return True
                raise commands.CheckFailure(F"You must be in the same voice channel, {ctx.me.voice.channel.mention}")
            raise commands.CheckFailure("You must be in voice channel") if not ctx.me.voice or not ctx.me.voice.channel else commands.CheckFailure(F"You must be in voice channel, {ctx.me.voice.channel.mention}")
        raise commands.CheckFailure("I'm not in a voice channel")

    # Player
    @commands.command(name="player", alieses=["pr"], help="Shows you the ultimate player")
    @commands.guild_only()
    @commands.check(full_voice)
    async def player(self, ctx:commands.Context):
        prmbed = discord.Embed(
            color=self.bot.color,
            title="Now Playing:",
            timestamp=ctx.voice_client.current.ctx.message.created_at
        )
        prmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        if ctx.voice_client.is_playing or ctx.voice_client.is_paused:
            params = {
                'title': ctx.voice_client.current.author,
                'thumbnail_url': ctx.voice_client.current.thumbnail,
                'seconds_played': ctx.voice_client.position/1000,
                'total_seconds': ctx.voice_client.current.length/1000,
                'line_1': ctx.voice_client.current.title,
                'line_2': ctx.voice_client.current.requester.display_name
            }
            session = await self.bot.session.get("https://api.jeyy.xyz/discord/player", params=params)
            response = io.BytesIO(await session.read())
            prmbed.set_image(url="attachment://player.png")
            return await ctx.reply(embed=prmbed, file=discord.File(fp=response, filename="player.png"), view=ViewPlayer(ctx, self))
        prmbed.title = "Nothing is playing"
        return await ctx.reply(embed=prmbed)

    # Join
    @commands.command(name="join", aliases=["jn"], help="Joins a voice channel")
    @commands.guild_only()
    @commands.check(user_voice)
    async def join(self, ctx:commands.Context):
        jnmbed = discord.Embed(
            color=self.bot.color,
            title="Join:",
            timestamp=ctx.message.created_at
        )
        jnmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        channel = ctx.author.voice.channel
        if not ctx.me.voice:
            if channel.permissions_for(ctx.me).connect:
                self.bot.pomice.get_best_node(algorithm=pomice.enums.NodeAlgorithm.by_ping)
                await channel.connect(cls=pomice.Player)
                await ctx.guild.change_voice_state(channel=channel, self_mute=False, self_deaf=True)
                ctx.voice_client.queue = asyncio.Queue()
                ctx.voice_client.lqueue = []
                ctx.voice_client.loop = None
                jnmbed.description = F"Joined the voice channel {ctx.author.voice.channel.mention}"
                return await ctx.reply(embed=jnmbed)
            jnmbed.description = F"I don't have permission to join {channel.mention}"
            return await ctx.reply(embed=jnmbed)
        jnmbed.description = F"Someone else is using to me in {ctx.me.voice.channel.mention}"
        return await ctx.reply(embed=jnmbed)

    # Disconnect
    @commands.command(name="disconnect", aliases=["dc"], help="Disconnects from the voice channel")
    @commands.guild_only()
    @commands.check(full_voice)
    async def disconnect(self, ctx:commands.Context):
        dcmbed = discord.Embed(
            color=self.bot.color,
            title="Disconnect:",
            description=ctx.me.voice.channel.mention,
            timestamp=ctx.message.created_at
        )
        dcmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        if ctx.voice_client.is_playing or ctx.voice_client.is_paused:
            params = {
                'title': ctx.voice_client.current.author,
                'thumbnail_url': ctx.voice_client.current.thumbnail,
                'seconds_played': ctx.voice_client.position/1000,
                'total_seconds': ctx.voice_client.current.length/1000,
                'line_1': ctx.voice_client.current.title,
                'line_2': ctx.voice_client.current.requester.display_name
            }
            session = await self.bot.session.get("https://api.jeyy.xyz/discord/player", params=params)
            response = io.BytesIO(await session.read())
            dcmbed.set_image(url="attachment://player.png")
            view = discord.ui.View()
            view.add_item(item=discord.ui.Button(emoji="🔗", label="URL", url=ctx.voice_client.current.uri))
            return await ctx.reply(embed=dcmbed, file=discord.File(fp=response, filename="player.png"))
        await ctx.voice_client.destroy()                    
        return await ctx.reply(embed=dcmbed)

    # Play
    @commands.command(name="play", aliases=["pl"], help="Plays music with the given query, the query can be a url or a title or a playlist")
    @commands.guild_only()
    @commands.check(user_voice)
    async def play(self, ctx:commands.Context, *, query:str=commands.Option(description="The query you want the music from")):
        plmbed = discord.Embed(
            color=self.bot.color,
            title="Play:",
            timestamp=ctx.message.created_at
        )
        plmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        if not ctx.voice_client:
            await ctx.invoke(self.join)
        if ctx.me.voice.channel == ctx.author.voice.channel:
            results = await ctx.voice_client.get_tracks(query=query, ctx=ctx)
            if not results:
                plmbed.description = "No results were found for that query."
                return await ctx.reply(embed=plmbed)
            if isinstance(results, pomice.Playlist):
                for track in results.tracks:
                    await ctx.voice_client.queue.put(track)
                    ctx.voice_client.lqueue.append(F"{track.title} - {track.author} | {ctx.author.mention} / {self.duration(track.length)}")
            elif isinstance(results, pomice.Track):
                await ctx.voice_client.queue.put(results)
                ctx.voice_client.lqueue.append(F"{results.title} - {results.author} | {ctx.author.mention} / {self.duration(results.length)}")
            else:
                await ctx.voice_client.queue.put(results[0])
                ctx.voice_client.lqueue.append(F"{results[0].title} - {results[0].author} | {ctx.author.mention} / {self.duration(results[0].length)}")
            if not ctx.voice_client.is_playing:
                return await ctx.voice_client.play(track=(await ctx.voice_client.queue.get()))
            else:
                result = results if isinstance(results, pomice.Playlist) else results[0]
                plmbed.title = "Playlist:"
                plmbed.description = F"Added {result} to the queue"
                plmbed.set_image(url=result.thumbnail)
                view = discord.ui.View()
                view.add_item(item=discord.ui.Button(emoji="🔗", label="URL", url=result.uri))
                return await ctx.reply(embed=plmbed)
        plmbed.description = F"Someone else is using to me in {ctx.me.voice.channel.mention}"
        return await ctx.reply(embed=plmbed)

    # Stop
    @commands.command(name="stop", aliases=["so"], help="Stops playing and Clears queue")
    @commands.guild_only()
    @commands.check(full_voice)
    async def stop(self, ctx:commands.Context):
        sombed = discord.Embed(
            color=self.bot.color,
            title="Stop",
            timestamp=ctx.message.created_at
        )
        sombed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        if ctx.voice_client.is_playing or ctx.voice_client.is_paused:
            params = {
                'title': ctx.voice_client.current.author,
                'thumbnail_url': ctx.voice_client.current.thumbnail,
                'seconds_played': ctx.voice_client.position/1000,
                'total_seconds': ctx.voice_client.current.length/1000,
                'line_1': ctx.voice_client.current.title,
                'line_2': ctx.voice_client.current.requester.display_name
            }
            session = await self.bot.session.get("https://api.jeyy.xyz/discord/player", params=params)
            response = io.BytesIO(await session.read())
            sombed.set_image(url="attachment://player.png")
            view = discord.ui.View()
            view.add_item(item=discord.ui.Button(emoji="🔗", label="URL", url=ctx.voice_client.current.uri))
            for _ in range(ctx.voice_client.queue.qsize()):
                    ctx.voice_client.queue.get_nowait()
                    ctx.voice_client.queue.task_done()
            for _ in range(len(ctx.voice_client.lqueue)):
                ctx.voice_client.lqueue.pop(0)
            ctx.voice_client.loop = None
            sombed.description = "Stopped:"
            await ctx.reply(embed=sombed, file=discord.File(fp=response, filename="player.png"), view=view)
            return await ctx.voice_client.stop()
        sombed.description = "Nothing is playing"
        return await ctx.reply(embed=sombed)

    # Skip
    @commands.command(name="skip", aliases=["sk"], help="Skips the music")
    @commands.guild_only()
    @commands.check(full_voice)
    async def skip(self, ctx:commands.Context):
        skmbed = discord.Embed(
            color=self.bot.color,
            title="Skip:",
            timestamp=ctx.message.created_at
        )
        skmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        if ctx.voice_client.is_playing:
            if not ctx.voice_client.queue.empty():
                params = {
                    'title': ctx.voice_client.current.author,
                    'thumbnail_url': ctx.voice_client.current.thumbnail,
                    'seconds_played': ctx.voice_client.position/1000,
                    'total_seconds': ctx.voice_client.current.length/1000,
                    'line_1': ctx.voice_client.current.title,
                    'line_2': ctx.voice_client.current.requester.display_name
                }
                session = await self.bot.session.get("https://api.jeyy.xyz/discord/player", params=params)
                response = io.BytesIO(await session.read())
                skmbed.set_image(url="attachment://player.png")
                view = discord.ui.View()
                view.add_item(item=discord.ui.Button(emoji="🔗", label="URL", url=ctx.voice_client.current.uri))
                ctx.voice_client.loop = None
                await ctx.reply(embed=skmbed, file=discord.File(fp=response, filename="player.png"), view=view)
                return await ctx.voice_client.stop()
            skmbed.description = "There is nothing in the queue"
            return await ctx.reply(embed=skmbed)
        skmbed.description = "Nothing is playing"
        return await ctx.reply(embed=skmbed)

    # Resume
    @commands.command(name="resume", aliases=["ru"], help="Resumes the paused music")
    @commands.guild_only()
    @commands.check(full_voice)
    async def resume(self, ctx:commands.Context):
        rumbed = discord.Embed(
            color=self.bot.color,
            title="Resume:",
            timestamp=ctx.message.created_at
        )
        rumbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        params = {
            'title': ctx.voice_client.current.author,
            'thumbnail_url': ctx.voice_client.current.thumbnail,
            'seconds_played': ctx.voice_client.position/1000,
            'total_seconds': ctx.voice_client.current.length/1000,
            'line_1': ctx.voice_client.current.title,
            'line_2': ctx.voice_client.current.requester.display_name
        }
        session = await self.bot.session.get("https://api.jeyy.xyz/discord/player", params=params)
        response = io.BytesIO(await session.read())
        rumbed.set_image(url="attachment://player.png")
        view = discord.ui.View()
        view.add_item(item=discord.ui.Button(emoji="🔗", label="URL", url=ctx.voice_client.current.uri))
        if ctx.voice_client.is_paused:
            await ctx.voice_client.set_pause(pause=False)
            rumbed.description = "Resumed the music"
            return await ctx.reply(embed=rumbed, file=discord.File(fp=response, filename="player.png"), view=view)
        rumbed.description = "The music is already playing"
        return await ctx.reply(embed=rumbed, file=discord.File(fp=response, filename="player.png"), view=view)

    # Pause
    @commands.command(name="pause", aliases=["pu"], help="Pauses playing music")
    @commands.guild_only()
    @commands.check(full_voice)
    async def pause(self, ctx:commands.Context):
        pumbed = discord.Embed(
            color=self.bot.color,
            title="Pause:",
            timestamp=ctx.message.created_at
        )
        pumbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        params = {
            'title': ctx.voice_client.current.author,
            'thumbnail_url': ctx.voice_client.current.thumbnail,
            'seconds_played': ctx.voice_client.position/1000,
            'total_seconds': ctx.voice_client.current.length/1000,
            'line_1': ctx.voice_client.current.title,
            'line_2': ctx.voice_client.current.requester.display_name
        }
        session = await self.bot.session.get("https://api.jeyy.xyz/discord/player", params=params)
        response = io.BytesIO(await session.read())
        pumbed.set_image(url="attachment://player.png")
        view = discord.ui.View()
        view.add_item(item=discord.ui.Button(emoji="🔗", label="URL", url=ctx.voice_client.current.uri))
        if ctx.voice_client.is_paused:
            pumbed.description = "Music is already paused"
            return await ctx.reply(embed=pumbed, file=discord.File(fp=response, filename="player.png"), view=view)
        await ctx.voice_client.set_pause(pause=True)
        pumbed.description = "Paused the music"
        return await ctx.reply(embed=pumbed, file=discord.File(fp=response, filename="player.png"), view=view)

    # Loop
    @commands.command(name="loop", aliases=["lp"], help="Loops over the music")
    @commands.guild_only()
    @commands.check(full_voice)
    async def loop(self, ctx:commands.Context):
        lpmbed = discord.Embed(
            color=self.bot.color,
            title="Pause:",
            timestamp=ctx.message.created_at
        )
        lpmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        if ctx.voice_client.is_playing or ctx.voice_client.is_paused:
            params = {
                'title': ctx.voice_client.current.author,
                'thumbnail_url': ctx.voice_client.current.thumbnail,
                'seconds_played': ctx.voice_client.position/1000,
                'total_seconds': ctx.voice_client.current.length/1000,
                'line_1': ctx.voice_client.current.title,
                'line_2': ctx.voice_client.current.requester.display_name
            }
            session = await self.bot.session.get("https://api.jeyy.xyz/discord/player", params=params)
            response = io.BytesIO(await session.read())
            lpmbed.set_image(url="attachment://player.png")
            view = discord.ui.View()
            view.add_item(item=discord.ui.Button(emoji="🔗", label="URL", url=ctx.voice_client.current.uri))
            if not ctx.voice_client.loop:
                ctx.voice_client.loop = ctx.voice_client.current
                lpmbed.description = "Loop has been turned on"
                return await ctx.reply(embed=lpmbed, file=discord.File(fp=response, filename="player.png"), view=view)
            ctx.voice_client.loop = None
            lpmbed.description = "Loop has been turned off"
            return await ctx.reply(embed=lpmbed, file=discord.File(fp=response, filename="player.png"), view=view)
        lpmbed.description = "Nothing is playing"
        return await ctx.reply(embed=lpmbed)

    # NowPlaying
    @commands.command(name="nowplaying", aliases=["np"], help="Tells the playing music")
    @commands.guild_only()
    @commands.check(bot_voice)
    async def nowplaying(self, ctx:commands.Context):
        npmbed = discord.Embed(
            color=self.bot.color,
            title="Playing:",
            timestamp=ctx.voice_client.current.ctx.message.created_at
        )
        npmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        if ctx.voice_client.is_playing or ctx.voice_client.is_paused:
            params = {
                'title': ctx.voice_client.current.author,
                'thumbnail_url': ctx.voice_client.current.thumbnail,
                'seconds_played': ctx.voice_client.position/1000,
                'total_seconds': ctx.voice_client.current.length/1000,
                'line_1': ctx.voice_client.current.title,
                'line_2': ctx.voice_client.current.requester.display_name
            }
            session = await self.bot.session.get("https://api.jeyy.xyz/discord/player", params=params)
            response = io.BytesIO(await session.read())
            npmbed.set_image(url="attachment://player.png")
            view = discord.ui.View()
            view.add_item(item=discord.ui.Button(emoji="🔗", label="URL", url=ctx.voice_client.current.uri))
            return await ctx.reply(embed=npmbed, file=discord.File(fp=response, filename="player.png"), view=view)
        npmbed.description = "Nothing is playing"
        return await ctx.reply(embed=npmbed)

    # Queue
    @commands.command(name="queue", aliases=["qu"], help="Shows the queue")
    @commands.guild_only()
    @commands.check(bot_voice)
    async def queue(self, ctx:commands.Context):
        if len(ctx.voice_client.lqueue) > 1:
            counter = 1
            es = []
            paginator = commands.Paginator(prefix=None, suffix=None)
            for i in ctx.voice_client.lqueue:
                paginator.add_line(F"#{counter} {i}")
                counter += 1
            for page in paginator.pages:
                qumbed = discord.Embed(
                    color=self.bot.color,
                    title="Queue:",
                    description=page,
                    timestamp=ctx.message.created_at
                )
                qumbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
                es.append(qumbed)
            return await pagination.ViewPagination(ctx, es).start() if len(es) > 1 else await ctx.reply(embed=es[0])
        return await ctx.invoke(self.nowplaying)

    # Queue-Clear
    @commands.command(name="queueclear", aliases=["qucr"], help="Clears the queue")
    @commands.guild_only()
    @commands.check(full_voice)
    async def queue_clear(self, ctx:commands.Context):
        qucrmbed = discord.Embed(
            color=self.bot.color,
            title="Queue Clear:",
            timestamp=ctx.message.created_at
        )
        qucrmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        if len(ctx.voice_client.lqueue) > 1:
            await ctx.invoke(self.queue)
            view = confirm.ViewConfirm()
            viewmessage = await ctx.reply("Do you want to clear the queue?", view=view)
            await view.wait()
            if view.value:
                for _ in range(ctx.voice_client.queue.qsize()):
                    ctx.voice_client.queue.get_nowait()
                    ctx.voice_client.queue.task_done()
                for _ in range(len(ctx.voice_client.lqueue)):
                    ctx.voice_client.lqueue.pop(0)
                await viewmessage.delete()
                qucrmbed.description = "Queue has been cleared"
                return await ctx.reply(embed=qucrmbed)
            qucrmbed.description = "Queue has not been cleared"
            return await ctx.reply(embed=qucrmbed)
        qucrmbed.description = "Nothing is in the queue"
        return await ctx.reply(embed=qucrmbed)

    # Seek
    @commands.command(name="seek", aliases=["se"], help="Seeks to the given time")
    @commands.guild_only()
    @commands.check(full_voice)
    async def seek(self, ctx:commands.Context, *, time:str=commands.Option(description="The time you want to seek to (split by space)")):
        sembed = discord.Embed(
            color=self.bot.color,
            title="Seek:",
            timestamp=ctx.message.created_at
        )
        sembed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        if ctx.voice_client.is_playing or ctx.voice_client.is_paused:
            data = time.split(" ")
            datacounter = 0
            dates = ['h', 'm', 's']
            hours = None
            minutes = None
            seconds = None
            for item in dates:
                try:
                    numIndex = data[datacounter].index(item)
                    if item == "h":
                        hours = data[datacounter][:numIndex] 
                    if item == "m": 
                        minutes = data[datacounter][:numIndex] 
                    if item == "s":
                        seconds = data[datacounter][:numIndex] 
                    datacounter += 1
                except: pass
            if hours is None and minutes is None and seconds is None:
                sembed.description = "You must pass a valid time, e.g. `1h 2m 30s`"
                return await ctx.reply(embed=sembed)
            dtime = datetime.timedelta(hours=0 if not hours else int(hours), minutes=0 if not minutes else int(minutes), seconds=0 if not seconds else int(seconds))
            if not (dtime.seconds*1000) >= ctx.voice_client.current.length:
                params = {
                    'title': ctx.voice_client.current.author,
                    'thumbnail_url': ctx.voice_client.current.thumbnail,
                    'seconds_played': dtime.seconds,
                    'total_seconds': ctx.voice_client.current.length/1000,
                    'line_1': ctx.voice_client.current.title,
                    'line_2': ctx.voice_client.current.requester.display_name
                }
                session = await self.bot.session.get("https://api.jeyy.xyz/discord/player", params=params)
                response = io.BytesIO(await session.read())
                sembed.set_image(url="attachment://player.png")
                view = discord.ui.View()
                view.add_item(item=discord.ui.Button(emoji="🔗", label="URL", url=ctx.voice_client.current.uri))
                await ctx.voice_client.seek(dtime.seconds*1000)
                return await ctx.reply(embed=sembed, file=discord.File(fp=response, filename="player.png"),  view=view)
            sembed.description = "Seek time is greater than the duration of the song"
            return await ctx.reply(embed=sembed)
        sembed.description = "Nothing is playing"
        return await ctx.reply(embed=sembed)

    # Volume
    @commands.command(name="volume", aliases=["vol"], help="Sets or Tells the volume of the music")
    @commands.guild_only()
    @commands.check(full_voice)
    async def volume(self, ctx:commands.Context, *, volume:int=commands.Option(description="The volume you want be set to")):
        volmbed = discord.Embed(
            color=self.bot.color,
            title="Volume:",
            timestamp=ctx.message.created_at
        )
        volmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        if ctx.voice_client.is_playing or ctx.voice_client.is_paused:
            params = {
                'title': ctx.voice_client.current.author,
                'thumbnail_url': ctx.voice_client.current.thumbnail,
                'seconds_played': ctx.voice_client.position/1000,
                'total_seconds': ctx.voice_client.current.length/1000,
                'line_1': ctx.voice_client.current.title,
                'line_2': ctx.voice_client.current.requester.display_name
            }
            session = await self.bot.session.get("https://api.jeyy.xyz/discord/player", params=params)
            response = io.BytesIO(await session.read())
            volmbed.set_image(url="attachment://player.png")
            view = discord.ui.View()
            view.add_item(item=discord.ui.Button(emoji="🔗", label="URL", url=ctx.voice_client.current.uri))
            if volume:
                if volume == ctx.voice_client.volume:
                    if not volume < 0 or not volume > 500:
                        await ctx.voice_client.set_volume(volume)
                        volmbed.description = F"Volume has been changed to {volume}"
                        return await ctx.reply(embed=volmbed, file=discord.File(response, filename="player.png"), view=view)
                    volmbed.description = "The volume must be between 0 and 500"
                    return await ctx.reply(embed=volmbed, file=discord.File(response, filename="player.png"), view=view)
                volmbed.description = F"The volume is already at {ctx.voice_client.volume}"
                return await ctx.reply(embed=volmbed, file=discord.File(response, filename="player.png"), view=view)
            volmbed.description = F"The volume is currently at {ctx.voice_client.volume}"
            return await ctx.reply(embed=volmbed, file=discord.File(response, filename="player.png"), view=view)
        volmbed.description = "Nothing is playing"
        return await ctx.reply(embed=volmbed)

    # Lyrics
    @commands.command(name="lyrics", aliases=["ly"], help="Shows the lyrics for music")
    @commands.guild_only()
    async def lyrics(self, ctx:commands.Context, *, music:str=commands.Option(description="The music you want to get the lyrics for", default=None)):
        lymbed = discord.Embed(
            color=self.bot.color,
            title="Lyrics:",
            timestamp=ctx.message.created_at
        )
        lymbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        if not music:
            if ctx.voice_client.is_playing or ctx.voice_client.is_paused: music = ctx.voice_client.current.title
            else: raise commands.CheckFailure("Since I'm not in a voice channel you need to pass a music")
        lyrics = await self.bot.openrobot.lyrics(music)
        if lyrics.lyrics:
            lys = lyrics.lyrics.split('\n')
            es = []
            paginator = commands.Paginator(prefix=None, suffix=None)
            for l in lys:
                paginator.add_line(l)
            for page in paginator.pages:
                lymbed = discord.Embed(
                color=self.bot.color,
                    title=lyrics.title,
                    description=page,
                    timestamp=ctx.message.created_at
                )
                lymbed.set_thumbnail(url=lyrics.images.track or discord.Embed.Empty)
                lymbed.set_author(name=lyrics.artist, icon_url=lyrics.images.background or discord.Embed.Empty)
            return await pagination.ViewPagination(ctx, es).start() if len(es) > 1 else await ctx.reply(embed=es[0], ephemeral=True)
        lymbed.description = F"Didn't find any lyrics for {music}"
        return await ctx.reply(embed=lymbed)

    @commands.Cog.listener()
    async def on_pomice_track_start(self, player:pomice.Player, track:pomice.Track):
        tsmbed = discord.Embed(
            color=self.bot.color,
            title="Playing:",
            timestamp=track.ctx.message.created_at
        )
        params = {
            'title': track.author,
            'thumbnail_url': track.thumbnail,
            'seconds_played': 0,
            'total_seconds': track.length/1000,
            'line_1': track.title,
            'line_2': track.requester.display_name
        }
        session = await self.bot.session.get("https://api.jeyy.xyz/discord/player", params=params)
        response = io.BytesIO(await session.read())
        tsmbed.set_image(url="attachment://player.png")
        view = discord.ui.View()
        view.add_item(item=discord.ui.Button(emoji="🔗", label="URL", url=track.uri))
        return await track.ctx.reply(embed=tsmbed, file=discord.File(fp=response, filename="player.png"), view=view)

    @commands.Cog.listener()
    async def on_pomice_track_end(self, player:pomice.Player, track:pomice.Track, reason:str):
        if not player.loop:
            if player.queue.empty():
                tembed = discord.Embed(
                    color=self.bot.color,
                    title="Ended:",
                    timestamp=track.ctx.message.created_at
                )
                tembed.set_image(url="attachment://player.png")
                params = {
                    'title': track.author,
                    'thumbnail_url': track.thumbnail,
                    'seconds_played': track.position/1000,
                    'total_seconds': track.length/1000,
                    'line_1': track.title,
                }
                session = await self.bot.session.get("https://api.jeyy.xyz/discord/player", params=params)
                response = io.BytesIO(await session.read())
                view = discord.ui.View()
                view.add_item(item=discord.ui.Button(emoji="🔗", label="URL", url=track.uri))
                return await track.ctx.reply(embed=tembed, file=discord.File(fp=response, filename="player.png"), view=view)
            player.lqueue.pop(0)
            return await player.play(track=(await player.queue.get()))
        await player.play(track=player.loop)

def setup(bot):
    bot.add_cog(Music(bot))
