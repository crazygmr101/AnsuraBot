import re
from typing import List, Union

from discord.ext import commands
import discord
import random

from discord.ext.commands import check

import core.util.HelpEntries as HE


class Owner(commands.Cog):
    def __init__(self, bot: discord.ext.commands.Bot):
        self.bot = bot
        print("Owner cog loaded")
        self.guilds: List[discord.Guild] = []

    @commands.command(pass_context=True)
    @commands.is_owner()
    async def guilds(self, ctx: commands.Context):
        g: discord.Guild
        i = 0
        for g in self.bot.guilds:
            await ctx.send(str(i) + ":" + g.name)
            self.guilds.append(g)
            i += 1

    @commands.command(pass_context=True)
    @commands.is_owner()
    async def ginfo(self, ctx: commands.Context, n: int):
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
    @commands.is_owner()
    async def guild_leave(self, ctx: commands.Context, id: int):
        g: discord.Guild = await self.bot.fetch_guild(id)
        await g.leave()



    @commands.command()
    @commands.is_owner()
    async def die(self, ctx:discord.ext.commands.Context):
        quit()

    @commands.command()
    @commands.is_owner()
    async def snick(self, ctx: discord.ext.commands.Context):
        g = ctx.guild
        a: List[Union[discord.Member, discord.User]] = [x for x in g.members]
        b: List[Union[discord.Member, discord.User]] = [x for x in g.members]
        random.shuffle(a)
        for u in range(len(b)):
            try:
                await b[u].edit(nick=a[u].name)
                print(b[u].name + " , " + b[u].nick)
            except:
                pass

    @commands.command()
    @commands.is_owner()
    async def nick(self, ctx: discord.ext.commands.Context, name: str):
        await ctx.send("Nicknaming " + str())
        g: discord.Guild = ctx.guild
        s = 0
        f = 0
        i: Union[discord.Member, discord.User]
        a: List[Union[discord.Member, discord.User]] = [x for x in g.members]
        a.sort(key=lambda x: x.joined_at)
        c = 0
        for i in a:
            c += 1
            try:
                s += 1
                n = name
                n = re.sub(r"<join-num100>", str(c).zfill(3), n)
                n = re.sub(r"<join-num>", str(c), n)
                n = re.sub(r"<joined>", str(i.joined_at), n)
                n = re.sub(r"<disc>", str(i.discriminator), n)
                n = re.sub(r"<name>", str(i.name), n)
                await i.edit(nick=n)
            except:
                f += 1
                pass
        await ctx.send("Nicked " + str(s) + " (" + str(f) + " failed)")

def setup(bot):
    bot.add_cog(Owner(bot))