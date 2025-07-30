FROM python:3.10-slim

# Install system dependencies
RUN apt update && apt install -y \
    libreoffice \
    unoconv \
    poppler-utils \
    build-essential \
    libpango-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libcairo2 \
    wkhtmltopdf \
    && apt clean && rm -rf /var/lib/apt/lists/*

# Set workdir
WORKDIR /app

# Copy app files
COPY . .

# Install Python deps
RUN pip install --no-cache-dir -r requirements.txt

# Expose port (Render uses PORT env var)
ENV PORT 5000
EXPOSE $PORT

# Run Flask app
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
