from PyPDF2 import PdfMerger

def merge_pdfs(files, output_path):
    merger = PdfMerger()
    for f in files:
        merger.append(f)
    merger.write(output_path)
    merger.close()
