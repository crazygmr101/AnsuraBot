from typing import List

from discord.ext import commands
import discord
import core.util.HelpEntries as HE
import re
import gtts

from core.crosschat import Crosschat


class Fun(commands.Cog):
    def __init__(self, bot: discord.ext.commands.Bot):
        self.bot = bot
        print("Fun cog loaded")
        self.cxchat = Crosschat(bot)

    @commands.command(pass_context=True)
    async def ship(self, ctx: commands.Context, user1: discord.Member, user2: discord.Member):
        name1: str = user1.display_name
        name2: str = user2.display_name
        def split(s: str):
            import re
            if s == "crazygmr101": return ["crazy","gmr101"]
            if len(s.split(" ")) > 1:
                ar = s.split(" ")
                return [
                    " ".join(ar[:1]),
                    " ".join(ar[1:])
                ]
            if len(s.split("_")) > 1:
                ar = s.split("_")
                return [
                    " ".join(ar[:1]),
                    " ".join(ar[1:])
                ]
            # check for alt caps
            ar = re.sub('([A-Z][a-z]+)', r' \1', re.sub('([A-Z]+)', r' \1', s)).split()
            if len(ar) > 1:
                return [
                    " ".join(ar[:1]),
                    " ".join(ar[1:])
                ]
            # TODO: work on this code a tad more, just push
            half = int(len(s)/2)
            return [s[:half], s[half:]]
        await ctx.send("I ship it: " + split(name1)[0] + split(name2)[1])

    @commands.command(pass_context=True, aliases=["xc"])
    async def xchat(self, ctx: commands.Context):
        ctx.message.content = " ".join(ctx.message.content.split(" ")[1:])
        await self.cxchat.xchat(ctx.message)

    @commands.command(pass_context=True)
    @commands.is_owner()
    @commands.has_permissions(manage_messages=True)
    async def summon(self, ctx: commands.Context):
        await ctx.author.voice.channel.connect()

    @commands.command(pass_context=True)
    @commands.has_permissions(manage_messages=True)
    @commands.is_owner()
    async def leave(self, ctx: commands.Context):
        await ctx.guild.voice_client.disconnect()

    @commands.command(pass_context=True)
    @commands.is_owner()
    @commands.has_permissions(manage_messages=True)
    async def say(self, ctx: commands.Context, text):
        message = gtts.gTTS(text)
        message.save('tts.mp3')
        ctx.guild.voice_client.play(discord.FFmpegPCMAudio('tts.mp3'))




def setup(bot):
    bot.add_cog(Fun(bot))
    HE.HelpEntries.register("ship", "%ship @person1 @person2", "Ship <3")
    HE.HelpEntries.register("xchat", "%xchat message", "Crosschat between servers", "Alias: xc")