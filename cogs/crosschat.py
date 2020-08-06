from itertools import chain
import os
from typing import Dict, List, Optional, Tuple, Union

import discord
import discord.errors
from discord import Guild, TextChannel
from discord.ext import commands
from ruamel.yaml import YAML
from disputils import BotEmbedPaginator
from lib.utils import pages

def ansura_staff():
    def predicate(ctx: commands.Context):
        ansura_guild: discord.Guild = ctx.bot.get_guild(604823602973376522)
        if not ansura_guild.get_member(ctx.author.id):
            return
        return 691752324787339351 in [r.id for r in ansura_guild.get_member(ctx.author.id).roles]
    return commands.check(predicate)

class Crosschat(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.colors = {}
        self.bot = bot
        self._cd = commands.CooldownMapping.from_cooldown(3, 15, commands.BucketType.user)
        self.channels: Optional[Dict[int, int]] = None
        self.banned: Optional[List[int]] = None
        self.exempt: Optional[List[int]] = None
        self.messages: List[List[int, int, int, List[Tuple[int, int]]]] = []
        self.ansura_color = discord.Colour.from_rgb(0x4a, 0x14, 0x8c)

    def _resolve(self, u):
        if self.bot.get_user(u):
            return f"*U* {self.bot.get_user(u)}"
        if self.bot.get_guild(u):
            return f"*G* {self.bot.get_guild(u)}"
        return None

    @commands.command()
    @ansura_staff()
    async def xclist(self, ctx: commands.Context):
        channels = pages([f"{self.bot.get_guild(k)} ({k})\n - {self.bot.get_channel(v)} ({v})"
                          for k, v in self.channels.items()], 10, fmt="%s", title="Channels")
        banned = pages([f"{self._resolve(u)} - {u}"
                        for u in self.banned], 10, fmt="%s", title="Banned")
        exempt = pages([f"{self.bot.get_user(u)} - {u}" for u in self.exempt], 10, fmt="%s", title="Exempt")
        await BotEmbedPaginator(ctx, list(chain(channels, banned, exempt))).run()

    @commands.command()
    @ansura_staff()
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

    def _save(self):
        with open("xchat.yaml", "w") as fp:
            YAML().dump({"banned": self.banned, "channels": self.channels, "exempt": self.exempt}, fp)

    @commands.command()
    @ansura_staff()
    async def xcbans(self, ctx: commands.Context):
        await BotEmbedPaginator(ctx,
                                pages(
                                    [f"{self._resolve(x)} - {x}" for x in self.banned],
                                    10, "Crosschat bans", fmt="%s"
                                )).run()

    @commands.command()
    @ansura_staff()
    async def xcservers(self, ctx: commands.Context):
        await BotEmbedPaginator(ctx,
                                pages(
                                    [f"**{self.bot.get_guild(int(x))}** ({x})\n- "
                                     f"{self.bot.get_channel(c)} ({c})" for x, c in self.channels.items()],
                                    10, "Crosschat servers", fmt="%s"
                                )).run()

    @commands.command()
    @commands.check_any(
        commands.has_permissions(administrator=True),
        commands.has_guild_permissions(administrator=True)
    )
    async def crosschat(self, ctx: commands.Context, arg: Union[discord.TextChannel, str] = None):
        if ctx.guild.id in self.banned:
            await ctx.send("This guild is banned from crosschat. If this is a mistake, or to appeal this ban, "
                           "go to https://discord.gg/t5MGS2X to appeal.")
            return
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
        self._save()
        for i in self.channels:
            color = int(i) // 64 % (14 ** 3) + 0x222
            rd = color >> 8
            gr = (color & 0x0f0) >> 4
            bl = (color & 0xf)
            if abs(rd - self.ansura_color.r) < 0x20:
                rd = (rd + 0x40) % 0x100
            if abs(gr - self.ansura_color.g) < 0x20:
                gr = (gr + 0x40) % 0x100
            if abs(bl - self.ansura_color.b) < 0x20:
                bl = (bl + 0x40) % 0x100
            self.colors[int(i)] = discord.Colour.from_rgb(rd * 0x10, gr * 0x10, bl * 0x10)

    @commands.command()
    @ansura_staff()
    async def xcgban(self, ctx: commands.Context, guild: int):
        if guild in self.banned:
            return await ctx.send(f"Guild {self.bot.get_guild(guild).name} already banned.")
        self.banned.append(guild)
        self._save()
        await ctx.send(f"Guild {self.bot.get_guild(guild).name or guild} banned.")

    @commands.command()
    @ansura_staff()
    async def xcgunban(self, ctx: commands.Context, guild: int):
        if guild not in self.banned:
            return await ctx.send(f"Guild {self.bot.get_guild(guild).name} not banned.")
        self.banned.remove(guild)
        self._save()
        await ctx.send(f"Guild {self.bot.get_guild(guild).name or guild} unbanned.")

    @commands.command()
    @ansura_staff()
    async def xcban(self, ctx: commands.Context, member: Union[discord.Member, int]):
        if isinstance(member, discord.Member):
            member = member.id
        if member not in self.banned:
            self.banned.append(member)
            self._save()
            await ctx.send(f"{self.bot.get_user(member)} ({member}) xchat banned")
        else:
            await ctx.send(f"{self.bot.get_user(member)} ({member}) already xchat banned")

    @commands.command()
    @ansura_staff()
    async def xcunban(self, ctx: commands.Context, member: Union[discord.Member, int]):
        if isinstance(member, discord.Member):
            member = member.id
        if member in self.banned:
            self.banned.remove(member)
            self._save()
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
        if message.author.id in self.banned or message.guild.id in self.banned:
            try:
                await message.delete()
            except discord.errors.Forbidden:
                pass
            return
        time = self._cd.get_bucket(message).update_rate_limit()
        if time and message.author.id not in self.exempt:
            try:
                await message.delete()
            except discord.errors.Forbidden:
                pass
            await message.channel.send(f"{message.author.mention}, you're sending messages too fast! "
                                       f"Try again in {round(time)} seconds.", delete_after=30)
            return

        guild: discord.Guild = channel.guild
        author: discord.Member = message.author
        e = discord.Embed()
        g: discord.Guild = self.bot.get_guild(604823602973376522)
        m: discord.Member = g.get_member(author.id)
        e.title = f"Chat from **{guild.name}**"
        e.colour = self.colors[int(guild.id)]
        if m and 691752324787339351 in [r.id for r in m.roles]:
            e.set_author(name="Ansura Developer" if author.id == 267499094090579970 else
                         "Ansura Staff Member",
                         icon_url="https://cdn.discordapp.com/icons/604823602973376522/"
                                  "cab59a4cb92c877f5b7c3fc1ae402298.png")
            e.colour = self.ansura_color
        user: discord.User = message.author
        e.description = message.content
        err_s = ""
        file = None
        if message.attachments:
            if self._is_image(message.attachments[0].filename):
                with open(f"attachments/{message.attachments[0].filename}", "wb") as fp:
                    await message.attachments[0].save(fp)
                file = True
                e.set_image(url=f"attachment://{message.attachments[0].filename}")
        else:
            file = False
        try:
            await message.delete()
        except discord.errors.Forbidden as err:
            if err.status == 403:
                err_s = " | Could not delete from source server"
        except discord.errors.NotFound as e:
            pass
        e.set_footer(text=user.name + "#" + str(user.discriminator)[0:2] + "xx" + err_s, icon_url=user.avatar_url)
        sent = []

        for k in self.channels.keys():
            c: discord.TextChannel = self.bot.get_channel(self.channels[k])
            if c is not None:
                if file:
                    with open(f"attachments/{message.attachments[0].filename}", "rb") as fp:
                        msg = await c.send(embed=e, file=discord.File(fp, message.attachments[0].filename))
                else:
                    msg = await c.send(embed=e)
                sent.append((c.id, msg.id))
        self.messages.append([message.guild.id, message.channel.id, message.author.id, sent])
        if len(self.messages) > 250:
            del self.messages[0]
        if file:
            os.remove(f"attachments/{message.attachments[0].filename}")

    def _is_image(self, url: str):
        for i in "jpg,jpeg,png,gif".split(","):
            if url.endswith("." + i):
                return True
        else:
            return False

    @commands.command()
    @ansura_staff()
    async def xclookup(self, ctx: commands.Context, message: Union[discord.Message, int]):
        if isinstance(message, discord.Message):
            msg_id = message.id
        else:
            msg_id = message
        guild = None
        messages = None
        msgs = None
        author = None
        found = False
        channel = None
        for i in self.messages:
            guild = i[0]
            channel = i[1]
            author = i[2]
            msgs = i[3]
            for m in msgs:
                if m[1] == msg_id:
                    found = True
                    break
            if found: break
        else:
            return await ctx.send("Message not found")
        await ctx.send(
            embed=discord.Embed(
                title="Message lookup",
            ).add_field(
                name="Guild",
                value=f"{self.bot.get_guild(guild)} - {guild}",
                inline=False
            ).add_field(
                name="Channel",
                value=f"{self.bot.get_channel(channel)} - {channel}",
                inline=False
            ).add_field(
                name="Author",
                value=f"{self.bot.get_user(author)} - {author}",
                inline=False
            )
        )

    @commands.command()
    @ansura_staff()
    async def xcdelete(self, ctx: commands.Context, message: Union[discord.Message, int]):
        if isinstance(message, discord.Message):
            msg_id = message.id
        else:
            msg_id = message
        guild = None
        messages = None
        msgs = None
        author = None
        found = False
        channel = None
        for i in self.messages:
            guild = i[0]
            channel = i[1]
            author = i[2]
            msgs = i[3]
            for m in msgs:
                if m[1] == msg_id:
                    found = True
                    break
            if found: break
        else:
            return await ctx.send("Message not found")
        count = 0
        fail = 0
        for g, c in self.channels.items():
            for m in msgs:
                chan: discord.TextChannel = self.bot.get_channel(m[0])
                if chan:
                    try:
                        await (await chan.fetch_message(m[1])).delete()
                        count += 1
                    except:
                        pass
        await ctx.send(f"Deleted message from {count} servers. {fail} failed")


    @commands.command()
    @ansura_staff()
    async def xchelp(self, ctx: commands.Context):
        await ctx.send(embed=discord.Embed(
            title="Ansura Crosschat Moderation",
            description="**Guild Ban Management**:`xcgunban guild_id` `xcgban guild_id`\n"
                        "**User Ban Management**: `xcunban member_id_or_@`/`xcban member_id_or_@`\n"
                        "**List Guilds, Bans, Exemptions**: `xclist`\n"
                        "**Lookup a message**: `xclookup message_link`\n"
                        "**Delete a message**: `xcldelete message_link`"
        ))

def setup(bot):
    bot.add_cog(Crosschat(bot))
