FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY receiver.py .

# Create data directory for storage
RUN mkdir -p /data

# Command to run the application
CMD ["python", "receiver.py"]