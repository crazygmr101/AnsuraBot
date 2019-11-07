"""
await member.guild.get_channel(586199960198971418).send(
            "Welcome to United Minecrafters, " + member.mention + "!
            Be sure to read " +
            "what cookie left you in " +
            member.guild.get_channel(599974490662764545).mention +
            ", and read " + member.guild.get_channel(600014362719158297).mention + ". " +


"""
import discord
import random

welcome = ["Hiya, {0}, and welcome to United Minecrafters!",
           "Welcome to United Minecrafters, {0}!"]
rules = ["Be sure to read what cookie left you in {0}, and read {1}."]
more = ["If you need more help, do `%server` and I'll DM you some stuff about us."]

def build(member: discord.Member):
    return random.choice(welcome).format(member.mention) + " " + \
           random.choice(rules).format(member.guild.get_channel(599974490662764545).mention,
                                       member.guild.get_channel(600014362719158297).mention) + " " + \
           random.choice(more)