# Base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy application code
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 8080

# Set environment variables for Flask
ENV PORT 8080
ENV GOOGLE_APPLICATION_CREDENTIALS="/app/credentials.json"

# Command to run the application
CMD ["flask", "run", "--host=0.0.0.0", "--port=8080"]
