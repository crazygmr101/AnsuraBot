import asyncio
import logging
import random
import re
from typing import Optional, Callable, Dict, Coroutine, Awaitable

import aiohttp
import inflect
from discord.ext import commands

from lib.database import AnsuraDatabase
from lib.slash_lib import SlashContext, process_slash
from lib.voicemanager import VoiceManager
from .ansuracontext import AnsuraContext


class AnsuraBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        print("[BOT] Initializing bot")
        self.db: AnsuraDatabase = AnsuraDatabase()
        super(AnsuraBot, self).__init__(*args, **kwargs)
        self.vm: Optional[VoiceManager] = None
        self.inflect: inflect.engine = inflect.engine()
        self.slashes: Dict[str, Callable[[SlashContext], Awaitable[None]]] = {}

        async def on_socket_response(msg):
            if msg["t"] != "INTERACTION_CREATE":
                return
            ctx = process_slash(self, msg)
            if ctx.cmd_signature in self.slashes:
                await self.slashes[ctx.cmd_signature](ctx)

        self.add_listener(on_socket_response, "on_socket_response")

    async def on_message(self, message):
        if message.author.bot:
            return

        if message.content == "/placeblock chicken":
            message.content = "%placeblock_chicken"
            await self.process_commands(message)
            return
        xchat = self.get_cog("Crosschat")
        hello_regex = rf"^\s*(?:hi|hiya|hi there|hello|hei|hola|hey),?\s*(?:[Aa]nsura|<@!{self.user.id}>)[!\.]*\s*$"
        if message.content == "<@!" + str(self.user.id) + ">":
            await message.channel.send(random.choice("I'm alive!,Hm?,Yea? :3,:D,That's me!".split(",")))
        if re.findall(hello_regex, message.content.lower(), re.MULTILINE).__len__() != 0:
            await message.channel.send(random.choice(["Hi, " + message.author.mention + " :3",
                                                      "Hey, " + message.author.display_name,
                                                      "Hello :D"]))
            return
        await xchat.xchat(message)
        await self.get_cog("Voice").tts(message)

        ctx = await self.get_context(message, cls=AnsuraContext)
        await self.invoke(ctx)

    async def start(self, *args, **kwargs):
        """|coro|
        A shorthand coroutine for :meth:`login` + :meth:`connect`.
        Raises
        -------
        TypeError
            An unexpected keyword argument was received.
        """
        bot = kwargs.pop('bot', True)
        reconnect = kwargs.pop('reconnect', True)
        if kwargs:
            raise TypeError("unexpected keyword argument(s) %s" % list(kwargs.keys()))

        for i in range(0, 6):
            try:
                await self.login(*args, bot=bot)
                break
            except aiohttp.ClientConnectionError as e:
                logging.warning(f"bot:Connection {i}/6 failed")
                logging.warning(f"bot:  {e}")
                logging.warning(f"bot: waiting {2 ** (i + 1)} seconds")
                await asyncio.sleep(2 ** (i + 1))
                logging.info("bot:attempting to reconnect")
        else:
            logging.error("bot: FATAL failed after 6 attempts")
            return

        await self.connect(reconnect=reconnect)
