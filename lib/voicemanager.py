import asyncio
import os
from typing import Dict, List

import discord
from discord.ext import commands


class VoiceManager:
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.active_guilds: Dict[int, discord.TextChannel] = {}
        self.tts_mutes: Dict[int, List[str]] = {}
        self.tts_timeout: Dict[int, bool] = {}
        self.queues: Dict[int, _TTSQueue] = {}
        self.guild_states: Dict[int, int] = {}

class _TTSQueue:
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
