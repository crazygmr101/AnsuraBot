from typing import Union

import discord
from discord.ext import commands

import cogs.gamertags


class Administration(commands.Cog):
    def error(self, title, message={}, color=0xff0000):
        e = discord.Embed()
        e.colour = color
        e.title = title
        for k in message.keys():
            e.add_field(name=k, value=message[k])
        return e

    def __init__(self, bot: discord.ext.commands.Bot):
        self.bot = bot
        print("Administration cog loaded")

    @commands.command(aliases=["sgv"])
    async def setgtval(self, ctx: discord.ext.commands.Context,
                       typ: str, user: Union[discord.Member, discord.User],
                       val: str):
        ch: discord.TextChannel = \
            ctx.channel
        if not ch.permissions_for(ctx.author).administrator:
            await ctx.send(embed=
                           self.error("Permission error",
                                      message={
                                          "Message":
                                              "You must have administrator permission"
                                      })
                           )
            return
        if typ not in "xbox,mojang,youtube,twitch,mixer".split(","):
            await ctx.send(embed=
                           self.error("Invalid gametag type"))
            await self.bot.get_cog("Help").help_(ctx, "setgtval")
            return
        util: cogs.gamertags.Util = self.bot.get_cog("Util")
        db = util.db
        if typ == "xbox": typ = "xboxlive"
        rec = db.lookup_gaming_record(user.id)
        e = discord.Embed()
        e.colour = user.color
        e.title = user.display_name + " before"
        e.add_field(name="XBox", value=rec[2] if rec[2] is not None else "N/A")
        e.add_field(name="Mojang", value=rec[1] if rec[1] is not None else "N/A")
        e.add_field(name="Youtube", value=rec[3] if rec[3] is not None else "N/A")
        e.add_field(name="Twitch", value=rec[4] if rec[4] is not None else "N/A")
        e.add_field(name="Mixer", value=rec[5] if rec[5] is not None else "N/A")
        await ctx.send(embed=e)
        db.set_gaming_record(user.id, typ, val)
        rec = db.lookup_gaming_record(user.id)
        e = discord.Embed()
        e.colour = user.color
        e.title = user.display_name + " after"
        e.add_field(name="XBox", value=rec[2] if rec[2] is not None else "N/A")
        e.add_field(name="Mojang", value=rec[1] if rec[1] is not None else "N/A")
        e.add_field(name="Youtube", value=rec[3] if rec[3] is not None else "N/A")
        e.add_field(name="Twitch", value=rec[4] if rec[4] is not None else "N/A")
        e.add_field(name="Mixer", value=rec[5] if rec[5] is not None else "N/A")
        await ctx.send(embed=e)


def setup(bot):
    bot.add_cog(Administration(bot))
