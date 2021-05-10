import os
import re
from typing import Union

import discord
from discord.ext import commands

import lib.hypixel
import lib.hypixel
from ansura import AnsuraBot, AnsuraContext


class Gaming(commands.Cog):
    def __init__(self, bot: AnsuraBot):
        self.bot = bot
        self.htoken = os.getenv("HYPIXEL")

    async def hypixel(self, ctx: AnsuraContext, player: Union[discord.Member, str], *,
                      profile_type: str = None):
        """
        Checks a player's hypixel profile
        - player: the minecraft username
          or a @mention of a user with their
          mojang profile linked
        - profile_type:
          > None - basic hp profile
          > sb/skyblock
          > bw/bedwars
          > uhc
          > sw/skywars
          > raw - uploads raw data to pastebin
        """
        if isinstance(player, discord.Member):
            player = self.bot.db.lookup_gaming_record(player.id)[1]
            if not player:
                if re.match(r"<@!?\d{17,21}>", ctx.message.content.split()[1]):
                    await ctx.send(embed=discord.Embed(title="No mojang linked",
                                                       description="The person mentioned needs to set their mojang "
                                                                   "tag with `%mojang username`"))
                    return
                player = ctx.message.content.split()[1]
        await lib.hypixel.hypixel(ctx, player, self.bot, self.htoken, profile_type)


def setup(bot: AnsuraBot):
    gaming = Gaming(bot)
    bot.add_cog(gaming)


"""
async def lolping(_, ctx: AnsuraContext):
    "" "Pings LoL servers"" "
    embed = discord.Embed()
    lol_ips = {
        "North America (NA)": "104.160.131.3",
        "Europe (EUW)": "104.160.141.3",
        "Europe (EUNE)": "104.160.142.3",
        "Australia (OCE)": "104.160.156.1",
        "Latin America (LAN)": "104.160.136.3"
    }
    m: discord.Message = await ctx.send("Pinging...")
    c = 1
    embed.description = "Note: These pings are from Canada, yours may vary"
    for i in lol_ips.keys():
        p = await ping(lol_ips[i])
        embed.add_field(
            name=i,
            value=f"{p[0]}, {p[1]}",
            inline=False
        )
        await m.edit(content=f"Pinging {c} of 5...", embed=embed)
        c += 1
    await m.edit(content="", embed=embed)


async def owping(_, ctx: AnsuraContext):
    " ""Pings overwatch servers"" "
    embed = discord.Embed()
    ow_ips = {
        "US West": "24.105.30.129",
        "US Central": "24.105.62.129",
        "Europe 1": "185.60.112.157",
        "Europe 2": "185.60.114.159",
        "Korea": "211.234.110.1",
        "Taiwan": "203.66.81.98"
    }
    m: discord.Message = await ctx.send("Pinging...")
    c = 1
    embed.description = "Note: These pings are from Canada, yours may vary"
    for i in ow_ips.keys():
        p = await ping(ow_ips[i])
        embed.add_field(
            name=i,
            value=f"{p[0]}, {p[1]}",
            inline=False
        )
        await m.edit(content=f"Pinging {c} of 6...", embed=embed)
        c += 1
    await m.edit(content="", embed=embed)
"""
