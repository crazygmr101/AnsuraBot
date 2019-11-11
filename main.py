from discord.ext import commands
from lexical import Lexical
import re
import random
import logging
import os

logging.basicConfig(level=logging.WARN)


def get_prefix(bot, message):
    prefixes = ['%']
    if not message.guild:
        return '%'
    return commands.when_mentioned_or(*prefixes)(bot,message)


bot = commands.Bot(command_prefix=get_prefix)
bot.remove_command('help')
initial_extensions = ['cogs.util', 'cogs.conversation', 'cogs.serverhelp', 'cogs.map', 'cogs.help',
                      'cogs.administration', 'cogs.misc', 'cogs.minecraft']
if __name__ == '__main__':
    for ext in initial_extensions:
        bot.load_extension(ext)
lex = Lexical()

@bot.event
async def on_ready():
    print("Bot ready!")


@bot.event
async def on_message(message):
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
    if message.content.startswith("?") and False:
        await lex.answer(message)
    await bot.process_commands(message)


bot.run(os.getenv("ANSURA"))