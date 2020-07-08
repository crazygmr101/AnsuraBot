from typing import List, Dict


def descend(obj: Dict, keys: List[str]):
    temp = obj
    for k in keys:
        temp = temp[k]
    return temp

import asyncio
from typing import Any, List

import discord
from discord.ext import commands

NBSP = "͔"


def letter_emoji(a: str):
    if a.isascii() and a.isalpha() and len(a) == 1:
        a = a.upper()
    else:
        return None
    return chr(ord(a[0]) + 0x1f1a5)


def quote(st: str):
    return "\n".join(f"> {n}" for n in st.split("\n"))


def trim(st: str, length: int = 300) -> str:
    """
    Trims a string to be less than `length` characters
    :param st: the string to trim
    :param length: the length to trim to
    :return: the trimmed string
    """
    return st if len(st) < length else st[:length]


async def trash_reaction(msg: discord.Message, bot: commands.Bot, ctx: commands.Context):
    """
    Puts a "trash can" on a message, so the calling user can delete it
    :param msg: the :class:`discord.Message` the reaction gets added to
    :param bot: the :class:`discord.ext.commands.Bot`
    :param ctx: the :class:`discord.ext.commands.Context`
    :return:
    """

    def check(_reaction: discord.Reaction, _user: discord.User):
        return _user.id == ctx.author.id and _reaction.message.id == msg.id and str(_reaction) == "🗑️"

    await msg.add_reaction("🗑️")
    try:
        _, _ = await bot.wait_for("reaction_add", timeout=60.0, check=check)
    except asyncio.TimeoutError:
        await msg.clear_reactions()
    else:
        await msg.delete()


def group_list(lst: List[Any], n: int) -> List[List[Any]]:
    """
    Splits a list into sub-lists of n
    :param lst: the list
    :param n: the subgroup size
    :return: The list of lists
    """
    return [lst[i * n:(i + 1) * n] for i in range((len(lst) + n - 1) // n)]


def pages(lst: List[Any], n: int, title: str, *, fmt: str = "```%s```", sep: str = "\n") -> List[discord.Embed]:
    # noinspection GrazieInspection
    """
        Paginates a list into embeds to use with :class:disputils.BotEmbedPaginator
        :param lst: the list to paginate
        :param n: the number of elements per page
        :param title: the title of the embed
        :param fmt: a % string used to format the resulting page
        :param sep: the string to join the list elements with
        :return: a list of embeds
        """
    l: List[List[str]] = group_list([str(i) for i in lst], n)
    pgs = [sep.join(page) for page in l]
    return [
        discord.Embed(
            title=f"{title} - {i + 1}/{len(pgs)}",
            description=fmt % pg
        ) for i, pg in enumerate(pgs)
    ]


def numbered(lst: List[Any]) -> List[str]:
    """
    Returns a numbered version of a list
    """
    return [f"{i} - {a}" for i, a in enumerate(lst)]
