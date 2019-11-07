from discord.ext import commands
import discord


class Conversation(commands.Cog):
    def __init__(self, bot: discord.ext.commands.Bot):
        self.bot = bot
        print("Conversation cog loaded")


def setup(bot):
    bot.add_cog(Conversation(bot))