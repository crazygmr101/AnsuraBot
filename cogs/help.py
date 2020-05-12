import inspect

import discord
from discord.ext import commands


class Help(commands.Cog):
    def __init__(self, bot: discord.ext.commands.Bot):
        self.bot = bot
        print("Help cog loaded")

    @commands.command(aliases=["h"])
    async def help(self, ctx: commands.Context, command: str = None):
        """Lists modules, or help for a command"""
        if not command:
            help = discord.Embed(title="Module List",
                                 description="Do `%commands modulename` to list commands within a module",
                                 color=0x004400)
            for i in self.bot.cogs:
                if self.bot.cogs[i].qualified_name.lower() not in ["configcog", "errorhandler", "dbl"]:
                    help.add_field(name=self.bot.cogs[i].qualified_name, value=self.bot.cogs[i].description or "_ _")
            await ctx.send(embed=help)
            return
        c: commands.Command = self.bot.get_command(command)
        if c is None:
            await ctx.send(embed=discord.Embed(
                title="Command not found",
                color=0xff0000,
                description=f"Command `{command}` not found"
            ))
            return
        else:
            arg_str = []
            p: inspect.Parameter
            for key in c.clean_params:
                p = c.clean_params[key]
                arg_str.append(f"<{p.name}:{p.default}>" if p.default.__class__ is not type else p.name)
            await ctx.send(embed=discord.Embed(
                title=c.qualified_name,
                description=f"`%{'[' if c.aliases else ''}"
                            f"{'|'.join(c.aliases + [c.name])}"
                            f"{']' if c.aliases else ''} "
                            f"{' '.join(arg_str)}`"
            ).add_field(
                name="Help",
                value=c.help or "No help available for this command"
            ).set_footer(text=f"Module: {c.cog.qualified_name}"))

    @commands.command(aliases=["cmds"])
    async def commands(self, ctx: commands.Context, module: str = None):
        """Lists commands in a module"""
        if module is None:
            await self.help(ctx)
            return
        c: commands.Cog = self.bot.get_cog(module.title()) or self.bot.get_cog(module.upper())
        if c is None:
            await ctx.send(embed=discord.Embed(
                title="Module not found",
                color=0xff0000,
                description=f"Module `{module}` not found, do `%help` for a list of modules"
            ))
            return
        i: commands.Command
        await ctx.send(embed=discord.Embed(title=c.qualified_name,
                                           description=((c.description + "\n" if c.description else "") +
                                                        "```css\n" +
                                                        "\n".join(
                                                            [
                                                                f"{i.qualified_name.ljust(20, ' ')}"
                                                                f"[{'|'.join(i.aliases) or ''}]"
                                                                for i in c.walk_commands()]
                                                        ) +
                                                        "```")
                                           ).set_footer(text="Do `%help command_name` for help on a command"))


def setup(bot):
    bot.add_cog(Help(bot))
