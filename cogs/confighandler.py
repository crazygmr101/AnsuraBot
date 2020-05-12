import os

import discord
import yaml
from discord.ext import commands


class ConfigHandler:
    def __init__(self, bot):
        print("Loading config handler")
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
            docs = yaml.dump(y, file)
            file.close()
        print(" Opening config file")
        self.config_file = open("config.yaml")
        self.data = yaml.full_load(self.config_file)
        self.config_file.close()
        print("Config Handler Loaded")

    def save(self):
        print("Saving config file")
        self.config_file = open("config.yaml", "w")
        yaml.dump(self.data, self.config_file)
        self.config_file.close()
        print("Config file saved")

    def reload(self):
        print("Reloading config file")
        self.config_file = open("config.yaml")
        self.data = yaml.full_load(self.config_file)
        self.config_file.close()
        print("Config file reloaded")


class ConfigCog(commands.Cog):
    def __init__(self, bot):
        print("Adding Configuration cog")
        self.bot = bot
        self.cfg = ConfigHandler(bot)
        print("Configuration cog added")

    @commands.command()
    @commands.is_owner()
    async def reload(self, ctx: commands.Context):
        await ctx.send("Reloading config...")
        self.cfg.reload()
        await ctx.send("Reloaded!")

    @commands.command()
    @commands.is_owner()
    async def save(self, ctx: commands.Context):
        await ctx.send("Saving config...")
        self.cfg.reload()
        await ctx.send("Saved!")


def setup(bot):
    bot.add_cog(ConfigCog(bot))
