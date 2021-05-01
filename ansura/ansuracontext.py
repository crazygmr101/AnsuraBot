import asyncio
import io
import re
from typing import Union, List, Tuple

import discord
from discord.ext import commands


def _wrap_user(user: discord.abc.User):
    return f"**{user}** "


class AnsuraContext(commands.Context):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    INFO = 0
    OK = 1
    ERROR = 2

    async def trash_reaction(self, message: discord.Message):
        if len(message.embeds) == 0:
            return

        def check(_reaction: discord.Reaction, _user: Union[discord.User, discord.Member]):
            return all([
                _user.id == self.author.id or _user.guild_permissions.manage_messages,
                _reaction.message.id == message.id,
                str(_reaction) == "🗑️"
            ])

        await message.add_reaction("🗑️")
        await asyncio.sleep(0.5)
        try:
            _, _ = await self.bot.wait_for("reaction_add", timeout=60.0, check=check)
        except asyncio.TimeoutError:
            await message.clear_reactions()
        else:
            await message.delete()

    async def send_info(self, message: str, *, user: discord.abc.User = None,
                        title: str = None, trash: bool = False):
        if not user:
            user = self.author
        msg = await self.send(embed=discord.Embed(
            title=title,
            description=f"{_wrap_user(user) if user else ''}{message}",
            colour=discord.Colour.from_rgb(0x4a, 0x14, 0x8c)
        ))
        if trash:
            await self.trash_reaction(msg)

    async def send_ok(self, message: str, *, user: discord.abc.User = None,
                      title: str = None, trash: bool = False):
        if not user:
            user = self.author
        msg = await self.send(embed=discord.Embed(
            title=title,
            description=f"{_wrap_user(user) if user else ''}{message}",
            colour=discord.Color.green()
        ))
        if trash:
            await self.trash_reaction(msg)

    async def send_error(self, message: str, *, user: discord.abc.User = None,
                         title: str = None, trash: bool = False):
        if not user:
            user = self.author
        msg = await self.send(embed=discord.Embed(
            title=title,
            description=f"{_wrap_user(user) if user else ''}{message}",
            colour=discord.Color.red()
        ))
        if trash:
            await self.trash_reaction(msg)

    def get_color(self, clr: int):
        return [
            discord.Colour.from_rgb(0x4a, 0x14, 0x8c),
            discord.Color.green(),
            discord.Color.red()
        ][clr]

    async def embed(self, *,
                    description: str = None,
                    title: str = None,
                    title_url: str = None,
                    typ: int = INFO,
                    fields: List[Tuple[str, str]] = None,
                    thumbnail: str = None,
                    clr: discord.Colour = None,
                    image: Union[str, io.BufferedIOBase] = None,
                    footer: str = None,
                    not_inline: List[int] = []):
        if typ and clr:
            raise ValueError("typ and clr can not be both defined")
        embed = discord.Embed(
            title=title,
            description=description,
            colour=(self.get_color(typ) if not clr else clr),
            title_url=title_url
        )
        if image:
            if isinstance(image, str):
                embed.set_image(url=image)
                f = None
            else:
                image.seek(0)
                f = discord.File(image, filename="image.png")
                embed.set_image(url="attachment://image.png")
        else:
            f = None
        if footer:
            embed.set_footer(text=footer)
        if thumbnail:
            embed.set_thumbnail(url=thumbnail)
        for n, r in enumerate(fields or []):
            embed.add_field(name=r[0], value=r[1] or "None", inline=n not in not_inline)
        msg = await self.send(embed=embed, file=f)
        await self.trash_reaction(msg)

    @staticmethod
    def escape(text: str, ctx):
        role_mentions = re.findall(r"<@&\d{17,21}>", text)
        for mention in role_mentions:
            role = ctx.guild.get_role(int(mention[3:-1]))
            text = text.replace(mention, f"**@{role.name}**" if role else mention)
        user_mentions = re.findall(r"<@!?\d{17,21}>", text)
        for mention in user_mentions:
            user = ctx.guild.get_member(int(mention.replace('!', '')[2:-1]))
            text = text.replace(mention, f"**@{user.name}**" if user else mention)
        channel_mentions = re.findall(r"<#\d{17,21}>", text)
        for mention in channel_mentions:
            channel = ctx.guild.get_channel(int(mention[2:-1]))
            text = text.replace(mention, f"**#{channel.name}**" if channel else mention)
        return text

    @staticmethod
    def bold(text: str):
        return f"**{text}**"

    @staticmethod
    def italic(text: str):
        return f"*{text}*"
