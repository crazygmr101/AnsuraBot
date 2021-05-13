import datetime

import discord
import pytz
from discord.ext import commands
from fuzzywuzzy import process

from ansura import AnsuraBot
from lib.slash_lib import SlashContext


class Misc(commands.Cog):
    def __init__(self, bot: AnsuraBot):
        self.bot = bot
        self.bot.slashes["time"] = self._time
        self.bot.slashes["timezone.set"] = self._timezone
        self.bot.slashes["timezone.search"] = self._timezone_search

    async def _time(self, ctx: SlashContext):
        await ctx.defer()
        user = self.bot.get_user(int(ctx.options["user"]))
        tz = self.bot.db.lookup_timezone(user.id)[1]
        e = discord.Embed()
        if tz is None:
            await ctx.reply(f"**{user.display_name}** doesn't have their timezone set. "
                            "Have them set it with `%timezone`")
        else:
            e.title = f"{user.display_name}"
            now_utc = datetime.datetime.now(pytz.timezone("UTC"))
            local = now_utc.astimezone(pytz.timezone(tz)).strftime("%H:%M:%S %a %Z (%z)")
            await ctx.reply(f"**{user.display_name}**'s time is **{local}**",
                            allowed_mentions=discord.AllowedMentions.none())

    async def _timezone(self, ctx: SlashContext):
        await ctx.defer(True)
        tz = ctx.options["timezone"].replace(" ", "_")
        try:
            zone = pytz.timezone(tz)
            self.bot.db.set_timezone(ctx.author.id, zone.zone)
            await ctx.reply(f"Timezone set to **{str(zone).replace('_', ' ')}**")
        except pytz.UnknownTimeZoneError:
            await ctx.reply(f"{tz} is an invalid timezone. Search for your timezone with `/timezone search location`")

    # noinspection PyMethodMayBeStatic
    async def _timezone_search(self, ctx: SlashContext):
        await ctx.defer(True)
        all_timezones = [str(tz).replace("_", " ") for tz in pytz.all_timezones]
        top_5 = process.extract(ctx.options["text"], all_timezones, limit=5)
        await ctx.reply(f"Top 5 timezones matching **{ctx.options['text']}**:\n⋄ " +
                        "\n⋄ ".join(choice[0] for choice in top_5) + "\n" +
                        "If your timezone isn't listed, try different location terms or check [this]"
                        "(https://en.wikipedia.org/wiki/List_of_tz_database_time_zones) list.")


def setup(bot):
    bot.add_cog(Misc(bot))
