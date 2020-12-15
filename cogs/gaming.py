import asyncio
import concurrent.futures
import io
import os
import platform
import re
import socket
import subprocess
from typing import Union

import aiohttp
import discord
import mcstatus
from bs4 import BeautifulSoup
from discord import Embed
from discord.ext import commands

import lib.hypixel
from ansura import AnsuraBot, AnsuraContext
from lib.utils import find_text


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


class Gaming(commands.Cog):
    def __init__(self, bot: AnsuraBot):
        self.bot = bot
        self.htoken = os.getenv("HYPIXEL")

    @commands.command()
    async def jping(self, ctx: AnsuraContext, url: str):
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

    @commands.command()
    async def bping(self, ctx: AnsuraContext, url: str, port: int = 19132):
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
        except socket.timeout as t:
            await ctx.send_error("*Oops ):*\n Looks like the ping I made to " + url + ":" + str(port) + " timed out. "
                                                                                                        "Either the server is down, not responding, or I was given a wrong URL or port.")
        except socket.gaierror as e:
            await ctx.send_error("I can't figure out how to reach that URL. ): Double check that it's correct.")
            return
        except Exception as e:
            await ctx.send_error("*Uh-oh D:*\n An error happened"
                                 " while I was pinging the server.")
            print(e)

    @commands.command()
    async def lolping(self, ctx: AnsuraContext):
        """Pings LoL servers"""
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

    @commands.command()
    async def owping(self, ctx: AnsuraContext):
        """Pings overwatch servers"""
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

    @commands.command(aliases=["hp"])
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
                await ctx.send(embed=discord.Embed(title="No mojang linked",
                                                   description="The person mentioned needs to set their mojang "
                                                               "tag with `%mojang username`"))
                return
        await lib.hypixel.hypixel(ctx, player, self.bot, self.htoken, profile_type)

    @commands.command()
    async def mod(self, ctx: AnsuraContext, mod: str):
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
                    f"https://www.curseforge.com/minecraft/mc-mods/{mod.replace(' ', '-')}",
                    headers=hdr) as resp:
                if resp.status == 404:
                    return await ctx.send_error(
                        "This mod doesn't exist\n"
                        "Check your spelling or try using the acronym for the mod"
                    )
                buf.write(await resp.content.read())
        buf.seek(0)
        soup = BeautifulSoup(buf, features="html.parser")
        mod_name = soup.find_all("h2", class_="font-bold text-lg break-all")[0].text
        mod_version = find_text("game version", soup.find_all("span", class_="text-gray-500"),
                                get="text")
        mod_updated = find_text("last updated", soup.find_all("span", class_="text-gray-500"),
                                get="text")
        mod_downloads = find_text("downloads", soup.find_all("span", class_="text-gray-500"),
                                  get="text")
        mod_files = find_text("files", soup.find_all("a"), get="href")
        mod_source = find_text("source", soup.find_all("a"), get="href")
        mod_avatar = soup.find_all(
            "div",
            class_="project-avatar project-avatar-64")[0].contents[1].contents[1]["src"]
        await ctx.embed(title=mod_name,
                        description=f"**{mod_downloads}**" + "\n" +
                                    f"**{mod_updated}**" + "\n" +
                                    f"**{mod_version}**",
                        clr=discord.Color.from_rgb(103, 65, 165),
                        fields=[
                            ("Game Files", f"[Files]({mod_files})"),
                            ("Source Files", f"[Source]({mod_source})")
                        ],
                        thumbnail=mod_avatar)


def setup(bot):
    bot.add_cog(Gaming(bot))
