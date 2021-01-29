import sys
import traceback

from discord.ext import commands

from ansura import AnsuraBot, AnsuraContext


class ErrorHandler(commands.Cog):
    def __init__(self, bot: AnsuraBot):
        self.bot = bot

    # @commands.Cog.listener()
    async def on_command_error(self, ctx: AnsuraContext, error: Exception):
        print(traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr))
        if hasattr(ctx.command, 'error'):
            return

        ignored = (commands.CommandNotFound, commands.UserInputError)

        error = getattr(error, 'original', error)

        if isinstance(error, ignored):
            print(error)

        elif isinstance(error, commands.MissingPermissions):
            await ctx.send_error("You can't do that! >.>\n" +
                                 str(error))

        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send_error("Oops. Doesn't look like I was given the proper permissions for that!\n" +
                                 str(error))

        else:
            print(error)


def setup(bot):
    bot.add_cog(ErrorHandler(bot))
