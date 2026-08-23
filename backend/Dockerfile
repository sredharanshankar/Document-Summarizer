FROM python:3.11-slim

# Tesseract is a system binary, not a Python package - this is why the
# backend can't run on pure-serverless hosts that don't allow installing
# system packages. See the README's "OCR Setup" section.
RUN apt-get update \
    && apt-get install -y --no-install-recommends tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
