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
