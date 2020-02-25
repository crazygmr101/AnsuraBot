import os

import requests
from discord.ext import commands
import discord


class Streamer(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        print("Streamer cog loading")
        print(" Opening mixer session...")
        self.mixer_key = os.getenv("MIXER")
        print(f' Loaded mixer API with key {self.mixer_key}')
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


def setup(bot):
    bot.add_cog(Streamer(bot))
