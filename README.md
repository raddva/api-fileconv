# 🧾 File Converter Backend

This is the backend for a full-stack file converter application built using Flask and Python.

## 📦 Features

- Convert between:
  - PDF ↔️ DOCX
  - PDF ↔️ PPTX
  - PDF ↔️ XLSX
  - PDF ↔️ Images
- Split, merge, and compress PDF files
- Designed to be used with a Next.js frontend
- Dockerized for easy deployment
- Render-compatible deployment (`render.yaml` included)

## 📁 Project Structure

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

## 🚀 Getting Started

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
