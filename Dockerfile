# Dockerfile for Amount Detection Service
# Uses Debian-slim image, installs tesseract so OCR works inside the container.
FROM python:3.11-slim

# install system deps (tesseract for OCR and build deps)
RUN apt-get update && apt-get install -y --no-install-recommends \ 
    tesseract-ocr \ 
    libtesseract-dev \ 
    libleptonica-dev \ 
    pkg-config \ 
    gcc \ 
    && rm -rf /var/lib/apt/lists/*

# Create working dir
WORKDIR /app

# Copy requirements and install
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy app code
COPY . /app

# Expose port and run
EXPOSE 5000
ENV FLASK_ENV=production
CMD ["python", "app.py"]
