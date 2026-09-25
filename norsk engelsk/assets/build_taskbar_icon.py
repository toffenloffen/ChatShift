"""Render the existing two-arrow logo with strokes sized for Windows icons."""
from pathlib import Path
from PIL import Image, ImageDraw


def render(size):
    scale = 4
    image = Image.new('RGBA', (size * scale, size * scale))
    draw = ImageDraw.Draw(image)
    def points(values):
        return [(round(x * size * scale), round(y * size * scale)) for x, y in values]
    draw.rounded_rectangle((0, 0, size * scale - 1, size * scale - 1),
                           radius=round(size * scale * .21), fill='#142139')
    width = max(2, round(size * .085)) * scale
    for color, path in (
        ('#66ffe1', [( .17,.34),(.80,.34),(.62,.17)]),
        ('#66ffe1', [( .80,.34),(.62,.51)]),
        ('#c4acff', [( .83,.67),(.20,.67),(.38,.50)]),
        ('#c4acff', [( .20,.67),(.38,.84)]),
    ):
        draw.line(points(path), fill=color, width=width, joint='curve')
    return image.resize((size, size), Image.Resampling.LANCZOS)


if __name__ == '__main__':
    folder = Path(__file__).resolve().parent
    frames = [render(size) for size in (16, 20, 24, 32, 40, 48, 64, 128, 256)]
    frames[-1].save(folder / 'chatshift-taskbar.ico',
                    sizes=[frame.size for frame in frames], append_images=frames[:-1])
