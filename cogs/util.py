from typing import Union

from discord.ext import commands
import discord
import core.help as HE
import core.database as AD

class Util(commands.Cog):
    def __init__(self, bot: discord.ext.commands.Bot):
        self.bot = bot
        print("Util cog loaded")
        self.db = AD.AnsuraDatabase()

    @commands.command()
    async def xbox(self, ctx: discord.ext.commands.Context, username):
        self.db.set_gaming_record(ctx.author.id, "xboxlive", username)
        await ctx.send(ctx.author.mention + ": Set to " + username)

    @commands.command()
    async def mojang(self, ctx: discord.ext.commands.Context, username):
        self.db.set_gaming_record(ctx.author.id, "mojang", username)
        await ctx.send(ctx.author.mention + ": Set to " + username)

    @commands.command(aliases=["yt"])
    async def youtube(self, ctx: discord.ext.commands.Context, username):
        self.db.set_gaming_record(ctx.author.id, "youtube", username)
        await ctx.send(ctx.author.mention + ": Set to " + username)

    @commands.command()
    async def mixer(self, ctx: discord.ext.commands.Context, username):
        self.db.set_gaming_record(ctx.author.id, "mixer", username)
        await ctx.send(ctx.author.mention + ": Set to " + username)

    @commands.command()
    async def twitch(self, ctx: discord.ext.commands.Context, username):
        self.db.set_gaming_record(ctx.author.id, "twitch", username)
        await ctx.send(ctx.author.mention + ": Set to " + username)

    @commands.command(aliases=["gt"])
    async def gametags(self, ctx: discord.ext.commands.Context, user: Union[discord.Member, discord.User] = None):
        if user is None:
            user = ctx.author
        rec = self.db.lookup_gaming_record(user.id)
        e = discord.Embed()
        e.colour = user.color
        e.title = user.display_name
        e.add_field(name="XBox", value=rec[2] if rec[2] is not None else "N/A")
        e.add_field(name="Mojang", value=rec[1] if rec[1] is not None else "N/A")
        e.add_field(name="Youtube", value=rec[3] if rec[3] is not None else "N/A")
        e.add_field(name="Twitch", value=rec[4] if rec[4] is not None else "N/A")
        e.add_field(name="Mixer", value=rec[5] if rec[5] is not None else "N/A")
        await ctx.send(embed=e)

    @commands.command()
    async def ping(self, ctx: discord.ext.commands.Context):
        await ctx.send("Pong :D " + str(int(self.bot.latency * 1000)) + "ms")

    @commands.command()
    async def tthru(self, ctx:discord.ext.commands.Context):
        if ctx.author.id != 267499094090579970:
            return
        s = input(">")
        while (s != "quit"):
            await ctx.send(s)
            s = input(">")

    @commands.command()
    async def role(self, ctx: discord.ext.commands.Context, r: discord.Role):
        def val_or_space(val: str): return "-" if val == "" else val
        e = discord.Embed()
        e.title = "Role: " + r.name
        e.colour = r.colour
        online = []
        offline = []
        m: discord.Member
        for m in r.members:
            if m.status == discord.Status.offline:
                if len(offline) < 30: offline.append(m)
            else:
                if len(online) < 30: online.append(m)
            if len(offline) > 29 and len(online) > 29:
                break
        if len(r.members) == 0:
            e.description = f"No members with role"
        else:
            e.description = f"Listing {len(online) + len(offline)} of {len(r.members)}"
            e.add_field(name=f"Online ({len(online)})", value=val_or_space("".join([m.mention for m in online])))
            e.add_field(name=f"Offline ({len(offline)})", value=val_or_space("".join([m.mention for m in offline])))
        await ctx.send(embed=e)

    @role.error
    async def role_error(self, ctx: discord.ext.commands.Context, error: Exception):
        if isinstance(error, discord.ext.commands.ConversionError) or\
           isinstance(error, discord.ext.commands.BadArgument):
            await ctx.send("Oops. I can't seem to find that role. Double-check capitalization and spaces.")
        else:
            raise error


    @commands.command(pass_context=True)
    async def who(self, ctx: discord.ext.commands.Context, tag: str):
        db = self.db
        records = db.get_all()
        #id, mojang, xbox, youtube, twitch, mixer
        users = []
        async with ctx.channel.typing():
            for r in records:
                for k in r.keys():
                    if k != "id" and r[k] == tag:
                        users.append([r["id"], k, r[k]])
        if len(users) == 0:
            await ctx.send("Tag " + tag + " not found in the database.")
            return
        s = "```\nSearch results for " + tag + "\n"
        not_in_guild = []
        for i in users:
            u: discord.User = (await self.bot.fetch_user(int(i[0])))
            s += u.name + "#" + u.discriminator + " - " + i[1] + ": " + i[2] + "\n"
        s += "```"
        await ctx.send(s)

    @commands.command()
    @commands.bot_has_permissions(embed_links=True)
    @commands.has_permissions(manage_messages=True)
    async def embed(self, ctx: discord.ext.commands.Context, title: str, desc: str, ch: discord.TextChannel = None,
                    color: discord.Colour = None, id: int = 0):
        color = ctx.author.color if color is None else color
        ch = ctx.channel if ch is None else ch
        e = discord.Embed()
        e.title = title
        e.description = desc
        e.colour = color
        e.set_author(icon_url=ctx.author.avatar_url, name=ctx.author.name)
        if id == 0:
            await ch.send(embed=e)
            await ctx.send()
        else:
            message = await ch.fetch_message(id)
            await message.edit(embed=e)

    @commands.Cog.listener()
    async def on_command(self, ctx: discord.ext.commands.Context):
        print(str(ctx.command) + " command called with " + str(ctx.invoked_with))
        print("\tUser: " + str(ctx.message.author.id))
        print("\t>>>>> " + ctx.message.content)



def setup(bot):
    bot.add_cog(Util(bot))
    HE.HelpEntries.register("ping", "%ping", "Checks bot latency")
    HE.HelpEntries.register("xbox", "%xbox username", "Sets your xbox username")
    HE.HelpEntries.register("mojang", "%mojang username", "Sets your mojang username")
    HE.HelpEntries.register("mixer", "%mixer username", "Sets your mixer username")
    HE.HelpEntries.register("youtube", "%youtube username", "Sets your youtube username", "Alias: yt")
    HE.HelpEntries.register("twitch", "%twitch username", "Sets your twitch username")
    HE.HelpEntries.register("gametags", "%gametags @user", "Look up a user's gamertags", "Alias: gt")
    HE.HelpEntries.register("who","%who tag","Find a user#1234 by gamertag")
    HE.HelpEntries.register("role", "%role rolename", "Lists users in a role")
    HE.HelpEntries.register("embed", "%embed title description channel color <id if editing>",
                            "Sends or edits an embed", "`channel` defaults to current channel\n"
                                                       "`color` defaults to author's role color")