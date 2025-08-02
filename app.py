from flask import Flask, request, send_file, jsonify, make_response
from flask_cors import CORS
import os
import uuid
import threading
from werkzeug.utils import secure_filename

from utils.merge import merge_pdfs
from utils.split import split_pdf_ranges
from utils.compress import compress_pdf
from utils.convert import (
    docx_to_pdf as docx_to_pdf_func,
    pdf_to_word as pdf_to_word_func,
    images_to_pdf,
    pdf_to_images,
    pptx_to_pdf,
    pdf_to_pptx,
    xlsx_to_pdf,
    pdf_to_xlsx,
    zip_files
)
from utils.remover import remove_background
from utils.imgTools import image_to_text, compress_image, upscale_image, to_jpg

import time
import datetime

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

TEMP_DIR = "temp"
os.makedirs(TEMP_DIR, exist_ok=True)

COMPRESSION_LEVELS = {
    "high": 30,     # maximum compression (lowest quality)
    "medium": 60,   # good balance
    "low": 85       # least compression (highest quality)
}


# -------------------- UTILITIES --------------------

def start_temp_cleanup(interval=60, max_age=300):
    def cleanup():
        now = time.time()
        for fname in os.listdir(TEMP_DIR):
            fpath = os.path.join(TEMP_DIR, fname)
            try:
                if os.path.isfile(fpath) and now - os.path.getmtime(fpath) > max_age:
                    os.remove(fpath)
                    print(f"[Cleanup] Deleted expired file: {fpath}")
                elif os.path.isdir(fpath):
                    # Check if any file inside is older than max_age
                    expired = all(now - os.path.getmtime(os.path.join(fpath, f)) > max_age
                                  for f in os.listdir(fpath))
                    if expired:
                        for f in os.listdir(fpath):
                            os.remove(os.path.join(fpath, f))
                        os.rmdir(fpath)
                        print(f"[Cleanup] Deleted expired folder: {fpath}")
            except Exception as e:
                print(f"[Cleanup Error] {e}")
        threading.Timer(interval, cleanup).start()

    cleanup()

def save_temp_file(file, prefix=""):
    filename = secure_filename(file.filename)
    temp_name = f"{prefix}{uuid.uuid4()}_{filename}"
    temp_path = os.path.join(TEMP_DIR, temp_name)
    file.save(temp_path)
    return temp_path, os.path.splitext(filename)[0]


def send_named_file(path, filename):
    response = make_response(send_file(
        path,
        as_attachment=True,
        download_name=filename,
        mimetype="application/pdf" if filename.endswith(".pdf") else None
    ))
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Expose-Headers"] = "Content-Disposition"
    return response

# -------------------- ROUTES --------------------

@app.route('/merge', methods=['POST'])
def merge():
    files = request.files.getlist('files')
    if not files:
        return jsonify({"error": "No files provided"}), 400

    paths = []
    base_name = None
    for f in files:
        path, name = save_temp_file(f)
        if not base_name:
            base_name = name
        paths.append(path)

    output_name = f"{base_name}_merged.pdf"
    output_path = os.path.join(TEMP_DIR, output_name)
    merge_pdfs(paths, output_path)

    return send_named_file(output_path, output_name)

@app.route('/compress', methods=['POST'])
def compress_route():
    file = request.files.get('file')
    power = request.form.get('power', "medium")
    if not file:
        return jsonify({"error": "No file uploaded"}), 400

    input_path, base_name = save_temp_file(file)
    output_name = f"{base_name}_compressed.pdf"
    output_path = os.path.join(TEMP_DIR, output_name)

    try:
        compress_pdf(input_path, output_path, power=power)
    except Exception as e:
        return jsonify({"error": f"Compression failed: {str(e)}"}), 500

    return send_named_file(output_path, output_name)

@app.route('/split', methods=['POST'])
def split_route():
    file = request.files.get('file')
    ranges = request.form.get('ranges')

    if not file or not ranges:
        return jsonify({"error": "File and page ranges are required"}), 400

    def parse_ranges(r):
        parts = r.split(",")
        result = []
        for part in parts:
            part = part.strip()
            if "-" in part:
                a, b = map(int, part.split("-"))
                result.append((a, b))
            else:
                page = int(part)
                result.append((page, page))
        return result

    try:
        # Save
        filename = secure_filename(file.filename)
        ext = os.path.splitext(filename)[1]
        unique_name = f"{uuid.uuid4()}{ext}"
        input_path = os.path.join(TEMP_DIR, unique_name)
        file.save(input_path)

        # Output dir
        base_name = os.path.splitext(filename)[0]
        split_dir = os.path.join(TEMP_DIR, f"split_{uuid.uuid4().hex}")
        os.makedirs(split_dir, exist_ok=True)

        # Split
        ranges_parsed = parse_ranges(ranges)
        split_paths = split_pdf_ranges(input_path, split_dir, ranges_parsed)

        # Zip
        zip_path = os.path.join(TEMP_DIR, f"{base_name}_split.zip")
        zip_files(split_paths, zip_path)

        return send_named_file(zip_path, os.path.basename(zip_path))

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route('/docx-to-pdf', methods=['POST'])
def docx_to_pdf_route():
    file = request.files.get('file')
    input_path, base_name = save_temp_file(file)
    output_path = os.path.join(TEMP_DIR, f"{base_name}.pdf")

    docx_to_pdf_func(input_path, output_path)

    return send_named_file(output_path, f"{base_name}.pdf")

@app.route('/pdf-to-docx', methods=['POST'])
def pdf_to_word_route():
    file = request.files.get('file')
    input_path, base_name = save_temp_file(file)
    output_path = os.path.join(TEMP_DIR, f"{base_name}.docx")

    pdf_to_word_func(input_path, output_path)

    return send_named_file(output_path, f"{base_name}.docx")

@app.route('/images-to-pdf', methods=['POST'])
def images_to_pdf_route():
    files = request.files.getlist('files')
    if not files:
        return jsonify({"error": "No images uploaded"}), 400

    image_paths = []
    base_name = None
    for f in files:
        path, name = save_temp_file(f)
        image_paths.append(path)
        if not base_name:
            base_name = name

    output_path = os.path.join(TEMP_DIR, f"{base_name}_combined.pdf")
    images_to_pdf(image_paths, output_path)

    return send_named_file(output_path, os.path.basename(output_path))

@app.route('/pdf-to-images', methods=['POST'])
def pdf_to_images_route():
    file = request.files.get('file')
    original_name = os.path.splitext(file.filename or "document")[0]
    file_bytes = file.read()

    image_paths = pdf_to_images(file_bytes)
    zip_path = os.path.join(TEMP_DIR, f"{original_name}_images.zip")
    zip_files(image_paths, zip_path)

    return send_named_file(zip_path, os.path.basename(zip_path))

@app.route('/pptx-to-pdf', methods=['POST'])
def pptx_to_pdf_route():
    file = request.files.get('file')
    input_path, base_name = save_temp_file(file)
    output_path = os.path.join(TEMP_DIR, f"{base_name}.pdf")

    pptx_to_pdf(input_path, output_path)

    return send_named_file(output_path, f"{base_name}.pdf")

@app.route('/pdf-to-pptx', methods=['POST'])
def pdf_to_pptx_route():
    file = request.files.get('file')
    input_path, base_name = save_temp_file(file)
    output_path = os.path.join(TEMP_DIR, f"{base_name}.pptx")

    pdf_to_pptx(input_path, output_path)

    return send_named_file(output_path, f"{base_name}.pptx")

@app.route('/xlsx-to-pdf', methods=['POST'])
def xlsx_to_pdf_route():
    file = request.files.get('file')
    input_path, base_name = save_temp_file(file)
    output_path = os.path.join(TEMP_DIR, f"{base_name}.pdf")

    xlsx_to_pdf(input_path, output_path)

    return send_named_file(output_path, f"{base_name}.pdf")

@app.route('/pdf-to-xlsx', methods=['POST'])
def pdf_to_xlsx_route():
    file = request.files.get('file')
    input_path, base_name = save_temp_file(file)
    output_path = os.path.join(TEMP_DIR, f"{base_name}.xlsx")

    pdf_to_xlsx(input_path, output_path)

    return send_named_file(output_path, f"{base_name}.xlsx")

## ----- IMAGE -----

@app.route('/remove-bg', methods=['POST'])
def remove_bg_route():
    file = request.files.get('file')
    if not file:
        return jsonify({"error": "No image uploaded"}), 400

    input_path, base_name = save_temp_file(file)
    output_path = os.path.join(TEMP_DIR, f"{base_name}_nobg.png")

    try:
        remove_background(input_path, output_path)
    except Exception as e:
        return jsonify({"error": f"Background removal failed: {str(e)}"}), 500

    return send_named_file(output_path, os.path.basename(output_path))

@app.route('/image-to-text', methods=['POST'])
def image_to_text_route():
    file = request.files.get('file')
    lang = request.form.get('lang', 'en') 

    if not file:
        return jsonify({"error": "No image uploaded"}), 400

    input_path, _ = save_temp_file(file)

    try:
        text = image_to_text(input_path, lang)
        return jsonify({"text": text})
    except Exception as e:
        return jsonify({"error": f"OCR failed: {str(e)}"}), 500


@app.route('/image-compress', methods=['POST'])
def compress_image_route():
    file = request.files.get('file')
    level = request.form.get('power', 'medium').lower()

    if not file:
        return jsonify({"error": "No image uploaded"}), 400

    if level not in COMPRESSION_LEVELS:
        return jsonify({"error": "Invalid compression level. Choose low, medium, or high."}), 400

    quality = COMPRESSION_LEVELS[level]

    input_path, base_name = save_temp_file(file)
    output_path = os.path.join(TEMP_DIR, f"{base_name}_compressed.jpg")

    try:
        compress_image(input_path, output_path, quality=quality)
    except Exception as e:
        return jsonify({"error": f"Image compression failed: {str(e)}"}), 500

    return send_named_file(output_path, os.path.basename(output_path))


@app.route('/upscale', methods=['POST'])
def upscale_route():
    file = request.files.get('file')
    scale = int(request.form.get('scale', 2))
    if not file:
        return jsonify({"error": "No file uploaded"}), 400
    if scale < 1 or scale > 4:
        return jsonify({"error": "Scale must be 1-4"}), 400

    input_path, base_name = save_temp_file(file)
    output_path = os.path.join(TEMP_DIR, f"{base_name}_upscaled.jpg")

    try:
        upscale_image(input_path, output_path, scale)
    except Exception as e:
        return jsonify({"error": f"Upscaling failed: {str(e)}"}), 500

    return send_named_file(output_path, os.path.basename(output_path))

@app.route('/to-jpg', methods=['POST'])
def to_jpg_route():
    file = request.files.get('file')
    if not file:
        return jsonify({"error": "No image uploaded"}), 400
    input_path, base_name = save_temp_file(file)
    output_path = os.path.join(TEMP_DIR, f"{base_name}.jpg")
    
    try:
        to_jpg(input_path, output_path)
    except Exception as e:
        return jsonify({"error": f"Conversion to JPG failed: {str(e)}"}), 500
    
    return send_named_file(output_path, os.path.basename(output_path))

@app.route('/')
def home():
    return "PDF API is running"

if __name__ == "__main__":
    start_temp_cleanup()  # Every 60 seconds, deletes files older than 300s (5 min)
    app.run(debug=True)
