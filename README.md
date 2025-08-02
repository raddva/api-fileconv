# 🧾 File Converter Backend

This is the backend for a full-stack file converter application built using Flask and Python.

## 📦 Features

- Convert between:
  - PDF ↔️ DOCX
  - PDF ↔️ PPTX
  - PDF ↔️ XLSX
  - PDF ↔️ Images
- Split, merge, and compress PDF files
- Remove Image Background, Upscale Image, & Image to Text Conversion (new!) 
- Designed to be used with a Next.js frontend
- Dockerized for easy deployment

## 📁 Project Structure

```bash
backend/
├── temp/ # Temporary working files (ignored in Git)
├── utils/ # All core conversion utilities
│ ├── convert.py # DOCX ↔️ PDF, IMG ↔️ PDF
│ ├── merge.py # PDF merge logic
│ ├── split.py # PDF split logic
├── app.py # Flask app entry point
├── Dockerfile # Docker setup for deployment
├── render.yaml # Render deploy config
└── requirements.txt # Python dependencies
```

## 🚀 Getting Started

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
2. **Run the Server**
   ```bash
   python app.py
   ```
3. **Docker (optional)**
   ```bash
   docker build -t file-converter .
   docker run -p 5000:5000 file-converter
   ```

## 📡 API Documentation

You can find the API Documentation at [Postman]() _(Coming Soon)_


## 🌐 Deployment

This project has been deployed to [Railway](https://api-fileconv.up.railway.app/)
