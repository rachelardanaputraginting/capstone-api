# Gunakan Python 3.12-slim sebagai base image
FROM python:3.12-slim

# Install dependencies sistem yang diperlukan
RUN apt-get update && apt-get install -y \
    gcc \
    musl-dev \
    linux-headers \
    postgresql-dev \
    libffi-dev \
    openssl-dev \
    mysql-dev \
    build-essential \
    file 

# Set working directory
WORKDIR /app

# Copy requirements.txt terlebih dahulu
COPY requirements.txt .

# Install dependencies Python dengan opsi tambahan
RUN pip install --no-cache-dir \
    --upgrade pip \
    wheel \
    numpy \
    && pip install --no-cache-dir -r requirements.txt

# Salin file aplikasi
COPY . .

# Expose port yang diperlukan
EXPOSE 8080

# Start aplikasi menggunakan gunicorn
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8080", "app:app"]
