# Base image
FROM python:3.10-alpine

# Install system dependencies
RUN apk add --no-cache \
    gcc \
    musl-dev \
    linux-headers \
    postgresql-dev \
    libffi-dev \
    openssl-dev \
    mysql-dev \
    build-base \
    file-dev \
    # Additional dependencies for scientific computing
    lapack-dev \
    g++ \
    libstdc++

# Set working directory
WORKDIR /app

# Copy requirements first
COPY requirements.txt .

# Install Python dependencies with additional options
RUN pip install --no-cache-dir \
    --upgrade pip \
    wheel \
    numpy \
    && pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Expose the required port
EXPOSE 8080

# Start the application with gunicorn
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8080", "app:app"]