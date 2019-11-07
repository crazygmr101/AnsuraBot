import discord
import mcstatus
from discord import Embed
from discord.ext import commands
import re

class Minecraft(commands.Cog):
    def __init__(self, bot: discord.ext.commands.Bot):
        self.bot = bot
        print("Minecraft cog loaded")

    @commands.command(pass_context=True)
    async def mcping(self, ctx: discord.ext.commands.Context, url: str, arg1: str = None):
        server = mcstatus.MinecraftServer.lookup(url)
        status = server.status()
        e = Embed()
        e.title = url
        e.description = re.sub("§.", "", status.description)
        e.add_field(name="Players", value=str(status.players.online) + "/" + str(status.players.max))
        e.add_field(name="Ping", value=str(status.latency))
        e.add_field(name="Version", value=status.version.name)
        e.add_field(name="Protocol", value="v" + str(status.version.protocol))
        await ctx.send(embed=e)

def setup(bot):
    bot.add_cog(Minecraft(bot))
