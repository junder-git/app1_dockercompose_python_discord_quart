FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY services/music_central/requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the client libraries and service code
COPY clients/ /app/clients/
COPY services/music_central/ /app/music_central/

# Add clients to Python path
ENV PYTHONPATH="/app:${PYTHONPATH}"

# Expose API port
EXPOSE 5002

# Run the service
CMD ["python", "-u", "music_central/service.py"]