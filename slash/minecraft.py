import glob
import io
import itertools
import os
import re
import socket

import aiohttp
import discord
from bs4 import BeautifulSoup
from discord.ext import commands
from mcstatus import MinecraftServer

from ansura import AnsuraBot
from lib.linq import LINQ
from lib.minecraft import load_recipes, load_tags, ShapedCraftingRecipe, StonecuttingRecipe, SmokingRecipe, \
    BlastingRecipe, SmeltingRecipe, SmithingRecipe, ShapelessCraftingRecipe, BlockDrop, ChestLoot, EntityDrop, Barter, \
    CatGift, HeroGift, FishingLoot
from lib.slash_lib import SlashContext
from lib.utils import find_text, ping
import lib.hypixel


class MinecraftSlash(commands.Cog):
    def __init__(self, bot: AnsuraBot):
        # initialize minecraft stuff
        if not os.path.isdir("data"):
            os.mkdir("data")
        if not os.path.isdir("data/minecraft"):
            os.mkdir("data/minecraft")
        if not os.path.isdir("data/minecraft/recipes"):
            os.mkdir("data/minecraft/recipes")
        if not os.path.isdir("data/minecraft/loot_tables"):
            os.mkdir("data/minecraft/loot_tables")
        if not os.path.isdir("data/minecraft/loot_tables/blocks"):
            os.mkdir("data/minecraft/loot_tables/blocks")
        if not os.path.isdir("data/minecraft/loot_tables/chests"):
            os.mkdir("data/minecraft/loot_tables/chests")
        if not os.path.isdir("data/minecraft/loot_tables/entities"):
            os.mkdir("data/minecraft/loot_tables/entities")
        if not os.path.isdir("data/minecraft/loot_tables/gameplay"):
            os.mkdir("data/minecraft/loot_tables/gameplay")

        self.recipes = load_recipes(glob.glob("data/minecraft/recipes/**/*.json", recursive=True)) + \
                       load_recipes(glob.glob("data/minecraft/loot_tables/**/*.json", recursive=True))
        self.tags = load_tags(glob.glob("data/minecraft/tags/**/*.json", recursive=True))
        self.bot = bot
        self.htoken = os.getenv("HYPIXEL")
        self.bot.slashes["minecraft.mod"] = self._mod
        self.bot.slashes["minecraft.recipe"] = self._recipe
        self.bot.slashes["minecraft.tag-info"] = self._tag_info
        self.bot.slashes["minecraft.info"] = self._info
        self.bot.slashes["minecraft.ping"] = self._ping
        self.bot.slashes["minecraft.hypixel"] = self._hypixel
        self.bot.slashes["minecraft.color-codes"] = self._color_codes
        self.bot.slashes["minecraft.color-code-pattern"] = self._cc_pattern

    async def _cc_pattern(self, ctx: SlashContext):
        await ctx.defer(True)
        sep = "&" if ctx.options["character"] == "java" else "§"
        pattern = ctx.options["pattern"]
        message = ctx.options["message"]
        builder = ''
        cycle = itertools.cycle(pattern.split())
        for char in message:
            if char.isspace():
                builder += char
            else:
                for formatting_code in cycle.__next__():
                    builder += f"{sep}{formatting_code}"
                builder += char
        await ctx.reply(f"```{builder}```{'**Over 256 characters' if len(builder) > 256 else ''}")

    async def _hypixel(self, ctx: SlashContext):
        await lib.hypixel.hypixel(ctx, ctx.options["player-name"],
                                  self.bot, self.htoken, ctx.options["profile-type"])

    async def _ping(self, ctx: SlashContext):
        await ctx.defer()
        port = ctx.options.get("port", 25565 if ctx.options["type"] == "java" else 19132)
        url = f"{ctx.options['url']}:{port}"
        if ctx.options.get("type", "java") == "java":
            server = MinecraftServer.lookup(ctx.options["url"])
            status = server.status()
            description = re.sub('§.', '', status.description['text'] \
                if isinstance(status.description, dict) else status.description) # noqa
            await ctx.reply(f"**{url}**\n"
                            f"> {description}\n"
                            f"> {status.players.online}/{status.players.max}   {status.latency}ms\n"
                            f"> Minecraft v{status.version.name}   Protocol v{status.version.protocol}")
        else:
            try:
                latency = await ping(url)
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.setblocking(False)
                sock.settimeout(10)
                sock.sendto(bytearray.fromhex(
                    "0100000000003c6d0d00ffff00fefefefefdfdfdfd12345678"), (url, port))
                data, addr = sock.recvfrom(255)
                status = data[35::].decode("ISO-8859-1").split(";")
                await ctx.reply(f"**{url}**\n"
                                f"> {re.sub('§.', '', status[7])} - {status[8]}"
                                f"> {re.sub('[§Â].', '', status[1])}\n"
                                f"> {status[4]}/{status[3]}   "
                                f"{(str(round((latency[0] + latency[1]) / 2)) + 'ms') if latency[0] != 'ERR' else ''}\n"
                                f"> Minecraft v{status[3]}   Protocol v{status[2]}\n")
            except socket.timeout:
                await ctx.reply(f"*Oops ):*\n Looks like the ping I made to {url} timed out. "
                                f"Either the server is down, not responding, or I was given a wrong URL or port.")
            except socket.gaierror:
                await ctx.reply("I can't figure out how to reach that URL. ): Double check that it's correct.")
                return
            except Exception as e:
                await ctx.reply("An error happened while I was pinging the server.")
                print(e)

    async def _mod(self, ctx: SlashContext):
        await ctx.defer()
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
                    f"https://www.curseforge.com/minecraft/mc-mods/{ctx.options['mod-name'].replace(' ', '-')}",
                    headers=hdr) as resp:
                if resp.status == 404:
                    return await ctx.reply("This mod doesn't exist\n"
                                           "Check your spelling or try using the acronym for the mod")
                if resp.status != 200:
                    return await ctx.reply(f"Curseforge returned a {resp.status} error, and results cannot be "
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
        mod_categories = LINQ(soup.select("div.px-1 > a[href*=mc-mods]:not([class])")) \
            .select(lambda elem: elem.attrs["href"]) \
            .select(lambda text: text.split("/")[-1].replace("world-gen", "worldgen").replace("-", "/").title()) \
            .join(", ")
        recent_files = LINQ(soup.find("h3", text="Recent Files").parent.parent.select("h4>a")) \
            .select(lambda elem: elem.text.replace("Minecraft", "").strip()) \
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
        await ctx.reply(
            embeds=[
                discord.Embed(
                    title=mod_name,
                    url=f"https://www.curseforge.com/minecraft/mc-mods/{ctx.options['mod-name'].replace(' ', '-')}",
                    description=f"{mod_desc[:500]}\n"
                                f"**Downloads:** {mod_downloads.split(' ')[0]}\n"
                                f"**Updated:** {mod_updated}\n"
                                f"**Version:** {mod_version.split(' ')[2]}\n"
                                f"**Categories:** {mod_categories}\n"
                                f"**Recent Updates:** {recent_files}",
                    color=discord.Color.from_rgb(103, 65, 165),
                )
                    .add_field(name="Game Files",
                               value=f"[Files]({mod_files})")  # noqa what the fuck is that autoformat
                    .add_field(name="Source Files", value=f"[Source]({mod_source})")
                    .set_image(url=mod_image)
                    .set_thumbnail(url=mod_avatar)
            ]
        )

    async def _recipe(self, ctx: SlashContext):
        await ctx.defer()
        found = []
        drops = []
        found_in = []
        result = ctx.options["item"]
        for rec in self.recipes:
            if rec.result.replace("_", "").lower() == result.replace(" ", "").replace("_", "").lower():
                found.append(rec)
        if not found:
            return await ctx.reply(f"No recipes for {result} found.")
        fr_result = found[0].result.replace('_', ' ').title()
        st = f"Recipe for **{fr_result}**\n"
        for rec in found:
            if isinstance(rec, ShapedCraftingRecipe):
                pattern = "\n> ".join(rec.pattern)
                ingredients = "\n> ".join(f"**{k}**: {v}" for k, v in rec.keys.items())
                res_str = f"> Makes **{rec.result_count}**\n" if rec.result_count != 1 else ""
                st += f"__**Crafting table**__\n> ```\n> {pattern}```" \
                      f"{ingredients}\n" \
                      f"{res_str}"
            elif isinstance(rec, StonecuttingRecipe):
                st += f"__**Stonecutter**__\n> **{rec.ingredient}** → **{fr_result}** ×{rec.result_count}\n"
            elif isinstance(rec, SmokingRecipe):
                st += f"__**Smoker**__\n> **{rec.ingredient}** → **{fr_result}**\n" \
                      f"> Gives **{rec.experience}** XP and takes **{rec.cooking_time}** ticks\n"
            elif isinstance(rec, BlastingRecipe):
                st += f"__**Blast Furnace**__\n> **{rec.ingredient}** → **{fr_result}**\n" \
                      f"> Gives **{rec.experience}** XP and takes **{rec.cooking_time}** ticks\n"
            elif isinstance(rec, SmeltingRecipe):
                st += f"__**Furnace**__\n> **{rec.ingredient}** → **{fr_result}**\n" \
                      f"> Gives **{rec.experience}** XP and takes **{rec.cooking_time}** ticks\n"
            elif isinstance(rec, SmithingRecipe):
                st += f"__**Smithing**__\n> **{rec.base}** + **{rec.addition}** → **{fr_result}**\n"
            elif isinstance(rec, ShapelessCraftingRecipe):
                ingredients = " + ".join(f"**{i[0]}** × **{i[1]}**" for i in rec.ingredients)
                count = f" × **{rec.result_count}**" if rec.result_count != 1 else ""
                st += f"__**Shapeless crafting**__\n> {ingredients} → **{fr_result}**{count}\n"
            elif isinstance(rec, BlockDrop):
                silk = " *Silk*" if rec.silk else ""
                if rec.fortune_chances == [1]:
                    fortune = " *Fortune*"
                elif not rec.fortune_chances:
                    fortune = ""
                else:
                    fortune = (" (" +
                               " ".join(
                                   f"F{n}: **{int(rec.fortune_chances[n] * 100)}**%" for n in [0, 1, 2, 3]) + ")")
                drops.append(f"{rec.block}{silk}{fortune}")
            elif isinstance(rec, ChestLoot):
                found_in.append(f"{rec.location.replace('_', ' ').title()}")
            elif isinstance(rec, EntityDrop):
                drops.append(f"{rec.entity.replace('_', ' ').title()}")
            elif isinstance(rec, Barter):
                st += "__**Bartering**__\n"
            elif isinstance(rec, CatGift):
                st += "__**Cat Morning Gift**__\n"
            elif isinstance(rec, HeroGift):
                drops.append(f"{rec.entity} *Hero of the village*")
            elif isinstance(rec, FishingLoot):
                drops.append(f"Fishing *{rec.pool}*")

        if drops:
            st += "__**Drops from**__\n" + "\n".join(f"> {drop}" for drop in drops) + "\n"

        if found_in:
            st += "__**Found in**__\n" + "\n".join(f"> {loc}" for loc in found_in) + "\n"

        await ctx.reply(st)

    async def _tag_info(self, ctx: SlashContext):
        await ctx.defer()

        def _get(tag_name: str):
            for _t in self.tags:
                if _t.name == tag_name:
                    return _t
            return None

        for _tag in self.tags:
            if _tag.name.replace("_", "").lower() == \
                    ctx.options['tag'].replace("_", "").replace(" ", "").replace("minecraft:", "").lower():
                return await ctx.reply(f"__**Items in `{_tag.name}`**__\n" +
                                       LINQ(_tag.items)
                                       .select(
                                           lambda t:
                                           f"> `{t}`: " + ", ".join(f"`{child}`" for child in _get(t[1:]).items)
                                           if "#" in t else f"> `{t}`")
                                       .join("\n"))
        await ctx.reply(f"No tag matching `{ctx.options['tag']}` found")

    async def _info(self, ctx: SlashContext):
        await ctx.defer()
        found_recipes = 0
        found_tags = []
        for rec in self.recipes:
            if rec.result.replace("_", "").lower() == ctx.options["item"].replace(" ", "").replace("_", "").lower():
                found_recipes += 1
                ctx.options["item"] = rec.result
        for tag in self.tags:
            for item in tag.items:
                if item.replace("_", "").lower() == ctx.options["item"].replace(" ", "").replace("_", "").lower():
                    found_tags.append(tag.name)
                    break
        await ctx.reply(f"**__`{ctx.options['item']}`__**\n" +
                        (f"> {found_recipes} {self.bot.inflect.plural('recipe', found_recipes)} found, "
                         f"do `/minecraft recipe ` to view\n" if found_recipes else "") +
                        (f"> {self.bot.inflect.plural('Tag', len(found_tags))}: "
                         + LINQ(found_tags).distinct().format("`%s`").join(" ") if found_tags else ""))

    @commands.command()
    async def _color_codes(self, ctx: SlashContext):
        await ctx.defer(True)
        url = "https://cdn.discordapp.com/attachments/799034707726827561/841481558040248360/200px-Minecraft_Formatting.gif" # noqa

        await ctx.reply(embeds=[discord.Embed(
            title="Minecraft Color Codes",
            url="https://minecraft.gamepedia.com/Formatting_codes",
            description=""
                        "To type `§`:\n"
                        "- Windows: `Alt`+`21`, or `Alt`+`0167`, using the numpad\n"
                        "- Mac (US): `Option`+`6` (`5` for US Extended)\n"
                        "- Mac (Other): `Option`+`00a7`\n"
                        "- Linux: `Compose` `s` `o`\n\n"
                        "[Color code list](https://minecraft.gamepedia.com/Formatting_codes#Color_codes)"
        ).set_image(url=url)])


def setup(bot):
    bot.add_cog(MinecraftSlash(bot))
