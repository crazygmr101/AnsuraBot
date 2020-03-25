from typing import List

from discord import Guild, TextChannel
from discord.ext import commands
import discord


class Crosschat:
    def __init__(self, bot: commands.Bot):
        self.colors = {}
        self.channels = {}
        self.bot = bot

    async def init_channels(self):
        g: Guild
        c: discord.TextChannel
        async for g in self.bot.fetch_guilds():
            for c in await g.fetch_channels():
                if type(c) is not TextChannel:
                    continue
                if c.topic is None:
                    continue
                if "ansura crosschat" in c.topic or c.topic == "ansura crosschat":
                    print("Found channel " + c.name + " (" + str(c.id) + ") in " + g.name + " (" + str(g.id) + ")")
                    color = int(g.id/64) % (14**3) + 0x222
                    rd = color >> 8
                    gr = (color & 0x0f0) >> 4
                    bl = (color & 0xf)
                    print(" Added with color: " + hex(color))
                    self.channels[g.id] = int(c.id)
                    self.colors[g.id] = discord.Colour.from_rgb(rd*0x11, gr*0x11, bl*0x11)
                    break

    async def xchat(self, message: discord.Message):
        channel: discord.TextChannel = message.channel
        if channel.id not in self.channels.values():
            return

        guild: discord.Guild = channel.guild
        author: discord.Member = message.author
        e = discord.Embed()
        e.title = f"Chat from {guild.name}"
        e.colour = self.colors[int(guild.id)]
        user: discord.User = message.author
        e.description = message.content
        e.set_footer(text=user.name + "#" + str(user.discriminator)[0:2] + "xx", icon_url=user.avatar_url)
        for k in self.channels.keys():
            if self.channels[k] == channel.id:
                pass
            c: discord.TextChannel = self.bot.get_channel(self.channels[k])
            if c is not None:
                await c.send(embed=e)
        await message.delete()