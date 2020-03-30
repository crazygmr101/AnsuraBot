import re
from typing import List, Union

from discord.ext import commands
import discord
import random

class Owner(commands.Cog):
    def __init__(self, bot: discord.ext.commands.Bot):
        self.bot = bot
        print("Owner cog loaded")
        self.guilds: List[discord.Guild] = []

    @commands.command()
    @commands.is_owner()
    @commands.has_permissions(manage_guild=True, manage_nicknames=True)
    @commands.bot_has_permissions(manage_guild=True, manage_nicknames=True)
    async def nick_all(self, ctx: discord.ext.commands.Context, name: str):
        """
        Nickname all users in a server according to a pattern
        <join-num100> - 3 digit padded join num
        <join-num>
        <joined> - timestamp of user join
        <disc>
        <name>
        """
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

    @commands.command()
    @commands.is_owner()
    @commands.has_permissions(manage_guild=True, manage_nicknames=True)
    @commands.bot_has_permissions(manage_guild=True, manage_nicknames=True)
    async def shufflenicks(self, ctx: discord.ext.commands.Context):
        """
        Shuffle the nicknames of all users in a server
        """
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
    @commands.has_permissions(manage_guild=True, manage_roles=True)
    @commands.bot_has_permissions(manage_guild=True, manage_roles=True)
    async def role_all(self, ctx: discord.ext.commands.Context, role: discord.Role):
        """
        Gives a role to all members of a server
        - role: the role to give a user
        """
        g: discord.Guild = ctx.guild
        s = 0
        f = 0
        r = role
        i: Union[discord.Member, discord.User]
        a: List[Union[discord.Member, discord.User]] = [x for x in g.members]
        await ctx.send("Giving everyone  " + r.mention)
        c = 0
        for i in a:
            c += 1
            try:
                await i.add_roles(r)
                print("Added to " + str(i.display_name))
            except Exception as e:
                f += 1
                print("Failed on " + str(i.display_name))
                print(e)
                pass
        await ctx.send("Gave " + r.mention + " to " + str(s) + " (" + str(f) + " failed)")

    @commands.command(pass_context=True)
    @commands.is_owner()
    async def guilds(self, ctx: commands.Context):
        """
        Gets the list of guilds Ansura is in.
        """
        g: discord.Guild
        i = 0
        for g in self.bot.guilds:
            await ctx.send(str(i) + ":" + g.name)
            self.guilds.append(g)
            i += 1

    @commands.command(pass_context=True)
    @commands.is_owner()
    async def ginfo(self, ctx: commands.Context, n: int):
        """
        Gets basic guild info of a guild from %guilds
        - n: guilds list index
        """
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
        """Leaves a guild given by <id>"""
        g: discord.Guild = await self.bot.fetch_guild(id)
        await g.leave()



    @commands.command()
    @commands.is_owner()
    async def die(self, ctx: discord.ext.commands.Context):
        await ctx.send(random.choice([
            "Oh..okay..sure..I'll brb",
            "): Okay",
            "D: But..why? *sighs* fInE"
        ]))
        exit()


def setup(bot):
    bot.add_cog(Owner(bot))