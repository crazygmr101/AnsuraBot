import discord
from discord.ext import commands


class Util(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    #@commands.command()


def setup(bot: commands.Bot) -> None:
    bot.add_cog(Util(bot))
