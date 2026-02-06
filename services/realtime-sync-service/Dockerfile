# T052: Dockerfile for realtime-sync-service
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install PyJWT for token verification
RUN pip install --no-cache-dir PyJWT>=2.8.0

# Copy application code
COPY src/ ./src/

# Set environment variables
ENV PYTHONPATH=/app
ENV PORT=8002

# Expose the service port
EXPOSE 8002

# Run the application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8002"]
