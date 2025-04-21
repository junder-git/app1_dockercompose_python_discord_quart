FROM python

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install tools
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Copy requirements first for better caching
COPY services/quart_web/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the client libraries and service code
COPY clients/ /app/clients/
COPY services/quart_web/ /app/quart_web/

# Add clients to Python path
ENV PYTHONPATH="/app:${PYTHONPATH}"

# Expose web port
EXPOSE 80

# Run the service using Hypercorn
CMD ["hypercorn", "quart_web.service:app", "--bind", "0.0.0.0:80"]