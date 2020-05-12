from discord.ext import commands


class ErrorHandler(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        print("Error handler loaded")

    # @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: Exception):
        if hasattr(ctx.command, 'error'):
            return

        ignored = (commands.CommandNotFound, commands.UserInputError)

        error = getattr(error, 'original', error)

        if isinstance(error, ignored):
            print(error)

        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("You can't do that! >.>\n" +
                           str(error))

        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send("Oops. Doesn't look like I was given the proper permissions for that!\n" +
                           str(error))

        else:
            print(error)


def setup(bot):
    bot.add_cog(ErrorHandler(bot))
