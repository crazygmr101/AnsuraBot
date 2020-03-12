# Invite Link
[Click here](https://discordapp.com/api/oauth2/authorize?client_id=603640674234925107&permissions=0&redirect_uri=https%3A%2F%2Fdiscordapp.com%2Fapi%2Foauth2%2Fauthorize&scope=bot) to invite me.

# Image Commands - %image
Usage - `%image filter_list`<br><br>
Valid Filters
- `rotate [n]` - rotates an image `n` degrees counter-clockwise.
- `autocontrast` - stretches the image over the widest range possible
- `invert` - inverts the image's colors
- `grayscale`
- `sepia`
- `posterize [n]` - keeps `n` bits of the image's colors
- `solarize [n]` - inverts values with a luminance above `n`
  - `n` defaults to *128* or half-brightness
- `flip` - flips an image top-to-bottom
- `mirror` - flips an image right-to-left
- `blur [n]` - applies a gaussian blur with a radius of `n` pixels
  - `n` defaults to *2*
- `scale [n]` - scales an image, with bicubic filtering<sup>1</sup>
- `pscale [n]` - scales an image, with nearest pixel filtering<sup>1</sup>
- `scalexy [w] [h]` - scales an image by relative width and height<sup>1</sup>
    with bicubic pixel filtering
- `pscalexy [w] [h]` - scales an image by relative width and height<sup>1</sup>
    with nearest pixel filtering
- `potography` - applies `%image pscalexy 0.05 0.25, pscalexy 20 4, posterize 2,
    sepia, rotate 25`
- `matrix [w] [h]` - scales the image to a matrix of `w` by `h`, and scales it
    back to the image size

<sup>1</sup> - `n`, `x`, and `y` are all *relative*. A value of 1 means no
    scaling is done (100%) 
