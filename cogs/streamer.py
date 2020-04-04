import os
import cogs
import requests
from discord.ext import commands
import discord
from core.database import AnsuraDatabase

class Streamer(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        print("Streamer cog loading")
        print(" Opening mixer session...")
        self.db: AnsuraDatabase = bot.db
        self.mixer_key = os.getenv("MIXER")
        self.session = requests.Session()
        self.session.headers.update({'Client-ID': self.mixer_key})
        print(" Mixer session opened")
        print("Streamer cog loaded")

    def _add_stream_record(self, guild: discord.Guild):
        self.db.cursor.execute("insert into streamer values (?,?,?,?)", (guild.id, 0, "%user% is streaming!", 0))
        self.db.conn.commit()

    def _edit_stream_record(self, guild: discord.Guild, *, stream_role: int = None, stream_message: str = None,
                            stream_channel: int = None):
        if self._lookup_stream_record(guild=guild) is None:
            self._add_stream_record(guild)
        if stream_role: self.db.cursor.execute("update streamer set streamrole=? where guildid=?",
                                               (stream_role, guild.id))
        if stream_message: self.db.cursor.execute("update streamer set streammsg=? where guildid=?",
                                                  (stream_message, guild.id))
        if stream_channel: self.db.cursor.execute("update streamer set streamchannel=? where guildid=?",
                                                  (stream_channel, guild.id))
        self.db.conn.commit()

    def _has_stream_record(self, guild: discord.Guild):
        return self._lookup_stream_record(guild) is not None

    def _lookup_stream_record(self, guild: discord.Guild):
        if self.db.cursor.execute("select * from streamer where guildid=?", (guild.id,)).fetchone() is None:
            self._add_stream_record(guild)
        return self.db.cursor.execute("select * from streamer where guildid=?", (guild.id,)).fetchone()

    @commands.command()
    async def profile(self, ctx: commands.Context, profile_type: str, username: str):
        """
        Looks up a profile.
        - profile_type: Mixer
        - username: Username on the service
        """
        ptype = profile_type.lower()
        if ptype == "mixer":
            await self.mixer(ctx, username)
        else:
            await ctx.send("I don't recognize that profile type ):")

    async def mixer(self, ctx: commands.Context, user: str):
        resp = self.session.get('https://mixer.com/api/v1/channels/{}'.format(user))
        j = resp.json()

        embed = discord.Embed(title=(user + "'s Mixer"), color=0x0000ff)
        embed.add_field(name="Bio", value=j['user']['bio'], inline=False)
        embed.add_field(name="Latest Stream", value=j['name'], inline=False)
        embed.add_field(name="Total Viewers", value=j['viewersTotal'])
        embed.add_field(name="Viewers", value=j['viewersCurrent'])
        embed.add_field(name="Audience", value=j['audience'])
        embed.add_field(name="Online", value=j['online'])
        embed.set_thumbnail(url=j['user']['avatarUrl'])
        await ctx.send(embed=embed)

    @commands.command(aliases=["ssr","streamrole"])
    @commands.check_any(
        commands.has_permissions(manage_roles=True, manage_guild=True),
        commands.is_owner(),
        commands.has_permissions(administrator=True)
    )
    async def setstreamrole(self, ctx: commands.Context, role: discord.Role):
        """
        Sets the streamer role on a server
        """
        self._edit_stream_record(guild=ctx.guild, stream_role=role.id)
        await ctx.send(embed=discord.Embed(title="Role set", description=f"Streamer role set to {role.mention}"))

    @setstreamrole.error
    async def setstreamrole_error(self, ctx: discord.ext.commands.Context, error: Exception):
        if isinstance(error, discord.ext.commands.ConversionError) or\
           isinstance(error, discord.ext.commands.BadArgument):
            await ctx.send("Oops. I can't seem to find that role. Double-check capitalization and spaces.")
        else:
            raise error

    @commands.command(aliases=["ssc","streamch"])
    @commands.check_any(
        commands.has_permissions(manage_roles=True, manage_guild=True),
        commands.is_owner(),
        commands.has_permissions(administrator=True)
    )
    async def setstreamchannel(self, ctx: commands.Context, ch: discord.TextChannel):
        """
        Sets the streamer channel on a server
        """
        self._edit_stream_record(guild=ctx.guild, stream_channel=ch.id)
        await ctx.send(embed=discord.Embed(title="Channel set", description=f"Streamer role set to {ch.mention}"))

    @setstreamrole.error
    async def setstreamrole_error(self, ctx: discord.ext.commands.Context, error: Exception):
        if isinstance(error, discord.ext.commands.ConversionError) or\
           isinstance(error, discord.ext.commands.BadArgument):
            await ctx.send("Oops. I can't seem to find that channel. Double-check capitalization.")
        else:
            raise error

    @commands.command(aliases=["ssm", "streammsg"])
    @commands.check_any(
        commands.has_permissions(manage_roles=True, manage_guild=True),
        commands.is_owner(),
        commands.has_permissions(administrator=True)
    )
    async def setstreammessage(self, ctx: commands.Context, *, msg: str):
        """
        Sets the streamer message on a server
        """
        self._edit_stream_record(guild=ctx.guild, stream_message=msg)
        await ctx.send(embed=discord.Embed(title="Message set", description=f"Message set to:\n{msg}"))

    @commands.command(aliases=["gss"])
    async def getstreamsettings(self, ctx: commands.Context):
        """
        Gets the streamer role, channel, and message on a server
        """
        rec = self._lookup_stream_record(ctx.guild)
        role, msg, ch = rec[1], rec[2], rec[3]
        await ctx.send(embed=discord.Embed(title=f"Stream info in *{ctx.guild.name}*")
                       .add_field(name="Role", value=f"<@&{role}>" if role != 0 else "Not set")
                       .add_field(name="Message", value=msg)
                       .add_field(name="Channel", value=f"<#{ch}>" if ch != 0 else "Not set"))


def setup(bot):
    bot.add_cog(Streamer(bot))
