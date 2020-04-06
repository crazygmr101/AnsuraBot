import asyncio
import os
import re
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
        self.tts_mutes: Dict[int, List[str]] = {}
        self.tts_timeout: Dict[int, bool] = {}

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

    @commands.command(aliases=["tunmute"])
    @commands.has_guild_permissions(mute_members=True)
    async def ttsunmute(self, ctx: commands.Context, member: discord.Member = None):
        if member is None:
            await ctx.send("You must tag a member")
            return
        try:
            del self.tts_mutes[ctx.guild.id][self.tts_mutes[ctx.guild.id].index(member.id)]
            await ctx.send(f"TTS unmuted **{member.display_name}**")
        except:
            self.tts_mutes[ctx.guild.id].append(member.id)
            await ctx.send(f"**{member.display_name}** isn't TTS muted")

    @commands.command(aliases=["tmutel"])
    async def ttsmutelist(self, ctx: commands.Context):
        """Lists TTS-muted members"""
        if ctx.guild.id not in self.tts_mutes.keys():
            await ctx.send("No members TTS muted")
        if len(self.tts_mutes[ctx.guild.id]) == 0:
            await ctx.send("No members TTS muted")
        embed = discord.Embed(title="TTS muted members")
        embed.add_field(name=f"{len(self.tts_mutes[ctx.guild.id])} members TTS-muted",
                        value=" ".join([f"<@{x}>" for x in self.tts_mutes[ctx.guild.id]]))
        await ctx.send(embed=embed)

    @commands.command(aliases=["tmute"])
    @commands.has_guild_permissions(mute_members=True)
    async def ttsmute(self, ctx: commands.Context, member: discord.Member = None):
        """Makes messages from a member not autotts"""
        if member is None:
            await ctx.send("You must tag a member")
            return
        try:
            self.tts_mutes[ctx.guild.id].index(member.id)
            await ctx.send(f"**{member.display_name}** is already TTS muted")
        except:
            self.tts_mutes[ctx.guild.id].append(member.id)
            await ctx.send(f"TTS muted **{member.display_name}**")

    @commands.command()
    @commands.has_guild_permissions(manage_messages=True)
    @commands.bot_has_guild_permissions(speak=True)
    async def autotts(self, ctx: commands.Context):
        """
        Makes Ansura join the voice channel you are in and watch the current channel
        """
        if ctx.guild.id not in self.tts_mutes.keys():
            self.tts_mutes[ctx.guild.id] = []
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
        await ctx.send("Stopping")
        await ctx.guild.voice_client.disconnect()


    async def tts(self, message: discord.Message):
        def create_tts(m: str):
            msg = gtts.gTTS(m)
            fname = f"{message.id}"
            msg.save(f"{fname}.mp3")
            return fname
        if message.content.startswith("%"):
            return
        try:
            if message.guild.voice_client is None:
                try:
                    del self.active_guilds[message.guild.id]
                    self.queue[message.guild.id] = []
                    return
                except: pass
            if message.guild.id not in self.active_guilds.keys():
                return
            if message.channel.id != self.active_guilds[message.guild.id].id:
                return
            if message.author.id in self.tts_mutes[message.guild.id]:
                return
            m = f"{message.author.display_name} says {message.clean_content}"
            m = re.sub(r"((http[s]?|ftp):\/)?\/?([^:\/\s]+)((\/\w+)*\/)([\w\-\.]+[^#?\s]+)(.*)?(#[\w\-]+)?", ".Link.", m)
            m = re.sub("[^0-9A-Za-z.\u0020\u00c0-\u00d6\u00d8-\u00f6\u00f8-\u02af\u1d00-\u1d25\u1d62-\u1d65\u1d6b-\u1d77"
                       "\u1d79-\u1d9a\u1e00-\u1eff\u2090-\u2094\u2184-\u2184\u2488-\u2490\u271d-\u271d\u2c60-\u2c7c"
                       "\u2c7e-\u2c7f\ua722-\ua76f\ua771-\ua787\ua78b-\ua78c\ua7fb-\ua7ff\ufb00-\ufb06]", "", m)
            if m == "": return
            fname = await self.bot.loop.run_in_executor(None, create_tts, m)
            self.queue[message.guild.id].append(fname)
            def wait_for_queue():
                while True:
                    while message.guild.voice_client.is_playing():
                        pass
                    if len(self.queue[message.guild.id]) == 0:
                        os.remove(f"{fname}.mp3")
                        return 0
                    if self.queue[message.guild.id][0] == fname:
                        def final(arg):
                            os.remove(f"{fname}.mp3")
                            del self.queue[message.guild.id][0]
                        message.guild.voice_client.play(discord.FFmpegPCMAudio(f'{fname}.mp3'), after=final)
                        return 1
            if await self.bot.loop.run_in_executor(None, wait_for_queue) == 0:
                return
            await message.add_reaction("✅")
            await asyncio.sleep(10)
            await message.remove_reaction("✅", self.bot.user)
        except Exception as e:
            print(type(e))
            await message.add_reaction("❎")
            await asyncio.sleep(10)
            await message.remove_reaction("❎", self.bot.user)
            raise


def setup(bot): bot.add_cog(TTS(bot))