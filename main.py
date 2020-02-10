from discord.ext import commands
import re
import random
import logging
import os
import discord
from core.crosschat import Crosschat

logging.basicConfig(level=logging.WARN)


def get_prefix(bot, message):
    prefixes = ['%','>']
    if not message.guild:
        return '%'
    return commands.when_mentioned_or(*prefixes)(bot,message)


bot = commands.Bot(command_prefix=get_prefix)
bot.remove_command('help')
xchat = Crosschat(bot)

initial_extensions = ['cogs.util', 'cogs.conversation', 'cogs.map', 'cogs.help',
                      'cogs.administration', 'cogs.misc', 'cogs.minecraft',
                      'cogs.fun', 'cogs.owner']
if __name__ == '__main__':
    for ext in initial_extensions:
        bot.load_extension(ext)

@bot.event
async def on_ready():
    await xchat.init_channels()
    print("Bot ready!")


@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return

    if message.content == "/placeblock chicken":
        message.content = "%placeblock_chicken"
        await bot.process_commands(message)
        return
    """
    print("Message sent")
    print("\t" + message.content)
    print("\tin " + str(message.channel.id) + " by " + str(message.author.id))
    """
    hello_regex = r"^\s*(?:hi|hiya|hi there|hello|hei|hola|hey),?\s*(?:[Aa]nsura|<@603640674234925107>)[!\.]*\s*$"
    if message.content == "<@603640674234925107>":
        await message.channel.send(random.choice("I'm alive!,Hm?,Yea? :3,:D,That's me!".split(",")))
    if re.findall(hello_regex, message.content.lower(), re.MULTILINE).__len__() != 0:
        await message.channel.send("Hi, " + message.author.mention + " :3")
        return
    await xchat.xchat(message)
    await bot.process_commands(message)


bot.run(os.getenv("ANSURA"))
