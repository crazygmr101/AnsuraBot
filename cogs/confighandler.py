import os

import discord
import yaml
from discord.ext import commands

from ansura.ansurabot import AnsuraBot
from ansura.ansuracontext import AnsuraContext


class ConfigHandler:
    def __init__(self, bot: AnsuraBot):
        print("[CONFIG] Loading internal config handler")
        bot.cfg = self
        self.bot = bot
        self.data = {}

    async def start(self):
        if not os.path.exists("config.yaml"):
            file = open("config.yaml", "w")
            print(" Config file not present, creating default")
            g: discord.Guild
            # y = [{str(g.id): {"streamer-role": 0, "streamer-announce-channel": 1}} for g in bot.guilds]
            y = {}
            print(self.bot.guilds)
            async for g in self.bot.fetch_guilds():
                y[g.id] = {"streamer-role": 0, "streamer-announce-channel": 1}
            yaml.dump(y, file)
            file.close()
        print("[CONFIG] Opening config file")
        self.config_file = open("config.yaml")
        self.data = yaml.full_load(self.config_file)
        self.config_file.close()
        print("[CONFIG] Internal config handler loaded")

    def save(self):
        print('[CONFIG] Saving..', end="")
        self.config_file = open("config.yaml", "w")
        yaml.dump(self.data, self.config_file)
        self.config_file.close()
        print("Done")

    def reload(self):
        print('[CONFIG] Reloading..', end="")
        self.config_file = open("config.yaml")
        self.data = yaml.full_load(self.config_file)
        self.config_file.close()
        print("Done")


class ConfigCog(commands.Cog):
    def __init__(self, bot):
        print("[CONFIG] Initializing")
        self.bot = bot
        self.cfg = ConfigHandler(bot)
        print("[CONFIG] Initialized")

    @commands.command()
    @commands.is_owner()
    async def reload(self, ctx: AnsuraContext):
        await ctx.send("Reloading streamer config...")
        self.cfg.reload()
        await ctx.send("Reloaded!")

    @commands.command()
    @commands.is_owner()
    async def save(self, ctx: AnsuraContext):
        await ctx.send("Saving streamer config...")
        self.cfg.reload()
        await ctx.send("Saved!")


def setup(bot):
    bot.add_cog(ConfigCog(bot))
