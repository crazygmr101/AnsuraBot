from typing import Union

import discord
from discord.ext import commands
import core.help as HE
import random

class Misc(commands.Cog):
    def __init__(self, bot: discord.ext.commands.Bot):
        self.bot = bot
        print("Misc cog loaded")

    @commands.command(aliases=["av"])
    async def avatar(self, ctx: discord.ext.commands.Context, user: Union[discord.Member, discord.User] = None):
        if user is None:
            user = ctx.author
        await ctx.send(user.avatar_url)

    @commands.command()
    async def role(self, ctx: discord.ext.commands.Context, r: discord.Role):
        def val_or_space(val: str): return "-" if val == "" else val
        e = discord.Embed()
        e.title = "Role: " + r.name
        e.colour = r.colour
        online = []
        offline = []
        m: discord.Member
        if len(r.members) == 0:
            e.description = f"No members with role"
            await ctx.send(embed=e)
            return
        for m in r.members:
            if m.status == discord.Status.offline:
                offline.append(m)
            else:
                online.append(m)
        online_t = []
        for x in online:
            online_t.append(x)
            if len(online_t) > 30: break
        offline_t = []
        for x in offline:
            offline_t.append(x)
            if len(offline_t) > 30: break
        e.description = f"Listing {len(online_t) + len(offline_t)} of {len(r.members)}"
        e.add_field(name=f"Online ({len(online_t)} of {len(online)})",
                    value=val_or_space(" ".join([m.mention for m in online_t])))
        e.add_field(name=f"Offline ({len(offline_t)} of {len(offline)})",
                    value=val_or_space(" ".join([m.mention for m in offline_t])))
        await ctx.send(embed=e)

    @role.error
    async def role_error(self, ctx: discord.ext.commands.Context, error: Exception):
        if isinstance(error, discord.ext.commands.ConversionError) or\
           isinstance(error, discord.ext.commands.BadArgument):
            await ctx.send("Oops. I can't seem to find that role. Double-check capitalization and spaces.")
        else:
            raise error

    @commands.command()
    @commands.bot_has_permissions(embed_links=True)
    @commands.has_permissions(manage_messages=True)
    async def embed(self, ctx: discord.ext.commands.Context, title: str, desc: str, ch: discord.TextChannel = None,
                    color: discord.Colour = None, id: int = 0):
        color = ctx.author.color if color is None else color
        ch = ctx.channel if ch is None else ch
        e = discord.Embed()
        e.title = title
        e.description = desc
        e.colour = color
        e.set_author(icon_url=ctx.author.avatar_url, name=ctx.author.name)
        if id == 0:
            await ch.send(embed=e)
            await ctx.send()
        else:
            message = await ch.fetch_message(id)
            await message.edit(embed=e)

    @commands.command()
    async def info(self, ctx: discord.ext.commands.Context, user: Union[discord.Member, discord.User] = None):
        if user is None:
            user = ctx.author
        e = discord.Embed()
        e.title = user.name + "#" + user.discriminator
        e.set_thumbnail(url=user.avatar_url)
        e.add_field(name="ID", value=user.id)
        if type(user) == discord.Member:
            e.add_field(name="Display Name", value=user.display_name)
            e.add_field(name="Top Role", value=user.top_role.name + " (" + str(user.top_role.id) + ")")
            e.add_field(name="Created on", value=user.created_at)
            e.add_field(name="Joined on", value=user.joined_at)
            e.add_field(name="Mobile", value=str(user.is_on_mobile()))
            e.colour = user.color
        await ctx.send(embed=e)

    @commands.command()
    async def ping(self, ctx: discord.ext.commands.Context):
        await ctx.send("Pong :D " + str(int(self.bot.latency * 1000)) + "ms")


def setup(bot):
    bot.add_cog(Misc(bot))
    HE.HelpEntries.register("placeblock_chicken", "%placeblock_chicken", "Does a <@276365523045056512>.",
                            "Placeblock chicken. Never forget.\nNOTE: This is NOT *placeblovk fhivkrn*.\n"
                            "Aliases: pbc, chicken")
    HE.HelpEntries.register("maddify", "%maddify message", "It's ëpïc")
    HE.HelpEntries.register("avatar", "%avatar @user", "Gets avatar for user", "Aliases: av")
    HE.HelpEntries.register("info", "%info @user", "Displays info for a user")
