import fitz


def compress_pdf(input_path, output_path, power="medium"):
    """
    Compress a PDF by rendering each page as an image and saving at lower DPI.
    Works best for scanned/image-based PDFs.
    """
    dpi_settings = {
        "low": 50,
        "medium": 72,
        "high": 120
    }

    dpi = dpi_settings.get(power, 100)
    zoom = dpi / 72

    original = fitz.open(input_path)
    compressed = fitz.open()

    for page in original:
        pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom))
        img_bytes = pix.tobytes("jpeg")

        rect = fitz.Rect(0, 0, pix.width, pix.height)
        new_page = compressed.new_page(width=pix.width, height=pix.height)

        new_page.insert_image(rect, stream=img_bytes)

    compressed.save(output_path, deflate=True)
    original.close()
    compressed.close()
