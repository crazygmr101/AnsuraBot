import discord
import gtts
from discord.ext import commands

class TTS(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot



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


def setup(bot): bot.add_cog(TTS(bot))