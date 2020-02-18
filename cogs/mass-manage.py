import re
from typing import List, Union
import core.help as help
from discord.ext import commands
import discord
import random
from discord.permissions import Permissions as perms

class MassManage(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        print("Server Management cog loaded")

    @commands.command()
    @commands.is_owner()
    @commands.has_permissions(manage_guild=True, manage_nicknames=True)
    @commands.bot_has_permissions(manage_guild=True, manage_nicknames=True)
    async def nick_all(self, ctx: discord.ext.commands.Context, name: str):
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
    async def role_all(self, ctx: discord.ext.commands.Context, role: str):
        g: discord.Guild = ctx.guild
        s = 0
        f = 0
        r: discord.Role = discord.utils.get(g.roles, name=role)
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


def setup(bot):
    bot.add_cog(MassManage(bot))
    help.HelpEntries.register("nick_all", "%nick_all nickname-pattern", "Nicknames all the members of a server according to a pattern",
                              "*Replacements*\n"
                              "<join-num> - the order someone joined the server\n"
                              "<join-num100> - same as <join-num>, but padded to 3 digits\n"
                              "<disc> - the user's discriminator\n"
                              "<name> - the user's username, without discriminator")
    help.HelpEntries.register("role_all", "%role_all rolename", "Gives a role to everyone in a server")
    help.HelpEntries.register("shuffle_nicks", "%shuffle_nicks", "Shuffles nicknames in a server")