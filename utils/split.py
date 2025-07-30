from PyPDF2 import PdfReader, PdfWriter
from pathlib import Path

def split_pdf_ranges(file, output_dir, ranges):
    """
    Split PDF into multiple files based on page ranges.
    ranges = [(1, 3), (5, 5)] will extract pages 1–3 and 5 into two separate files.
    Returns a list of split file paths.
    """
    reader = PdfReader(file)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    output_files = []

    for idx, (start, end) in enumerate(ranges, start=1):
        writer = PdfWriter()
        for i in range(start - 1, end):
            writer.add_page(reader.pages[i])
        output_path = output_dir / f"split_part_{idx}.pdf"
        with open(output_path, 'wb') as f_out:
            writer.write(f_out)
        output_files.append(str(output_path))

    return output_files
