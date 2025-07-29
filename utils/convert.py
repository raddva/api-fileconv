import os
import uuid
import subprocess
from pdf2image import convert_from_bytes
from docx2pdf import convert as docx_convert
from pdf2docx import Converter
from PIL import Image
from pptx import Presentation
import pandas as pd
import pdfplumber
import fitz  # PyMuPDF
import zipfile
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape, A4

def zip_images(image_paths, zip_path):
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for path in image_paths:
            arcname = os.path.basename(path)
            zipf.write(path, arcname)

# DOCX to PDF
def docx_to_pdf(input_path, output_path):
    docx_convert(input_path, output_path)


# PDF to DOCX
def pdf_to_word(input_path, output_path):
    cv = Converter(input_path)
    cv.convert(output_path, start=0, end=None)
    cv.close()


# Images to PDF
def images_to_pdf(file_paths, output_path):
    images = [Image.open(f).convert("RGB") for f in file_paths]
    images[0].save(output_path, save_all=True, append_images=images[1:])


# PDF to Images
def pdf_to_images(file_bytes):
    os.makedirs("temp", exist_ok=True)
    pdf = fitz.open(stream=file_bytes, filetype="pdf")
    output_paths = []

    for i, page in enumerate(pdf):
        pix = page.get_pixmap(dpi=200)
        path = f"temp/page_{uuid.uuid4().hex}_{i+1}.png"
        pix.save(path)
        output_paths.append(path)

    pdf.close()
    return output_paths

# PPTX to PDF
def pptx_to_pdf(input_path, output_path):
    prs = Presentation(input_path)
    image_paths = []

    for i, slide in enumerate(prs.slides):
        img = Image.new('RGB', (1280, 720), 'white')  # blank slide
        img_path = f'temp/slide_{uuid.uuid4().hex}_{i+1}.png'
        img.save(img_path)
        image_paths.append(img_path)

    c = canvas.Canvas(output_path, pagesize=landscape(A4))
    for img_path in image_paths:
        c.drawImage(img_path, 0, 0, width=landscape(A4)[0], height=landscape(A4)[1])
        c.showPage()
    c.save()


# PDF to PPTX
def pdf_to_pptx(input_path, output_path):
    images = pdf_to_images(open(input_path, 'rb').read())
    prs = Presentation()
    for img_path in images:
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        slide.shapes.add_picture(img_path, 0, 0, width=prs.slide_width)
    prs.save(output_path)


# XLSX to PDF
def xlsx_to_pdf(input_path, output_path):
    df = pd.read_excel(input_path)
    c = canvas.Canvas(output_path, pagesize=A4)

    x, y = 50, 800
    for i, row in df.iterrows():
        line = ", ".join([str(cell) for cell in row])
        c.drawString(x, y, line[:120])  # crude text draw
        y -= 15
        if y < 50:
            c.showPage()
            y = 800

    c.save()



# PDF to XLSX
def pdf_to_xlsx(input_path, output_path):
    all_data = []
    with pdfplumber.open(input_path) as pdf:
        for page in pdf.pages:
            table = page.extract_table()
            if table:
                df = pd.DataFrame(table[1:], columns=table[0])
                all_data.append(df)
    if all_data:
        result = pd.concat(all_data, ignore_index=True)
        result.to_excel(output_path, index=False)
    else:
        raise ValueError("No tables found in PDF.")
