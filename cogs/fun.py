from typing import List

from discord.ext import commands
import discord
import core.util.HelpEntries as HE
import re

class Fun(commands.Cog):
    def __init__(self, bot: discord.ext.commands.Bot):
        self.bot = bot
        print("Fun cog loaded")

    @commands.command(pass_context=True)
    async def ship(self, ctx: commands.Context, user1: discord.Member, user2: discord.Member):
        name1: str = user1.display_name
        name2: str = user2.display_name
        def split(s: str):
            import re
            if s == "crazygmr101": return ["crazy","gmr101"]
            if len(s.split(" ")) > 1:
                ar = s.split(" ")
                return [
                    " ".join(ar[:1]),
                    " ".join(ar[1:])
                ]
            if len(s.split("_")) > 1:
                ar = s.split("_")
                return [
                    " ".join(ar[:1]),
                    " ".join(ar[1:])
                ]
            # check for alt caps
            ar = re.sub('([A-Z][a-z]+)', r' \1', re.sub('([A-Z]+)', r' \1', s)).split()
            if len(ar) > 1:
                return [
                    " ".join(ar[:1]),
                    " ".join(ar[1:])
                ]
            # TODO: work on this code a tad more, just push
            half = int(len(s)/2)
            return [s[:half], s[half:]]
        await ctx.send("I ship it: " + split(name1)[0] + split(name2)[1])

def setup(bot):
    bot.add_cog(Fun(bot))