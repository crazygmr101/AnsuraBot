from typing import List, Union
import datetime

from discord.ext import commands
import discord


class MessageTracker:
    def __init__(self, bot):
        self.bot = bot

    async def get_last_message(self, member: discord.Member) -> discord.Message:
        guild: discord.Guild = member.guild
        now: datetime = datetime.datetime.now()
        channels: List[discord.TextChannel] = guild.text_channels
        msgs: List[discord.Message] = []
        for channel in channels:
            iter: List[discord.Message] = await channel.history(limit=250).flatten()
            for msg in iter:
                if msg.author == member:
                    msgs.append(msg)
                    break
        if len(msgs) == 0:
            return None
        msg: discord.Message = msgs[0]
        for m in msgs:
            if m.created_at < msg.created_at:
                msg = m
        return m

    async def get_last_message_embed(self, member: Union[discord.Member,discord.User]):
        e = discord.Embed()
        e.title = "Last message by " + member.display_name
        msg = await self.get_last_message(member)
        if msg is None:
            e.add_field(name="Uh oh...",value="I couldn't find that user =/")
        else:
            e.add_field(name="Timestamp",value=str(msg.created_at), inline=False)
            e.add_field(name="Message",value=str(msg.clean_content))
        return e
