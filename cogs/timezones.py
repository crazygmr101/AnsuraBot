import discord
from discord.ext import commands
import pytz
from core.database import AnsuraDatabase as DB
import datetime

class Timezones(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db: DB = bot.db

    @commands.command()
    async def gettz(self, ctx: commands.Context, user: discord.Member):
        tz = self.db.lookup_timezone(user.id)[1]
        e = discord.Embed()
        if tz is None:
            e.title = "No timezone"
            e.colour = discord.Colour.dark_gold()
            e.description = f"{user.mention} doesn't have their timezone set"
        else:
            e.title = f"{user.display_name}"
            e.description = f"{user.display_name}'s timezone is `{tz}`"
        await ctx.send(embed=e)

    @commands.command()
    async def time(self, ctx: commands.Context, user: discord.Member):
        try:
            tz = self.db.lookup_timezone(user.id)[1]
            e = discord.Embed()
            if tz is None:
                e.title = "No timezone"
                e.colour = discord.Colour.dark_gold()
                e.description = f"{user.mention} doesn't have their timezone set"
            else:
                e.title = f"{user.display_name}"
                now_utc = datetime.datetime.now(pytz.timezone("UTC"))
                local = now_utc.astimezone(pytz.timezone(tz)).strftime("%H:%M:%S %a %Z (%z)")
                e.description = f"{user.display_name}'s time is `{local}`"
            await ctx.send(embed=e)
        except Exception as e:
            print(type(e))
            print(str(e))

    @commands.command(aliases=["timezone","tz"])
    async def settz(self, ctx: commands.Context, tz: str):
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
                            f"https://en.wikipedia.org/wiki/List_of_tz_database_time_zones for a list of supported " \
                            f"timezones "
            await ctx.send(embed=e)
            return
        except Exception as ex:
            print(type(ex))
            print(ex.__str__())

def setup(bot):
    bot.add_cog(Timezones(bot))