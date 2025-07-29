from PyPDF2 import PdfReader, PdfWriter

def split_pdf(file, output_path, start_page, end_page):
    reader = PdfReader(file)
    writer = PdfWriter()
    for i in range(start_page - 1, end_page):  # zero-indexed
        writer.add_page(reader.pages[i])
    with open(output_path, 'wb') as f_out:
        writer.write(f_out)
