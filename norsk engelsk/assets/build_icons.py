"""Rebuild raster Windows icons from the same simple vector geometry as chatshift.svg.

Development utility only; requires Pillow. The app uses the committed PNG directly.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

folder = Path(__file__).resolve().parent
scale = 4
image = Image.new('RGBA', (256*scale, 256*scale))
d = ImageDraw.Draw(image)

def box(coords):
    return tuple(int(c*scale) for c in coords)

def line(points, color, width):
    points = [(int(x*scale), int(y*scale)) for x, y in points]
    d.line(points, fill=color, width=width*scale, joint='curve')
    radius = width*scale/2
    for x, y in points:
        d.ellipse((x-radius, y-radius, x+radius, y+radius), fill=color)

d.rounded_rectangle(box((4, 4, 251, 251)), radius=54*scale, fill='#090d18', outline='#273a53', width=2*scale)
outline = [(67,43),(193,43),(216,66),(216,165),(193,188),(119,188),(66,221),(66,188),(40,162),(40,70),(67,43)]
glow = Image.new('RGBA', image.size)
g = ImageDraw.Draw(glow)
g.line([box(p) for p in outline], fill='#986dff', width=8*scale, joint='curve')
image = Image.alpha_composite(image, glow.filter(ImageFilter.GaussianBlur(9*scale)))
d = ImageDraw.Draw(image)
d.polygon([box(p) for p in outline], fill='#142139')
line(outline, '#aa8bff', 5)
line([(78,92),(179,92),(158,71)], '#66ffe1', 13)
line([(179,92),(158,113)], '#66ffe1', 13)
line([(178,143),(78,143),(99,122)], '#b89aff', 13)
line([(78,143),(99,164)], '#b89aff', 13)
line([(168,213),(185,213)], '#66ffe1', 5)
line([(199,213),(213,213)], '#66ffe1', 5)
image = image.resize((256, 256), Image.Resampling.LANCZOS)
image.save(folder/'chatshift.png')
image.resize((72, 72), Image.Resampling.LANCZOS).save(folder/'chatshift-header.png')
image.save(folder/'chatshift.ico', sizes=[(16,16),(24,24),(32,32),(48,48),(64,64),(128,128),(256,256)])
