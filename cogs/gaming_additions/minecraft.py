from __future__ import annotations

import asyncio
import concurrent.futures
import io
import platform
import re
import socket
import subprocess
from typing import Union, Optional, TYPE_CHECKING
from lib.linq import LINQ

import aiohttp
import discord
import mcstatus
from bs4 import BeautifulSoup, Tag
from discord import Embed
from discord.ext import commands

import lib.hypixel
from ansura import AnsuraContext
from lib.utils import find_text

if TYPE_CHECKING:
    from cogs.gaming import Gaming

cog: Optional[Gaming] = None
group: Optional[commands.Group] = None


async def ping(url: str):
    ping_var = "-n" if platform.system() == "Windows" else "-c"

    def pshell(url: str):
        return str(subprocess.check_output(["ping", url, ping_var, "2"]), "utf-8")

    try:
        with concurrent.futures.ThreadPoolExecutor() as pool:
            s = await asyncio.get_event_loop().run_in_executor(pool, pshell, url)
        print(s)
        try:
            if platform.system() != "Windows":
                ar = s.strip("\n\r").split("\r\n")[-1].split(" ")[-2].split("/")
                return f"{ar[0]} ms", f"{ar[2]} ms"
            else:
                ar = s.strip("\n\r").split("\r\n")[-1].split(" ")
                return ar[-7].strip(","), ar[-4].strip(",")
        except Exception as e:
            print(e)
    except Exception as e:
        print(e)
        print(type(e))
        return "ERR", "ERR"


async def group_command(ctx: AnsuraContext):
    if not ctx.invoked_subcommand:
        return await ctx.send(f"Valid subcommands: {', '.join(cmd.name for cmd in group.walk_commands())}")


async def jping(_, ctx: AnsuraContext, url: str):
    """
    Pings a minecraft java server
    Command can be used as:
    - %jping example.com (default port)
    - %jping example.com:25562 (trailing port)
    """
    server = mcstatus.MinecraftServer.lookup(url)
    status = server.status()
    e = Embed()
    e.title = url
    e.description = re.sub("§.", "", status.description)
    e.add_field(name="Players", value=str(status.players.online) + "/" + str(status.players.max))
    e.add_field(name="Ping", value=str(status.latency))
    e.add_field(name="Version", value=status.version.name)
    e.add_field(name="Protocol", value="v" + str(status.version.protocol))
    await ctx.send(embed=e)


async def bping(_, ctx: AnsuraContext, url: str, port: int = 19132):
    """
    Pings a minecraft bedrock server
    Command can be used as:
    - %bping example.com (uses default port)
    - %bping example.com:19182 (uses port)
    - %bping example.com 19182 (uses port)
    """
    try:
        if len(url.split(":")) == 2:
            port = int(url.split(":")[1])
            url = url.split(":")[0]
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setblocking(False)
        sock.settimeout(10)
        sock.sendto(bytearray.fromhex(
            "0100000000003c6d0d00ffff00fefefefefdfdfdfd12345678"), (url, port))
        data, addr = sock.recvfrom(255)
        status = data[35::].decode("ISO-8859-1").split(";")
        e = Embed()
        e.title = url
        e.description = re.sub("[§Â].", "", status[1])
        e.add_field(name="Players", value=status[4] + "/" + status[5])
        e.add_field(name="Version", value=status[3])
        e.add_field(name="Protocol", value="v" + status[2])
        e.add_field(name="World Name", value=re.sub("§.", "", status[7]))
        e.add_field(name="Default Gamemode", value=status[8])
        await ctx.send(embed=e)
    except socket.timeout:
        await ctx.send_error(f"*Oops ):*\n Looks like the ping I made to {url}:{port} timed out. "
                             f"Either the server is down, not responding, or I was given a wrong URL or port.")
    except socket.gaierror:
        await ctx.send_error("I can't figure out how to reach that URL. ): Double check that it's correct.")
        return
    except Exception as e:
        await ctx.send_error("*Uh-oh D:*\n An error happened"
                             " while I was pinging the server.")
        print(e)


async def hypixel(_, ctx: AnsuraContext, player: Union[discord.Member, str], *,
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
        player = cog.bot.db.lookup_gaming_record(player.id)[1]
        if not player:
            if re.match(r"<@!?\d{17,21}>", ctx.message.content.split()[1]):
                await ctx.send(embed=discord.Embed(title="No mojang linked",
                                                   description="The person mentioned needs to set their mojang "
                                                               "tag with `%mojang username`"))
                return
            player = ctx.message.content.split()[1]
    await lib.hypixel.hypixel(ctx, player, cog.bot, cog.htoken, profile_type)


async def mod(_, ctx: AnsuraContext, *, _mod: str):
    hdr = {
        'User-Agent': ('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko)'
                       ' Chrome/23.0.1271.64 Safari/537.11'),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
        'Accept-Encoding': 'none',
        'Accept-Language': 'en-US,en;q=0.8'}
    buf = io.BytesIO()
    async with aiohttp.ClientSession() as sess:
        async with sess.get(
                f"https://www.curseforge.com/minecraft/mc-mods/{_mod.replace(' ', '-')}",
                headers=hdr) as resp:
            if resp.status == 404:
                return await ctx.send_error(
                    "This mod doesn't exist\n"
                    "Check your spelling or try using the acronym for the mod"
                )
            if resp.status != 200:
                return await ctx.send_error(f"Curseforge returned a {resp.status} error, and results cannot be "
                                            f"displayed.")
            buf.write(await resp.content.read())
    buf.seek(0)
    soup = BeautifulSoup(buf, features="html.parser")
    mod_name = soup.find_all("h2", class_="font-bold text-lg break-all")[0].text
    mod_version = find_text("game version", soup.find_all("span", class_="text-gray-500"),
                            get="text")
    mod_updated = LINQ(find_text("last updated", soup.find_all("span", class_="text-gray-500"),
                                 get="text").split()).skip(2).join(" ")
    mod_downloads = find_text("downloads", soup.find_all("span", class_="text-gray-500"),
                              get="text")
    mod_categories = LINQ(soup.select("div.px-1 > a[href*=mc-mods]:not([class])"))\
        .select(lambda elem: elem.attrs["href"])\
        .select(lambda text: text.split("/")[-1].replace("world-gen", "worldgen").replace("-", "/").title())\
        .join(", ")
    recent_files = LINQ(soup.find("h3",text="Recent Files").parent.parent.select("h4>a"))\
        .select(lambda elem: elem.text.replace("Minecraft", "").strip())\
        .distinct().join(", ")
    mod_files = find_text("files", soup.find_all("a"), get="href")
    mod_source = find_text("source", soup.find_all("a"), get="href")
    mod_avatar = soup.find_all(
        "div",
        class_="project-avatar project-avatar-64")[0].contents[1].contents[1]["src"]
    mod_image = soup.select_one(
        ".project-detail__content img",
    ).attrs["src"]
    mod_desc = soup.select_one(
        ".project-detail__content p",
    ).text
    await ctx.embed(title=mod_name,
                    title_url=f"https://www.curseforge.com/minecraft/mc-mods/{_mod.replace(' ', '-')}",
                    description=f"{mod_desc[:500]}\n"
                                f"**Downloads:** {mod_downloads.split(' ')[0]}\n"
                                f"**Updated:** {mod_updated}\n"
                                f"**Version:** {mod_version.split(' ')[2]}\n"
                                f"**Categories:** {mod_categories}\n"
                                f"**Recent Updates:** {recent_files}",
                    clr=discord.Color.from_rgb(103, 65, 165),
                    fields=[
                        ("Game Files", f"[Files]({mod_files})"),
                        ("Source Files", f"[Source]({mod_source})")
                    ],
                    image=mod_image,
                    thumbnail=mod_avatar)


def setup(gaming_cog: Gaming):
    global cog
    global group
    cog = gaming_cog

    group = commands.Group(name="minecraft", func=group_command)
    for i in (jping, bping, hypixel, mod):
        cmd = commands.Command(name=i.__name__, func=i)
        cmd.cog = gaming_cog
        group.add_command(
            cmd
        )
    gaming_cog.bot.add_command(group)
    gaming_cog.__cog_commands__ += (group,)
