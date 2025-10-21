# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file
COPY requirements.txt .

# Explicitly uninstall any conflicting fitz package and install dependencies
RUN pip uninstall -y fitz || true && \
    pip install --no-cache-dir -r requirements.txt

# Verify PyMuPDF installation
RUN python -c "import fitz; print(f'PyMuPDF version: {fitz.__version__}')"

# Copy the rest of the application code
COPY . .

# Command to run the application
CMD ["python", "pipeline.py"]