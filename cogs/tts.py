import os
import sys
import traceback
from io import BytesIO
from typing import List, Dict

import discord
import gtts
from discord.ext import commands

class TTS(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.active_guilds: Dict[int, discord.TextChannel] = {}
        self.queue: Dict[int, List[str]] = {}

    @commands.command()
    @commands.is_owner()
    @commands.has_permissions(manage_messages=True)
    async def summon(self, ctx: commands.Context):
        """Summons Ansura to your voice channel"""
        await ctx.author.voice.channel.connect()

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    @commands.is_owner()
    async def leave(self, ctx: commands.Context):
        """Makes Ansura leave your voice channel"""
        await ctx.guild.voice_client.disconnect()

    @commands.command()
    @commands.is_owner()
    @commands.has_permissions(manage_messages=True)
    async def say(self, ctx: commands.Context, text):
        """Makes ansura say something in the voice channel with TTS"""
        message = gtts.gTTS(text)
        message.save('tts.mp3')
        ctx.guild.voice_client.play(discord.FFmpegPCMAudio('tts.mp3'))

    @commands.command()
    @commands.has_guild_permissions(manage_messages=True)
    @commands.bot_has_guild_permissions(speak=True)
    async def autotts(self, ctx: commands.Context):
        """
        Makes Ansura join the voice channel you are in and watch the current channel
        """
        if ctx.guild.id in self.active_guilds.keys():
            await ctx.send("Already watching a channel! Do %stoptts to stop")
        if not ctx.author.voice:
            await ctx.send("Join a voice channel!")
            return
        await ctx.send("Watching this channel for messages, do %stoptts to stop")
        await ctx.author.voice.channel.connect()
        self.active_guilds[ctx.guild.id] = ctx.channel
        self.queue[ctx.guild.id] = []

    @commands.command()
    @commands.has_guild_permissions(manage_messages=True)
    async def stoptts(self, ctx: commands.Context):
        if ctx.guild.id not in self.active_guilds.keys():
            await ctx.send("Not watching a voice channel!")
            return
        del self.active_guilds[ctx.guild.id]
        self.queue[ctx.guild.id] = []
        await ctx.send("Stopping when queue is empty")
        await ctx.guild.voice_client.disconnect()


    async def tts(self, message: discord.Message):
        try:
            if message.guild.id not in self.active_guilds.keys():
                return
            if message.channel.id != self.active_guilds[message.guild.id].id:
                return
            msg = gtts.gTTS(f"{message.author.display_name} says {message.content}")
            fname = f"{message.id}"
            msg.save(f"{fname}.mp3")
            self.queue[message.guild.id].append(fname)
            while True:
                while message.guild.voice_client.is_playing():
                    pass
                if len(self.queue[message.guild.id]) == 0:
                    os.remove(f"{fname}.mp3")
                    return
                if self.queue[message.guild.id][0] == fname: break
            del self.queue[message.guild.id][0]
            message.guild.voice_client.play(discord.FFmpegPCMAudio(f'{fname}.mp3'), after=lambda x: os.remove(f"{fname}.mp3"))
        except Exception as e:
            print(type(e))
            raise


def setup(bot): bot.add_cog(TTS(bot))