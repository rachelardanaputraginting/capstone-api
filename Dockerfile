# Gunakan python 3.10 slim sebagai base image
FROM python:3.10-slim

# Install sistem dependensi yang diperlukan untuk TensorFlow dan pustaka lainnya
RUN apt-get update && apt-get install -y \
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

# Setel direktori kerja
WORKDIR /app

# Salin requirements.txt ke dalam container
COPY requirements.txt .

# Install dependensi Python
RUN pip install --no-cache-dir -r requirements.txt

# Salin seluruh aplikasi ke dalam container
COPY . .

# Tentukan port yang akan diekspos
EXPOSE 8080

# Tentukan command untuk menjalankan aplikasi (ganti dengan sesuai aplikasi Anda)
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8080", "app:app"]
