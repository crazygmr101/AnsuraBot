from discord.ext import commands
import discord


class Crosschat:
    def __init__(self):
        pass

    async def crosschat(message: discord.Message, bot: commands.Bot):
        channels = {
            604823602973376522: 643522630934069259,  # ansura test
            523136895245615124: 643519574674898964,  # hustlers
            586199960198971409: 643519468928237568,  # united
            570393863559315456: 643540235644567583  # uwus r us
        }
        channel: discord.TextChannel = message.channel
        if channel.id not in channels.values():
            return

        guild: discord.Guild = channel.guild
        author: discord.Member = message.author
        e = discord.Embed()
        e.title = f"Chat from {guild.name}"
        e.colour = author.colour
        user: discord.User = message.author
        e.set_thumbnail(url=user.avatar_url)
        e.add_field(name=user.name + "#" + str(user.discriminator)[0:2] + "xx", value=message.content)
        for k in channels.keys():
            if channels[k] == channel.id:
                continue
            c: discord.TextChannel = bot.get_channel(channels[k])
            await c.send(embed=e)