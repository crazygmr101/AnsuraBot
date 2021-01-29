from discord.ext import commands

from ansura import AnsuraBot


class Util(commands.Cog):
    def __init__(self, bot: AnsuraBot):
        self.bot = bot

    # @commands.command()


def setup(bot: AnsuraBot) -> None:
    bot.add_cog(Util(bot))
