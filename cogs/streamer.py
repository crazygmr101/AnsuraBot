import os
import cogs
import requests
from discord.ext import commands
import discord
from core.database import AnsuraDatabase

class Streamer(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        print("Streamer cog loading")
        print(" Opening mixer session...")
        self.db = bot.db
        self.mixer_key = os.getenv("MIXER")
        self.session = requests.Session()
        self.session.headers.update({'Client-ID': self.mixer_key})
        print(" Mixer session opened")
        print("Streamer cog loaded")

    @commands.command()
    async def profile(self, ctx: commands.Context, ptype: str, user: str):
        ptype = ptype.lower()
        if ptype == "mixer":
            await self.mixer(ctx, user)
        else:
            await ctx.send("I don't recognize that profile type ):")

    async def mixer(self, ctx: commands.Context, user: str):
        resp = self.session.get('https://mixer.com/api/v1/channels/{}'.format(user))
        j = resp.json()

        embed = discord.Embed(title=(user + "'s Mixer"), color=0x0000ff)
        embed.add_field(name="Bio", value=j['user']['bio'], inline=False)
        embed.add_field(name="Latest Stream", value=j['name'], inline=False)
        embed.add_field(name="Total Viewers", value=j['viewersTotal'])
        embed.add_field(name="Viewers", value=j['viewersCurrent'])
        embed.add_field(name="Audience", value=j['audience'])
        embed.add_field(name="Online", value=j['online'])
        embed.set_thumbnail(url=j['user']['avatarUrl'])
        await ctx.send(embed=embed)

    @commands.command()
    @commands.check_any(
        commands.has_permissions(manage_roles=True, manage_guild=True),
        commands.is_owner(),
        commands.has_permissions(administrator=True)
    )
    async def setstreamrole(self, ctx: commands.Context, role: discord.Role):
        cfg: cogs.confighandler.ConfigHandler = self.bot.cfg
        cfg.data[ctx.guild.id]["streamer-role"] = role.id
        cfg.save()
        await ctx.send(embed=discord.Embed(title="Role set",description=f"Streamer role set to {role.mention}"))

    @commands.command()
    async def getstreamrole(self, ctx: commands.Context):
        cfg: cogs.confighandler.ConfigHandler = self.bot.cfg
        role = cfg.data[ctx.guild.id]["streamer-role"]
        await ctx.send(embed=discord.Embed(title="Role set",description=f"Streamer role set to <@&{role}>"))

def setup(bot):
    bot.add_cog(Streamer(bot))
