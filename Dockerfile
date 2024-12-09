# Base image
FROM python:3.12-alpine

# Install system dependencies
RUN apk add --no-cache \
    gcc \
    musl-dev \
    linux-headers \
    postgresql-dev \
    libffi-dev \
    openssl-dev \
    mysql-dev \
    build-base

# Set working directory
WORKDIR /app

# Copy requirements first
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Expose the required port
EXPOSE 8080

# Start the application
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8080", "app:app"]