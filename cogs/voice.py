import asyncio
import re

import discord
import gtts
from discord.ext import commands

from ansura import AnsuraBot, AnsuraContext
from lib.voicemanager import VoiceManager, TTSQueue, YTDLSource


class Voice(commands.Cog):
    def __init__(self, bot: AnsuraBot):
        self.bot = bot
        self.vm: VoiceManager = bot.vm

    @commands.command(aliases=["radio"])
    async def stream(self, ctx, *, url):
        """Streams from a url (same as yt, but doesn't predownload)"""

        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
            ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)

        await ctx.send('Now playing: {}'.format(player.title))

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def summon(self, ctx: AnsuraContext):
        """Summons Ansura to your voice channel"""
        await ctx.author.voice.channel.connect()

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def leave(self, ctx: AnsuraContext):
        """Makes Ansura leave your voice channel"""
        await ctx.guild.voice_client.disconnect()

    @commands.command(aliases=["tunmute"])
    @commands.has_guild_permissions(mute_members=True)
    async def ttsunmute(self, ctx: AnsuraContext, member: discord.Member = None):
        if member is None:
            await ctx.send("You must tag a member")
            return
        try:
            del self.vm.tts_mutes[ctx.guild.id][self.vm.tts_mutes[ctx.guild.id].index(member.id)]
            await ctx.send(f"TTS unmuted **{member.display_name}**")
        except:  # noqa e722
            self.vm.tts_mutes[ctx.guild.id].append(member.id)
            await ctx.send(f"**{member.display_name}** isn't TTS muted")

    @commands.command(aliases=["tmutel"])
    async def ttsmutelist(self, ctx: AnsuraContext):
        """Lists TTS-muted members"""
        if ctx.guild.id not in self.vm.tts_mutes.keys():
            await ctx.send("No members TTS muted")
            return
        if len(self.vm.tts_mutes[ctx.guild.id]) == 0:
            await ctx.send("No members TTS muted")
            return
        embed = discord.Embed(title="TTS muted members")
        embed.add_field(name=f"{len(self.vm.tts_mutes[ctx.guild.id])} members TTS-muted",
                        value=" ".join([f"<@{x}>" for x in self.vm.tts_mutes[ctx.guild.id]]))
        await ctx.send(embed=embed)

    @commands.command(aliases=["tmute"])
    @commands.has_guild_permissions(mute_members=True)
    async def ttsmute(self, ctx: AnsuraContext, member: discord.Member = None):
        """Makes messages from a member not autotts"""
        if member is None:
            await ctx.send("You must tag a member")
            return
        if ctx.guild.id not in self.vm.tts_mutes.keys():
            self.vm.tts_mutes[ctx.guild.id] = []
        try:
            self.vm.tts_mutes[ctx.guild.id].index(member.id)
            await ctx.send(f"**{member.display_name}** is already TTS muted")
        except ValueError:
            self.vm.tts_mutes[ctx.guild.id].append(member.id)
            await ctx.send(f"TTS muted **{member.display_name}**")

    @commands.command()
    @commands.has_guild_permissions(manage_messages=True)
    @commands.bot_has_guild_permissions(speak=True)
    async def autotts(self, ctx: AnsuraContext):
        """
        Makes Ansura join the voice channel you are in and watch the current channel
        """
        if self.vm.guild_states.get(ctx.guild.id, 0) != 0:
            await ctx.send("Already active in a channel!")
        if ctx.guild.id not in self.vm.tts_mutes.keys():
            self.vm.tts_mutes[ctx.guild.id] = []
        if ctx.guild.id in self.vm.active_guilds.keys():
            await ctx.send("Do %stoptts to stop")
            return
        if not ctx.author.voice:
            await ctx.send("Join a voice channel!")
            return
        await ctx.send("Watching this channel for messages, do %stoptts to stop")
        try:
            await ctx.author.voice.channel.connect()
        except:  # noqa e722
            pass
        # TODO fix this
        self.vm.guild_states[ctx.guild.id] = 1
        self.vm.active_guilds[ctx.guild.id] = ctx.channel
        self.vm.queues[ctx.guild.id] = TTSQueue(ctx.guild.id, ctx.guild.voice_client)

    @commands.command()
    @commands.has_guild_permissions(manage_messages=True)
    async def stoptts(self, ctx: AnsuraContext):
        if ctx.guild.id not in self.vm.active_guilds.keys():
            await ctx.send("Not watching a voice channel!")
            return
        del self.vm.active_guilds[ctx.guild.id]
        del self.vm.guild_states[ctx.guild.id]
        self.vm.queues[ctx.guild.id].stop()
        await ctx.send("Stopping")
        await ctx.guild.voice_client.disconnect()

    async def tts(self, message: discord.Message):  # noqa c901
        def create_tts(m: str):
            msg = gtts.gTTS(m)
            fname = f"{message.id}"
            msg.save(f"{fname}.mp3")
            return fname

        if message.content.startswith("%") \
                or message.content.startswith("!"): # beta's prefix
            return
        try:
            if message.guild.voice_client is None:
                try:
                    del self.vm.active_guilds[message.guild.id]
                    del self.vm.queues[message.guild.id]
                    return
                except:  # noqa e722
                    pass
            if message.guild.id not in self.vm.active_guilds.keys():
                return
            if message.channel.id != self.vm.active_guilds[message.guild.id].id:
                return
            if message.author.id in self.vm.tts_mutes[message.guild.id]:
                return
            m = message.clean_content
            m = re.sub(r"((http[s]?|ftp):/)?/?([^:/\s]+)((/\w+)*/)([\w\-.]+[^#?\s]+)(.*)?(#[\w\-]+)?", ".Link.",
                       m)
            m = re.sub(r"<:[A-Za-z0-9_]+:[0-9]{18}>", ".", m)
            m = re.sub(
                "[^0-9A-Za-z.\u0020\u00c0-\u00d6\u00d8-\u00f6\u00f8-\u02af\u1d00-\u1d25\u1d62-\u1d65\u1d6b-\u1d77"
                "\u1d79-\u1d9a\u1e00-\u1eff\u2090-\u2094\u2184-\u2184\u2488-\u2490\u271d-\u271d\u2c60-\u2c7c"
                "\u2c7e-\u2c7f\ua722-\ua76f\ua771-\ua787\ua78b-\ua78c\ua7fb-\ua7ff\ufb00-\ufb06]", "", m)
            if m.strip(" .") == "":
                return
            fname = await self.bot.loop.run_in_executor(None, create_tts, f"{message.author.display_name} says {m}")
            self.vm.queues[message.guild.id].add(fname)
            await message.add_reaction("✅")
            await asyncio.sleep(10)
            await message.remove_reaction("✅", self.bot.user)
        except Exception as e:
            print(type(e))
            await message.add_reaction("❎")
            await asyncio.sleep(10)
            await message.remove_reaction("❎", self.bot.user)
            raise


def setup(bot):
    bot.add_cog(Voice(bot))
