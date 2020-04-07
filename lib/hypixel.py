from typing import Dict

import aiohttp
import discord
import pytz
from discord.ext import commands
from datetime import datetime, date
import discord.utils


async def hypixel(ctx: commands.Context, player: str, bot: commands.Bot, token, key: str = None):
    with ctx.typing():
        async with aiohttp.ClientSession() as sess:
            async with sess.get(f"https://api.hypixel.net/player?key={token}&name={player}") as resp:
                status = resp.status
                data = await resp.json()
    if data["player"] is None:
        await ctx.send("That player doesn't seem to exist on hypixel.")
        return

    player = data["player"]
    player_name = player["playername"]

    e = _mk_embed(player_name)

    if key is None:
        e.add_field(name="Previous Names",
                    value=_("\n".join(player["knownAliases"])))
        if "mcVersionRp" in player.keys():
            e.add_field(name="Minecraft Version",
                        value=_(player["mcVersionRp"]))
            # .strftime("%x %X")
        tz = pytz.timezone("America/Winnipeg")
        time = tz.localize(datetime.fromtimestamp(player["lastLogout"]/1000))
        player_tz = bot.db.lookup_timezone(ctx.author.id)[1]
        timel = time.astimezone(pytz.timezone(player_tz)) if player_tz else None
        #
        e.add_field(name="Last Seen",
                    value=f"{time.strftime('%x %X')} (Server)\n{timel.strftime('%x %X') if timel else 'N/A'} (Local)"
                        if player["lastLogout"] > player["lastLogin"] else "Now")
        e.add_field(name="Hypixel Level",
                    value=f"{_get_level(player['networkExp'])}")

    await ctx.send(embed=e)


def _(text: str, *, as_needed: bool = False, ignore_links: bool = True):
    return discord.utils.escape_markdown(text, as_needed=as_needed, ignore_links=ignore_links)


def _get_level(exp: int):
    lvl = 1
    cnt = 0
    while exp >= 0:
        need = 10000 + 2500 * (lvl-1)
        exp -= need
        if exp < 0:
            return lvl
        lvl += 1
    return -1  # this should never happen


def _mk_embed(name: str, game: str = None) -> discord.Embed:
    e = discord.Embed()
    e.title = f"{name}'s {game.title if game else 'Hypixel'} Profile"
    e.set_thumbnail(url=f"https://minotar.net/helm/{name}/128.png")
    return e