import asyncio
import os
from typing import Dict, List

import discord
import youtube_dl
from discord.ext import commands


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
        self.queue: List[str] = []
        self.active: bool = True
        self.waiting = asyncio.Event()
        asyncio.create_task(self.loop())

    async def loop(self):
        try:
            while self.active:
                self.playing.clear()
                await self.waiting.wait()
                self.play_next()
                await self.playing.wait()
        except Exception as e:
            print(type(e))
            print(e)

    def _del(self, e):
        os.remove(f'{self.queue[0]}.mp3')
        del self.queue[0]
        self.playing.set()
        if len(self.queue) == 0:
            self.waiting.clear()

    def stop(self):
        self.queue = []

    def play_next(self):
        self.client.play(discord.FFmpegPCMAudio(f'{self.queue[0]}.mp3'), after=self._del)

    def add(self, fname: str):
        self.queue.append(fname)
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
