import random
from typing import Union

from discord.ext import commands
import discord
import core.help as HE
import gtts
import requests


class Fun(commands.Cog):
    def __init__(self, bot: discord.ext.commands.Bot):
        self.bot = bot
        print("Fun cog loaded")

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

    @commands.command()
    async def cake(self, ctx: commands.Context):
        if random.randint(1, 5) == 1:
            msg = 'nah, {0.author.mention}'.format(ctx.message)
        else:
            msg = '*gives :cake: to {0.author.mention}*'.format(ctx.message)
        await ctx.send(msg)
        await ctx.message.delete()

    @commands.command()
    async def givecake(self, ctx: commands.Context, user: Union[discord.User,discord.Member]):
        await ctx.send('*takes :cake: from {0.author.mention} and gives it to {1}*'.format(ctx.message, user.name))
        await ctx.message.delete()

    @commands.command()
    async def hug(self, ctx: commands.Context, user: Union[discord.User,discord.Member]):
        e = discord.Embed()
        e.title = f'{ctx.author.name} hugs {user.name}'
        e.set_image(url=requests.get("https://nekos.life/api/v2/img/hug").json()["url"])
        await ctx.send(embed=e)
        await ctx.message.delete()




def setup(bot):
    bot.add_cog(Fun(bot))
    HE.HelpEntries.register("ship", "%ship @person1 @person2", "Ship <3")
    HE.HelpEntries.register("xchat", "%xchat message", "Crosschat between servers", "Alias: xc")
    HE.HelpEntries.register("cake", "%cake", "Try to get cake")
    HE.HelpEntries.register("givecake", "%givecake @user", "Give cake, cuz sharing is caring :D")
    HE.HelpEntries.register("hug", "%hug @user", "HUGGGGGGGGGGGGGGGGGGGGGGGGGGG")