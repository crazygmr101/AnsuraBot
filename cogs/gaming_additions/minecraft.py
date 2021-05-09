from __future__ import annotations

import asyncio
import concurrent.futures
import glob
import io
import os
import platform
import re
import socket
import subprocess
from typing import Union, Optional, TYPE_CHECKING, List

import aiohttp
import discord
import mcstatus
from bs4 import BeautifulSoup
from discord import Embed
from discord.ext import commands

import lib.hypixel
from ansura import AnsuraContext
from lib.linq import LINQ
from lib.minecraft import load_recipes, Recipe, ShapedCraftingRecipe, StonecuttingRecipe, BlastingRecipe, \
    SmeltingRecipe, SmithingRecipe, ShapelessCraftingRecipe, SmokingRecipe, BlockDrop, ChestLoot, EntityDrop, Barter, \
    CatGift, HeroGift, FishingLoot, Tag, load_tags
from lib.utils import find_text

if TYPE_CHECKING:
    from cogs.gaming import Gaming

cog: Optional[Gaming] = None
group: Optional[commands.Group] = None
recipes: List[Recipe] = []
tags: List[Tag] = []


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




async def info(_, ctx: AnsuraContext, *, i: str):
    found_recipes = 0
    found_tags = []
    for rec in recipes:
        if rec.result.replace("_", "").lower() == i.replace(" ", "").replace("_", "").lower():
            found_recipes += 1
            i = rec.result
    for tag in tags:
        for item in tag.items:
            if item.replace("_", "").lower() == i.replace(" ", "").replace("_", "").lower():
                found_tags.append(tag.name)
                break
    await ctx.send(f"**__`{i}`__**\n" +
                   (f"> {found_recipes} {ctx.inflect.plural('recipe', found_recipes)} found, "
                    f"do `{ctx.prefix}minecraft recipe {i}` to view\n" if found_recipes else "") +
                   (f"> {ctx.inflect.plural('Tag', len(found_tags))}: "
                    + LINQ(found_tags).distinct().format("`%s`").join(" ") if found_tags else ""))


async def setup(gaming_cog: Gaming):
    global cog
    global group
    global recipes
    global tags
    cog = gaming_cog

    # initialize minecraft stuff
    if not os.path.isdir("data"):
        os.mkdir("data")
    if not os.path.isdir("data/minecraft"):
        os.mkdir("data/minecraft")
    if not os.path.isdir("data/minecraft/recipes"):
        os.mkdir("data/minecraft/recipes")
    if not os.path.isdir("data/minecraft/blocks"):
        os.mkdir("data/minecraft/blocks")
    if not os.path.isdir("data/minecraft/chests"):
        os.mkdir("data/minecraft/chests")
    if not os.path.isdir("data/minecraft/entities"):
        os.mkdir("data/minecraft/entities")
    if not os.path.isdir("data/minecraft/gameplay"):
        os.mkdir("data/minecraft/gameplay")

    recipes = load_recipes(glob.glob("data/minecraft/recipes/**/*.json", recursive=True)) + \
              load_recipes(glob.glob("data/minecraft/loot_tables/**/*.json", recursive=True))
    tags = load_tags(glob.glob("data/tags/**/*json"))

    group = commands.Group(name="minecraft", func=group_command)
    for i in (jping, bping, hypixel, mod, recipe, taginfo, info):
        cmd = commands.Command(name=i.__name__, func=i)
        cmd.cog = gaming_cog
        group.add_command(
            cmd
        )
    gaming_cog.bot.add_command(group)
    gaming_cog.__cog_commands__ += (group,)