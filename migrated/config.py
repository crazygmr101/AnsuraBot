import discord
from discord.ext import commands, tasks

from ansura import AnsuraBot, AnsuraContext


class Config(commands.Cog):
    def __init__(self, bot: AnsuraBot):
        self.bot = bot
        self.update_status.start()

    @commands.guild_only()
    @commands.command()
    async def prefix(self, ctx: AnsuraContext, prefix: str = None):
        if not prefix:
            await ctx.send_info(f"Prefix for this server is `{self.bot.db.get_prefix(ctx.guild.id)}`")
        else:
            author: discord.Member = ctx.author
            if not author.guild_permissions.administrator:
                raise commands.MissingPermissions("administrator")
            self.bot.db.set_prefix(ctx.guild.id, prefix)
            await ctx.send_info(f"Prefix for this server set to `{self.bot.db.get_prefix(ctx.guild.id)}`")

    @tasks.loop(seconds=300)
    async def update_status(self):
        await self.bot.wait_until_ready()
        await self.bot.change_presence(
            status=discord.Status.online,
            activity=discord.Activity(
                name=str(len(self.bot.guilds)) + " servers | %help",
                type=discord.ActivityType.watching
            )
        )


def setup(bot):
    bot.add_cog(Config(bot))
