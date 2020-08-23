import asyncio
import logging
from typing import Optional

import aiohttp
from discord.ext import commands

from lib.database import AnsuraDatabase
from lib.voicemanager import VoiceManager
from .ansuracontext import AnsuraContext


class AnsuraBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super(AnsuraBot, self).__init__(*args, **kwargs)
        self.db: AnsuraDatabase = AnsuraDatabase()
        self.vm: Optional[VoiceManager] = None

    async def on_message(self, message):
        await self.invoke(await self.get_context(message, cls=AnsuraContext))

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
