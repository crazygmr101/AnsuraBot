import datetime

import discord
import pytz
from discord.ext import commands

from lib.database import AnsuraDatabase as DB
from lib.utils import pages
from disputils import BotEmbedPaginator


class Timezones(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db: DB = bot.db

    @commands.command()
    async def gettz(self, ctx: commands.Context, user: discord.Member):
        """Gets a user's timezone"""
        tz = self.db.lookup_timezone(user.id)[1]
        e = discord.Embed()
        if tz is None:
            e.title = "No timezone"
            e.colour = discord.Colour.dark_gold()
            e.description = f"{user.mention} doesn't have their timezone set. Have them set it with `%timezone`"
        else:
            e.title = f"{user.display_name}"
            e.description = f"{user.display_name}'s timezone is `{tz}`"
        await ctx.send(embed=e)

    @commands.command()
    async def time(self, ctx: commands.Context, user: discord.Member):
        """Checks the time of a user"""
        try:
            tz = self.db.lookup_timezone(user.id)[1]
            e = discord.Embed()
            if tz is None:
                e.title = "No timezone"
                e.colour = discord.Colour.dark_gold()
                e.description = f"{user.mention} doesn't have their timezone set. Have them set it with `%timezone`"
            else:
                e.title = f"{user.display_name}"
                now_utc = datetime.datetime.now(pytz.timezone("UTC"))
                local = now_utc.astimezone(pytz.timezone(tz)).strftime("%H:%M:%S %a %Z (%z)")
                e.description = f"{user.display_name}'s time is `{local}`"
            await ctx.send(embed=e)
        except Exception as e:
            print(type(e))
            print(str(e))

    @commands.command(aliases=["timezone", "tz"])
    async def settz(self, ctx: commands.Context, tz: str):
        """sets your timezone"""
        try:
            zone = pytz.timezone(tz)
            self.db.set_timezone(ctx.author.id, zone.zone)
            e = discord.Embed()
            e.colour = discord.Colour.green()
            e.title = "Timezone set"
            e.description = f"Timezone set to `{zone}`"
            await ctx.send(embed=e)
        except pytz.UnknownTimeZoneError as e:
            e = discord.Embed()
            e.colour = discord.Colour.red()
            e.title = "Invalid Timezone"
            e.description = f"{tz} is an invalid timezone. Refer to " \
                            f"`%timezones` for a list of supported " \
                            f"timezones "
            await ctx.send(embed=e)
            return
        except Exception as ex:
            print(type(ex))
            print(ex.__str__())

    @commands.command()
    async def timezones(self, ctx: commands.Context, search: str = None):
        """Gets a list of supported timezones, use `%timezones akhjdlksa` to search by text"""
        if not search:
            search = ""
        all_timezones = [tz for tz in pytz.all_timezones if (search.lower() or "") in tz.lower()]
        await BotEmbedPaginator(
            ctx,
            pages(all_timezones, 20, "Supported Timezones", fmt="%s"),
        ).run()


def setup(bot):
    bot.add_cog(Timezones(bot))
