import glob

from discord.ext import commands
import re
import random
import logging
import os
import discord
from core.crosschat import Crosschat
import cogs

logging.basicConfig(level=logging.WARN)


def get_prefix(bot, message):
    prefixes = ['%']
    if not message.guild:
        return '%'
    return commands.when_mentioned_or(*prefixes)(bot,message)


bot = commands.Bot(command_prefix=get_prefix)
bot.remove_command('help')
xchat = Crosschat(bot)

initial_extensions = ['cogs.gamertags',
                      'cogs.administration', 'cogs.misc', 'cogs.gaming',
                      'cogs.fun', 'cogs.owner', 'cogs.image',
                      'cogs.error-handler', 'cogs.streamer', 'cogs.confighandler',
                      'cogs.dbl', 'cogs.timezones', 'cogs.tts', 'cogs.help']
if __name__ == '__main__':
    for ext in initial_extensions:
        print("= Adding " + ext + " =")
        bot.load_extension(ext)

filelist = glob.glob("*.mp3")
for file in filelist:
    try: os.remove(file)
    except: print(f"err removing {file}")


@bot.event
async def on_ready():
    await xchat.init_channels()
    await bot.change_presence(status=discord.Status.online, activity=discord.Game("%help"))
    print("Bot ready!")
    print(bot.cfg)
    await bot.cfg.start()

@bot.event
async def on_member_update(before: discord.Member, after: discord.Member):
    guild: discord.Guild = before.guild
    if not (discord.Streaming in [type(x) for x in after.activities] and
        discord.Streaming not in [type(x) for x in before.activities]):
        return
    streamer: cogs.streamer.Streamer = bot.get_cog("Streamer")
    rec = streamer._lookup_stream_record(guild)
    if rec is None: return
    if rec[1] == 0 or rec[3] == 0: return
    if rec[1] in [r.id for r in before.roles]:
        channel = guild.get_channel(rec[3])
        s: discord.Streaming
        for a in after.activities:
            if type(a) is discord.Streaming:
                s = a
                break
        msg = re.sub("%user.mention%", after.mention, rec[2])
        msg = re.sub("%user%", after.display_name, msg)
        msg = re.sub("%url%", s.url, msg)
        await channel.send(msg)

@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return

    if message.content == "/placeblock chicken":
        message.content = "%placeblock_chicken"
        await bot.process_commands(message)
        return
    hello_regex = r"^\s*(?:hi|hiya|hi there|hello|hei|hola|hey),?\s*(?:[Aa]nsura|<@!" + str(bot.user.id) + ">)[!\.]*\s*$"
    if message.content == "<@!" + str(bot.user.id) + ">":
        await message.channel.send(random.choice("I'm alive!,Hm?,Yea? :3,:D,That's me!".split(",")))
    if re.findall(hello_regex, message.content.lower(), re.MULTILINE).__len__() != 0:
        await message.channel.send(random.choice(["Hi, " + message.author.mention + " :3",
                                                  "Hey, " + message.author.display_name,
                                                  "Hello :D"]))
        return
    await xchat.xchat(message)
    await bot.get_cog("TTS").tts(message)
    await bot.process_commands(message)


bot.run(os.getenv("ANSURA"))
