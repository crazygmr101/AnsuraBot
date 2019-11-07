from discord.ext import commands
import discord
from discord.embeds import Embed
import core.util.HelpEntries as HE
import core.util.welcome_builder as WB

class ServerHelp(commands.Cog):
    def __init__(self, bot: discord.ext.commands.Bot):
        self.bot = bot
        print("Server help cog loaded")

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        await member.guild.get_channel(599974490662764545).send(WB.build(member))

    @commands.command()
    async def server(self, ctx: discord.ext.commands.Context):
        if ctx.author.dm_channel is None:
            await ctx.author.create_dm()
        e = Embed()
        e.title = "Welcome to United Minecrafters"
        e.description = "We are a server dedicated to giving" \
                        "All minecrafters a community no matter" \
                        "what you play on :3"
        e.add_field(name="XP",value="If you talk, you gain xp. You can check your xp "
                                    "and roles. You can check your level "
                                    "level in the #bot-spam channel with the command "
                                    "`.xp`.")
        e.add_field(name="Flowers", value="Flowers are our currency, buy waifus in #waifu-discuss, "
                                          "`.plant` some for your friends, and `.pick` stray flowers. "
                                          "Join in games, and get enough flowers to get *Rich* role and access"
                                          "to a 3rd game channel")
        e.add_field(name="MC Roles", value="We have a number of self-roles, which you can see buy using the"
                                           " command `.lsar`. Category 0 is all about your minecraft playing"
                                           " style. Category 3 is the type of minecraft you play. Note that"
                                           "Win10, XBox, and MCPE are all *Bedrock*. Do `.iam mc bedrock`,"
                                           " for instance, to give yourself the role, or react to the messages"
                                           " in #role-select.")
        e.add_field(name="Ping Roles", value="Category 4 roles are our pingable roles. Anyone can ping these roles, "
                                             "so keep that in mind if you join them. We ping them for updates, polls, "
                                             "and other players can ping them to get people to play or just join voice"
                                             "to talk :D")
        e.add_field(name="Misc Roles", value="Our *Waifu Stuff* role is for players to get access to the "
                                             "#waifu-stuff channel to level up, trade, and gift their waifus. The "
                                             "NadekoGamer role is to get access to the nadeko gaming channels, which"
                                             "can get spammy, so I recommend you mute them :3")
        e.add_field(name="Rules", value="Don't forget to read our rules. Mutes and bans are automatic, unless a mod"
                                        "sees fit to mute/kick/ban you before Cookie would")
        await ctx.author.dm_channel.send(embed=e)
        await ctx.author.dm_channel.send("Cookie (Nadeko)'s commands can be found at: https://nadeko.bot/commands")

def setup(bot):
    bot.add_cog(ServerHelp(bot))
    HE.HelpEntries.register("server", "%server", "Get info about our server. I must be able to DM you")