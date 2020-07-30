from typing import Dict, List, Optional, Union

import discord
import discord.errors
from discord import Guild, TextChannel
from discord.ext import commands
from ruamel.yaml import YAML
from disputils import BotEmbedPaginator
from lib.utils import pages

class Crosschat(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.colors = {}
        self.bot = bot
        self._cd = commands.CooldownMapping.from_cooldown(3, 30, commands.BucketType.user)
        self.channels: Optional[Dict[str, int]] = None
        self.banned: Optional[List[int]] = None
        self.exempt: Optional[List[int]] = None

    @commands.command()
    @commands.is_owner()
    async def xcreload(self, ctx: commands.Context):
        self._reload()
        await ctx.send("Reloaded")

    def _reload(self):
        with open("xchat.yaml") as fp:
            config = YAML().load(fp)
        self.channels = config["channels"]
        self.banned = config["banned"]
        self.exempt = config["exempt"]
        for i in self.channels:
            color = int(i) // 64 % (14 ** 3) + 0x222
            rd = color >> 8
            gr = (color & 0x0f0) >> 4
            bl = (color & 0xf)
            self.colors[int(i)] = discord.Colour.from_rgb(rd * 0x11, gr * 0x11, bl * 0x11)

    @commands.command()
    @commands.is_owner()
    async def xcbans(self, ctx: commands.Context):
        await BotEmbedPaginator(ctx,
                                pages(
                                    [f"{self.bot.get_user(x)} - {x}" for x in self.banned],
                                    10, "Crosschat bans"
                                )).run()

    @commands.command()
    @commands.is_owner()
    async def xcservers(self, ctx: commands.Context):
        await BotEmbedPaginator(ctx,
                                pages(
                                    [f"{self.bot.get_guild(int(x))} ({x}) - "
                                     f"{self.bot.get_channel(c)} ({c})" for x, c in self.channels.items()],
                                    10, "Crosschat servers"
                                )).run()

    @commands.command()
    @commands.check_any(
        commands.has_permissions(administrator=True),
        commands.has_guild_permissions(administrator=True)
    )
    async def crosschat(self, ctx: commands.Context, arg: Union[discord.TextChannel, str] = None):
        if not arg:
            if ctx.guild.id in self.channels.keys():
                await ctx.send(f"Crosschat is set to <#{self.channels[ctx.guild.id]}>. Do "
                               f"`%crosschat #channel` to change this or `%crosschat clear` to "
                               f"turn off crosschat")
            else:
                await ctx.send(f"Crosschat is not enabled on this server. Do "
                               f"`%crosschat #channel` to change this.")
            return
        if isinstance(arg, discord.TextChannel):
            self.channels[ctx.guild.id] = arg.id
            await ctx.send(f"Crosschat is set to <#{self.channels[ctx.guild.id]}>. Do "
                           f"`%crosschat #channel` to change this or `%crosschat clear` to "
                           f"turn off crosschat")
        elif arg == "clear":
            del self.channels[ctx.guild.id]
            await ctx.send(f"Crosschat channel cleared. Do `%crosschat #channel` to change this.")
        else:
            return
        with open("xchat.yaml", "w") as fp:
            YAML().dump({"banned": self.banned, "channels": self.channels, "exempt": self.exempt}, fp)
        for i in self.channels:
            color = int(i) // 64 % (14 ** 3) + 0x222
            rd = color >> 8
            gr = (color & 0x0f0) >> 4
            bl = (color & 0xf)
            self.colors[int(i)] = discord.Colour.from_rgb(rd * 0x11, gr * 0x11, bl * 0x11)


    @commands.command()
    @commands.is_owner()
    async def xcban(self, ctx: commands.Context, member: Union[discord.Member, int]):
        if isinstance(member, discord.Member):
            member = member.id
        if member not in self.banned:
            self.banned.append(member)
            with open("xchat.yaml", "w") as fp:
                YAML().dump({"banned": self.banned, "channels": self.channels}, fp)
            await ctx.send(f"{self.bot.get_user(member)} ({member}) xchat banned")
        else:
            await ctx.send(f"{self.bot.get_user(member)} ({member}) already xchat banned")

    @commands.command()
    @commands.is_owner()
    async def xcunban(self, ctx: commands.Context, member: Union[discord.Member, int]):
        if isinstance(member, discord.Member):
            member = member.id
        if member in self.banned:
            self.banned.remove(member)
            with open("xchat.yaml", "w") as fp:
                YAML().dump({"banned": self.banned, "channels": self.channels}, fp)
            await ctx.send(f"{self.bot.get_user(member)} ({member}) xchat unbanned")
        else:
            await ctx.send(f"{self.bot.get_user(member)} ({member}) already not banned")

    async def init_channels(self):
        print("[XCHAT] Looking for channels")
        self._reload()
        print(f" - Found {len(self.channels)} channels")
        print(f" - Found {len(self.banned)} banned members")
        print("[XCHAT] Channel search done")

    async def xchat(self, message: discord.Message):
        channel: discord.TextChannel = message.channel
        if channel.id not in self.channels.values():
            return
        if message.author.id in self.banned:
            try:
                await message.delete()
            except discord.errors.Forbidden:
                pass
            return
        if self._cd.get_bucket(message).update_rate_limit() and message.author.id not in self.exempt:
            try:
                await message.delete()
            except discord.errors.Forbidden:
                pass
            await message.channel.send(f"{message.author.mention}, you're sending messages too fast!", delete_after=30)
            return

        guild: discord.Guild = channel.guild
        author: discord.Member = message.author
        e = discord.Embed()
        e.title = f"Chat from **{guild.name}**"
        e.colour = self.colors[int(guild.id)]
        user: discord.User = message.author
        e.description = message.content
        err_s = ""
        try:
            await message.delete()
        except discord.errors.Forbidden as err:
            if err.status == 403:
                err_s = " | Could not delete from source server"
        except discord.errors.NotFound as e:
            pass
        e.set_footer(text=user.name + "#" + str(user.discriminator)[0:2] + "xx" + err_s, icon_url=user.avatar_url)
        for k in self.channels.keys():
            if self.channels[k] == channel.id:
                pass
            c: discord.TextChannel = self.bot.get_channel(self.channels[k])
            if c is not None:
                await c.send(embed=e)


def setup(bot):
    bot.add_cog(Crosschat(bot))
