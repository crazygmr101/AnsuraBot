import glob
import logging
import os

import discord
import dotenv
from discord.ext import commands

from ansura import AnsuraBot
from cogs.crosschat import Crosschat
from lib.voicemanager import VoiceManager

logging.basicConfig(level=logging.WARN)

# os.chdir(os.path.dirname(sys.argv[0]))

dotenv.load_dotenv(".env")


def get_prefix(_bot: AnsuraBot, message: discord.Message):
    return commands.when_mentioned_or(_bot.db.get_prefix(message.guild.id) if message.guild else "%")(_bot, message)


bot = AnsuraBot(command_prefix=get_prefix, intents=discord.Intents.all())
bot.remove_command('help')

bot.vm = VoiceManager(bot)

bot.initial_extensions = ['cogs.gamertags',
                          'cogs.administration',
                          'cogs.fun',
                          'cogs.owner',
                          'cogs.image',
                          'cogs.error-handler',
                          'cogs.voice',
                          'cogs.help',
                          'cogs.crosschat',
                          'slash.time',
                          "slash.minecraft"]
if __name__ == '__main__':
    for ext in bot.initial_extensions:
        print(f"[COGS] Loading {ext}")
        bot.load_extension(ext)

filelist = glob.glob("*.mp3")
for file in filelist:
    try:
        os.remove(file)
    except FileNotFoundError:
        print(f"err removing {file}")
filelist = glob.glob("attachments/*")
for file in filelist:
    try:
        os.remove(file)
    except FileNotFoundError:
        print(f"err removing {file}")


@bot.event
async def on_ready():
    if bot.user.id == 603640674234925107:
        import cogs.dbl
        await bot.add_cog(cogs.dbl.DBL(bot))

    xchat: Crosschat = bot.get_cog("Crosschat")
    await xchat.init_channels()
    await bot.change_presence(status=discord.Status.online, activity=discord.Game("%help"))
    print("Ansura online! :D")
    print(f" {len(bot.guilds)} Guilds")
    print(bot.user)


bot.run(os.getenv("ANSURA"))
