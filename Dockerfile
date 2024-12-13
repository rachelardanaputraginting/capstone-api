# Menggunakan image dasar Python 3.11 slim
FROM python:3.11-slim

# Install dependencies sistem yang dibutuhkan untuk beberapa pustaka
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip, setuptools, dan wheel ke versi terbaru
RUN pip install --upgrade pip setuptools wheel

# Mengatur working directory di dalam container
WORKDIR /app

# Salin file requirements dan instal dependensi Python
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Meng expose port yang digunakan aplikasi Flask
EXPOSE 8080

# Menjalankan aplikasi menggunakan Gunicorn dengan 4 worker
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8080", "app:app"]
