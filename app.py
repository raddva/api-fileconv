from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import tempfile
import os
import uuid
import threading

from utils.merge import merge_pdfs
from utils.split import split_pdf
from utils.convert import (
    docx_to_pdf as docx_to_pdf_func,
    pdf_to_word as pdf_to_word_func,
    images_to_pdf,
    pdf_to_images,
    pptx_to_pdf,
    pdf_to_pptx,
    xlsx_to_pdf,
    pdf_to_xlsx,
    zip_images
)

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000"], supports_credentials=True)

os.makedirs("temp", exist_ok=True)

# AUTO DELETE TEMP FILES AFTER DELAY
def schedule_file_deletion(file_path, delay=300):
    def delete_file():
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"Deleted: {file_path}")
        except Exception as e:
            print(f"Error deleting file {file_path}: {e}")

    timer = threading.Timer(delay, delete_file)
    timer.start()


@app.route('/merge', methods=['POST'])
def merge():
    files = request.files.getlist('files')
    if not files:
        return jsonify({"error": "No files provided"}), 400

    input_paths = []
    for file in files:
        filename = f"{uuid.uuid4()}.pdf"
        path = os.path.join("temp", filename)
        file.save(path)
        input_paths.append(path)
        schedule_file_deletion(path)

    merged_path = os.path.join("temp", f"{uuid.uuid4()}_merged.pdf")
    merge_pdfs(input_paths, merged_path)
    schedule_file_deletion(merged_path)

    return send_file(merged_path, as_attachment=True)


@app.route('/docx-to-pdf', methods=['POST'])
def docx_to_pdf_route():
    file = request.files.get('file')
    if not file:
        return jsonify({"error": "No file uploaded"}), 400

    input_path = os.path.join("temp", f"{uuid.uuid4()}.docx")
    output_path = os.path.join("temp", f"{uuid.uuid4()}.pdf")

    file.save(input_path)
    docx_to_pdf_func(input_path, output_path)

    schedule_file_deletion(input_path)
    schedule_file_deletion(output_path)

    return send_file(output_path, as_attachment=True)


@app.route('/pdf-to-word', methods=['POST'])
def pdf_to_word_route():
    file = request.files.get('file')
    if not file:
        return jsonify({"error": "No file uploaded"}), 400

    input_path = os.path.join("temp", f"{uuid.uuid4()}.pdf")
    output_path = os.path.join("temp", f"{uuid.uuid4()}.docx")

    file.save(input_path)
    pdf_to_word_func(input_path, output_path)

    schedule_file_deletion(input_path)
    schedule_file_deletion(output_path)

    return send_file(output_path, as_attachment=True)


@app.route('/images-to-pdf', methods=['POST'])
def images_to_pdf_route():
    files = request.files.getlist('files')
    if not files:
        return jsonify({"error": "No images uploaded"}), 400

    input_paths = []
    for f in files:
        path = os.path.join("temp", f"{uuid.uuid4()}.png")
        f.save(path)
        input_paths.append(path)
        schedule_file_deletion(path)

    output_path = os.path.join("temp", f"{uuid.uuid4()}.pdf")
    images_to_pdf(input_paths, output_path)
    schedule_file_deletion(output_path)

    return send_file(output_path, as_attachment=True)


@app.route('/pdf-to-images', methods=['POST'])
def pdf_to_images_route():
    file = request.files['file']
    file_bytes = file.read()

    image_paths = pdf_to_images(file_bytes)

    # Create temporary zip file
    zip_filename = f"{uuid.uuid4().hex}_images.zip"
    zip_path = os.path.join("temp", zip_filename)

    zip_images(image_paths, zip_path)

    # Clean up files
    schedule_file_deletion(zip_path)
    for img_path in image_paths:
        schedule_file_deletion(img_path)

    return send_file(zip_path, as_attachment=True)


@app.route('/pptx-to-pdf', methods=['POST'])
def pptx_to_pdf_route():
    file = request.files.get('file')
    input_path = os.path.join("temp", f"{uuid.uuid4()}.pptx")
    output_path = os.path.join("temp", f"{uuid.uuid4()}.pdf")
    file.save(input_path)
    pptx_to_pdf(input_path, output_path)
    schedule_file_deletion(input_path)
    schedule_file_deletion(output_path)
    return send_file(output_path, as_attachment=True)


@app.route('/pdf-to-pptx', methods=['POST'])
def pdf_to_pptx_route():
    file = request.files.get('file')
    input_path = os.path.join("temp", f"{uuid.uuid4()}.pdf")
    output_path = os.path.join("temp", f"{uuid.uuid4()}.pptx")
    file.save(input_path)
    pdf_to_pptx(input_path, output_path)
    schedule_file_deletion(input_path)
    schedule_file_deletion(output_path)
    return send_file(output_path, as_attachment=True)


@app.route('/xlsx-to-pdf', methods=['POST'])
def xlsx_to_pdf_route():
    file = request.files.get('file')
    input_path = os.path.join("temp", f"{uuid.uuid4()}.xlsx")
    output_path = os.path.join("temp", f"{uuid.uuid4()}.pdf")
    file.save(input_path)
    xlsx_to_pdf(input_path, output_path)
    schedule_file_deletion(input_path)
    schedule_file_deletion(output_path)
    return send_file(output_path, as_attachment=True)


@app.route('/pdf-to-xlsx', methods=['POST'])
def pdf_to_xlsx_route():
    file = request.files.get('file')
    input_path = os.path.join("temp", f"{uuid.uuid4()}.pdf")
    output_path = os.path.join("temp", f"{uuid.uuid4()}.xlsx")
    file.save(input_path)
    pdf_to_xlsx(input_path, output_path)
    schedule_file_deletion(input_path)
    schedule_file_deletion(output_path)
    return send_file(output_path, as_attachment=True)


@app.route('/')
def home():
    return "PDF API is running"


if __name__ == "__main__":
    app.run(debug=True)
