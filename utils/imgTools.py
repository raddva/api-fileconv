import easyocr
import os
from PIL import Image


readers = {
    "en": easyocr.Reader(['en'], gpu=False),
    "id": easyocr.Reader(['id'], gpu=False),
    "en-id": easyocr.Reader(['en', 'id'], gpu=False)
}

def image_to_text(image_path, lang):
    reader = readers.get(lang, readers[lang])
    results = reader.readtext(image_path, detail=0)
    return "\n".join(results)

def compress_image(input_path, output_path, quality):
    with Image.open(input_path) as img:
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")

        img.save(output_path, "JPEG", optimize=True, quality=quality)

def upscale_image(input_path, output_path, scale=2):
    with Image.open(input_path) as img:
        new_size = (int(img.width * scale), int(img.height * scale))
        upscaled = img.resize(new_size, Image.LANCZOS)
        upscaled.save(output_path)

def to_jpg(input_path, output_path):
    with Image.open(input_path) as img:
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        img.save(output_path, "JPG")

    return output_path