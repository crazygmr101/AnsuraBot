from discord.ext import commands
import discord


class Crosschat:
    def __init__(self, bot: commands.Bot):
        self.channels = {}
        ch: str = open("Assets/crosschat.txt",'r').read()
        print(ch)
        chl = ch.split("\n")
        print(chl)
        chl = [x.lstrip().rstrip() for x in chl]
        for i in chl:
            print(i)
            ar = i.split(":")
            self.channels[int(ar[0])] = int(ar[1])
        self.bot = bot
        print(self.channels)

    async def xchat(self, message: discord.Message):
        channel: discord.TextChannel = message.channel
        if channel.id not in self.channels.values():
            return

        guild: discord.Guild = channel.guild
        author: discord.Member = message.author
        e = discord.Embed()
        e.title = f"Chat from {guild.name}"
        e.colour = author.colour
        user: discord.User = message.author
        e.set_thumbnail(url=user.avatar_url)
        e.add_field(name=user.name + "#" + str(user.discriminator)[0:2] + "xx", value=message.content)
        for k in self.channels.keys():
            if self.channels[k] == channel.id:
                continue
            c: discord.TextChannel = self.bot.get_channel(self.channels[k])
            if c is not None:
                await c.send(embed=e)