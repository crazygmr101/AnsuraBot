import os

import dbl
import discord
from discord.ext import commands, tasks


class DBL(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.token = os.getenv("DBL")
        self.dblpy = dbl.DBLClient(self.bot, self.token, autopost=True)

    @tasks.loop(seconds=600)
    async def update_status(self):
        await self.bot.change_presence(
            status=discord.Status.online,
            activity=discord.Activity(
                name=str(len(self.bot.guilds)) + " servers | %help",
                type=discord.ActivityType.watching
            )
        )


def setup(bot):
    bot.add_cog(DBL(bot))
