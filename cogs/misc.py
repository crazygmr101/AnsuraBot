from typing import Union

import discord
from discord.ext import commands

from ansura import AnsuraBot, AnsuraContext


class Misc(commands.Cog):
    def __init__(self, bot: AnsuraBot):
        self.bot = bot

    @commands.command(aliases=["av"])
    async def avatar(self, ctx: AnsuraContext, user: Union[discord.Member, discord.User] = None):
        """Gets a link to a users avatar"""
        if user is None:
            user = ctx.author
        try:
            await ctx.embed(
                image=str(user.avatar_url),
                title=f"{user}'s avatar",
                description=f"[jpg]({user.avatar_url_as(format='jpeg')}) "
                            f"[png]({user.avatar_url_as(format='png')}) "
                            f"[webp]({user.avatar_url_as(format='webp')}) "
                            f"[gif]({user.avatar_url_as(format='gif')}) "
            )
        except discord.InvalidArgument:
            await ctx.embed(
                image=str(user.avatar_url),
                title=f"{user}'s avatar",
                description=f"[jpg]({user.avatar_url_as(format='jpeg')}) "
                            f"[png]({user.avatar_url_as(format='png')}) "
                            f"[webp]({user.avatar_url_as(format='webp')}) "
            )

    @commands.command()
    async def role(self, ctx: AnsuraContext, r: discord.Role):
        """
        Lists members of a role
        """

        def val_or_space(val: str):
            return "-" if val == "" else val
        online = []
        offline = []
        m: discord.Member
        if len(r.members) == 0:
            return await ctx.send_info(f"No members with role {r}")
        for m in r.members:
            if m.status == discord.Status.offline:
                offline.append(m)
            else:
                online.append(m)
        online_t = []
        for x in online:
            online_t.append(x)
            if len(online_t) > 30:
                break
        offline_t = []
        for x in offline:
            offline_t.append(x)
            if len(offline_t) > 30:
                break
        await ctx.embed(
            title=("Role: " + r.name),
            description=f"Listing {len(online_t) + len(offline_t)} of {len(r.members)}",
            fields=[
                (f"Online ({len(online_t)} of {len(online)})",
                 val_or_space(" ".join([m.mention for m in online_t]))),
                (f"Offline ({len(offline_t)} of {len(offline)})",
                 val_or_space(" ".join([m.mention for m in offline_t])))
            ],
            clr=r.colour

        )

    @role.error
    async def role_error(self, ctx: AnsuraContext, error: Exception):
        if isinstance(error, discord.ext.commands.ConversionError) or \
                isinstance(error, discord.ext.commands.BadArgument):
            await ctx.send("Oops. I can't seem to find that role. Double-check capitalization and spaces.")
        else:
            raise error

    @commands.command()
    @commands.bot_has_permissions(embed_links=True)
    @commands.has_permissions(manage_messages=True)
    async def embed(self, ctx: AnsuraContext, title: str, desc: str, ch: discord.TextChannel = None,
                    color: discord.Colour = None, id: int = None):
        """
        Creates or edits an embed
        - ch: defaults to current channel
        - color: defaults to color of caller's highest role
        - id: embed id if editing
        """
        color = ctx.author.color if color is None else color
        ch = ctx.channel if ch is None else ch
        e = discord.Embed()
        e.title = title
        e.description = desc
        e.colour = color
        e.set_author(icon_url=ctx.author.avatar_url, name=ctx.author.name)
        if id is None:
            await ch.send(embed=e)
        else:
            message = await ch.fetch_message(id)
            await message.edit(embed=e)

    @commands.command()
    async def info(self, ctx: AnsuraContext, user: Union[discord.Member, discord.User] = None):
        """Gets info about a user"""
        if user is None:
            user = ctx.author
        e = discord.Embed()
        e.title = user.name + "#" + user.discriminator
        e.set_thumbnail(url=user.avatar_url)
        e.add_field(name="ID", value=user.id)
        if type(user) == discord.Member:
            e.add_field(name="Display Name", value=user.display_name)
            e.add_field(name="Top Role", value=user.top_role.name + " (" + str(user.top_role.id) + ")")
            e.add_field(name="Created on", value=user.created_at)
            e.add_field(name="Joined on", value=user.joined_at)
            e.add_field(name="Mobile", value=str(user.is_on_mobile()))
            e.colour = user.color
        await ctx.send(embed=e)

    @commands.command()
    async def ping(self, ctx: AnsuraContext):
        await ctx.send("Pong :D " + str(int(self.bot.latency * 1000)) + "ms")


def setup(bot):
    bot.add_cog(Misc(bot))
