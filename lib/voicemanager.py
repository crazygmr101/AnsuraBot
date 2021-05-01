import asyncio
import io
import shlex
import subprocess
from typing import Dict, List

import discord
import youtube_dl
from discord.ext import commands
from discord.opus import Encoder


class VoiceManager:
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.active_guilds: Dict[int, discord.TextChannel] = {}
        self.tts_mutes: Dict[int, List[str]] = {}
        self.tts_timeout: Dict[int, bool] = {}
        self.queues: Dict[int, TTSQueue] = {}
        self.guild_states: Dict[int, int] = {}
        self.guild_players: Dict[int, YTDLSource] = {}


class TTSQueue:
    def __init__(self, guild: int, client: discord.VoiceClient):
        self.guild = guild
        self.client = client
        self.playing = asyncio.Event()
        self.queue: List[io.BytesIO] = []
        self.active: bool = True
        self.waiting = asyncio.Event()
        asyncio.create_task(self.loop())

    async def loop(self):
        while self.active:
            self.playing.clear()
            await self.waiting.wait()
            self.play_next()
            await self.playing.wait()

    def _del(self, e):
        self.queue[0].close()
        del self.queue[0]
        self.playing.set()
        if len(self.queue) == 0:
            self.waiting.clear()

    def stop(self):
        self.queue = []

    def play_next(self):
        self.client.play(FFmpegPCMAudio(self.queue[0].read(), pipe=True), after=self._del)

    def add(self, buf: io.BytesIO):
        self.queue.append(buf)
        self.waiting.set()


print("[VOICE MANAGER] Loading YTDL")

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'  # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.1):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


class FFmpegPCMAudio(discord.AudioSource):
    # modified from d.py according to the solution given in
    # https://github.com/Rapptz/discord.py/issues/5192
    def __init__(self, source, *, executable='ffmpeg', pipe=False, stderr=None, before_options=None, options=None):
        stdin = None if not pipe else source
        args = [executable]
        if isinstance(before_options, str):
            args.extend(shlex.split(before_options))
        args.append('-i')
        args.append('-' if pipe else source)
        args.extend(('-f', 's16le', '-ar', '48000', '-ac', '2', '-loglevel', 'warning'))
        if isinstance(options, str):
            args.extend(shlex.split(options))
        args.append('pipe:1')
        self._process = None
        try:
            self._process = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=stderr)
            self._stdout = io.BytesIO(
                self._process.communicate(input=stdin)[0]
            )
        except FileNotFoundError:
            raise discord.ClientException(executable + ' was not found.') from None
        except subprocess.SubprocessError as exc:
            raise discord.ClientException('Popen failed: {0.__class__.__name__}: {0}'.format(exc)) from exc

    def read(self):
        ret = self._stdout.read(Encoder.FRAME_SIZE)
        if len(ret) != Encoder.FRAME_SIZE:
            return b''
        return ret

    def cleanup(self):
        proc = self._process
        if proc is None:
            return
        proc.kill()
        if proc.poll() is None:
            proc.communicate()

        self._process = None
