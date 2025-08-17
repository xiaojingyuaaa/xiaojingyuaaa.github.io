# Stage 1: Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Set environment variables to prevent Python from writing .pyc files and to keep output unbuffered
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies that might be needed by 'unstructured'
# For example, libreoffice is needed for .doc/.docx files, tesseract for OCR.
# This is a minimal set; more might be needed depending on the exact documents.
RUN apt-get update && apt-get install -y --no-install-recommends \
    libreoffice \
    tesseract-ocr \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container first to leverage Docker's layer caching
COPY requirements.txt .

# Install Python dependencies
# We use --no-cache-dir to reduce image size
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
# This includes the main app, scripts, and the .env file
COPY ./app /app/app
COPY ./scripts /app/scripts
COPY ./.env /app/.env

# The 'data' and 'vector_store' directories are intended to be mounted as volumes
# in docker-compose, so we don't copy them directly into the image.
# This allows the data and index to persist even if the container is removed.
# We create the directories so the application can write to them if no volume is mounted.
RUN mkdir -p /app/data && mkdir -p /app/vector_store

# Expose the port the app runs on
EXPOSE 8000

# Define the command to run the application
# For production, consider using Gunicorn with Uvicorn workers for better performance and process management.
# Example: CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "-w", "4", "app.main:app", "-b", "0.0.0.0:8000"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
