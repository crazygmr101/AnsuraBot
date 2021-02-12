from datetime import datetime
from typing import Union

import discord
import pytz
from discord.ext import commands

from ansura import AnsuraBot, AnsuraContext


class Gamertags(commands.Cog):
    def __init__(self, bot: AnsuraBot):
        self.bot = bot
        self.db = bot.db

    @commands.command()
    async def private(self, ctx: AnsuraContext, status: bool = None):
        """
        Sets your privacy for %gt. People with manage server permissions can always see gamertags of people in a server
        """
        p, w = self.db.isprivate(ctx.author.id)
        p, w = self.db.setprivate(userid=ctx.author.id, gt=status if status is not None else not p)
        await ctx.send(embed=discord.Embed(
            title="Your profile status",
            description=f"Website: {'Private' if w else 'Public'}\n"
                        f"Servers: {'Private' if p else 'Public if you share a server'}"
        ))

    @commands.command()
    async def webprivate(self, ctx: AnsuraContext, status: bool = None):
        """
        Sets your profile privacy for the website.
        """
        p, w = self.db.isprivate(ctx.author.id)
        p, w = self.db.setprivate(userid=ctx.author.id, web=status if status is not None else not w)
        await ctx.send(embed=discord.Embed(
            title="Your profile status",
            description=f"Website: {'Private' if w else 'Public'}\n"
                        f"Servers: {'Private' if p else 'Public if you share a server'}"
        ))

    @commands.command()
    async def setbio(self, ctx: AnsuraContext, *, bio: str):
        """
        Sets your bio
        """
        if len(bio) > 1000:
            bio = bio[:1000]
        self.db.set_bio(ctx.author.id, bio)
        await ctx.send(embed=discord.Embed(
            title="Bio set",
            description=bio,
        ))

    @commands.command()
    async def bio(self, ctx: AnsuraContext, member: discord.Member = None):
        """
        Gets your or another user's bio
        """
        if not member:
            member = ctx.author
        s = self.db.lookup_gaming_record(member.id)[8]
        if s == 1:
            await ctx.send("That user's bio is private")
        r = self.db.get_bio(member.id)
        if not r:
            await ctx.send(embed=discord.Embed(
                title="No Bio",
                description=f"{member.mention} hasn't set a bio yet. Have them do `%setbio cool bio here`"
            ))
        else:
            await ctx.send(embed=discord.Embed(
                title=f"{member}'s Bio",
                description=r,
            ))

    @commands.command()
    async def profile(self, ctx: AnsuraContext, member: discord.Member = None):
        """
        Gets a link to someone's profile on Ansura's website
        """
        if not member:
            member = ctx.author
        await ctx.send(embed=discord.Embed(
            title=f"{member}'s Profile",
            description=f"[Click here](https://www.ansura.xyz/profile/{member.id}) for a link"
        ))

    @commands.command()
    async def xbox(self, ctx: AnsuraContext, *, username):
        """
        Sets your xbox username
        """
        self.db.set_gaming_record(ctx.author.id, "xboxlive", username)
        await ctx.send_info(ctx.author.mention + ": Set to " + username)

    @commands.command()
    async def mojang(self, ctx: AnsuraContext, *, username):
        """
        Sets your mojang username
        """
        self.db.set_gaming_record(ctx.author.id, "mojang", username)
        await ctx.send_info(ctx.author.mention + ": Set to " + username)

    @commands.command(aliases=["yt"])
    async def youtube(self, ctx: AnsuraContext, *, username):
        """
        Sets your youtube username
        """
        self.db.set_gaming_record(ctx.author.id, "youtube", username)
        await ctx.send_info(ctx.author.mention + ": Set to " + username)

    @commands.command()
    async def mixer(self, ctx: AnsuraContext, *, username):
        """
        Sets your mixer username
        """
        self.db.set_gaming_record(ctx.author.id, "mixer", username)
        await ctx.send_info(ctx.author.mention + ": Set to " + username)

    @commands.command()
    async def twitch(self, ctx: AnsuraContext, *, username):
        """
        Sets your twitch username
        """
        self.db.set_gaming_record(ctx.author.id, "twitch", username)
        await ctx.send_info(ctx.author.mention + ": Set to " + username)

    @commands.command()
    async def reddit(self, ctx: AnsuraContext, *, username):
        """
        Sets your reddit username
        """
        self.db.set_gaming_record(ctx.author.id, "reddit", username)
        await ctx.send_info(ctx.author.mention + ": Set to " + username)

    @commands.command()
    async def steam(self, ctx: AnsuraContext, *, username):
        """
        Sets your steam username/link
        """
        self.db.set_gaming_record(ctx.author.id, "steam", username)
        await ctx.send_info(ctx.author.mention + ": Set to " + username)

    @commands.command(aliases=["gt"])
    async def gametags(self, ctx: AnsuraContext, user: Union[discord.Member, discord.User] = None,
                       override: bool = False):
        """
        Lists a user's gamertags
        This only shows members of the server, bot owner can set `override` to change this
        """
        if override and not await self.bot.is_owner(ctx.author):
            override = False
        if user is None:
            user = ctx.author
        if isinstance(user, discord.User) and not override:
            await ctx.send("That user isn't in this server")
            return
        rec = self.db.lookup_gaming_record(user.id)
        priv = self.db.isprivate(user.id)
        if priv[0] == 1 and not ctx.author.guild_permissions.manage_guild:
            await ctx.send(embed=discord.Embed(
                title=user.display_name,
                description="This user's profile is private"
            ))
            return
        if priv[0] == 1:
            await ctx.send("This profile is private. Do you want to continue to display it anyway?")
            resp = await self.bot.wait_for("message", timeout=60, check=lambda m: m.author.id == ctx.author.id and
                                                                                  m.channel.id == ctx.channel.id)
            if resp.content.lower()[0] != "y":
                await resp.add_reaction("👍")
                return
        e = discord.Embed()
        if self.bot.user.id in [643869468774105099, 603640674234925107]:
            guild: discord.Guild = self.bot.get_guild(604823602973376522)
            member: discord.Member = guild.get_member(user.id)
            if member and 691752324787339351 in [r.id for r in member.roles]:
                e.set_author(name="Ansura Developer" if member.id == 267499094090579970 else "Ansura Staff Member",
                             icon_url="https://cdn.discordapp.com/icons/604823602973376522/"
                                      "cab59a4cb92c877f5b7c3fc1ae402298.png")
        e.colour = user.color
        e.title = user.display_name
        e.set_thumbnail(url=user.avatar_url)
        tz = self.db.lookup_timezone(user.id)[1]
        if tz is not None:
            now_utc = datetime.now(pytz.timezone("UTC"))
            offset = now_utc.astimezone(pytz.timezone(tz)).strftime("%z")
        e.add_field(name="XBox", value=rec[2] if rec[2] is not None else "N/A")
        e.add_field(name="Mojang", value=rec[1] if rec[1] is not None else "N/A")
        e.add_field(name="Youtube", value=rec[3] if rec[3] is not None else "N/A")
        e.add_field(name="Twitch", value=rec[4] if rec[4] is not None else "N/A")
        e.add_field(name="Mixer", value=rec[5] if rec[5] is not None else "N/A")
        e.add_field(name="Reddit", value=rec[6] if rec[6] is not None else "N/A")
        e.add_field(name="Steam", value=rec[7] if rec[7] is not None else "N/A")
        e.add_field(name="Time Zone", value=f"{tz} ({offset})" if tz is not None else "N/A")
        await ctx.send(embed=e)

    @commands.command()
    async def who(self, ctx: AnsuraContext, tag: str):
        """
        Finds users with a gamertag of <tag>
        """
        db = self.db
        records = db.get_all()
        # id, mojang, xbox, youtube, twitch, mixer
        users = []
        async with ctx.channel.typing():
            for r in records:
                for k in r.keys():
                    if k != "id" and r[k] == tag:
                        users.append([r["id"], k, r[k]])
        if len(users) == 0:
            await ctx.send("Tag " + tag + " not found in the database.")
            return
        s = "```\nSearch results for " + tag + "\n"
        for i in users:
            u: discord.User = (await self.bot.fetch_user(int(i[0])))
            s += u.name + "#" + u.discriminator + " - " + i[1] + ": " + i[2] + "\n"
        s += "```"
        await ctx.send(s)


def setup(bot):
    bot.add_cog(Gamertags(bot))
