from __future__ import annotations

import glob
import os
import re
from typing import Union, Optional, TYPE_CHECKING, List

import discord
from discord.ext import commands

import lib.hypixel
from ansura import AnsuraContext
from lib.minecraft import load_recipes, Recipe, Tag, load_tags

if TYPE_CHECKING:
    from cogs.gaming import Gaming

cog: Optional[Gaming] = None
group: Optional[commands.Group] = None
recipes: List[Recipe] = []
tags: List[Tag] = []


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
