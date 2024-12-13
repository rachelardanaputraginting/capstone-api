# Gunakan Python 3.11 sebagai base image
FROM python:3.11-slim

# Perbarui sistem dan instal dependensi TensorFlow
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libopenblas-dev \
    liblapack-dev \
    python3-dev \
    libffi-dev \
    libssl-dev \
    libcurl4-openssl-dev \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Perbarui pip ke versi terbaru
RUN pip install --upgrade pip

# Buat direktori kerja
WORKDIR /app

# Salin file requirements.txt
COPY requirements.txt .

# Instal dependensi Python
RUN pip install --no-cache-dir -r requirements.txt

# Salin kode aplikasi
COPY . .

# Ekspose port aplikasi
EXPOSE 8080

# Jalankan aplikasi
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8080", "app:app"]
