import json
import os
from typing import Dict
import pastebin
import aiohttp
import discord
import pytz
from discord.ext import commands
from datetime import datetime, date
import discord.utils
import asyncio
import urllib.parse
import urllib.request

async def hypixel(ctx: commands.Context, player: str, bot: commands.Bot, token, key: str = None):
    with ctx.typing():
        data = await _get(player, token)
    if data["player"] is None:
        await ctx.send("That player doesn't seem to exist on hypixel.")
        return

    player = data["player"]
    player_name = player["playername"]

    e = _mk_embed(player_name, key)
    key = key.lower() if key else key

    if key is None:
        e.add_field(name="Previous Names",
                    value=_("\n".join(player["knownAliases"])))
        if "mcVersionRp" in player.keys():
            e.add_field(name="Minecraft Version",
                        value=_(player["mcVersionRp"]))
            # .strftime("%x %X")
        tz = pytz.timezone("America/Winnipeg")
        time = tz.localize(datetime.fromtimestamp(player["lastLogout"] / 1000))
        player_tz = bot.db.lookup_timezone(ctx.author.id)[1]
        timel = time.astimezone(pytz.timezone(player_tz)) if player_tz else None
        #
        e.add_field(name="Last Seen",
                    value=f"{time.strftime('%x %X')} (Server)\n{timel.strftime('%x %X') if timel else 'N/A'} (Local)"
                    if player["lastLogout"] > player["lastLogin"] else "Now")
        e.add_field(name="Hypixel Level",
                    value=f"{_get_level(player['networkExp'])}")

    elif key in ["bedwars", "bw"]:
        player = player["stats"]["Bedwars"]
        prefixes = {
            "2v2": "eight_two",
            "3v3v3v3": "four_three",
            "4v4v4v4": "four_four",
            "4v4": "two_four"
        }
        s = "```"
        s += f"Level {_get_level(player['Experience'])}\n"
        for _prefix in prefixes:
            w = player[f"{prefixes[_prefix]}_wins_bedwars"]
            l = player[f"{prefixes[_prefix]}_losses_bedwars"]
            fk = player[f"{prefixes[_prefix]}_final_kills_bedwars"]
            k = player[f"{prefixes[_prefix]}_kills_bedwars"]
            d = player[f"{prefixes[_prefix]}_deaths_bedwars"]
            s += _prefix.center(13, "=") + "\n"
            s += f"{w}/{w + l} Won\n"
            s += f"{k}:{d} KDR ({round(k / d, 2)}\n"
            s += f"({fk} Final Kills)\n"

        e.description = s + "```"

    elif key in ["skywars", "sw"]:
        player = player["stats"]["SkyWars"]
        prefixes = {
            "Solo": "solo",
            "Solo Normal": "solo_normal",
            "Solo Insane": "solo_insane",
            "Teams": "team",
            "Teams Normal": "teams_normal",
            "Teams Insane": "teams_insane"
        }
        results = []
        for _prefix in prefixes:
            s = [_prefix]
            vk = player.get(f'void_kills_{prefixes[_prefix]}', "-")
            w = player.get(f'wins_{prefixes[_prefix]}', "-")
            g = player.get(f'games_{prefixes[_prefix]}', "-")
            k = player.get(f'kills_{prefixes[_prefix]}', "-")
            d = player.get(f'deaths_{prefixes[_prefix]}', "-")
            s.append(f"{w}/{g} Won".ljust(21, " "))
            s.append(f"{k}:{d} KDR ({round(k / d, 2) if '-' not in [k, d] else ''})".ljust(21, " "))
            s.append(f"{vk} Void kills".ljust(21, " "))
            results.append(s)

        e.description = ""
        for r in results:
            e.add_field(name=r[0],
                        value="```" + "\n".join(r[1:4]) + "```")

    elif key in ["uhc"]:
        player = player["stats"]["UHC"]
        e.description = "```" \
                        f"{player['kills']} K\n" \
                        f"{player['deaths']} D" \
                        "```"

    elif key in ["raw"]:
        e.description = await asyncio.get_event_loop().run_in_executor(None, _raw, data)

    await ctx.send(embed=e)


def _raw(data):
    dstr = json.dumps(data, indent=2)
    url = "http://pastebin.com/api/api_post.php"
    values = {'api_option': 'paste',
              'api_dev_key': os.getenv("PASTEBIN"),
              'api_paste_code': dstr,
              'api_paste_private': '0',
              'api_paste_name': 'Hypixel Profile',
              'api_paste_expire_date': 'N',
              'api_paste_format': 'javascript'
            }

    data = urllib.parse.urlencode(values)
    data = data.encode('utf-8')  # data should be bytes
    req = urllib.request.Request(url, data)
    with urllib.request.urlopen(req) as response:
        resp = response.read()
    return str(resp, "utf-8")


async def _get(player: str, token: str):
    async with aiohttp.ClientSession() as sess:
        async with sess.get(f"https://api.hypixel.net/player?key={token}&name={player}") as resp:
            status = resp.status
            data = await resp.json()
    return data


def _(text: str, *, as_needed: bool = False, ignore_links: bool = True):
    return discord.utils.escape_markdown(text, as_needed=as_needed, ignore_links=ignore_links)


def _get_level(exp: int):
    lvl = 1
    cnt = 0
    while exp >= 0:
        need = 10000 + 2500 * (lvl - 1)
        exp -= need
        if exp < 0:
            return lvl
        lvl += 1
    return -1  # this should never happen


def _sub_one(string, repl: Dict[str, str]):
    if (string.lower() if string else None) in repl.keys():
        return repl[string]
    return string


def _mk_embed(name: str, game: str = None) -> discord.Embed:
    e = discord.Embed()
    game = _sub_one(game, {
        "bw": "Bedwars",
        None: "Hypixel",
        "sw": "Skywars"
    })
    e.title = f"{name}'s {game.title()} Profile"
    if game != "Hypixel":
        e.set_footer(icon_url=f"https://minotar.net/helm/{name}/128.png", text="")
    else:
        e.set_thumbnail(url=f"https://minotar.net/helm/{name}/128.png")
    return e