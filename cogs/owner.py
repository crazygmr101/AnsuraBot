import random
import re
from typing import List, Union

import discord
from discord.ext import commands

import cogs
from ansura import AnsuraBot, AnsuraContext


class Owner(commands.Cog):
    def __init__(self, bot: AnsuraBot):
        self.bot = bot
        self.guilds: List[discord.Guild] = []

    @commands.command()
    @commands.is_owner()
    async def setgame(self, ctx: AnsuraContext, status: str):
        await self.bot.change_presence(status=discord.Status.online, activity=discord.Game(status))

    @commands.command()
    @commands.is_owner()
    async def guilds(self, ctx: AnsuraContext):
        g: discord.Guild
        m: discord.Message = await ctx.send("Building list...")
        s = """```"""
        async with ctx.typing():
            for g in self.bot.guilds:
                s += f"{g.id} - {g.name}\n"
        await m.edit(content=s + "```")

    @commands.command()
    @commands.is_owner()
    async def ginfo(self, ctx: AnsuraContext, guild_id: int):
        async with ctx.typing():
            if guild_id not in [g.id for g in self.bot.guilds]:
                await ctx.send("I'm not in a guild with that ID")
                return
            m: discord.User
            g: discord.Guild = self.bot.get_guild(guild_id)
            users, bots = 0, 0
            for m in g.members:
                if m.bot:
                    bots += 1
                else:
                    users += 1
            e = discord.Embed()
            e.title = g.name
            e.set_thumbnail(url=g.icon_url)
            e.description = g.description
            e.add_field(name="Total Members", value=g.member_count)
            e.add_field(name="Users/Bots", value=f"{users}/{bots}")
            e.add_field(name="Region", value=str(g.region))
            e.add_field(name="ID", value=str(g.id), inline=False)
            u: discord.User = g.owner
            e.add_field(name="Owner", value=f"{u.name}#{u.discriminator} ({g.owner_id})", inline=False)
        await ctx.send(embed=e)

    @commands.command()
    @commands.is_owner()
    async def guild_leave(self, ctx: AnsuraContext, id: int):
        """Leaves a guild given by <id>"""
        g: discord.Guild = self.bot.get_guild(id)
        if g is None:
            await ctx.send("I'm not in a guild with this ID")
            return
        s = g.name
        await g.leave()
        await ctx.send(f"Left {s}")

    @commands.command()
    @commands.is_owner()
    async def die(self, ctx: AnsuraContext):
        await ctx.send_ok(random.choice([
            "Oh..okay..sure..I'll brb",
            "): Okay",
            "D: But..why? *sighs* fInE"
        ]))
        for ext in self.bot.initial_extensions:  # noqa
            if "owner" not in ext:
                print(f"[SHUTDOWN] Unloading {ext}")
                self.bot.unload_extension(ext)
        await self.bot.logout()


def setup(bot):
    bot.add_cog(Owner(bot))
