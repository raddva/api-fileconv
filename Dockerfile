FROM python:3.10-slim

RUN apt update && apt install -y \
    poppler-utils \
    build-essential \
    libpango-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libcairo2 \
    libgl1 \
    libmagic1 \
    && apt clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

ENV PORT=5000
EXPOSE $PORT

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
