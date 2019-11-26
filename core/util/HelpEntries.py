import core.util
from discord import Embed

class HelpEntries:
    cmds = []

    @classmethod
    def register(cls, command, usage, helpmsg, notes="N/A"):
        cls.cmds.append(core.util.HelpEntries.HelpEntry(command, usage, helpmsg, notes))
        """
        print("Help command registered: ")
        print("  [C] " + command)
        print("  [U] " + str(usage))
        print("  [H] " + helpmsg)
        if notes != "N/A":
            print("  [N] " + notes)
        """

    @classmethod
    def lookup(cls, cmd):
        for i in cls.cmds:
            if i.cmd == cmd:
                return i
        else:
            return None

    @classmethod
    def get_embed(cls, cmd):
        e = Embed()
        entry = cls.lookup(cmd)
        if entry == None:
            return None
        else:
            e.title = entry.cmd
            e.colour = 0x00ff00
            if type(entry.usage) is list:
                e.add_field(name="Usage", value="```" + "```\n```".join(entry.usage) + "```", inline=False)
            else:
                e.add_field(name="Usage", value="```"+entry.usage+"```",inline=False)
            e.add_field(name="Help", value=entry.help,inline=False)
            if entry.notes != "N/A":
                e.add_field(name="Notes", value=entry.notes)
            return e


class HelpEntry:
    def __init__(self, cmd: str, usage: str, help: str, notes:str=None):
        self.cmd = cmd
        self.usage = usage
        self.help = help
        self.notes = notes
