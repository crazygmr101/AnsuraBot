from datetime import datetime
from typing import Union

import discord
import pytz
from discord.ext import commands

import lib.database as AD


class Gamertags(commands.Cog):
    def __init__(self, bot: discord.ext.commands.Bot):
        self.bot = bot
        bot.db = AD.AnsuraDatabase()
        self.db = bot.db

    @commands.command()
    async def xbox(self, ctx: discord.ext.commands.Context, username):
        """
        Sets your xbox username
        """
        self.db.set_gaming_record(ctx.author.id, "xboxlive", username)
        await ctx.send(ctx.author.mention + ": Set to " + username)

    @commands.command()
    async def mojang(self, ctx: discord.ext.commands.Context, username):
        """
        Sets your mojang username
        """
        self.db.set_gaming_record(ctx.author.id, "mojang", username)
        await ctx.send(ctx.author.mention + ": Set to " + username)

    @commands.command(aliases=["yt"])
    async def youtube(self, ctx: discord.ext.commands.Context, username):
        """
        Sets your youtube username
        """
        self.db.set_gaming_record(ctx.author.id, "youtube", username)
        await ctx.send(ctx.author.mention + ": Set to " + username)

    @commands.command()
    async def mixer(self, ctx: discord.ext.commands.Context, username):
        """
        Sets your mixer username
        """
        self.db.set_gaming_record(ctx.author.id, "mixer", username)
        await ctx.send(ctx.author.mention + ": Set to " + username)

    @commands.command()
    async def twitch(self, ctx: discord.ext.commands.Context, username):
        """
        Sets your twitch username
        """
        self.db.set_gaming_record(ctx.author.id, "twitch", username)
        await ctx.send(ctx.author.mention + ": Set to " + username)

    @commands.command()
    async def reddit(self, ctx: discord.ext.commands.Context, username):
        """
        Sets your reddit username
        """
        self.db.set_gaming_record(ctx.author.id, "reddit", username)
        await ctx.send(ctx.author.mention + ": Set to " + username)

    @commands.command()
    async def steam(self, ctx: discord.ext.commands.Context, username):
        """
        Sets your steam username/link
        """
        self.db.set_gaming_record(ctx.author.id, "steam", username)
        await ctx.send(ctx.author.mention + ": Set to " + username)

    @commands.command(aliases=["gt"])
    async def gametags(self, ctx: discord.ext.commands.Context, user: Union[discord.Member, discord.User] = None):
        """
        Lists a user's gamertags
        """
        if user is None:
            user = ctx.author
        rec = self.db.lookup_gaming_record(user.id)
        e = discord.Embed()
        e.colour = user.color
        e.title = user.display_name
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
    async def who(self, ctx: discord.ext.commands.Context, tag: str):
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
        not_in_guild = []
        for i in users:
            u: discord.User = (await self.bot.fetch_user(int(i[0])))
            s += u.name + "#" + u.discriminator + " - " + i[1] + ": " + i[2] + "\n"
        s += "```"
        await ctx.send(s)


def setup(bot):
    bot.add_cog(Gamertags(bot))
