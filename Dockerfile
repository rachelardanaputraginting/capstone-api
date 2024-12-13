# Menggunakan image dasar Python 3.11 slim
FROM python:3.10-slim

# Install dependencies sistem yang dibutuhkan untuk beberapa pustaka
RUN apt-get update && apt-get install -y \
    build-essential \
    libmariadb-dev \
    libjpeg-dev zlib1g-dev libpng-dev \
    gfortran liblapack-dev \
    libc6-dev libstdc++6 \
    libxml2-dev libxslt-dev \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip, setuptools, dan wheel ke versi terbaru
RUN pip install --upgrade pip setuptools wheel

# Menyalin requirements.txt ke dalam image
COPY requirements.txt .

# Mengatur working directory di dalam container
WORKDIR /app

# Install dependencies yang ada di requirements.txt
RUN pip install --no-cache-dir -r requirements.txt || tail -n 20 /root/.pip/pip.log

# Meng expose port yang digunakan aplikasi Flask
EXPOSE 8080

# Menjalankan aplikasi menggunakan Gunicorn dengan 4 worker
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8080", "app:app"]
