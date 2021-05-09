import asyncio
import glob
import os
from pprint import pprint
from typing import List

import discord
import json
from discord.ext import commands

from ansura import AnsuraBot
from lib.minecraft import Recipe, Tag, load_recipes, load_tags, ShapedCraftingRecipe, StonecuttingRecipe, SmokingRecipe, \
    BlastingRecipe, SmeltingRecipe, SmithingRecipe, ShapelessCraftingRecipe, BlockDrop, ChestLoot, EntityDrop, Barter, \
    CatGift, HeroGift, FishingLoot
from lib.slash_lib import SlashContext


class MinecraftSlash(commands.Cog):
    def __init__(self, bot: AnsuraBot):
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

        self.recipes = load_recipes(glob.glob("data/minecraft/recipes/**/*.json", recursive=True)) + \
                  load_recipes(glob.glob("data/minecraft/loot_tables/**/*.json", recursive=True))
        self.tags = load_tags(glob.glob("data/tags/**/*json"))
        self.bot = bot
        self.bot.slashes["minecraft.mod"] = self._mod
        self.bot.slashes["minecraft.recipe"] = self._recipe

    async def _mod(self, ctx: SlashContext):
        await ctx.defer()
        await asyncio.sleep(4)
        await ctx.reply("hello")
        await ctx.reply("hello v2")

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
                               " ".join(f"F{n}: **{int(rec.fortune_chances[n] * 100)}**%" for n in [0, 1, 2, 3]) + ")")
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

def setup(bot):
    bot.add_cog(MinecraftSlash(bot))