from discord.ext import commands


class AnsuraContext(commands.Context):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
