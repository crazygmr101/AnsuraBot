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
                    allowed_mentions: discord.AllowedMentions = None,
                    hidden: bool = False):
        embeds = embeds or []
        if self.deferred and not self.responded:
            return await self.edit_original(content, embeds=embeds, allowed_mentions=allowed_mentions, hidden=hidden)
        async with aiohttp.ClientSession() as sess:
            r = {
                "content": content,
                "embeds": [embed.to_dict() for embed in embeds],
                "allowed_mentions": allowed_mentions.to_dict() if allowed_mentions else {}
            }
            if hidden:
                r["data"] = {"flags": 64}
            resp = await sess.post(f"{BASE}/webhooks/{self.bot.user.id}/{self.token}",
                                   json=r)
            resp.raise_for_status()
            resp.close()

    async def edit_original(self,
                            content: str = None,
                            *,
                            embeds: List[Embed] = None,
                            allowed_mentions: discord.AllowedMentions = None,
                            hidden: bool = False):
        self.responded = True
        async with aiohttp.ClientSession() as sess:
            r = {
                "content": content,
                "embeds": [embed.to_dict() for embed in embeds],
                "allowed_mentions": allowed_mentions.to_dict() if allowed_mentions else {}
            }
            if hidden:
                r["data"] = {"flags": 64}
            else:
                r["data"] = {"flags": 0}
            resp = await sess.patch(f"{BASE}/webhooks/{self.bot.user.id}/{self.token}/messages/@original",
                                    json=r)
            resp.raise_for_status()
            resp.close()


def process_slash(bot: AnsuraBot, payload) -> SlashContext:
    data = payload["d"]
    guild = bot.get_guild(int(data["guild_id"]))
    options = {}
    opt = data["data"]["options"]
    subcommand = None
    if len(opt) == 1 and opt[0]["type"] == 1:
        subcommand = opt[0]["name"]
        opt = opt[0].get("options", {})
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
