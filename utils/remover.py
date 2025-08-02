from rembg import remove
from PIL import Image

def remove_background(input_image_path, output_image_path):
    with Image.open(input_image_path) as img:
        output = remove(img)
        output.save(output_image_path)
