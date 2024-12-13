FROM python:3.10-slim

# Install system dependencies including mariadb-dev
RUN apt-get update && apt-get install -y \
    build-essential \
    libmariadb-dev \
    libmariadb-dev-compat \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip before installing dependencies
RUN pip install --upgrade pip

# Set working directory
WORKDIR /app

# Menyalin requirements.txt terlebih dahulu
COPY requirements.txt .

# Install Python dependencies with verbose logging for debugging
RUN pip install -v --no-cache-dir -r requirements.txt

# Menyalin aplikasi lainnya
COPY . .

# Expose the required port
EXPOSE 8080

# Start the application with gunicorn
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8080", "app:app"]
