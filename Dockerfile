# Base image
FROM python:3.12-alpine

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Copy secrets
COPY .env /app/.env
COPY credentials.json /workspace/credentials.json

# Expose the required port
EXPOSE 8080

# Start the application
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8080", "app:app"]
