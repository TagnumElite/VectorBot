from discord.ext import commands
from ..utils import checks, config
import discord
import asyncio

if not discord.opus.is_loaded():
    discord.opus.load_opus('opus')

class VoiceEntry:
    def __init__(self, message, player):
        self.requester = message.author
        self.channel = message.channel
        self.player = player

    def __str__(self):
        fmt = '*{0.title}* uploaded by {0.uploader} and requested by @{1.display_name}'
        duration = self.player.duration
        if duration:
            fmt = fmt + ' [length: {0[0]}m {0[1]}s]'.format(divmod(duration, 60))
        return fmt.format(self.player, self.requester)

class VoiceState:
    def __init__(self, bot):
        self.current = None
        self.voice = None
        self.bot = bot
        self.now_playing
        self.play_next_song = asyncio.Event()
        self.songs = asyncio.Queue()
        self.skip_votes = set() # a set of user_ids that voted
        self.audio_player = self.bot.loop.create_task(self.audio_player_task())

    def is_playing(self):
        if self.voice is None or self.current is None:
            return False

        player = self.current.player
        return not player.is_done()

    @property
    def player(self):
        return self.current.player

    def skip(self):
        self.skip_votes.clear()
        if self.is_playing():
            self.player.stop()

    def toggle_next(self):
        self.bot.loop.call_soon_threadsafe(self.play_next_song.set)

    async def audio_player_task(self):
        while True:
            self.play_next_song.clear()
            self.current = await self.songs.get()
            if self.now_playing != None:
                self.now_playing.delete()
            self.now_playing = await self.current.channel.send('Now playing ' + str(self.current))
            self.current.player.start()
            await self.play_next_song.wait()

class Music:
    """Handles the bot's music system.

    Parameters
    ----------
    bot: discord.ext.commands.bot.Bot
        The bot that is currently running"""

    def __init__(self, bot):
        self.bot = bot
        self.voice_states = {}
        self.Config = bot.Config.get(self.__class__.__name__, {})
        self.guild = None

        if self.Config is None:
            raise Exception("Closing Music Functionallity: Not Setup in config.json")

    async def on_ready(self):
        for guild in self.bot.guilds:
            if guild.id == self.bot.Config["Guild"]:
                self.guild = guild
                break

        if self.guild == None:
            print ("Closing Music Functionallity: Unable to access main guild")
            self.bot.remove_cog(self.__class__.__name__)

    async def on_guild_remove(self, guild):
        if guild.id == self.bot.Configs["Guild"]:
            print ("Closing Music Functionallity: Unable to access main guild")
            self.bot.remove_cog(self.__class__.__name__)
        return

    def get_voice_state(self, guild):
        """"""

        state = self.voice_states.get(guild.id)
        if state is None:
            state = VoiceState(self.bot)
            self.voice_states[guild.id] = state

        return state

    async def create_voice_client(self, channel):
        voice = await self.bot.join_voice_channel(channel)
        state = self.get_voice_state(channel.guild)
        state.voice = voice

    def __unload(self):
        for state in self.voice_states.values():
            try:
                state.audio_player.cancel()
                if state.voice:
                    self.bot.loop.create_task(state.voice.disconnect())
            except:
                pass

    @commands.command()
    @commands.guild_only()
    async def join(self, ctx, *, channel : discord.abc.GuildChannel):
        """Joins a voice channel.
        Command: {prefix}join Music"""

        msgs = [ctx.message]
        chn = ctx.channel

        try:
            await self.create_voice_client(channel)
        except discord.ClientException:
            msgs.append(await chn.send('Already in a voice channel...'))
        except discord.InvalidArgument:
            msgs.append(await chn.send('This is not a voice channel...'))
        else:
            msgs.append(await chn.send('Ready to play audio in ' + channel.name))
        await asyncio.sleep(5)
        await chn.delete_messages(msgs)

    @commands.command()
    @commands.guild_only()
    async def summon(self, ctx):
        """Summons the bot to join your voice channel."""
        msgs = [ctx.message]

        summoned_channel = ctx.message.author.voice_channel
        if summoned_channel is None:
            msgs.append(await ctx.channel.send('You are not in a voice channel.'))
            return False

        state = self.get_voice_state(ctx.message.guild)
        if state.voice is None:
            state.voice = await self.bot.join_voice_channel(summoned_channel)
        else:
            await state.voice.move_to(summoned_channel)
        await asyncio.sleep(5)
        await ctx.channel.delete_messages(msgs)
        return True

    @commands.command()
    @commands.guild_only()
    async def play(self, ctx, *, song : str):
        """Plays a song.
        If there is a song currently in the queue, then it is
        queued until the next song is done playing.
        This command automatically searches as well from YouTube.
        The list of supported sites can be found here:
        https://rg3.github.io/youtube-dl/supportedsites.html
        """
        msgs = [ctx.message]

        state = self.get_voice_state(ctx.message.guild)
        opts = {
            'default_search': 'auto',
            'quiet': True,
        }

        if state.voice is None:
            success = await ctx.invoke(self.summon)
            if not success:
                return

        try:
            player = await state.voice.create_ytdl_player(song, ytdl_options=opts, after=state.toggle_next)
        except Exception as e:
            fmt = 'An error occurred while processing this request: ```py\n{}: {}\n```'
            msgs.append(await ctx.channel.send(fmt.format(type(e).__name__, e)))
        else:
            player.volume = self.bot.Config["Music"]["Default Volume"] / 100
            entry = VoiceEntry(ctx.message, player)
            msgs.append(await ctx.channel.send('Enqueued ' + str(entry)))
            await state.songs.put(entry)
        await asyncio.sleep(5)
        await ctx.channel.delete_messages(msgs)

    @commands.command()
    @commands.guild_only()
    async def volume(self, ctx, value : int):
        """Sets the volume of the currently playing song."""
        msgs = [ctx.message]

        state = self.get_voice_state(ctx.message.guild)
        if state.is_playing():
            player = state.player
            player.volume = value / 100
            msgs.append(await ctx.channel.send('Set the volume to {:.0%}'.format(player.volume)))
        await asyncio.sleep(5)
        await ctx.channel.delete_messages(msgs)

    @commands.command()
    @commands.guild_only()
    async def pause(self, ctx):
        """Pauses the currently played song."""
        await ctx.message.delete()
        state = self.get_voice_state(ctx.message.guild)
        if state.is_playing():
            player = state.player
            player.pause()

    @commands.command()
    @commands.guild_only()
    async def resume(self, ctx):
        """Resumes the currently played song."""
        await ctx.message.delete()
        state = self.get_voice_state(ctx.message.guild)
        if state.is_playing():
            player = state.player
            player.resume()

    @commands.command()
    @commands.guild_only()
    async def stop(self, ctx):
        """Stops playing audio and leaves the voice channel.
        This also clears the queue.
        """
        await ctx.message.delete()
        guild = ctx.message.guild
        state = self.get_voice_state(guild)

        if state.is_playing():
            player = state.player
            player.stop()

        try:
            state.audio_player.cancel()
            del self.voice_states[guild.id]
            await state.voice.disconnect()
        except:
            pass

    @commands.command()
    @commands.guild_only()
    async def skip(self, ctx):
        """Vote to skip a song. The song requester can automatically skip.
        3 skip votes are needed for the song to be skipped.
        """
        msgs = [ctx.message]

        state = self.get_voice_state(ctx.message.guild)
        if not state.is_playing():
            msgs.append(await ctx.channel.send('Not playing any music right now...'))
            return

        voter = ctx.message.author
        if voter == state.current.requester:
            msgs.append(await ctx.channel.send('Requester requested skipping song...'))
            state.skip()
        elif voter.id not in state.skip_votes:
            state.skip_votes.add(voter.id)
            total_votes = len(state.skip_votes)
            if total_votes >= 3:
                msgs.append(await ctx.channel.send('Skip vote passed, skipping song...'))
                state.skip()
            else:
                msgs.append(await ctx.channel.send('Skip vote added, currently at [{}/3]'.format(total_votes)))
        else:
            msgs.append(await ctx.channel.send('You have already voted to skip this song.'))
        await asyncio.sleep(5)
        await ctx.channel.delete_messages(msgs)

    @commands.command(alias=["np"])
    @commands.guild_only()
    async def playing(self, ctx):
        """Shows info about the currently played song."""

        state = self.get_voice_state(ctx.message.guild)
        if state.current is None:
            await self.bot.send('Not playing anything.')
        else:
            skip_count = len(state.skip_votes)
            await self.bot.send('Now playing {} [skips: {}/3]'.format(state.current, skip_count))
        await asyncio.sleep(5)
        await ctx.channel.delete_messages(msgs)

def setup(bot):
    bot.add_cog(Music(bot))
