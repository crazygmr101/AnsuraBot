import os

from discord.ext import commands
from cogs.gaming_additions import minecraft
from ansura import AnsuraBot


class Gaming(commands.Cog):
    def __init__(self, bot: AnsuraBot):
        self.bot = bot
        self.htoken = os.getenv("HYPIXEL")


def setup(bot):
    gaming = Gaming(bot)
    bot.add_cog(gaming)
    minecraft.setup(gaming)


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