# Gunakan Python 3.11-alpine sebagai base image
FROM python:3.11-alpine

# Install dependencies sistem yang dibutuhkan untuk TensorFlow dan aplikasi lainnya
RUN apk add --no-cache \
    gcc \
    musl-dev \
    linux-headers \
    postgresql-dev \
    libffi-dev \
    openssl-dev \
    mysql-dev \
    build-base \
    file-dev  # Install file package yang mencakup libmagic

# Set working directory
WORKDIR /app

# Salin file requirements.txt
COPY requirements.txt .

# Install dependencies Python
RUN pip install --no-cache-dir -r requirements.txt

# Salin aplikasi ke dalam container
COPY . .

# Ekspose port yang diperlukan (misalnya 8080)
EXPOSE 8080

# Jalankan aplikasi dengan gunicorn
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8080", "app:app"]
