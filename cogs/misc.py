from typing import Union

import discord
from discord.ext import commands
import core.util.HelpEntries as HE
import random

class Misc(commands.Cog):
    def __init__(self, bot: discord.ext.commands.Bot):
        self.bot = bot
        print("Misc cog loaded")

    @commands.command(aliases=["pbc", "chicken"])
    async def placeblock_chicken(self, ctx: commands.Context):
        await ctx.send(random.choice("🐔,🐤,🐥,🐣".split(",")))

    @commands.command()
    async def maddify(self, ctx: commands.Context):
        e = discord.Embed()
        msg: str = ctx.message.content
        msg_o : discord.Message = ctx.message
        msg = " ".join(msg.split(" ")[1::])
        replacements = [
            "a,e,i,o,u,A,E,I,O,U".split(","),
            "ä,ë,ï,ö,ü,Ä,Ë,Ï,Ö,Ü".split(",")
        ]
        for i in range(len(replacements[0])):
            msg = msg.replace(replacements[0][i], replacements[1][i])
        author: discord.Member = ctx.author
        e.colour = author.color
        e.title = author.display_name
        e.description = msg
        await msg_o.delete()
        await ctx.send(embed=e)

    @commands.command(aliases=["av"])
    async def avatar(self, ctx: discord.ext.commands.Context, user: Union[discord.Member, discord.User] = None):
        if user is None:
            user = ctx.author
        await ctx.send(user.avatar_url)



def setup(bot):
    bot.add_cog(Misc(bot))
    HE.HelpEntries.register("placeblock_chicken", "%placeblock_chicken", "Does a <@276365523045056512>.",
                            "Placeblock chicken. Never forget.\nNOTE: This is NOT *placeblovk fhivkrn*.\n"
                            "Aliases: pbc, chicken")
    HE.HelpEntries.register("maddify", "%maddify message", "It's ëpïc")
    HE.HelpEntries.register("avatar", "%avatar @user", "Gets avatar for user", "Aliases: av")