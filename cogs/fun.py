import math
import random

import discord
import requests
from discord.ext import commands


class Fun(commands.Cog):
    def __init__(self, bot: discord.ext.commands.Bot):
        self.bot = bot

    @commands.command()
    async def ship(self, ctx: commands.Context, user1: discord.Member, user2: discord.Member):
        """Ships two users.. awww <3"""
        name1: str = user1.display_name
        name2: str = user2.display_name

        def split(s: str):
            import re
            if s == "crazygmr101": return ["crazy", "gmr101"]
            if len(s.split(" ")) > 1:
                ar = s.split(" ")
                return [
                    " ".join(ar[:math.floor(len(s.split(" ")) / 2)]),
                    " ".join(ar[math.floor(len(s.split(" ")) / 2):])
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
            half = int(len(s) / 2)
            return [s[:half], s[half:]]

        await ctx.send("I ship it: " + split(name1)[0] + split(name2)[1])

    @commands.command()
    async def hug(self, ctx: commands.Context, user: discord.Member):
        """Hug a user"""
        e = discord.Embed()
        e.title = f'{ctx.author.name} hugs {user.name}'
        e.set_image(url=requests.get("https://nekos.life/api/v2/img/hug").json()["url"])
        await ctx.send(embed=e)
        await ctx.message.delete()

    @commands.command()
    async def pat(self, ctx: commands.Context, user: discord.Member):
        """Pat a user"""
        e = discord.Embed()
        e.title = f'{ctx.author.name} pats {user.name}'
        e.set_image(url=requests.get("https://nekos.life/api/v2/img/pat").json()["url"])
        await ctx.send(embed=e)
        await ctx.message.delete()

    @commands.command()
    async def poke(self, ctx: commands.Context, user: discord.Member):
        """Poke a user"""
        e = discord.Embed()
        e.title = f'{ctx.author.name} pokes {user.name}'
        e.set_image(url=requests.get("https://nekos.life/api/v2/img/poke").json()["url"])
        await ctx.send(embed=e)
        await ctx.message.delete()

    @commands.command()
    async def cuddle(self, ctx: commands.Context, user: discord.Member):
        """Cuddle a user"""
        e = discord.Embed()
        e.title = f'{ctx.author.name} cuddles {user.name}'
        e.set_image(url=requests.get("https://nekos.life/api/v2/img/cuddle").json()["url"])
        await ctx.send(embed=e)
        await ctx.message.delete()

    @commands.command()
    async def kiss(self, ctx: commands.Context, user: discord.Member):
        """Kiss a user"""
        e = discord.Embed()
        e.title = f'{ctx.author.name} kisses {user.name}'
        e.set_image(url=requests.get("https://nekos.life/api/v2/img/kiss").json()["url"])
        await ctx.send(embed=e)
        await ctx.message.delete()

    @commands.command(aliases=["bork"])
    async def woof(self, ctx: commands.Context):
        """Sends a dog pic"""
        images = [
            "irXVvTn", "1Hy1Ivm", "snyoQYt", "iTD3btm", "gI2hJgp", "4JW8iDZ", "71ssqGq", "WjNBjzO", "LQOkhKM",
            "eVFf6Oy", "JL4jVlG", "C4E5iAl", "Ck08zJG", "k18Raxy", "aJG7iXc", "CThNFi4", "jg2zL7E", "DaHdglt",
            "FRstrnz", "0HrTq3Y", "ZK7VcJN", "8lPbfAJ", "E7dje1b", "1Hy1Ivm"
        ]
        e = discord.Embed()
        woof_text = random.choice(["Woof!", "Arf!", "Bork!"])
        woof_emoji = random.choice(["▼・ᴥ・▼", "▼(´ᴥ`)▼", "U ´ᴥ` U", "U・ᴥ・U", "U・ﻌ・U", "U ´x` U", "(U・x・U)",
                                    "υ´• ﻌ •`υ", "૮ ・ﻌ・ა", "(❍ᴥ❍ʋ)", "( ͡° ᴥ ͡° ʋ)", "V●ω●V", "V✪ω✪V", "V✪⋏✪V",
                                    "∪ ̿–⋏ ̿–∪", "∪･ω･∪", "໒( ●ܫฺ ●)ʋ", "໒( = ᴥ =)ʋ}"])
        woof_img = random.choice(images)
        e.title = f'{woof_text} {woof_emoji}'
        e.set_image(url=f"https://i.imgur.com/{woof_img}.jpg")
        await ctx.send(embed=e)
        await ctx.message.delete()

    @commands.command()
    async def meow(self, ctx: commands.Context):
        """Sends a cat pic"""
        e = discord.Embed()
        meow_text = random.choice(["(^-人-^)", "(^・ω・^ )", "(=;ェ;=)", "(=^・^=)", "(=^・ｪ・^=)", "(=^‥^=)", "(=ＴェＴ=)",
                                   "(=ｘェｘ=)", "＼(=^‥^)/`", "~(=^‥^)/", "└(=^‥^=)┐", "ヾ(=ﾟ・ﾟ=)ﾉ", "ヽ(=^・ω・^=)丿",
                                   "d(=^・ω・^=)b", "o(^・x・^)o"])
        e.title = f'Meow! {meow_text}'
        e.set_image(url=requests.get("https://nekos.life/api/v2/img/meow").json()["url"])
        await ctx.send(embed=e)
        await ctx.message.delete()

    @commands.command(aliases=["pbc", "chicken"])
    async def placeblock_chicken(self, ctx: commands.Context):
        """Does a Maddie"""
        await ctx.send(random.choice("🐔,🐤,🐥,🐣".split(",")))

    @commands.command()
    async def maddify(self, ctx: commands.Context):
        """Vöïds a message"""
        e = discord.Embed()
        msg: str = ctx.message.content
        msg_o: discord.Message = ctx.message
        msg = " ".join(msg.split(" ")[1::])
        replacements = [
            "a,e,i,o,u,A,E,I,O,U".split(","),
            "ä,ë,ï,ö,ü,Ä,Ë,Ï,Ö,Ü".split(",")
        ]
        for i in range(len(replacements[0])):
            msg = msg.replace(replacements[0][i], replacements[1][i])
        author: discord.Member = ctx.author
        e.colour = author.color
        e.title = author.display_name
        e.description = msg
        await ctx.send(embed=e)
        await msg_o.delete()


def setup(bot):
    bot.add_cog(Fun(bot))
