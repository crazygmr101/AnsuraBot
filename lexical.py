import discord
from core.parser import Parser
from core.geoloc import Geolocation
import random
import re

class Lexical:
    def __init__(self):
        self.p = Parser()
        self.g = Geolocation()

    async def answer(self, message: discord.Message):
        s = self.p.simplify(message.content)
        print(s)
        if s == "?" or s == "": return
        if s in "hey,hi,heyo,hiya,hello,hei,hola".split(","):
            await message.channel.send("Hi, " + message.author.mention + " :3")
            return
        if s.startswith("what time") or s.startswith("time"):
            ar = self.g.tzplace(s[(10 if s.startswith("what") else 5):])
            await message.channel.send("It is " + ar[0] + " in " + ar[1])
            return
        if s.startswith("where"):
            ar = self.g.locate(s[6:])
            await message.channel.send(s[6:] + " seems to be " + ar[2] + " at lat:" + str(ar[0]) + " lon:" + str(ar[1]))
            return
        await message.channel.send(random.choice("huh?,I don't understand.,whaaa?,=/,?,confuzzlement".split(",")))