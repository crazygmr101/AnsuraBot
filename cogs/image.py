import os

import PIL
import discord
from PIL import ImageOps, ImageFilter
from PIL.Image import Image
from discord.ext import commands


class Image(commands.Cog):
    def __init__(self, bot: discord.ext.commands.Bot):
        self.bot = bot

    @commands.command(aliases=["ihelp"])
    async def imagehelp(self, ctx: commands.Context, cmd: str = None):
        if cmd:
            cmd = cmd.lower()
        clist = [
            "rotate [n] - rotates an image n degrees counter-clockwise",
            "autocontrast - stretches the image over the widest range possible",
            "invert - inverts the image's colors",
            "grayscale - grayscales an image",
            "sepia - turns an image to sepia",
            "posterize [n] - keeps n bits of the image's colors",
            "solarize [n] - inverts values with a luminance above n. n defaults to 128 or half-brightness",
            "flip - flips an image top-to-bottom",
            "mirror - flips an image right-to-left",
            "blur [n] - applies a gaussian blur with a radius of n pixels. n defaults to 2",
            "boxblur [n] - applies a box blur with a radius of n pixels. n defaults to 2",
            "sharpen [radius] [percent] [threshold] - applies an unsharp mask. Blur radius defaults to 2, unsharp "
            "strength percent defaults to 150, and the minimum brightness change (threshold) that will be sharpened "
            "defaults to 3. See https://en.wikipedia.org/wiki/Unsharp_masking#Digital_unsharp_masking",
            "scale [n] - scales an image, with bicubic filtering",
            "pscale [n] - scales an image, with nearest pixel filtering",
            "scalexy [w] [h] - scales an image by relative width and height with bicubic pixel filtering",
            "pscalexy [w] [h] - scales an image by relative width and height with nearest pixel filtering",
            "potography - applies %image pscalexy 0.05 0.25, pscalexy 20 4, posterize 2, sepia, rotate 25",
            "matrix [w] [h] - scales the image to a matrix of w by h, and scales it back to the image size",
            "colorize [rgb] - colorize an image"
        ]
        cmds = [cmd.split(" ")[0] for cmd in clist]
        if not cmd:
            await ctx.send(embed=discord.Embed(
                title="Image help filters",
                description=", ".join(cmds),
                colour=discord.Colour.blue()
            ).set_footer(text="Do `!imagehelp filter` to view detailed help for a filter"))
            return
        if cmd not in cmds:
            await ctx.send(embed=discord.Embed(
                title="Invalid image filter",
                description="Available filters: " + ", ".join(cmds),
                colour=discord.Colour.red()
            ).set_footer(text="Do `!imagehelp filter` to view detailed help for a filter"))
        else:
            await ctx.send(embed=discord.Embed(
                title=f"Image filter: {cmd}",
                description="\n".join(a.strip() for a in clist[cmds.index(cmd)].split("-"))
            ))

    @commands.command()
    async def image(self, ctx: commands.Context, filter_list: str = None):
        message: discord.Message = ctx.message
        print(message.attachments)
        if filter_list is None:
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
        code = False
        try:
            code, msg = self._process_commands(" ".join(ctx.message.content.split(" ")[1::]), f.name)
            if code is True:
                await ctx.send(file=discord.File(msg))
        except commands.ConversionError as e:
            await ctx.send(str(e))
        print(f.name)
        os.remove(f.name)
        os.remove(msg)

    def _color(self, clr: str):
        if len(clr) == 3:
            clr = "".join(c + c for c in clr.split())
        if len(clr) == 6:
            try:
                c = tuple(int(clr[i:i + 2], 16) for i in range(0, len(clr), 2))
                return c
            except:
                raise commands.ConversionError("Oops! There's an invalid color ): Colors must be formatted "
                                               "`rgb` or `rrggbb`",
                                               original=None)
        raise commands.ConversionError("Oops! There's an invalid color ): Colors must be formatted "
                                       "`rgb` or `rrggbb`",
                                       original=None)

    def _process_commands(self, command: str, path: str):
        ar = [x.split(" ") for x in [a.strip(" ") for a in command.split(',')]]
        im: Image = PIL.Image.open(path)
        # im.load()
        im = im.convert("RGBA")
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
            if e[0] == "colorize":
                im = ImageOps.colorize(ImageOps.grayscale(im),
                                       (0, 0, 0), (255, 255, 255),
                                       mid=self._color(e[1]))
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
            if e[0] == "boxblur":
                if len(e) > 1:
                    a = int(e[1])
                else:
                    a = 2
                im = im.filter(ImageFilter.BoxBlur(a))
            if e[0] == "sharpen":
                for i in range(3):
                    e.append(None)
                im = im.filter(ImageFilter.UnsharpMask(int(e[1]) if e[1] else 2,
                                                       int(e[2]) if e[2] else 150,
                                                       int(e[3]) if e[3] else 3))
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
        b = path + ".png"  # + a[-1]
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
