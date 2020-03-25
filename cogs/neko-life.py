import discord
import requests
from discord.ext import commands
import random

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


def setup(bot):
    bot.add_cog(NekoLife(bot))