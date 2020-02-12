import asyncio
import os
from typing import List

from PIL import ImageOps, ImageFilter
from discord.ext import commands
import discord
import core.util.HelpEntries as HE
import PIL
from PIL.Image import Image

class Image(commands.Cog):
    def __init__(self, bot: discord.ext.commands.Bot):
        self.bot = bot
        print("Image cog loaded")


    @commands.command()
    async def image(self, ctx: commands.Context, cmd: str = None):
        message: discord.Message = ctx.message
        print(message.attachments)
        if cmd is None:
            await ctx.send("I need a command telling me what to do with the image")
            return
        if not message.attachments or len(message.attachments) == 0:
            await ctx.send("I need an image! Attach it with your command as a file")
            return
        attachment: discord.Attachment = message.attachments[0]
        if not self._is_image(attachment.filename):
            await ctx.send("I don't understand that kind of image. Give me a jpg, jpeg, png, or gif")
            return
        f = open("attachments/" + str(message.id) + self._fname(attachment.filename), "wb+")
        await attachment.save(f)
        f.close()
        code, msg = self._process_commands(" ".join(ctx.message.content.split(" ")[1::]), f.name)
        if code is True:
            await ctx.send(file=discord.File(msg))
        print(f.name)
        os.remove(f.name)
        os.remove(msg)

    def _process_commands(self, command: str, path: str):
        ar = [x.split(" ") for x in [a.strip(" ") for a in command.split(',')]]
        im: Image = PIL.Image.open(path)
        # im.load()
        im = im.convert("RGB")
        print(ar)
        for e in ar:
            if e[0] == "autocontrast":
                im = ImageOps.autocontrast(im)
            if e[0] == "rotate":
                im = im.rotate(int(e[1]))
            if e[0] == "invert":
                im = ImageOps.invert(im)
            if e[0] == "grayscale":
                im = ImageOps.grayscale(im)
            if e[0] == "equalize":
                im = ImageOps.equalize(im)
            if e[0] == "sepia":
                im = ImageOps.colorize(ImageOps.grayscale(im),
                                       (0, 0, 0), (255, 255, 255),
                                       mid=(112, 66, 20))
            if e[0] == "posterize":
                im = ImageOps.posterize(im, int(e[1]))
            if e[0] == "solarize":
                if len(e) > 1:
                    a = int(e[1])
                else:
                    a = 128
                im = ImageOps.solarize(im, a)
            if e[0] == "flip":
                im = ImageOps.flip(im)
            if e[0] == "mirror":
                im = ImageOps.mirror(im)
            if e[0] == "blur":
                if len(e) > 1:
                    a = int(e[1])
                else:
                    a = 2
                im = im.filter(ImageFilter.GaussianBlur(a))
            if e[0] == "scale":
                im = ImageOps.scale(im, float(e[1]))
            if e[0] == "pscale":
                im = ImageOps.scale(im, float(e[1]), PIL.Image.NEAREST)
            if e[0] == "scalexy":
                im = im.resize((int(im.width * float(e[1])), int(im.height * float(e[2]))))
            if e[0] == "pscalexy":
                im = im.resize((int(im.width * float(e[1])), int(im.height * float(e[2]))), PIL.Image.NEAREST)
            if e[0] == "potografy":
                im = im.resize((int(im.width / 20), int(im.height / 4)), PIL.Image.NEAREST)
                im = im.resize((int(im.width * 20), int(im.height * 4)), PIL.Image.NEAREST)
                im = ImageOps.posterize(im, 2)
                im = ImageOps.colorize(ImageOps.grayscale(im),
                                       (0, 0, 0), (255, 255, 255),
                                       mid=(112, 66, 20))
                im = im.rotate(25)
            if e[0] == "matrix":
                size = (im.width, im.height)
                im = im.resize((int(e[1]), int(e[2])), PIL.Image.NEAREST)
                im = im.resize(size, PIL.Image.NEAREST)
        a = path.split(".")
        b = path + "." + a[-1]
        im.save(b)
        return True, b


    def _fname(self, url: str):
        return url.split("/")[-1]

    def _is_image(self, url: str):
        for i in "jpg,jpeg,png,gif".split(","):
            if url.endswith("." + i):
                return True
        else:
            return False

def setup(bot):
    bot.add_cog(Image(bot))