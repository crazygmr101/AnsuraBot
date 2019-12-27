import re
from typing import List, Union

from discord.ext import commands
import discord
import core.util.HelpEntries as HE


class Owner(commands.Cog):
    def __init__(self, bot: discord.ext.commands.Bot):
        self.bot = bot
        print("Owner cog loaded")
        self.guilds: List[discord.Guild] = []

    @commands.command(pass_context=True)
    async def guilds(self, ctx: commands.Context):
        if ctx.author.id != 267499094090579970:
            return
        g: discord.Guild
        i = 0
        for g in self.bot.guilds:
            await ctx.send(str(i) + ":" + g.name)
            self.guilds.append(g)
            i += 1

    @commands.command(pass_context=True)
    async def ginfo(self, ctx: commands.Context, n: int):
        if ctx.author.id != 267499094090579970:
            return
        if n < 0 or n >= len(self.guilds):
            await ctx.send("Invalid number")
            return
        g: discord.Guild = self.guilds[n]
        e = discord.Embed()
        e.title = g.name
        e.set_image(url=g.icon_url)
        e.description = g.description
        e.add_field(name="Members", value=str(g.member_count))
        e.add_field(name="Region", value=str(g.region))
        e.add_field(name="ID", value=str(g.id))
        await ctx.send(embed=e)

    @commands.command(pass_context=True)
    async def guild_leave(self, ctx: commands.Context, id: int):
        if ctx.author.id != 267499094090579970:
            return
        g: discord.Guild = await self.bot.fetch_guild(id)
        await g.leave()



    @commands.command()
    async def die(self, ctx:discord.ext.commands.Context):
        if ctx.author.id == 267499094090579970:
            quit()
def setup(bot):
    bot.add_cog(Owner(bot))