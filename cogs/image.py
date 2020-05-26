import os

import PIL
import discord
from PIL import ImageOps, ImageFilter
from PIL.Image import Image, WEB, ADAPTIVE
from discord.ext import commands
import math
import asyncio

class Image(commands.Cog):
    def __init__(self, bot: discord.ext.commands.Bot):
        self.bot = bot
        self.counter = 100000
        self.lock = asyncio.Lock()

    @commands.command(aliases=["ihelp"])
    async def imagehelp(self, ctx: commands.Context, cmd: str = None):
        if cmd:
            cmd = cmd.lower()
        clist = [
            "rotate [n] - rotates an image n degrees counter-clockwise",
            "autocontrast [cutoff] - stretches the image over the widest range possible, cutting off a percentage "
            "of pixels off the edge of the histogram, defaulting to 0 - image is converted to RGB first, then back to RGBAp",
            "invert - inverts the image's colors",
            "grayscale - grayscales an image",
            "sepia - turns an image to sepia, equivalent to colorize 704214",
            "posterize [n] - keeps n bits of the image's colors",
            "solarize [n] - inverts values with a luminance above n. n defaults to 128 or half-brightness - image is converted to RGB first, then back to RGBA",
            "flip - flips an image top-to-bottom",
            "mirror - flips an image right-to-left",
            "blur [n] - applies a gaussian blur with a radius of n pixels. n defaults to 2",
            "boxblur [n] - applies a box blur with a radius of n pixels. n defaults to 2",
            "sharpen [radius] [percent] [threshold] - applies an unsharp mask. Blur radius defaults to 2, unsharp "
            "strength percent defaults to 150, and the minimum brightness change (threshold) that will be sharpened "
            "defaults to 3. See https://en.wikipedia.org/wiki/Unsharp_masking#Digital_unsharp_masking",
            "scale [n] - scales an image by n times, with bicubic filtering",
            "pscale [n] - scales an image by n times, with nearest pixel filtering",
            "scaleto [w] [h] - scales an image to w x h, with bicubic filtering",
            "pscaleto [w] [h] - scales an image to w x h, with nearest pixel filtering",
            "scalexy [w] [h] - scales an image by relative width and height with bicubic pixel filtering",
            "pscalexy [w] [h] - scales an image by relative width and height with nearest pixel filtering",
            "potography - applies %image pscalexy 0.05 0.25, pscalexy 20 4, posterize 2, sepia, rotate 25",
            "matrix [w] [h] - scales the image to a matrix of w by h, and scales it back to the image size",
            "colorize [rgb] - colorize an image",
            "bw - converts an image to only black and white - image is converted to RGB first, then back to RGBA",
            "luma - converts an image to grayscale according to apparent brightness - image is converted to RGB first, then back to RGBA",
            "format [format] - select the output format for the final image (jpg, gif, png)",
            "convert [params] - convert an image's colorspace - **Note: this will stop some filters from working, as"
            "some require an RGB color space** - params can be `bw` (1 bit), `rgb`, `rgba`, `luma` (no color), `web` "
            "(web-optimizes GIF palette), `adaptive n` (adaptive color palette, where n is an optional number of "
            "colors, defaulting to 256, and must be less than 256)"
        ]
        cmds = [cmd.split(" ")[0] for cmd in clist]
        if not cmd:
            await ctx.send(embed=discord.Embed(
                title="Image help filters",
                description=", ".join(cmds),
                colour=discord.Colour.blue()
            ).set_footer(text="Do `%imagehelp filter` to view detailed help for a filter"))
            return
        if cmd not in cmds:
            await ctx.send(embed=discord.Embed(
                title="Invalid image filter",
                description="Available filters: " + ", ".join(cmds),
                colour=discord.Colour.red()
            ).set_footer(text="Do `%imagehelp filter` to view detailed help for a filter"))
        else:
            await ctx.send(embed=discord.Embed(
                title=f"Image filter: {cmd}",
                description="\n".join(a.strip() for a in clist[cmds.index(cmd)].split("-"))
            ))

    @commands.command()
    async def image(self, ctx: commands.Context, filter_list: str = None):
        """
        Do `%ihelp` to view filter list, and `%ihelp filter` to view help for a filter
        """
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
            await ctx.send("I don't understand that kind of image ): Give me a jpg, jpeg, png, or gif")
            return
        f = open("attachments/" + str(message.id) + self._fname(attachment.filename), "wb+")
        await attachment.save(f)
        f.close()
        code = False
        try:
            code, msg, size = await self._process_commands(" ".join(ctx.message.content.split(" ")[1::]), f.name)
            if code is True:
                await ctx.send(content=f"{self._fsize(size)}", file=discord.File(msg))
        except commands.ConversionError as e:
            await ctx.send(str(e))
        finally:
            print(f.name)
            os.remove(f.name)
            os.remove(msg)

    def _fsize(self, size_bytes: int):
        if size_bytes == 0:
            return "0B"
        size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return "%s %s" % (s, size_name[i])

    def _color(self, clr: str):
        if len(clr) == 3:
            clr = f"{clr[0]}{clr[0]}{clr[1]}{clr[1]}{clr[2]}{clr[2]}"
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

    async def _process_commands(self, command: str, path: str):
        ar = [x.split(" ") for x in [a.strip(" ") for a in command.split(',')]]
        im: Image = PIL.Image.open(path)
        # im.load()
        im = im.convert("RGBA")
        print(ar)
        fmt = "png"
        for e in ar:
            for i in range(3):
                e.append(None)
            if e[0] == "convert":
                mode = e[1]
                if not mode or mode not in "bw,rgb,rgba,luma,web,adaptive":
                    raise commands.ConversionError("Unknown conversion mode", original=None)
                if mode == "bw":
                    im = im.convert("1")
                if mode in ["rgb", "rgba"]:
                    im = im.convert(mode.upper())
                if mode == "luma":
                    im = im.convert("L")
                if mode == "web":
                    im = im.convert("P")
                if mode == "adaptive":
                    im = im.convert("P", palette=ADAPTIVE, colors=min(int(e[2]), 256) if e[2] else 256)
            if e[0] == "format":
                if not e[1] or e[1] not in "png,jpg,gif".split(","):
                    raise commands.ConversionError(f"Invalid output format {e[1]}", original=None)
                fmt = e[1]
            if e[0] == "bw":
                im = im.convert("1").convert("RGBA")
            if e[0] == "luma":
                im = im.convert("L").convert("RGBA")
            if e[0] == "autocontrast":
                im = im.convert("RGB")
                im = ImageOps.autocontrast(im, int(e[1]) if e[1] else 0)
                im = im.convert("RGBA")
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
                im = ImageOps.posterize(im, int(e[1]) if e[1] else 128)
            if e[0] == "solarize":
                im = im.convert("RGB")
                if len(e) > 1:
                    a = int(e[1])
                else:
                    a = 128
                im = ImageOps.solarize(im, a)
                im = im.convert("RGBA")
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
            if e[0] == "scaleto":
                im = im.resize((int(e[1]), int(e[2])), PIL.Image.BICUBIC)
            if e[0] == "pscaleto":
                im = im.resize((int(e[1]), int(e[2])), PIL.Image.NEAREST)
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
        async with self.lock:
            self.counter += 1
        b = str(self.counter) + "." + fmt  # + a[-1]
        im.save(b)
        return True, b, os.path.getsize(b)

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
