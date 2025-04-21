FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install dependencies including FFmpeg for audio processing
RUN apt-get update && apt-get install -y \
    ffmpeg \
    build-essential \
    libffi-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY services/discord_bot/requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the client libraries and service code
COPY clients/ /app/clients/
COPY services/discord_bot/ /app/discord_bot/

# Add clients to Python path
ENV PYTHONPATH="/app:${PYTHONPATH}"

# Run the service
CMD ["python", "-u", "discord_bot/service.py"]