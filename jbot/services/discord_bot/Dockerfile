FROM python

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    ffmpeg \
    libffi-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY services/discord_bot/requirements.txt .

# Upgrade pip and install tools
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the client libraries and service code
COPY clients/ /app/clients/
COPY services/discord_bot/ /app/discord_bot/

# Add clients to Python path
ENV PYTHONPATH="/app:${PYTHONPATH}"

# Run the service
CMD ["python", "-u", "discord_bot/service.py"]