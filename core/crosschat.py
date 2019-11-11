from discord.ext import commands
import discord


async def crosschat(message: discord.Message, bot: commands.Bot):
    channels = {
        604823602973376522: 643522630934069259,  # ansura test
        523136895245615124: 643519574674898964,  # hustlers
        586199960198971409: 643519468928237568  # united
    }
    channel: discord.TextChannel = message.channel
    if channel not in channels.values():
        return
    guild: discord.Guild = channel.guild
    author: discord.Member = message.author
    e = discord.Embed()
    e.title = f"Chat from {guild.name}"
    e.colour = author.colour
    e.description = message.content

    for k in channels.keys():
        if k == channel.id:
            continue
        c: discord.TextChannel = await bot.get_channel(channels[k])
        await c.send(embed=e)