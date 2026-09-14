"""Experimental 16:9 Among Us draft reader. Local OCR, no screenshot files."""
import asyncio
import re
from PIL import Image, ImageChops, ImageDraw


def remove_caret(image):
    """Remove a trailing tall, narrow caret in the tested Among Us font/layout."""
    rgb = image.convert('RGB')
    channels = rgb.split()
    light = ImageChops.lighter(ImageChops.lighter(channels[0], channels[1]), channels[2])
    mask = light.point(lambda x: 255 if x < 100 else 0)
    bounds = mask.getbbox()
    if bounds:
        tall = []
        for x in range(bounds[0], bounds[2]):
            column = mask.crop((x, 0, x+1, mask.height)).getbbox()
            if column and column[3]-column[1] > mask.height*.55:
                tall.append(x)
        if tall and max(tall)-min(tall) < mask.height*.2:
            ImageDraw.Draw(light).rectangle((min(tall)-1, 0, max(tall)+2, mask.height), fill=255)
    # Normalize green/white backgrounds without modifying letter shapes.
    return light.convert('RGBA')


async def recognize(image, language='nb'):
    from winrt.windows.media.ocr import OcrEngine
    from winrt.windows.globalization import Language
    from winrt.windows.graphics.imaging import SoftwareBitmap, BitmapPixelFormat
    from winrt.windows.storage.streams import DataWriter
    engine = OcrEngine.try_create_from_language(Language(language))
    if engine is None:
        raise ValueError('Windows OCR language is unavailable. Install Norwegian OCR support.')
    writer = DataWriter()
    bitmap = None
    try:
        writer.write_bytes(image.convert('RGBA').tobytes('raw', 'BGRA'))
        bitmap = SoftwareBitmap.create_copy_from_buffer(writer.detach_buffer(),
            BitmapPixelFormat.BGRA8, image.width, image.height)
        result = await engine.recognize_async(bitmap)
        return result.text.strip()
    finally:
        if bitmap:
            bitmap.close()
        writer.close()


def regions(image):
    w, h = image.size
    if abs(w / h - 16 / 9) > .025 or w < 1280:
        raise ValueError('Among Us OCR currently requires a 16:9 game window, at least 1280 pixels wide.')
    def crop(box):
        return image.crop(tuple(round(v * (w if i % 2 == 0 else h)) for i, v in enumerate(box)))
    draft = crop((.190, .750, .668, .824))
    count = crop((.731, .702, .776, .731))
    return draft, count


def validate_read(text, counter):
    match = re.fullmatch(r'(\d{1,3})\s*/\s*100', counter.strip())
    if not match or int(match[1]) > 100:
        raise ValueError('Could not identify the Among Us chat field and character counter.')
    count = int(match[1])
    if len(text) != count:
        raise ValueError(f'Could not read the complete chat draft ({len(text)} of {count} characters). Nothing was replaced; shorten the message and try again.')
    if any(ord(c) < 32 for c in text):
        raise ValueError('The chat draft could not be read as a single line.')
    return text


def read_image(image):
    draft, count = regions(image)
    async def run():
        text = await recognize(remove_caret(draft))
        counter = await recognize(count, 'en-GB')
        return validate_read(text, counter)
    return asyncio.run(run())
