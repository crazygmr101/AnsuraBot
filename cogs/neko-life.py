import discord
import requests
from discord.ext import commands
import random
from core.help import HelpEntries as help

class NekoLife(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = "Bot"
        print("Neko cog loaded")

    @commands.command()
    async def hug(self, ctx: commands.Context, user: discord.Member):
        e = discord.Embed()
        e.title = f'{ctx.author.name} hugs {user.name}'
        e.set_image(url=requests.get("https://nekos.life/api/v2/img/hug").json()["url"])
        await ctx.send(embed=e)
        await ctx.message.delete()

    @commands.command()
    async def pat(self, ctx: commands.Context, user: discord.Member):
        e = discord.Embed()
        e.title = f'{ctx.author.name} pats {user.name}'
        e.set_image(url=requests.get("https://nekos.life/api/v2/img/pat").json()["url"])
        await ctx.send(embed=e)
        await ctx.message.delete()

    @commands.command()
    async def poke(self, ctx: commands.Context, user: discord.Member):
        e = discord.Embed()
        e.title = f'{ctx.author.name} pokes {user.name}'
        e.set_image(url=requests.get("https://nekos.life/api/v2/img/poke").json()["url"])
        await ctx.send(embed=e)
        await ctx.message.delete()

    @commands.command()
    async def cuddle(self, ctx: commands.Context, user: discord.Member):
        e = discord.Embed()
        e.title = f'{ctx.author.name} cuddles {user.name}'
        e.set_image(url=requests.get("https://nekos.life/api/v2/img/cuddle").json()["url"])
        await ctx.send(embed=e)
        await ctx.message.delete()

    @commands.command()
    async def kiss(self, ctx: commands.Context, user: discord.Member):
        e = discord.Embed()
        e.title = f'{ctx.author.name} kisses {user.name}'
        e.set_image(url=requests.get("https://nekos.life/api/v2/img/kiss").json()["url"])
        await ctx.send(embed=e)
        await ctx.message.delete()

    @commands.command(aliases=["bork"])
    async def woof(self, ctx: commands.Context):
        images = [
            "irXVvTn", "1Hy1Ivm", "snyoQYt", "iTD3btm", "gI2hJgp", "4JW8iDZ", "71ssqGq", "WjNBjzO", "LQOkhKM",
            "eVFf6Oy", "JL4jVlG", "C4E5iAl", "Ck08zJG", "k18Raxy", "aJG7iXc", "CThNFi4", "jg2zL7E", "DaHdglt",
            "FRstrnz", "0HrTq3Y", "ZK7VcJN", "8lPbfAJ", "E7dje1b", "1Hy1Ivm"
        ]
        e = discord.Embed()
        woof_text = random.choice(["Woof!", "Arf!", "Bork!"])
        woof_emoji = random.choice(["▼・ᴥ・▼", "▼(´ᴥ`)▼", "U ´ᴥ` U", "U・ᴥ・U", "U・ﻌ・U", "U ´x` U","(U・x・U)",
                                    "υ´• ﻌ •`υ", "૮ ・ﻌ・ა", "(❍ᴥ❍ʋ)", "( ͡° ᴥ ͡° ʋ)", "V●ω●V","V✪ω✪V","V✪⋏✪V",
                                    "∪ ̿–⋏ ̿–∪", "∪･ω･∪", "໒( ●ܫฺ ●)ʋ", "໒( = ᴥ =)ʋ}"])
        woof_img = random.choice(images)
        e.title = f'{woof_text} {woof_emoji}'
        e.set_image(url=f"https://i.imgur.com/{woof_img}.jpg")
        await ctx.send(embed=e)
        await ctx.message.delete()

    @commands.command()
    async def meow(self, ctx: commands.Context):
        e = discord.Embed()
        meow_text = random.choice(["(^-人-^)", "(^・ω・^ )", "(=;ェ;=)", "(=^・^=)", "(=^・ｪ・^=)", "(=^‥^=)", "(=ＴェＴ=)", 
                                   "(=ｘェｘ=)", "＼(=^‥^)/`", "~(=^‥^)/", "└(=^‥^=)┐", "ヾ(=ﾟ・ﾟ=)ﾉ", "ヽ(=^・ω・^=)丿", 
                                   "d(=^・ω・^=)b", "o(^・x・^)o"])
        e.title = f'Meow! {meow_text}'
        e.set_image(url=requests.get("https://nekos.life/api/v2/img/meow").json()["url"])
        await ctx.send(embed=e)
        await ctx.message.delete()


def setup(bot):
    bot.add_cog(NekoLife(bot))
    for x in ["hug", "kiss", "pat", "poke", "cuddle"]:
        help.register(x, f"%{x} @user", f"{x} a user :)")
    help.register("meow", "%meow", "Cute cat pics, who doesn't like those?")
    help.register("meow", "%woof", "Cute dog pics, who doesn't like those?", "Aliases: Woof")