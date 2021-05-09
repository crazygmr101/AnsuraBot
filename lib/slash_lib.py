from __future__ import annotations

from dataclasses import dataclass
from pprint import pprint
from typing import Dict, Any, Optional, List
from typing import TYPE_CHECKING

import aiohttp
import discord
from discord import Embed

if TYPE_CHECKING:
    from ansura import AnsuraBot

"""
MIT License

Copyright (c) 2020-2021 eunwoo1104
Copyright (c) 2021 crazygmr101

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE."""
# portions of this code were adapted from https://github.com/eunwoo1104/discord-py-slash-command

BASE = "https://discord.com/api/v8"


@dataclass
class SlashContext:
    channel: discord.TextChannel
    guild: discord.Guild
    author: discord.Member
    command_name: str
    options: Dict[str, Any]
    token: str
    id: int
    subcommand: Optional[str]
    cmd_signature: str
    bot: AnsuraBot
    deferred: bool = False
    responded: bool = False

    async def defer(self, hidden: bool = False):
        if self.deferred:
            raise RuntimeError("Interaction was already deferred.")
        self.deferred = True
        self.responded = True
        resp = {"type": 5}
        if hidden:
            resp["data"] = {"flags": 64}
        async with aiohttp.ClientSession() as sess:
            await sess.post(f"{BASE}/interactions/{self.id}/{self.token}/callback", json=resp)

    async def reply(self,
                    content: str = None,
                    *,
                    embeds: List[Embed] = None,
                    allowed_mentions: discord.AllowedMentions = None):
        embeds = embeds or []
        if self.deferred and not self.responded:
            return await self.edit_original(content, embeds, allowed_mentions)
        async with aiohttp.ClientSession() as sess:
            resp = await sess.post(f"{BASE}/webhooks/{self.bot.user.id}/{self.token}",
                                   json={
                                       "content": content,
                                       "embeds": [embed.to_dict() for embed in embeds],
                                       "allowed_mentions": allowed_mentions.to_dict() if allowed_mentions else {}

                                   })
            resp.raise_for_status()

    async def edit_original(self,
                            content: str = None,
                            *,
                            embeds: List[Embed] = None,
                            allowed_mentions: discord.AllowedMentions = None):
        self.responded = True
        async with aiohttp.ClientSession() as sess:
            resp = await sess.patch(f"{BASE}/webhooks/{self.bot.user.id}/{self.token}/messages/@original",
                                    json={
                                        "content": content,
                                        "embeds": [embed.to_dict() for embed in embeds] if embeds else None,
                                        "allowed_mentions": allowed_mentions.to_dict() if allowed_mentions else {}

                                    })
            resp.raise_for_status()


def process_slash(bot: AnsuraBot, payload) -> SlashContext:
    data = payload["d"]
    pprint(data)
    guild = bot.get_guild(int(data["guild_id"]))
    options = {}
    opt = data["data"]["options"]
    subcommand = None
    if len(opt) == 1 and opt[0]["type"] == 1:
        subcommand = opt[0]["name"]
        opt = opt[0]["options"]
    for o in opt:
        options[o["name"]] = o["value"]
    return SlashContext(
        channel=bot.get_channel(int(data["channel_id"])),
        guild=guild,
        author=guild.get_member(int(data["member"]["user"]["id"])),
        command_name=data["data"]["name"],
        options=options,
        token=data["token"],
        subcommand=subcommand,
        cmd_signature=data["data"]["name"] + (f".{subcommand}" if subcommand else ""),
        id=data["id"],
        bot=bot
    )
