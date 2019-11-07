from discord.ext import commands
import discord
from core.geoloc import Geolocation
from core.map_image import Map_Imager
import core.util.HelpEntries as HE

class Map(commands.Cog):
    def __init__(self, bot: discord.ext.commands.Bot):
        self.bot = bot
        self.m = Map_Imager()
        self.g = Geolocation()
        print("Loaded map imager")

    @commands.command(pass_context=True)
    async def map(self, ctx: commands.Context, lat: float, lon: float, zoom: int = 2):
        await ctx.send(embed=self.build_map(lat, lon, zoom, str(lat) + "," + str(lon)))

    @commands.command(pass_context=True)
    async def maploc(self, ctx: commands.Context, loc: str, zoom: int = 7):
        ar = self.g.locate(loc)
        await ctx.send(embed=self.build_map(ar[0], ar[1], zoom, ar[2]))

    def build_map(self, lat: float, lon: float, zoom: int, title: str):
        e = discord.Embed()
        e.title = title
        e.add_field(name="Location", value=str(lat) + "," + str(lon))
        e.set_image(url=self.m.get_static_url(lat=lat, lon=lon, size=512, zoom=zoom))
        return e

def setup(bot):
    bot.add_cog(Map(bot))
    HE.HelpEntries.register("maploc", "%maploc location [zoom=2]", "`%maploc \"michigan, us\" 2` gives "
                                                                   "you a map of Michigan, with a zoom "
                                                                   "level of 2. The zoom level can be "
                                                                   "omitted and defaults to 2.")
    HE.HelpEntries.register("map", "%map lat lon [zoom=2]", "`%map 25.6 44.5 2` gives "
                                                            "you a map of (25.6,44.5), "
                                                            "with a zoom level of 2. The "
                                                            "zoom level can be "
                                                            "omitted and defaults to 2.")