"""Antialias small controller illustrations without external image assets."""
from pathlib import Path
import os
import tkinter.font as tkfont


def render(canvas, width, height):
    try:
        from PIL import Image, ImageDraw, ImageFont, ImageTk
    except ImportError:
        return None  # Source-only installations can still use the native diagram.
    scale = 3
    image = Image.new('RGB', (width*scale, height*scale), canvas.cget('background'))
    draw = ImageDraw.Draw(image)
    for item in canvas.find_all():
        kind = canvas.type(item)
        points = canvas.coords(item)
        fill = canvas.itemcget(item, 'fill') or None
        if kind == 'text':
            spec = tkfont.Font(font=canvas.itemcget(item, 'font')).actual()
            size = abs(spec['size']) * (canvas.winfo_fpixels('1i') / 72 if spec['size'] > 0 else 1)
            filename = 'segoeuib.ttf' if spec['weight'] == 'bold' else 'segoeui.ttf'
            path = Path(os.environ.get('WINDIR', 'C:/Windows')) / 'Fonts' / filename
            try:
                font = ImageFont.truetype(str(path), round(size*scale))
            except OSError:
                font = ImageFont.load_default(size=round(size*scale))
            draw.text((points[0]*scale, points[1]*scale), canvas.itemcget(item, 'text'),
                      font=font, fill=fill, anchor='mm')
            continue
        outline = canvas.itemcget(item, 'outline') or None if kind != 'line' else fill
        stroke = max(1, round(float(canvas.itemcget(item, 'width') or 1)*scale))
        if kind in ('oval', 'rectangle'):
            method = draw.ellipse if kind == 'oval' else draw.rectangle
            method([p*scale for p in points], fill=fill, outline=outline, width=stroke)
        elif kind in ('polygon', 'line'):
            pairs = list(zip(points[::2], points[1::2]))
            if kind == 'polygon' and canvas.itemcget(item, 'smooth') in ('1', 'true'):
                curve = []
                for index, center in enumerate(pairs):
                    prev, following = pairs[index-1], pairs[(index+1) % len(pairs)]
                    start = ((prev[0]+center[0])/2, (prev[1]+center[1])/2)
                    end = ((following[0]+center[0])/2, (following[1]+center[1])/2)
                    for step in range(16):
                        t = step/16
                        curve.append(tuple((1-t)**2*start[a]+2*(1-t)*t*center[a]+t*t*end[a] for a in (0, 1)))
                pairs = curve
            pairs = [(x*scale, y*scale) for x, y in pairs]
            if kind == 'polygon':
                draw.polygon(pairs, fill=fill)
                if outline:
                    draw.line(pairs+[pairs[0]], fill=outline, width=stroke, joint='curve')
            else:
                draw.line(pairs, fill=fill, width=stroke, joint='curve')
    return ImageTk.PhotoImage(image.resize((width, height), Image.Resampling.LANCZOS), master=canvas)
