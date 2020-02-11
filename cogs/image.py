from typing import List

from discord.ext import commands
import discord
import core.util.HelpEntries as HE


class Image(commands.Cog):
    def __init__(self, bot: discord.ext.commands.Bot):
        self.bot = bot
        print("Image cog loaded")


    @commands.command()
    async def image(self, ctx: commands.Context, message: str):
        message: discord.Message = ctx.message
        print(message.attachments)

def setup(bot):
    bot.add_cog(Image(bot))