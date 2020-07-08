import discord
import discord.errors
from discord import Guild, TextChannel
from discord.ext import commands


class Crosschat(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.colors = {}
        self.channels = {}
        self.bot = bot
        self._cd = commands.CooldownMapping.from_cooldown(2, 60, commands.BucketType.user)

    async def init_channels(self):
        print("[XCHAT] Looking for channels")
        g: Guild
        c: discord.TextChannel
        for g in self.bot.guilds:
            for c in g.channels:
                if type(c) is not TextChannel:
                    continue
                if c.topic is None:
                    continue
                if "ansura crosschat" in c.topic or c.topic == "ansura crosschat":
                    print(" FOUND " + c.name + " (" + str(c.id) + ") in " + g.name + " (" + str(g.id) + ")")
                    color = int(g.id / 64) % (14 ** 3) + 0x222
                    rd = color >> 8
                    gr = (color & 0x0f0) >> 4
                    bl = (color & 0xf)
                    self.channels[g.id] = int(c.id)
                    self.colors[g.id] = discord.Colour.from_rgb(rd * 0x11, gr * 0x11, bl * 0x11)
                    break
        print("[XCHAT] Channel search done")

    async def xchat(self, message: discord.Message):
        if self._cd.get_bucket(message).update_rate_limit():
            try:
                await message.delete()
            except discord.errors.Forbidden:
                pass
            await message.channel.send(f"{message.author.mention}, you're sending messages too fast!", delete_after=30)
            return
        channel: discord.TextChannel = message.channel
        if channel.id not in self.channels.values():
            return

        guild: discord.Guild = channel.guild
        author: discord.Member = message.author
        e = discord.Embed()
        e.title = f"Chat from **{guild.name}**"
        e.colour = self.colors[int(guild.id)]
        user: discord.User = message.author
        e.description = message.content
        err_s = ""
        try:
            await message.delete()
        except discord.errors.Forbidden as err:
            if err.status == 403:
                err_s = " | Could not delete from source server"
        except discord.errors.NotFound as e:
            pass
        e.set_footer(text=user.name + "#" + str(user.discriminator)[0:2] + "xx" + err_s, icon_url=user.avatar_url)
        for k in self.channels.keys():
            if self.channels[k] == channel.id:
                pass
            c: discord.TextChannel = self.bot.get_channel(self.channels[k])
            if c is not None:
                await c.send(embed=e)


def setup(bot):
    bot.add_cog(Crosschat(bot))
