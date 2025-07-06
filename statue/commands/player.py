import discord
from discord.ext import commands
from yt_dlp import YoutubeDL
from youtube_search import YoutubeSearch

FFMPEG_PATH = r"C:\ffmpeg\bin\ffmpeg.exe"  # Update if needed

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

YTDL_OPTIONS = {
    'format': 'bestaudio/best',
    'quiet': True,
    'noplaylist': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}

class MusicPlayer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queue = []
        self.is_playing = False
        self.is_looping = False
        print("player.py loaded")

    async def play_next(self, ctx):
        if len(self.queue) == 0:
            self.is_playing = False
            await ctx.send("Queue is empty. Add more songs to play.")
            print("Queue empty, stopping playback.")
            await ctx.voice_client.disconnect()
            print("Disconnected from voice channel.")
            return

        if not self.is_looping:
            song = self.queue.pop(0)
        else:
            # Loop: just replay the first song in queue without popping
            song = self.queue[0]

        print(f"Starting playback: {song['title']}")
        try:
            source = discord.FFmpegPCMAudio(song['url'], executable=FFMPEG_PATH, **FFMPEG_OPTIONS)
        except Exception as e:
            await ctx.send(f"Error creating audio source: {e}")
            print(f"Error creating audio source: {e}")
            return

        def after_play(error):
            if error:
                print(f"Playback error: {error}")
            coro = self.play_next(ctx)
            fut = self.bot.loop.create_task(coro)

        ctx.voice_client.play(source, after=after_play)
        self.is_playing = True
        await ctx.send(f"Now playing: **{song['title']}**")

    @commands.command(name="play", aliases=["p"])
    async def play(self, ctx, *, search: str):
        print(f"Received play command from {ctx.author} with query: {search}")

        voice_channel = ctx.author.voice.channel if ctx.author.voice else None
        if voice_channel is None:
            await ctx.send("You must be connected to a voice channel to play music.")
            print("User not connected to any voice channel.")
            return

        # Connect or move bot
        if ctx.voice_client is None:
            print(f"Connecting to voice channel: {voice_channel}")
            await voice_channel.connect()
            print("Connected.")
        elif ctx.voice_client.channel != voice_channel:
            print(f"Moving to user's voice channel: {voice_channel}")
            await ctx.voice_client.move_to(voice_channel)

        # Search YouTube
        try:
            results = YoutubeSearch(search, max_results=1).to_dict()
            if not results:
                await ctx.send("No results found on YouTube.")
                print("No YouTube results found.")
                return
            video_url = f"https://www.youtube.com{results[0]['url_suffix']}"
            print(f"YouTube video URL: {video_url}")
        except Exception as e:
            await ctx.send(f"Error searching YouTube: {e}")
            print(f"Error searching YouTube: {e}")
            return

        # Extract audio URL
        with YoutubeDL(YTDL_OPTIONS) as ydl:
            try:
                info = ydl.extract_info(video_url, download=False)
                audio_url = info['url']
                title = info.get('title', 'Unknown Title')
                print(f"Extracted audio URL: {audio_url}")
            except Exception as e:
                await ctx.send(f"Error extracting audio: {e}")
                print(f"Error extracting audio: {e}")
                return

        # Add song to queue
        self.queue.append({'url': audio_url, 'title': title})
        await ctx.send(f"Added to queue: **{title}**")
        print(f"Added to queue: {title}")

        # If not playing, start playing
        if not self.is_playing:
            await self.play_next(ctx)

    @commands.command(name="skip")
    async def skip(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            await ctx.send("Skipped current song.")
            print("Skipped current song.")
        else:
            await ctx.send("Nothing is playing right now.")
            print("Skip command received but nothing playing.")

    @commands.command(name="stop")
    async def stop(self, ctx):
        if ctx.voice_client:
            self.queue.clear()
            self.is_playing = False
            self.is_looping = False
            ctx.voice_client.stop()
            await ctx.voice_client.disconnect()
            await ctx.send("Stopped playback and disconnected.")
            print("Stopped and disconnected.")
        else:
            await ctx.send("I'm not connected to a voice channel.")
            print("Stop command received but bot not connected.")

    @commands.command(name="pause")
    async def pause(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.pause()
            await ctx.send("Paused playback.")
            print("Paused playback.")
        else:
            await ctx.send("Nothing is playing to pause.")
            print("Pause command received but nothing playing.")

    @commands.command(name="resume")
    async def resume(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_paused():
            ctx.voice_client.resume()
            await ctx.send("Resumed playback.")
            print("Resumed playback.")
        else:
            await ctx.send("Nothing is paused.")
            print("Resume command received but nothing paused.")

    @commands.command(name="loop")
    async def loop(self, ctx, toggle: str = None):
        if toggle is None:
            await ctx.send(f"Loop is currently {'ON' if self.is_looping else 'OFF'}. Use `loop on` or `loop off` to toggle.")
            print("Loop status requested.")
            return

        if toggle.lower() == "on":
            self.is_looping = True
            await ctx.send("Looping enabled.")
            print("Looping enabled.")
        elif toggle.lower() == "off":
            self.is_looping = False
            await ctx.send("Looping disabled.")
            print("Looping disabled.")
        else:
            await ctx.send("Invalid argument. Use `loop on` or `loop off`.")
            print("Invalid loop toggle argument.")

async def setup(bot):
    await bot.add_cog(MusicPlayer(bot))
