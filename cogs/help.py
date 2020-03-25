from typing import List

from discord.ext import commands
import discord
import core.help as HE

class Help(commands.Cog):
    def __init__(self, bot: discord.ext.commands.Bot):
        self.bot = bot
        print("Help cog loaded")

    @commands.command(pass_context=True)
    async def help(self, ctx: commands.Context, cmd: str = None):
        await self.help_(ctx,cmd)

    @commands.command(pass_context=True)
    async def helps(self, ctx: commands.Context, cmd: str = None):
        await self.helps_(ctx,cmd)

    async def helps_(self, ctx: commands.Context, cmd: str = None):
        if cmd is None:
            await self.help_(ctx, "helps")
            return
        cmds = []
        ar: List[HE.HelpEntry] = HE.HelpEntries.cmds
        for i in ar:
            if cmd.lower() in i.help.lower() or \
               cmd.lower() in i.cmd.lower() or \
               cmd.lower() in i.notes.lower() or \
               cmd.lower() in " ".join(i.usage).lower():
                cmds.append(i)
        if len(cmds) == 1:
            await self.help_(ctx,cmds[0].cmd)
            return
        e = discord.Embed()
        e.title = "Search" if len(cmds) > 0 else "No results"
        e.add_field(name="Term",value=cmd)
        if len(cmds) > 0:
            e.add_field(name="Commands",
                        value=", ".join(i.cmd for i in cmds))
            e.description = "Do %help for the command to view help"
        await ctx.send(embed=e)


    async def help_(self, ctx: commands.Context, cmd: str = None):
        if cmd is None:
            ar = HE.HelpEntries.cmds
            a = []
            for i in ar:
                a.append(i.cmd)
            e = discord.Embed()
            e.title = "Command list"
            e.description = "Do `%help command_name` for detailed help"
            e.add_field(name="Commands", value=", ".join(a))
            await ctx.send(embed=e)
        else:
            e: discord.Embed = HE.HelpEntries.get_embed(cmd)
            if e is not None:
                await ctx.send(embed=e)
            else:
                await self.helps_(ctx,cmd)

def setup(bot):
    bot.add_cog(Help(bot))